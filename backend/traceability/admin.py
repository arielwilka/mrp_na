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
    list_display = ('part_number', 'part_name', 'validation_rule')
    search_fields = ('part_number', 'part_name')

# Buat Tampilan Tabel (Inline) untuk Requirements
class RequirementInline(admin.TabularInline):
    model = TraceabilityRequirement
    extra = 1
    autocomplete_fields = ['part_master'] # Biar cari part gampang

@admin.register(TraceabilityVersion)
class TraceabilityVersionAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'version_code', 'valid_from', 'is_active')
    list_filter = ('product_type', 'is_active')
    search_fields = ('product_type__name', 'version_code')
    
    # Menampilkan Form Requirement di dalam Halaman Version
    inlines = [RequirementInline]
    
    # Logic agar hanya ada 1 Versi Aktif per Produk (Opsional/Advanced)
    # Bisa ditambahkan di save_model jika perlu