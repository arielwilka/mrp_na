from rest_framework import serializers
from traceability.models import PartMaster
from .models import InventoryItem, QCInspection, QCTemplate

# Serializer untuk melihat Stok
class InventoryItemSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part_master.part_name', read_only=True)
    part_number = serializers.CharField(source='part_master.part_number', read_only=True)

    class Meta:
        model = InventoryItem
        fields = ['id', 'part_master', 'part_name', 'part_number', 'serial_number', 'current_status', 'updated_at']

# Serializer untuk Form Template
class QCTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCTemplate
        fields = '__all__'

# Serializer KHUSUS Submit QC (Logic Input)
class QCSubmitSerializer(serializers.Serializer):
    part_id = serializers.IntegerField()
    serial_number = serializers.CharField()
    decision = serializers.ChoiceField(choices=['PASS', 'FAIL'])
    qc_data = serializers.JSONField() # Payload data dinamis

class QCInspectionListSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='inventory_item.part_master.part_name', read_only=True)
    part_number = serializers.CharField(source='inventory_item.part_master.part_number', read_only=True)
    serial_number = serializers.CharField(source='inventory_item.serial_number', read_only=True)
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)

    class Meta:
        model = QCInspection
        fields = [
            'id', 'inspection_date', 'judge_decision', 
            'qc_result_data', 'inspector_name', 
            'part_name', 'part_number', 'serial_number'
        ]