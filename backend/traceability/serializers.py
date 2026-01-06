from rest_framework import serializers
from .models import NumberingRule, PartMaster, PartItem

class NumberingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberingRule
        fields = '__all__'

class PartMasterSerializer(serializers.ModelSerializer):
    # Tampilkan detail rule agar di frontend enak dibaca (opsional)
    numbering_rule_name = serializers.CharField(source='numbering_rule.name', read_only=True)

    class Meta:
        model = PartMaster
        fields = '__all__'

class PartItemSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part_master.name', read_only=True)
    part_number = serializers.CharField(source='part_master.part_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = PartItem
        fields = '__all__'