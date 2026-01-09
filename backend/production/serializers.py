from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from django.db.models import Max # <--- PENTING

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
        source='traceability_triggers', 
        many=True,
        queryset=PartMaster.objects.all(),
        write_only=True
    )
    required_parts_names = serializers.StringRelatedField(
        source='traceability_triggers',
        many=True,
        read_only=True
    )
    class Meta:
        model = RouteStationConfig
        fields = [
            'id', 'route', 'station', 'station_name', 'station_code', 
            'sequence', 'progress_percentage', 
            'required_parts', 'required_parts_names'
        ]

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
        fields = [
            'id', 'origin_order', 'variant_name', 'color_name',
            'identity_label', 'internal_id', 'vin_record',
            'current_station', 'current_station_name',
            'status', 'is_paused', 'pause_reason'
        ]

    def get_identity_label(self, obj: ProductionUnit):
        if obj.vin_record:
            return obj.vin_record.full_vin
        return obj.internal_id

    def get_color_name(self, obj: ProductionUnit):
        plan = obj.origin_order.plan
        return plan.color.name if plan.color else '-'

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
            'status', 'tracking_mode_snapshot', 'created_at', 'total_wip'
        ]
        read_only_fields = ('order_number', 'carried_over_wip_qty', 'new_material_qty', 'actual_finish_qty', 'actual_reject_qty', 'tracking_mode_snapshot', 'status')

    def get_total_wip(self, obj):
        return obj.units.filter(status='WIP').count()

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # 1. Create Order
                order = ProductionOrder.objects.create(**validated_data)
                
                target_qty = order.target_total_qty
                
                # --- [FIX] INISIALISASI WIP QTY ---
                # Defaultnya 0. Kita set ke target_qty karena semua unit baru dimulai sbg WIP.
                # Ini mencegah error "CHECK constraint failed" saat pengurangan nanti.
                order.current_wip_qty = target_qty 
                
                mode = order.tracking_mode_snapshot
                plan = order.plan 
                product_variant = plan.product_variant
                product_color = plan.color
                
                year_obj = None
                current_serial_int = 0 

                if mode == 'VIN':
                    current_year = timezone.now().year
                    year_obj = YearCode.objects.filter(year=current_year).first()
                    if not year_obj:
                         year_obj, _ = YearCode.objects.get_or_create(year=current_year, defaults={'code': str(current_year)[-1]})
                    
                    # Cek Max Serial Number (Auto Increment)
                    last_vin = VinRecord.objects.filter(
                        product_type=product_variant.product_type,
                        production_year=year_obj
                    ).aggregate(Max('serial_number'))['serial_number__max']

                    if last_vin:
                        try:
                            current_serial_int = int(last_vin)
                        except ValueError:
                            current_serial_int = 0
                
                units_batch = []
                
                for i in range(target_qty):
                    next_serial_int = current_serial_int + 1 + i
                    seq_num_order = i + 1
                    temp_internal_id = f"{order.order_number}-{seq_num_order:03d}"
                    
                    vin_obj = None
                    if mode == 'VIN' and year_obj:
                        dummy_serial = f"{next_serial_int:06d}" 
                        
                        vin_obj = VinRecord.objects.create(
                            product_type=product_variant.product_type,
                            variant=product_variant,
                            color=product_color, 
                            production_year=year_obj,
                            serial_number=dummy_serial, 
                            full_vin=f"TMP-{temp_internal_id}", 
                            status='RESERVED'
                        )
                    
                    units_batch.append(ProductionUnit(
                        origin_order=order,
                        product_variant=product_variant,
                        internal_id=temp_internal_id,
                        vin_record=vin_obj,
                        status='WIP'
                    ))
                
                ProductionUnit.objects.bulk_create(units_batch)
                
                order.status = 'RELEASED'
                order.new_material_qty = target_qty
                order.save() # Save update current_wip_qty tadi
                
                return order

        except Exception as e:
            raise serializers.ValidationError({"detail": f"Gagal membuat order: {str(e)}"})

# ==========================================
# 3. HISTORY & LOG SERIALIZERS
# ==========================================

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
        if obj.unit.vin_record:
            return obj.unit.vin_record.full_vin
        return obj.unit.internal_id