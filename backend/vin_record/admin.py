from django.contrib import admin
from .models import YearCode, VinPrefix, VinRecord
from product.models import ProductType

# 1. ADMIN UNTUK TAHUN
@admin.register(YearCode)
class YearCodeAdmin(admin.ModelAdmin):
    list_display = ('year', 'code')
    ordering = ('-year',)
    search_fields = ('year', 'code') 

# 2. ADMIN UNTUK PREFIX
@admin.register(VinPrefix)
class VinPrefixAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'year_code', 'wmi_vds', 'plant_code')
    list_filter = ('product_type', 'year_code')
    search_fields = ('product_type__name', 'wmi_vds')
    autocomplete_fields = ['year_code'] 
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_type":
            # UPDATE: Gunakan tracking_mode='VIN'
            kwargs["queryset"] = ProductType.objects.filter(tracking_mode='VIN')
            
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# 3. ADMIN UNTUK VIN RECORD
@admin.register(VinRecord)
class VinRecordAdmin(admin.ModelAdmin):
    list_display = ('full_vin', 'serial_number', 'product_type', 'variant', 'production_year', 'created_at', 'status')
    list_filter = ('product_type', 'production_year', 'status', 'created_at')
    search_fields = ('full_vin', 'serial_number')
    readonly_fields = ('full_vin', 'created_at', 'created_by')
    
    autocomplete_fields = ['variant', 'color', 'production_year']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product_type":
            # UPDATE: Gunakan tracking_mode='VIN'
            kwargs["queryset"] = ProductType.objects.filter(tracking_mode='VIN')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)