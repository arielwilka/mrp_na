from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

# Import Models
from .models import (
    WorkCenter, Station, ProductionRoute, RouteStationConfig,
    ProductionPlan, ProductionOrder, ProductionUnit, 
    StationActivityLog, PartInstallationLog
)
from traceability.models import PartMaster 
from vin_record.models import VinRecord, YearCode

# ==========================================
# 1. MASTER DATA SERIALIZERS
# ==========================================
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'work_center', 'code', 'name', 'default_sequence', 'is_finish_point']

class WorkCenterSerializer(serializers.ModelSerializer):
    stations = StationSerializer(many=True, read_only=True)
    class Meta:
        model = WorkCenter
        fields = ['id', 'code', 'name', 'is_continuous', 'stations']

class RouteConfigSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_code = serializers.CharField(source='station.code', read_only=True)
    required_parts = serializers.PrimaryKeyRelatedField(
        source='traceability_triggers', many=True, queryset=PartMaster.objects.all(), write_only=True
    )
    required_parts_names = serializers.StringRelatedField(
        source='traceability_triggers', many=True, read_only=True
    )
    class Meta:
        model = RouteStationConfig
        fields = ['id', 'route', 'station', 'station_name', 'station_code', 'sequence', 'progress_percentage', 'required_parts', 'required_parts_names']

class ProductionRouteSerializer(serializers.ModelSerializer):
    steps = RouteConfigSerializer(many=True, read_only=True)
    product_type_name = serializers.CharField(source='product_type.name', read_only=True)
    class Meta:
        model = ProductionRoute
        fields = ['id', 'name', 'product_type', 'product_type_name', 'is_active', 'steps']

# ==========================================
# 2. OPERATIONAL SERIALIZERS
# ==========================================
class ProductionPlanSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_variant.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True) 
    class Meta:
        model = ProductionPlan
        fields = '__all__'

class ProductionUnitSerializer(serializers.ModelSerializer):
    identity_label = serializers.SerializerMethodField()
    current_station_name = serializers.CharField(source='current_station.name', read_only=True, default='-')
    variant_name = serializers.CharField(source='product_variant.name', read_only=True)
    color_name = serializers.SerializerMethodField()
    class Meta:
        model = ProductionUnit
        fields = ['id', 'origin_order', 'variant_name', 'color_name', 'identity_label', 'internal_id', 'vin_record', 'current_station', 'current_station_name', 'status', 'is_paused', 'pause_reason']
    
    def get_identity_label(self, obj: ProductionUnit):
        return obj.vin_record.full_vin if obj.vin_record else obj.internal_id
    
    def get_color_name(self, obj: ProductionUnit):
        plan = obj.origin_order.plan
        return plan.color.name if plan.color else '-'

