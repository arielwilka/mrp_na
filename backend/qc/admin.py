from django.contrib import admin
from .models import QCTemplate, InventoryItem, QCInspection

# --- 1. QC TEMPLATE ADMIN ---
@admin.register(QCTemplate)
class QCTemplateAdmin(admin.ModelAdmin):
    # Melihat template soal per part
    list_display = ('part_master', 'field_label', 'field_key', 'field_type', 'is_mandatory')
    list_filter = ('part_master', 'field_type', 'is_mandatory')
    search_fields = ('part_master__part_name', 'field_label')
    ordering = ['part_master', 'field_label']

# --- 2. INVENTORY (PHYSICAL STOCK) ADMIN ---
class QCInspectionInline(admin.TabularInline):
    """
    Menampilkan History QC langsung di dalam detail Barang Inventory.
    Hanya Read-Only agar tidak dimanipulasi manual.
    """
    model = QCInspection
    extra = 0
    readonly_fields = ('inspection_date', 'inspector', 'judge_decision', 'qc_result_data')
    can_delete = False

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'part_master', 'current_status', 'updated_at')
    list_filter = ('current_status', 'part_master')
    search_fields = ('serial_number', 'part_master__part_number')
    
    # Fitur Read-Only untuk tanggal agar data integritas terjaga
    readonly_fields = ('created_at', 'updated_at')
    
    # Melihat log history QC di bawah detail barang
    inlines = [QCInspectionInline]

# --- 3. QC INSPECTION LOG ADMIN ---
@admin.register(QCInspection)
class QCInspectionAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'judge_decision', 'inspector', 'inspection_date')
    list_filter = ('judge_decision', 'inspection_date')
    
    # JSON Field agar terlihat rapi di admin (jika pakai library json widget)
    # Default Django akan menampilkannya sebagai Text Area JSON
    readonly_fields = ('inspection_date',)