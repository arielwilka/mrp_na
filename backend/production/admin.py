from django.contrib import admin
from .models import (
    WorkCenter, Station, ProductionRoute, RouteStationConfig,
    ProductionPlan, ProductionOrder, ProductionUnit,
    StationBatchRecord, StationActivityLog, PartInstallationLog
)

# ==========================================
# 1. MASTER LOCATION (Work Center + Stations)
# ==========================================

# Kita buat StationAdmin agar bisa dipanggil via autocomplete
@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'work_center', 'default_sequence', 'is_finish_point')
    search_fields = ('name', 'code', 'work_center__name') # Wajib ada untuk autocomplete
    list_filter = ('work_center',)
    ordering = ('work_center', 'default_sequence')

class StationInline(admin.TabularInline):
    model = Station
    extra = 1
    fields = ('code', 'name', 'default_sequence', 'is_finish_point')

@admin.register(WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_continuous', 'total_stations')
    search_fields = ('code', 'name')
    inlines = [StationInline]

    def total_stations(self, obj):
        return obj.stations.count()
    total_stations.short_description = 'Jml Station'

# ==========================================
# 2. MASTER ROUTE (Route + Config)
# ==========================================
class RouteConfigInline(admin.TabularInline):
    model = RouteStationConfig
    extra = 1
    ordering = ('sequence',)
    filter_horizontal = ('traceability_triggers',) 
    autocomplete_fields = ['station'] # Station sudah aman sekarang

@admin.register(ProductionRoute)
class ProductionRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'is_active')
    list_filter = ('is_active', 'product_type')
    search_fields = ('name', 'product_type__name')
    inlines = [RouteConfigInline]

# ==========================================
# 3. PLANNING & ORDER
# ==========================================
@admin.register(ProductionPlan)
class ProductionPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_code', 'product_variant', 'target_qty', 'start_date', 'realized_qty')
    list_filter = ('start_date', 'product_variant__product_type')
    search_fields = ('plan_code', 'product_variant__name')
    autocomplete_fields = ['product_variant']

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'plan', 'target_total_qty', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'plan__product_variant')
    search_fields = ('order_number', 'plan__plan_code')
    
    readonly_fields = (
        'carried_over_wip_qty', 'new_material_qty', 
        'actual_finish_qty', 'actual_reject_qty', 'tracking_mode_snapshot'
    )

# ==========================================
# 4. OPERATIONAL (Units & Logs)
# ==========================================
@admin.register(ProductionUnit)
class ProductionUnitAdmin(admin.ModelAdmin):
    list_display = ('identity_display', 'origin_order', 'current_station', 'status', 'is_paused')
    list_filter = ('status', 'is_paused', 'current_station', 'origin_order__plan__product_variant')
    search_fields = ('vin_record__full_vin', 'internal_id', 'origin_order__order_number')
    
    # Autocomplete field 'current_station' sekarang akan berfungsi
    autocomplete_fields = ['origin_order', 'vin_record', 'product_variant', 'current_station']
    
    fieldsets = (
        ('Identitas', {
            'fields': ('origin_order', 'product_variant', 'vin_record', 'internal_id')
        }),
        ('Posisi & Status', {
            'fields': ('current_station', 'status', 'is_paused', 'pause_reason')
        }),
    )

    def identity_display(self, obj):
        if obj.vin_record:
            return f"VIN: {obj.vin_record.full_vin}"
        return f"ID: {obj.internal_id}"
    identity_display.short_description = 'Identity'

@admin.register(StationActivityLog)
class StationActivityLogAdmin(admin.ModelAdmin):
    list_display = ('unit', 'station', 'result_status', 'operator', 'check_out_time')
    list_filter = ('result_status', 'station', 'check_out_time')
    search_fields = ('unit__vin_record__full_vin', 'unit__internal_id')
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(PartInstallationLog)
class PartInstallationLogAdmin(admin.ModelAdmin):
    list_display = ('unit', 'part_master', 'serial_number_scanned', 'station', 'installed_at')
    search_fields = ('serial_number_scanned', 'unit__vin_record__full_vin')
    list_filter = ('part_master', 'station')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(StationBatchRecord)
class StationBatchRecordAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'station', 'current_wip_qty', 'output_good_qty')
    list_filter = ('station',)