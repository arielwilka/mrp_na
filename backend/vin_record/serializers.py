from rest_framework import serializers
from django.contrib.auth.models import User
from .models import YearCode, VinRecord, VinPrefix

# --- Import Helper untuk ReadOnlyField ---
# Kita tidak perlu mengimport Serializer lengkap dari product 
# jika tujuannya hanya untuk CRUD VIN Record, cukup referensi ID.

# --- 1. PREFIX SERIALIZER ---
class VinPrefixSerializer(serializers.ModelSerializer):
    year_id = serializers.ReadOnlyField(source='year_code.id')
    product_type_name = serializers.ReadOnlyField(source='product_type.name')
    year_code_label = serializers.ReadOnlyField(source='year_code.year')
    is_trace_active = serializers.ReadOnlyField(source='product_type.is_vin_trace')
    class Meta:
        model = VinPrefix
        fields = [
            'id', 
            'product_type', 'product_type_name','is_trace_active',
            'year_code', 'year_id', 'year_code_label',
            'wmi_vds', 'plant_code', 'static_ninth_digit'
        ]
    # --- VALIDASI BACKEND ---
    def validate(self, data):
        # 1. Ambil object product_type dari input
        product_type = data.get('product_type')

        # 2. Cek apakah ada update (instance) atau create baru
        # Jika partial update, mungkin product_type tidak dikirim, jadi ambil dari instance lama
        if not product_type and self.instance:
            product_type = self.instance.product_type

        # 3. LOGIC UTAMA: Tolak jika is_vin_trace False
        if product_type and not product_type.is_vin_trace:
            raise serializers.ValidationError({
                "product_type": f"Tipe '{product_type.name}' diset 'No Trace'. Tidak diizinkan membuat konfigurasi VIN."
            })

        return data

# --- 2. YEAR SERIALIZER ---
class YearCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearCode
        fields = '__all__'

# --- 3. VIN RECORD SERIALIZER ---
class VinRecordSerializer(serializers.ModelSerializer):
    # Helper Display (Flat)
    product_type_name = serializers.ReadOnlyField(source='product_type.name')
    production_year_code = serializers.ReadOnlyField(source='production_year.code')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    
    # Mengambil nama variant & color dari relasi (Product App)
    variant_name = serializers.ReadOnlyField(source='variant.name')
    color_name = serializers.ReadOnlyField(source='color.name')
    
    class Meta:
        model = VinRecord
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at')