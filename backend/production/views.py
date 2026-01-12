from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction 
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

# Models
from .models import (
    WorkCenter, Station, ProductionRoute, RouteStationConfig,
    ProductionPlan, ProductionOrder, ProductionUnit,
    StationActivityLog, PartInstallationLog, StationBatchRecord,
    DailyStationOutput
)
from traceability.models import PartMaster
from qc.models import InventoryItem 

# Serializers
from .serializers import (
    WorkCenterSerializer, StationSerializer, 
    ProductionRouteSerializer, RouteConfigSerializer,
    ProductionPlanSerializer, 
    ProductionOrderSerializer, ProductionOrderDetailSerializer, # <--- Import Serializer Detail
    ProductionUnitSerializer, ShopFloorDataSerializer
)

# --- CLASS PAGINATION ---
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

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

class ProductionPlanViewSet(viewsets.ModelViewSet):
    queryset = ProductionPlan.objects.all().order_by('-id')
    serializer_class = ProductionPlanSerializer

# ==========================================
# 2. PRODUCTION UNIT VIEWSET (MONITORING)
# ==========================================
class ProductionUnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet Utama untuk Monitoring Unit WIP & Aksi Supervisor.
    """
    queryset = ProductionUnit.objects.select_related(
        'product_variant',
        'current_station',
        'origin_order',
        'vin_record'
    ).order_by('-id')
    
    serializer_class = ProductionUnitSerializer
    pagination_class = StandardPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    filterset_fields = {
        'status': ['exact'],
        'current_station': ['exact'],
        'origin_order': ['exact'],
    }
    
    search_fields = [
        'internal_id', 
        'vin_record__full_vin', 
        'origin_order__order_number'
    ]

    # --- [BARU] START MANUAL ACTION ---
    @action(detail=True, methods=['post'])
    def start_manual(self, request, pk=None):
        """
        Action untuk Supervisor memulai unit secara manual.
        Syarat: Unit belum masuk station manapun (current_station IS NULL).
        """
        unit = self.get_object()
        
        # [UPDATE] Validasi diganti: Cek apakah sudah punya station
        if unit.current_station is not None:
             return Response({
                 "detail": f"Gagal. Unit sudah berada di station {unit.current_station.name}."
             }, status=400)

        # Cek jika sudah selesai/scrap
        if unit.status in ['FINISH_PROD', 'SCRAPPED']:
            return Response({"detail": "Unit sudah selesai atau di-scrap."}, status=400)
        
        # Cari Station Pertama
        first_route_config = RouteStationConfig.objects.filter(
            route__product_type=unit.product_variant.product_type,
            route__is_active=True
        ).order_by('sequence').first()

        if not first_route_config:
            return Response({"detail": "Route tidak ditemukan untuk produk ini."}, status=400)

        try:
            with transaction.atomic():
                # Pastikan status WIP (jika sebelumnya Planned/Paused)
                unit.status = 'WIP' 
                unit.current_station = first_route_config.station
                unit.save()
                
                StationActivityLog.objects.create(
                    unit=unit,
                    station=first_route_config.station,
                    result_status='START_MANUAL',
                    check_in_time=timezone.now(),
                    operator=request.user if request.user.is_authenticated else None
                )
            
            return Response({"status": "Unit Started Manually", "station": first_route_config.station.name})
        except Exception as e:
            return Response({"detail": str(e)}, status=500)

# ==========================================
# 3. ORDER VIEWSET (HANDOVER & POLICY)
# ==========================================
class ProductionOrderViewSet(viewsets.ModelViewSet):
    queryset = ProductionOrder.objects.all().order_by('-created_at')
    # Default serializer (untuk list)
    serializer_class = ProductionOrderSerializer 
    pagination_class = StandardPagination

    # [PENTING] Switch Serializer: List (Ringan) vs Detail (Berat/Lengkap)
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductionOrderDetailSerializer
        return ProductionOrderSerializer

    @action(detail=True, methods=['post'])
    def handover(self, request, pk=None):
        order = self.get_object()
        
        if order.status == 'CLOSED':
            return Response({"detail": "Order sudah ditutup sebelumnya."}, status=400)

        policy = order.plan.product_variant.product_type.scheduling_policy
        if policy == 'CONTINUOUS':
            return Response({
                "detail": "Gagal: Order ini bertipe CONTINUOUS. Tidak perlu handover harian."
            }, status=400)

        try:
            with transaction.atomic():
                leftover_units = order.units.filter(status__in=['WIP', 'PAUSED'])
                count = leftover_units.count()
                
                leftover_units.update(origin_order=None)
                
                order.status = 'CLOSED'
                order.closed_at = timezone.now()
                order.save()

            return Response({
                "status": "OK",
                "message": f"Order ditutup. {count} unit WIP telah di-handover."
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=500)

# ==========================================
# 4. SHOP FLOOR LOGIC (OPERATOR TABLET)
# ==========================================
class ShopFloorViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def scan_unit(self, request):
        scan_value = request.data.get('scan_value')
        station_id = request.data.get('station_id')
        
        if not scan_value: return Response({"detail": "Scan value kosong."}, status=400)
        
        # 1. CEK APAKAH SCAN ADALAH SPK (Mode BATCH)
        if "SPK-" in scan_value:
            order = ProductionOrder.objects.filter(order_number=scan_value).first()
            if order:
                if order.tracking_mode_snapshot == 'BATCH':
                    batch_rec, _ = StationBatchRecord.objects.get_or_create(
                        production_order=order, station_id=station_id
                    )
                    return Response({
                        "mode": "BATCH",
                        "order_id": order.id,
                        "order_number": order.order_number,
                        "product_name": order.plan.product_variant.name,
                        "target_qty": order.target_total_qty,
                        "current_output": batch_rec.output_good_qty,
                        "current_reject": batch_rec.output_reject_qty
                    })
                else:
                    return Response({"detail": "Order ini mode VIN/Unit. Silakan scan Unit."}, status=400)

        # 2. CEK APAKAH SCAN ADALAH VIN/INTERNAL ID (Mode UNIT)
        unit = ProductionUnit.objects.filter(vin_record__full_vin=scan_value).first()
        if not unit:
            unit = ProductionUnit.objects.filter(internal_id=scan_value).first()
        
        if not unit: return Response({"detail": "Unit/SPK tidak ditemukan."}, status=404)

        # [LOGIC BARU] VALIDASI POSISI UNIT
        # Apakah unit ada di stasiun ini? (Kasus Start Manual atau Resume)
        is_at_station = (unit.current_station_id == int(station_id)) and (unit.status == 'WIP')
        
        # Jika tidak, apakah ini unit baru PLANNED yang mau masuk Station 1?
        # (Optional: jika ingin operator bisa start tanpa supervisor)
        # ... logic skipped for strict supervisor flow ...

        serializer = ShopFloorDataSerializer(unit, context={'station_id': station_id})
        data = serializer.data
        data['mode'] = 'UNIT'
        
        # Tambahkan flag warning jika unit sebenarnya tidak ada di sini
        if not is_at_station and unit.current_station:
             data['warning'] = f"Unit tercatat di: {unit.current_station.name}. Lanjutkan?"
             # Frontend bisa memutuskan memblokir atau memberi konfirmasi
        
        return Response(data)

    @action(detail=False, methods=['post'])
    def scan_part(self, request):
        unit_id = request.data.get('unit_id')
        station_id = request.data.get('station_id')
        scanned_barcode = request.data.get('part_barcode')
        
        if not all([unit_id, station_id, scanned_barcode]): 
            return Response({"detail": "Data tidak lengkap."}, status=400)

        unit = get_object_or_404(ProductionUnit, pk=unit_id)
        
        active_route = ProductionRoute.objects.filter(product_type=unit.product_variant.product_type, is_active=True).first()
        step_config = RouteStationConfig.objects.filter(route=active_route, station_id=station_id).first()
        
        if not step_config: return Response({"detail": "Station tidak ada di Route."}, status=400)
        
        required_parts = step_config.traceability_triggers.all()
        matched_part = None
        inventory_item = None

        # Logic Pencocokan Part
        for part in required_parts:
            if part.is_qc_required:
                item = InventoryItem.objects.filter(part_master=part, serial_number=scanned_barcode).first()
                if item: matched_part = part; inventory_item = item; break 
            else:
                if part.part_number.upper() in scanned_barcode.upper() or part.part_name.upper() in scanned_barcode.upper():
                    matched_part = part; break
                if required_parts.count() == 1: matched_part = part; break

        if not matched_part: return Response({"detail": "Barcode salah/tidak valid."}, status=400)

        # Validasi QC
        if matched_part.is_qc_required:
            if not inventory_item: return Response({"detail": "Part QC tidak ditemukan."}, status=400)
            if inventory_item.current_status != 'OK': return Response({"detail": "Status Part NG/HOLD."}, status=400)
            if inventory_item.current_status == 'USED': return Response({"detail": "Part SUDAH TERPAKAI."}, status=400)

        if matched_part.is_unique_serial:
            if PartInstallationLog.objects.filter(part_master=matched_part, serial_number_scanned=scanned_barcode).exists():
                return Response({"detail": "Serial Number Duplikat."}, status=400)

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
            return Response({"status": "OK", "matched_part_name": matched_part.part_name})
        except Exception as e:
            return Response({"detail": str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def process_station(self, request):
        unit_id = request.data.get('unit_id')
        station_id = request.data.get('station_id')
        action_type = request.data.get('action') 
        
        unit = get_object_or_404(ProductionUnit, pk=unit_id)
        station = get_object_or_404(Station, pk=station_id)
        today = timezone.now().date()

        try:
            with transaction.atomic():
                # Jika unit baru Start Manual (Posisi Station 1, Status WIP),
                # Operator Station 1 menekan PASS -> Unit dianggap selesai Station 1 dan siap ke Station 2.
                # Namun dalam model sederhana, current_station menandakan "Posisi Terakhir Diketahui".
                # Jadi jika PASS, kita bisa biarkan current_station di sini (Completed state)
                # atau jika Anda punya logika sequence, pindahkan ke next station.
                
                # Di sini kita pakai logika simple: Update Current Station ke tempat proses dilakukan
                unit.current_station = station
                order = unit.origin_order
                if order: order = ProductionOrder.objects.select_for_update().get(pk=order.pk)

                if action_type == 'PASS':
                    if station.is_finish_point:
                        unit.status = 'FINISH_PROD'
                        if order:
                            order.actual_finish_qty += 1
                            if order.current_wip_qty > 0: order.current_wip_qty -= 1
                    else:
                        unit.status = 'WIP'
                elif action_type == 'REJECT':
                    unit.status = 'SCRAPPED'
                    if order:
                        order.actual_reject_qty += 1
                        if order.current_wip_qty > 0: order.current_wip_qty -= 1
                
                if order: order.save()
                unit.save()

                StationActivityLog.objects.create(
                    unit=unit, station=station, result_status=action_type,
                    check_out_time=timezone.now(),
                    operator=request.user if request.user.is_authenticated else None
                )
                
                if unit.origin_order:
                    batch_rec, _ = StationBatchRecord.objects.get_or_create(
                        production_order=unit.origin_order, station=station
                    )
                    if action_type == 'PASS': batch_rec.output_good_qty += 1
                    elif action_type == 'REJECT': batch_rec.output_reject_qty += 1
                    batch_rec.save()

                    daily_stat, _ = DailyStationOutput.objects.get_or_create(
                        production_order=unit.origin_order, station=station, date=today
                    )
                    if action_type == 'PASS': daily_stat.qty_good += 1
                    elif action_type == 'REJECT': daily_stat.qty_reject += 1
                    daily_stat.save()

            return Response({"status": f"Unit {action_type}ED"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def process_batch(self, request):
        order_id = request.data.get('order_id')
        station_id = request.data.get('station_id')
        type_act = request.data.get('type') 
        qty = int(request.data.get('qty', 1))

        order = get_object_or_404(ProductionOrder, pk=order_id)
        station = get_object_or_404(Station, pk=station_id)
        today = timezone.now().date()

        with transaction.atomic():
            batch_rec, _ = StationBatchRecord.objects.select_for_update().get_or_create(
                production_order=order, station=station
            )
            if type_act == 'GOOD': batch_rec.output_good_qty += qty
            elif type_act == 'REJECT': batch_rec.output_reject_qty += qty
            batch_rec.save()

            daily_stat, _ = DailyStationOutput.objects.select_for_update().get_or_create(
                production_order=order, station=station, date=today
            )
            if type_act == 'GOOD': daily_stat.qty_good += qty
            elif type_act == 'REJECT': daily_stat.qty_reject += qty
            daily_stat.save()

            order = ProductionOrder.objects.select_for_update().get(pk=order.pk)
            if type_act == 'GOOD' and station.is_finish_point:
                 order.actual_finish_qty += qty
            elif type_act == 'REJECT':
                 order.actual_reject_qty += qty
            order.save()

        return Response({
            "status": "OK", 
            "current_output": batch_rec.output_good_qty,
            "today_output": daily_stat.qty_good 
        })