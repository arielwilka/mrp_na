from django.contrib import admin
from .models import Brand, ProductType, ProductVariant, ProductColor

# 1. ADMIN UNTUK BRAND
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

# 2. ADMIN UNTUK TIPE KENDARAAN
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'brand', 'has_check_digit', 'is_vin_trace')
    list_filter = ('brand', 'has_check_digit', 'is_vin_trace')
    search_fields = ('name', 'code')
    
    # Agar saat input Tipe, bisa langsung pilih Brand dengan mudah
    autocomplete_fields = ['brand']

# 3. ADMIN UNTUK VARIAN
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'name')
    list_filter = ('product_type__brand',) # Filter berdasarkan Brand via Type
    search_fields = ('name', 'product_type__name')
    autocomplete_fields = ['product_type']

# 4. ADMIN UNTUK WARNA
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'name', 'code')
    search_fields = ('name', 'code', 'product_type__name')
    autocomplete_fields = ['product_type']