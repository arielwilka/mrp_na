from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction 
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Models Production
from .models import (
    WorkCenter, Station, ProductionRoute, RouteStationConfig,
    ProductionPlan, ProductionOrder, ProductionUnit,
    StationActivityLog, PartInstallationLog, StationBatchRecord
)
# Models Traceability & QC
from traceability.models import PartMaster
from qc.models import InventoryItem 

# Serializers
from .serializers import (
    WorkCenterSerializer, StationSerializer, 
    ProductionRouteSerializer, RouteConfigSerializer,
    ProductionPlanSerializer, ProductionOrderSerializer, 
    ProductionUnitSerializer
)

# ==========================================
# 1. MASTER DATA VIEWSETS
# ==========================================
class WorkCenterViewSet(viewsets.ModelViewSet):
    queryset = WorkCenter.objects.all().order_by('id')
    serializer_class = WorkCenterSerializer

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all().order_by('default_sequence')
    serializer_class = StationSerializer

class RouteViewSet(viewsets.ModelViewSet):
    queryset = ProductionRoute.objects.all().order_by('name')
    serializer_class = ProductionRouteSerializer

class RouteStationConfigViewSet(viewsets.ModelViewSet):
    queryset = RouteStationConfig.objects.all().select_related('station').order_by('route', 'sequence')
    serializer_class = RouteConfigSerializer

# ==========================================
# 2. PLANNING & ORDER VIEWSETS
# ==========================================
class ProductionPlanViewSet(viewsets.ModelViewSet):
    queryset = ProductionPlan.objects.all().order_by('-id')
    serializer_class = ProductionPlanSerializer

class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all().order_by('-created_at')
    serializer_class = ProductionOrderSerializer