# ==========================================
# 3. PRODUCTION ORDER (LOGIC INTIGRASI)
# ==========================================
class ProductionOrderSerializer(serializers.ModelSerializer):
    plan_code = serializers.CharField(source='plan.plan_code', read_only=True)
    product_variant_name = serializers.CharField(source='plan.product_variant.name', read_only=True)
    total_wip = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionOrder
        fields = [
            'id', 'order_number', 'plan', 'plan_code', 'product_variant_name',
            'target_total_qty', 'carried_over_wip_qty', 'new_material_qty',
            'actual_finish_qty', 'actual_reject_qty',
            'status', 'tracking_mode_snapshot', 'created_at', 'total_wip', 'current_wip_qty'
        ]
        read_only_fields = ('order_number', 'carried_over_wip_qty', 'new_material_qty', 'actual_finish_qty', 'actual_reject_qty', 'tracking_mode_snapshot', 'status', 'current_wip_qty')

    def get_total_wip(self, obj):
        return obj.units.filter(status='WIP').count()

    def create(self, validated_data):
        try:
            with transaction.atomic():
                plan = validated_data.get('plan')
                target_qty = validated_data.get('target_total_qty')
                mode = validated_data.get('tracking_mode_snapshot', 'VIN')

                # 1. HITUNG WIP GANTUNG (SISA KEMARIN)
                # Cari unit yg statusnya WIP atau PAUSED untuk Varian yg sama
                # Logic: Order baru ini akan "mengadopsi" unit-unit gantung tersebut
                existing_wip_count = ProductionUnit.objects.filter(
                    product_variant=plan.product_variant,
                    status__in=['WIP', 'PAUSED']
                ).count()

                # 2. HITUNG KEBUTUHAN BARU (NET REQUIREMENT)
                # Rumus: Yang perlu dibuat baru = Target - Sisa WIP
                net_new_needed = target_qty - existing_wip_count
                
                if net_new_needed < 0:
                    net_new_needed = 0

                # 3. BOOKING VIN (Hanya sejumlah Net Needed)
                available_vins = []
                if mode == 'VIN' and net_new_needed > 0:
                    # KUNCI: Cari VIN Available sesuai Varian & Warna
                    available_vins = list(VinRecord.objects.select_for_update().filter(
                        product_type=plan.product_variant.product_type,
                        variant=plan.product_variant,
                        color=plan.color,
                        status='AVAILABLE'
                    ).order_by('serial_number')[:net_new_needed])

                    if len(available_vins) < net_new_needed:
                        raise serializers.ValidationError(
                            f"Stok VIN Tidak Cukup! Target Order: {target_qty}. "
                            f"WIP Gantung: {existing_wip_count}. Butuh Baru: {net_new_needed}. "
                            f"Tersedia di VIN Record: {len(available_vins)}."
                        )

                # 4. CREATE ORDER HEADER
                order = ProductionOrder.objects.create(**validated_data)
                
                # ISI FIELD LOGIC
                order.carried_over_wip_qty = existing_wip_count # WIP Lama (misal 2)
                order.new_material_qty = net_new_needed         # WIP Baru (misal 8)
                
                # PENTING: Current WIP = Target Qty (2 + 8 = 10)
                # Karena order ini bertanggung jawab menyelesaikan SEMUA (Lama + Baru).
                # Nanti saat finish, dia akan mengurangi angka ini. 
                # Jika kita set cuma 8, nanti saat finish ke-9 dan 10 akan error negatif.
                order.current_wip_qty = target_qty 
                
                order.tracking_mode_snapshot = mode
                order.status = 'RELEASED'
                order.save()

                # 5. GENERATE UNIT BARU (Hanya sejumlah Net Needed)
                units_batch = []
                for i in range(net_new_needed):
                    seq_num = i + 1
                    # Internal ID tetap urut per order untuk referensi
                    temp_internal_id = f"{order.order_number}-{seq_num:03d}"
                    
                    vin_obj = None
                    if mode == 'VIN':
                        vin_obj = available_vins[i]
                        vin_obj.status = 'RESERVED'
                        vin_obj.booking_reference = order.order_number
                        vin_obj.save()
                    
                    units_batch.append(ProductionUnit(
                        origin_order=order,
                        product_variant=plan.product_variant,
                        internal_id=temp_internal_id,
                        vin_record=vin_obj,
                        status='WIP'
                    ))
                
                ProductionUnit.objects.bulk_create(units_batch)
                return order

        except Exception as e:
            if isinstance(e, serializers.ValidationError): raise e
            raise serializers.ValidationError({"detail": f"Gagal create order: {str(e)}"})

# ... (History Serializers TETAP SAMA) ...
class PartInstallationLogSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part_master.part_name', read_only=True)
    part_number = serializers.CharField(source='part_master.part_number', read_only=True)
    installed_by_name = serializers.CharField(source='installed_by.username', read_only=True)
    class Meta:
        model = PartInstallationLog
        fields = ['id', 'station', 'part_name', 'part_number', 'serial_number_scanned', 'installed_at', 'installed_by_name']

class StationActivityLogSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    unit_identity = serializers.SerializerMethodField()
    class Meta:
        model = StationActivityLog
        fields = ['id', 'unit', 'unit_identity', 'station_name', 'check_in_time', 'result_status', 'operator_name']
    def get_unit_identity(self, obj: StationActivityLog):
        return obj.unit.vin_record.full_vin if obj.unit.vin_record else obj.unit.internal_id