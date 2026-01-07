from django.contrib import admin
from .models import SerialRule, RuleSegment, PartMaster, TraceabilityVersion, TraceabilityRequirement

class RuleSegmentInline(admin.TabularInline):
    model = RuleSegment
    extra = 1

@admin.register(SerialRule)
class SerialRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    inlines = [RuleSegmentInline] # Bisa edit segmen langsung di dalam Rule

@admin.register(PartMaster)
class PartMasterAdmin(admin.ModelAdmin):
    # Menampilkan Flag Logic QC di tabel
    list_display = ('part_number', 'part_name', 'is_qc_required', 'is_unique_serial', 'validation_rule')
    
    # Filter samping agar mudah mencari mana yang Wajib QC
    list_filter = ('is_qc_required', 'is_unique_serial')
    
    # Search box
    search_fields = ('part_number', 'part_name')

# Buat Tampilan Tabel (Inline) untuk Requirements
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