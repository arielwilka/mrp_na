from django.contrib import admin
from .models import NumberingRule, SequenceCounter, PartMaster, PartItem

# 1. Konfigurasi Rule
@admin.register(NumberingRule)
class NumberingRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'prefix', 'reset_period', 'digit_length')
    search_fields = ('name', 'code', 'prefix')
    list_filter = ('reset_period',)
    ordering = ('name',)

# 2. Konfigurasi Counter (Untuk memantau nomor terakhir)
@admin.register(SequenceCounter)
class SequenceCounterAdmin(admin.ModelAdmin):
    list_display = ('rule', 'year', 'month', 'last_number')
    list_filter = ('rule', 'year')
    search_fields = ('rule__name',)
    
    # Biar tidak sembarangan edit counter manual, kita set readonly untuk field tertentu jika perlu
    # readonly_fields = ('last_number',) 

# 3. Konfigurasi Part Master (Katalog)
@admin.register(PartMaster)
class PartMasterAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'name', 'numbering_rule', 'created_at')
    search_fields = ('part_number', 'name', 'description')
    list_filter = ('numbering_rule',)
    autocomplete_fields = ['numbering_rule'] # Biar dropdown tidak berat jika rule banyak

# 4. Konfigurasi Part Item (Barang Fisik / Transaksi)
@admin.register(PartItem)
class PartItemAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'part_master', 'status', 'installed_vin', 'created_at')
    
    # Fitur Search yang kuat (Cari SN, cari Part Name, cari VIN)
    search_fields = ('serial_number', 'installed_vin', 'batch_no', 'part_master__name', 'part_master__part_number')
    
    # Filter samping
    list_filter = ('status', 'part_master', 'manufacturing_date')
    
    # Field yang tidak boleh diedit sembarangan
    readonly_fields = ('created_at', 'created_by')
    
    # Otomatis isi user saat save di admin
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)