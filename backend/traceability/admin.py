from django.contrib import admin
from .models import SerialRule, RuleSegment, PartMaster, TraceabilityVersion, TraceabilityRequirement

class RuleSegmentInline(admin.TabularInline):
    model = RuleSegment
    extra = 1

@admin.register(SerialRule)
class SerialRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    inlines = [RuleSegmentInline]

@admin.register(PartMaster)
class PartMasterAdmin(admin.ModelAdmin):
    # Menampilkan Config QC dan Unik Serial
    list_display = ('part_number', 'part_name', 'is_qc_required', 'is_unique_serial', 'validation_rule')
    list_filter = ('is_qc_required', 'is_unique_serial')
    search_fields = ('part_number', 'part_name')

class RequirementInline(admin.TabularInline):
    model = TraceabilityRequirement
    extra = 1
    autocomplete_fields = ['part_master']

@admin.register(TraceabilityVersion)
class TraceabilityVersionAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'version_code', 'valid_from', 'is_active')
    list_filter = ('product_type', 'is_active')
    search_fields = ('product_type__name', 'version_code')
    inlines = [RequirementInline]