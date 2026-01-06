from rest_framework import serializers
from .models import Brand, ProductType, ProductVariant, ProductColor

# --- 1. BRAND ---
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

# --- 2. VARIANT ---
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'product_type']

# --- 3. COLOR ---
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['id', 'name', 'code', 'product_type']

# --- 4. VEHICLE TYPE (Master) ---
class ProductTypeSerializer(serializers.ModelSerializer):
    # Nested Serializer untuk tampilan di Tabel Master (Read Only)
    variants = ProductVariantSerializer(many=True, read_only=True)
    colors = ProductColorSerializer(many=True, read_only=True)
    
    # Menampilkan nama brand (bukan cuma ID)
    brand_name = serializers.ReadOnlyField(source='brand.name')
    brand_code = serializers.ReadOnlyField(source='brand.code')

    class Meta:
        model = ProductType
        fields = [
            'id', 'brand', 'brand_name', 'brand_code', 
            'name', 'code', 'has_check_digit',
            'is_vin_trace', 
            'variants', 'colors'
        ]