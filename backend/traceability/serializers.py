from rest_framework import serializers
from django.db import transaction
from .models import SerialRule, RuleSegment, PartMaster, TraceabilityVersion, TraceabilityRequirement

# ==========================================
# 1. SERIAL RULE & SEGMENTS
# ==========================================
class RuleSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSegment
        fields = ['id', 'order', 'segment_type', 'start_index', 'length', 'static_value']

class SerialRuleSerializer(serializers.ModelSerializer):
    segments = RuleSegmentSerializer(many=True)

    class Meta:
        model = SerialRule
        fields = ['id', 'name', 'code', 'description', 'segments', 'created_at']

    def create(self, validated_data):
        segments_data = validated_data.pop('segments')
        with transaction.atomic():
            rule = SerialRule.objects.create(**validated_data)
            for seg in segments_data:
                RuleSegment.objects.create(rule=rule, **seg)
        return rule

    def update(self, instance, validated_data):
        segments_data = validated_data.pop('segments', None)
        with transaction.atomic():
            instance.name = validated_data.get('name', instance.name)
            instance.code = validated_data.get('code', instance.code)
            instance.description = validated_data.get('description', instance.description)
            instance.save()

            if segments_data is not None:
                instance.segments.all().delete()
                for seg in segments_data:
                    RuleSegment.objects.create(rule=instance, **seg)
        return instance

# ==========================================
# 2. PART MASTER
# ==========================================
class PartMasterSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='validation_rule.name', read_only=True)
    rule_code = serializers.CharField(source='validation_rule.code', read_only=True)
<<<<<<< HEAD
    
    # [BARU] Tampilkan nama-nama produk yang kompatibel (Read Only)
    compatible_product_names = serializers.SerializerMethodField()

    class Meta:
        model = PartMaster
        # [UPDATE] Tambahkan 'compatible_product_types' ke fields
=======

    class Meta:
        model = PartMaster
        # Update field baru disini
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
        fields = [
            'id', 'part_number', 'part_name', 
            'validation_rule', 'rule_name', 'rule_code',
            'is_qc_required', 'is_unique_serial', 
<<<<<<< HEAD
            'compatible_product_types', 'compatible_product_names', # <--- Field Baru
            'supplier', 'description', 'created_at'
        ]
        
    def get_compatible_product_names(self, obj):
        # Mengembalikan list nama string, misal: ["Fortuner", "Innova"]
        return [p.name for p in obj.compatible_product_types.all()]
=======
            'supplier', 'description', 'created_at'
        ]
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7

# ==========================================
# 3. TRACEABILITY BOM
# ==========================================
class TraceabilityRequirementSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part_master.part_name', read_only=True)
    part_number = serializers.CharField(source='part_master.part_number', read_only=True)
    
    class Meta:
        model = TraceabilityRequirement
        fields = ['id', 'part_master', 'part_name', 'part_number', 'qty', 'is_mandatory']

class TraceabilityVersionSerializer(serializers.ModelSerializer):
    requirements = TraceabilityRequirementSerializer(many=True)
    product_name = serializers.CharField(source='product_type.name', read_only=True)

    class Meta:
        model = TraceabilityVersion
        fields = ['id', 'product_type', 'product_name', 'version_code', 'valid_from', 'is_active', 'requirements', 'created_at']

    def create(self, validated_data):
        requirements_data = validated_data.pop('requirements')
        with transaction.atomic():
            version = TraceabilityVersion.objects.create(**validated_data)
            for req in requirements_data:
                TraceabilityRequirement.objects.create(version=version, **req)
        return version

    def update(self, instance, validated_data):
        requirements_data = validated_data.pop('requirements', None)
        with transaction.atomic():
            instance.product_type = validated_data.get('product_type', instance.product_type)
            instance.version_code = validated_data.get('version_code', instance.version_code)
            instance.valid_from = validated_data.get('valid_from', instance.valid_from)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.save() 

            if requirements_data is not None:
                instance.requirements.all().delete()
                for req in requirements_data:
                    TraceabilityRequirement.objects.create(version=instance, **req)
        return instance