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

# --- 4. PRODUCT TYPE (Master) ---
class ProductTypeSerializer(serializers.ModelSerializer):
    # Nested Serializer (Read Only)
    variants = ProductVariantSerializer(many=True, read_only=True)
    colors = ProductColorSerializer(many=True, read_only=True)
    
    # Read Only Fields
    brand_name = serializers.ReadOnlyField(source='brand.name')
    brand_code = serializers.ReadOnlyField(source='brand.code')
    
    # Display Labels (Text yang enak dibaca Frontend)
    tracking_mode_display = serializers.CharField(source='get_tracking_mode_display', read_only=True)
    scheduling_policy_display = serializers.CharField(source='get_scheduling_policy_display', read_only=True)

    class Meta:
        model = ProductType
        fields = [
            'id', 'brand', 'brand_name', 'brand_code', 
            'name', 'code', 'has_check_digit',
            'tracking_mode',          # VIN / INTERNAL_ID / BATCH
            'tracking_mode_display',  
            'scheduling_policy',      # DAILY_RESET / CONTINUOUS (Baru)
            'scheduling_policy_display',
            'variants', 'colors'
        ]