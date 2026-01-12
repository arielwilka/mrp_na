from django.contrib import admin
from .models import Brand, ProductType, ProductVariant, ProductColor

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    # UPDATE: Ganti is_vin_trace dengan tracking_mode
    list_display = ('name', 'code', 'brand', 'tracking_mode', 'has_check_digit')
    list_filter = ('brand', 'tracking_mode', 'has_check_digit')
    search_fields = ('name', 'code')
    autocomplete_fields = ['brand']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'name')
    list_filter = ('product_type__brand',)
    search_fields = ('name', 'product_type__name')
    autocomplete_fields = ['product_type']

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'name', 'code')
    search_fields = ('name', 'code', 'product_type__name')
    autocomplete_fields = ['product_type']