# ==========================================
# 3. SHOP FLOOR LOGIC (OPERATOR)
# ==========================================
class ShopFloorViewSet(viewsets.ViewSet):
    
    # --- A. SCAN UNIT ---
    @action(detail=False, methods=['post'])
    def scan_unit(self, request):
        scan_value = request.data.get('scan_value')
        station_id = request.data.get('station_id')
        
        if not scan_value:
            return Response({"detail": "Scan value kosong."}, status=400)

        # Cari Unit: Prioritas Full VIN
        unit = ProductionUnit.objects.filter(vin_record__full_vin=scan_value).first()
        if not unit:
            unit = ProductionUnit.objects.filter(internal_id=scan_value).first()
        
        if not unit:
            return Response({"detail": "Unit tidak ditemukan."}, status=404)

        # Cek Requirements
        requirements = []
        if station_id:
            active_route = ProductionRoute.objects.filter(
                product_type=unit.product_variant.product_type, is_active=True
            ).first()
            
            if active_route:
                step_config = RouteStationConfig.objects.filter(
                    route=active_route, station_id=station_id
                ).first()
                
                if step_config:
                    for part in step_config.traceability_triggers.all():
                        is_installed = PartInstallationLog.objects.filter(
                            unit=unit, part_master=part
                        ).exists()
                        requirements.append({
                            "part_name": part.part_name,
                            "part_number": part.part_number,
                            "is_scanned": is_installed,
                            "scanned_value": "INSTALLED" if is_installed else "-"
                        })

        serializer = ProductionUnitSerializer(unit)
        return Response({
            "unit": serializer.data,
            "requirements": requirements
        })

    # --- B. SCAN PART (INPUT POLICE) ---
    @action(detail=False, methods=['post'])
    def scan_part(self, request):
        unit_id = request.data.get('unit_id')
        station_id = request.data.get('station_id')
        scanned_barcode = request.data.get('part_barcode')
        
        if not all([unit_id, station_id, scanned_barcode]):
            return Response({"detail": "Data tidak lengkap."}, status=400)

        unit = get_object_or_404(ProductionUnit, pk=unit_id)

        # 1. Validasi BOM
        active_route = ProductionRoute.objects.filter(
            product_type=unit.product_variant.product_type, is_active=True
        ).first()

        step_config = RouteStationConfig.objects.filter(
            route=active_route, station_id=station_id
        ).first()

        if not step_config:
             return Response({"detail": "Station ini tidak terdaftar dalam Route."}, status=400)

        required_parts = step_config.traceability_triggers.all()
        if not required_parts.exists():
             return Response({"detail": "Station ini tidak membutuhkan scan part."}, status=400)

        matched_part = None
        inventory_item = None

        # 2. Matching Barcode
        for part in required_parts:
            # Jalur QC Strict
            if part.is_qc_required:
                item = InventoryItem.objects.filter(
                    part_master=part, serial_number=scanned_barcode
                ).first()
                if item:
                    matched_part = part
                    inventory_item = item
                    break 
            # Jalur Non-QC
            else:
                if part.part_number.upper() in scanned_barcode.upper() or \
                   part.part_name.upper() in scanned_barcode.upper():
                    matched_part = part
                    break
                if required_parts.count() == 1:
                    matched_part = part
                    break

        if not matched_part:
            return Response({"detail": f"Barcode '{scanned_barcode}' tidak valid atau belum lolos QC."}, status=400)

        # 3. Validasi Inventory
        if matched_part.is_qc_required:
            if not inventory_item: return Response({"detail": "Part QC tidak ditemukan."}, status=400)
            if inventory_item.current_status != 'OK':
                return Response({"detail": f"GAGAL: Status part '{inventory_item.current_status}'."}, status=400)

        if matched_part.is_unique_serial:
            if PartInstallationLog.objects.filter(part_master=matched_part, serial_number_scanned=scanned_barcode).exists():
                return Response({"detail": "GAGAL: Serial Number sudah terpasang (Duplikat)."}, status=400)

        # 4. Save
        try:
            with transaction.atomic():
                if inventory_item:
                    item_locked = InventoryItem.objects.select_for_update().get(pk=inventory_item.pk)
                    item_locked.current_status = 'USED'
                    item_locked.save()

                PartInstallationLog.objects.create(
                    unit=unit, station_id=station_id, part_master=matched_part,
                    serial_number_scanned=scanned_barcode,
                    installed_by=request.user if request.user.is_authenticated else None,
                    installed_at=timezone.now()
                )
            return Response({"status": "OK", "matched_part_name": matched_part.part_name, "scanned_sn": scanned_barcode})
        except Exception as e:
            return Response({"detail": f"DB Error: {str(e)}"}, status=500)

    # --- C. PROCESS STATION (FINISH/REJECT + WIP COUNTER) ---
    @action(detail=False, methods=['post'])
    def process_station(self, request):
        unit_id = request.data.get('unit_id')
        station_id = request.data.get('station_id')
        action_type = request.data.get('action') 
        
        unit = get_object_or_404(ProductionUnit, pk=unit_id)
        station = get_object_or_404(Station, pk=station_id)

        try:
            with transaction.atomic():
                unit.current_station = station
                order = unit.origin_order # Ambil Order untuk Update Counter

                if action_type == 'PASS':
                    if station.is_finish_point:
                        # FINISH GOOD: Keluar dari WIP, Masuk Finish
                        unit.status = 'FINISH_PROD'
                        order.actual_finish_qty += 1
                        if order.current_wip_qty > 0:
                            order.current_wip_qty -= 1
                        order.save()
                    else:
                        unit.status = 'WIP'
                        
                elif action_type == 'REJECT':
                    # REJECT: Keluar dari WIP, Masuk Reject
                    unit.status = 'SCRAPPED'
                    order.actual_reject_qty += 1
                    if order.current_wip_qty > 0:
                        order.current_wip_qty -= 1
                    order.save()
                
                unit.save()

                # Log
                StationActivityLog.objects.create(
                    unit=unit, station=station, result_status=action_type,
                    check_out_time=timezone.now(),
                    operator=request.user if request.user.is_authenticated else None
                )
                
                # Batch Record
                batch_rec, _ = StationBatchRecord.objects.get_or_create(
                    production_order=unit.origin_order, station=station
                )
                if action_type == 'PASS': batch_rec.output_good_qty += 1
                elif action_type == 'REJECT': batch_rec.output_reject_qty += 1
                batch_rec.save()

            return Response({"status": f"Unit {action_type}ED"}, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=500)