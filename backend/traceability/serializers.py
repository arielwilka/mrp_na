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
        # id dikirim agar frontend bisa tracking, tapi saat save kita recreate

class SerialRuleSerializer(serializers.ModelSerializer):
    # Nested Serializer: Menerima list object segments
    segments = RuleSegmentSerializer(many=True)

    class Meta:
        model = SerialRule
        fields = ['id', 'name', 'code', 'description', 'segments', 'created_at']

    # --- LOGIC CREATE NESTED (Header + Segments) ---
    def create(self, validated_data):
        segments_data = validated_data.pop('segments')
        
        with transaction.atomic(): # Atomic: Jika gagal di tengah, rollback semua
            rule = SerialRule.objects.create(**validated_data)
            
            # Buat segmen-segmennya
            for seg in segments_data:
                RuleSegment.objects.create(rule=rule, **seg)
            
        return rule

    # --- LOGIC UPDATE NESTED ---
    def update(self, instance, validated_data):
        segments_data = validated_data.pop('segments', None)
        
        with transaction.atomic():
            # 1. Update Header
            instance.name = validated_data.get('name', instance.name)
            instance.code = validated_data.get('code', instance.code)
            instance.description = validated_data.get('description', instance.description)
            instance.save()

            # 2. Update Segments (Strategy: Replace All / Delete Insert)
            # Ini cara paling aman untuk menangani perubahan urutan atau penghapusan baris
            if segments_data is not None:
                instance.segments.all().delete()
                for seg in segments_data:
                    RuleSegment.objects.create(rule=instance, **seg)

        return instance


# ==========================================
# 2. PART MASTER
# ==========================================

class PartMasterSerializer(serializers.ModelSerializer):
    # Read-only fields untuk mempermudah tampilan di Frontend
    rule_name = serializers.CharField(source='validation_rule.name', read_only=True)
    rule_code = serializers.CharField(source='validation_rule.code', read_only=True)

    class Meta:
        model = PartMaster
        fields = ['id', 'part_number', 'part_name', 'validation_rule', 'rule_name', 'rule_code', 'supplier', 'description', 'created_at']


# ==========================================
# 3. TRACEABILITY VERSION & REQUIREMENTS (BOM)
# ==========================================

class TraceabilityRequirementSerializer(serializers.ModelSerializer):
    # Read-only fields dari PartMaster
    part_name = serializers.CharField(source='part_master.part_name', read_only=True)
    part_number = serializers.CharField(source='part_master.part_number', read_only=True)
    
    class Meta:
        model = TraceabilityRequirement
        fields = ['id', 'part_master', 'part_name', 'part_number', 'qty', 'is_mandatory']

class TraceabilityVersionSerializer(serializers.ModelSerializer):
    # Nested Serializer: Menerima list requirements
    requirements = TraceabilityRequirementSerializer(many=True)
    
    # Info tambahan dari ProductType
    product_name = serializers.CharField(source='product_type.name', read_only=True)

    class Meta:
        model = TraceabilityVersion
        fields = ['id', 'product_type', 'product_name', 'version_code', 'valid_from', 'is_active', 'requirements', 'created_at']

    # --- LOGIC CREATE VERSION ---
    def create(self, validated_data):
        requirements_data = validated_data.pop('requirements')
        
        with transaction.atomic():
            # 1. Create Header (Model.save() akan otomatis handle auto-switch is_active)
            version = TraceabilityVersion.objects.create(**validated_data)
            
            # 2. Create Details
            for req in requirements_data:
                TraceabilityRequirement.objects.create(version=version, **req)
                
        return version

    # --- LOGIC UPDATE VERSION ---
    def update(self, instance, validated_data):
        requirements_data = validated_data.pop('requirements', None)
        
        with transaction.atomic():
            # 1. Update Header
            instance.product_type = validated_data.get('product_type', instance.product_type)
            instance.version_code = validated_data.get('version_code', instance.version_code)
            instance.valid_from = validated_data.get('valid_from', instance.valid_from)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.save() # Trigger logic auto-switch di models.py

            # 2. Update Details (Replace All)
            if requirements_data is not None:
                instance.requirements.all().delete()
                for req in requirements_data:
                    TraceabilityRequirement.objects.create(version=instance, **req)

        return instance