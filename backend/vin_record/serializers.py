from rest_framework import serializers
from django.contrib.auth.models import User
from .models import VehicleType, VehicleVariant, VehicleColor, YearCode, VinRecord, VinPrefix

# --- 1. VARIANT & COLOR (Master Data) ---
class VehicleVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleVariant
        fields = ['id', 'name', 'vehicle_type'] # Wajib ada vehicle_type untuk Create

class VehicleColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleColor
        fields = ['id', 'name', 'vehicle_type'] # Wajib ada vehicle_type untuk Create

# --- 2. PREFIX SERIALIZER (FIXED FOR FRONTEND CALCULATION) ---
class VinPrefixSerializer(serializers.ModelSerializer):
    # PENTING: Frontend 'VinCreatePage' butuh 'year_id' untuk mencocokkan dropdown tahun
    year_id = serializers.ReadOnlyField(source='year_code.id') 
    
    # Helper display untuk tabel Master
    vehicle_type_name = serializers.ReadOnlyField(source='vehicle_type.name')
    year_code_label = serializers.ReadOnlyField(source='year_code.year')

    class Meta:
        model = VinPrefix
        fields = [
            'id', 
            'vehicle_type', 'vehicle_type_name',
            'year_code', 'year_id', 'year_code_label', # year_id WAJIB ADA
            'wmi_vds', 'plant_code'
        ]

# --- 3. TYPE SERIALIZER (Nested untuk Frontend Dropdown) ---
class VehicleTypeSerializer(serializers.ModelSerializer):
    variants = VehicleVariantSerializer(many=True, read_only=True)
    colors = VehicleColorSerializer(many=True, read_only=True)
    prefixes = VinPrefixSerializer(many=True, read_only=True)

    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'variants', 'colors', 'prefixes']

# --- 4. YEAR SERIALIZER ---
class YearCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearCode
        fields = '__all__'

# --- 5. VIN RECORD SERIALIZER (FIXED FOR LIST) ---
class VinRecordSerializer(serializers.ModelSerializer):
    # Field Flat String untuk Tampilan Tabel Frontend
    vehicle_type_name = serializers.ReadOnlyField(source='vehicle_type.name')
    production_year_code = serializers.ReadOnlyField(source='production_year.code')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    
    # PENTING: Mengirim nama langsung agar tabel tidak kosong
    variant_name = serializers.ReadOnlyField(source='variant.name')
    color_name = serializers.ReadOnlyField(source='color.name')
    
    class Meta:
        model = VinRecord
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')