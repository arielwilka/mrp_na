from rest_framework import serializers
from django.db import transaction
from django.db.models import Q, Sum

# Import Models
from .models import (
    WorkCenter, Station, ProductionRoute, RouteStationConfig,
    ProductionPlan, ProductionOrder, ProductionUnit, 
    StationActivityLog, PartInstallationLog, StationBatchRecord
)
from traceability.models import PartMaster 
from vin_record.models import VinRecord

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
    required_parts_details = serializers.SerializerMethodField()

    class Meta:
        model = RouteStationConfig
        fields = [
            'id', 'route', 'station', 'station_name', 'station_code', 
            'sequence', 'job_description', 'job_weight', 
            'required_parts', 'required_parts_details'
        ]

    def get_required_parts_details(self, obj):
        return [
            {
                'id': p.id, 
                'part_name': p.part_name, 
                'part_number': p.part_number,
                'is_qc_required': p.is_qc_required
            } 
            for p in obj.traceability_triggers.all()
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
    variant_name = serializers.CharField(source='product_variant.name', read_only=True, default='-')
    color_name = serializers.SerializerMethodField()
    origin_order_number = serializers.CharField(source='origin_order.order_number', read_only=True, default='-')
    full_vin = serializers.CharField(source='vin_record.full_vin', read_only=True, default='-')
    origin_order_status = serializers.CharField(source='origin_order.status', read_only=True)
    class Meta:
        model = ProductionUnit
        fields = [
            'id', 
            'identity_label', 
            'internal_id', 
            'full_vin',
            'status', 
            'is_paused', 
            'pause_reason',
            'current_station', 
            'current_station_name',
            'variant_name', 
            'color_name',
            'origin_order', 
            'origin_order_number',
            'origin_order_status',
            'created_at' # Sudah aman karena Model sudah diupdate
        ]

    def get_identity_label(self, obj: ProductionUnit):
        if obj.vin_record and obj.vin_record.full_vin:
            return obj.vin_record.full_vin
        return obj.internal_id or f"UNIT-{obj.id}"

    def get_color_name(self, obj: ProductionUnit):
        if obj.origin_order and obj.origin_order.plan:
            return obj.origin_order.plan.color.name
        return '-'

# ==========================================
# 3. SHOP FLOOR SPECIAL SERIALIZER
# ==========================================
class ShopFloorDataSerializer(serializers.ModelSerializer):
    vin = serializers.SerializerMethodField()
    job_info = serializers.SerializerMethodField()

    class Meta:
        model = ProductionUnit
        fields = ['id', 'internal_id', 'status', 'current_station', 'vin', 'job_info']

    def get_vin(self, obj):
        return obj.vin_record.full_vin if obj.vin_record else obj.internal_id

    def get_job_info(self, obj):
        station_id = self.context.get('station_id')
        if not station_id: return None
        
        active_route = ProductionRoute.objects.filter(
            product_type=obj.product_variant.product_type, is_active=True
        ).first()
        if not active_route: return None

        config = RouteStationConfig.objects.filter(route=active_route, station_id=station_id).first()
        if not config: return None

        requirements = []
        for part in config.traceability_triggers.all():
            is_installed = PartInstallationLog.objects.filter(unit=obj, part_master=part).exists()
            requirements.append({
                'part_id': part.id,
                'part_name': part.part_name,
                'part_number': part.part_number,
                'is_scanned': is_installed,
                'status': "INSTALLED" if is_installed else "PENDING"
            })

        return {
            'description': config.job_description,
            'weight': config.job_weight,
            'bom_requirements': requirements
        }

# ==========================================
# 4. PRODUCTION ORDER SERIALIZERS
# ==========================================
class ProductionOrderSerializer(serializers.ModelSerializer):
    """
    Serializer Ringan untuk List View (Tanpa list units)
    """
    plan_code = serializers.CharField(source='plan.plan_code', read_only=True)
    product_variant_name = serializers.CharField(source='plan.product_variant.name', read_only=True)
    total_wip = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionOrder
        fields = [
            'id', 'order_number', 'plan', 'plan_code', 'product_variant_name',
            'target_total_qty', 'carried_over_wip_qty', 'new_material_qty',
            'actual_finish_qty', 'actual_reject_qty',
            'status', 'tracking_mode_snapshot', 'created_at', 'closed_at',
            'total_wip', 'current_wip_qty'
        ]
        read_only_fields = (
            'order_number', 'carried_over_wip_qty', 'new_material_qty', 
            'actual_finish_qty', 'actual_reject_qty', 
            'tracking_mode_snapshot', 'status', 'current_wip_qty', 'closed_at'
        )

    def get_total_wip(self, obj):
        # Menggunakan related_name='units' dari Model
        return obj.units.filter(status='WIP').count()

    def validate(self, data):
        plan = data.get('plan')
        target_qty = data.get('target_total_qty')

        if not plan or not target_qty:
            return data

        if target_qty <= 0:
            raise serializers.ValidationError({"target_total_qty": "Jumlah order harus lebih dari 0."})

        allocated_qty = ProductionOrder.objects.filter(
            plan=plan
        ).exclude(status='CANCELLED').aggregate(
            total=Sum('target_total_qty')
        )['total'] or 0

        remaining_quota = plan.target_qty - allocated_qty

        if target_qty > remaining_quota:
            raise serializers.ValidationError({
                "target_total_qty": (
                    f"Over Limit! Target Plan: {plan.target_qty}. "
                    f"Sisa tersedia: {remaining_quota}. Input: {target_qty}."
                )
            })
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                plan = validated_data.get('plan')
                target_qty = validated_data.get('target_total_qty')
                mode = plan.product_variant.product_type.tracking_mode
                
                # Logic WIP Carry Over
                wip_units_queryset = ProductionUnit.objects.select_for_update().filter(
                    product_variant=plan.product_variant,
                    status__in=['WIP', 'PAUSED']
                ).filter(
                    Q(origin_order__isnull=True) | Q(origin_order__status='CLOSED')
                )
                
                existing_wip_count = wip_units_queryset.count()
                if mode == 'BATCH': existing_wip_count = 0

                net_new_needed = target_qty - existing_wip_count
                if net_new_needed < 0: net_new_needed = 0

                # Logic VIN Reservation
                available_vins = []
                if mode == 'VIN' and net_new_needed > 0:
                    available_vins = list(VinRecord.objects.select_for_update().filter(
                        product_type=plan.product_variant.product_type,
                        variant=plan.product_variant,
                        color=plan.color,
                        status='AVAILABLE'
                    ).order_by('serial_number')[:net_new_needed])

                    if len(available_vins) < net_new_needed:
                        raise serializers.ValidationError(f"Stok VIN Tidak Cukup! Perlu: {net_new_needed}, Ada: {len(available_vins)}")

                order = ProductionOrder.objects.create(**validated_data)
                order.carried_over_wip_qty = existing_wip_count
                order.new_material_qty = net_new_needed
                order.current_wip_qty = existing_wip_count + net_new_needed 
                order.tracking_mode_snapshot = mode
                order.status = 'RELEASED'
                order.save()

                # Assign Units
                if mode in ['VIN', 'INTERNAL_ID']:
                    if existing_wip_count > 0:
                        wip_units_queryset.update(origin_order=order)
                    
                    units_batch = []
                    for i in range(net_new_needed):
                        seq_num = i + 1
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
                            status='WIP'# Default status awal
                        ))
                    ProductionUnit.objects.bulk_create(units_batch)
                
                return order
        except Exception as e:
            if isinstance(e, serializers.ValidationError): raise e
            raise serializers.ValidationError({"detail": f"Gagal create order: {str(e)}"})

class ProductionOrderDetailSerializer(ProductionOrderSerializer):
    """
    Serializer Berat untuk Detail View (Include List Units).
    Digunakan saat Supervisor membuka detail SPK.
    """
    units = ProductionUnitSerializer(many=True, read_only=True)
    
    class Meta(ProductionOrderSerializer.Meta):
        fields = ProductionOrderSerializer.Meta.fields + ['units']

# ==========================================
# 5. LOG SERIALIZERS
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
        return obj.unit.vin_record.full_vin if obj.unit.vin_record else obj.unit.internal_id