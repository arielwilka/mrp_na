from rest_framework import serializers
from django.contrib.auth.models import User
from .models import YearCode, VinRecord, VinPrefix

# --- 1. PREFIX SERIALIZER ---
class VinPrefixSerializer(serializers.ModelSerializer):
    year_id = serializers.ReadOnlyField(source='year_code.id')
    product_type_name = serializers.ReadOnlyField(source='product_type.name')
    year_code_label = serializers.ReadOnlyField(source='year_code.year')
    
    # UPDATE: Tampilkan tracking_mode string (Ex: "VIN", "BATCH")
    tracking_mode = serializers.ReadOnlyField(source='product_type.tracking_mode')

    class Meta:
        model = VinPrefix
        fields = [
            'id', 
            'product_type', 'product_type_name', 'tracking_mode',
            'year_code', 'year_id', 'year_code_label',
            'wmi_vds', 'plant_code', 'static_ninth_digit'
        ]

    def validate(self, data):
        product_type = data.get('product_type')

        # Ambil dari instance jika update partial
        if not product_type and self.instance:
            product_type = self.instance.product_type

        # UPDATE LOGIC: Tolak jika tracking_mode BUKAN VIN
        if product_type and product_type.tracking_mode != 'VIN':
            raise serializers.ValidationError({
                "product_type": f"Tipe '{product_type.name}' mode trackingnya '{product_type.tracking_mode}'. Wajib 'VIN' untuk setting prefix."
            })

        return data

# --- 2. YEAR SERIALIZER ---
class YearCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearCode
        fields = '__all__'

# --- 3. VIN RECORD SERIALIZER ---
class VinRecordSerializer(serializers.ModelSerializer):
    # Helper Display
    product_type_name = serializers.ReadOnlyField(source='product_type.name')
    production_year_code = serializers.ReadOnlyField(source='production_year.code')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    variant_name = serializers.ReadOnlyField(source='variant.name')
    color_name = serializers.ReadOnlyField(source='color.name')
    
    class Meta:
        model = VinRecord
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'status', 'booking_reference')