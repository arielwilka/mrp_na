from rest_framework import serializers
from .models import BatteryRecord

class BatteryRecordSerializer(serializers.ModelSerializer):
    # Field tambahan (Read Only) untuk kemudahan di Frontend
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, default='System')
    created_at_fmt = serializers.DateTimeField(source='created_at', format="%d/%m/%Y %H:%M", read_only=True)

    class Meta:
        model = BatteryRecord
        fields = [
            'id', 
            'serial_number', 
            'condition', 
            'voltage', 
            'screenshot',      # Ini akan mereturn URL lengkap gambar
            'created_at', 
            'created_at_fmt',
            'created_by_name'
        ]
        read_only_fields = ['created_at', 'created_by']
    
    # Validasi Custom: Paksa Upper Case untuk SN
    def validate_serial_number(self, value):
        return value.upper().strip()