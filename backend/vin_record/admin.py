from django.contrib import admin
from .models import VehicleType, VehicleVariant, VehicleColor, YearCode, VinRecord, VinPrefix

# --- INLINES ---
# Agar bisa input Varian, Warna, dan Prefix langsung di dalam halaman Tipe Kendaraan
class VehicleVariantInline(admin.TabularInline):
    model = VehicleVariant
    extra = 1

class VehicleColorInline(admin.TabularInline):
    model = VehicleColor
    extra = 1

class VinPrefixInline(admin.TabularInline):
    model = VinPrefix
    extra = 1

# --- ADMIN CLASSES ---

class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name',) # Hapus 'type_code' karena sudah dipindah ke VinPrefix
    search_fields = ('name',)
    # Tampilkan tabel input anak di dalam parent biar gampang
    inlines = [VinPrefixInline, VehicleVariantInline, VehicleColorInline]

class VinPrefixAdmin(admin.ModelAdmin):
    # Sesuaikan dengan field baru: vehicle_type, year_code, wmi_vds, plant_code
    list_display = ('vehicle_type', 'year_code', 'wmi_vds', 'plant_code')
    list_filter = ('vehicle_type', 'year_code')
    search_fields = ('wmi_vds', 'vehicle_type__name')

class YearCodeAdmin(admin.ModelAdmin):
    list_display = ('year', 'code')
    ordering = ('year',)

class VinRecordAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'vehicle_type', 'production_year', 'created_at')
    list_filter = ('vehicle_type', 'production_year')
    search_fields = ('serial_number',)

# --- REGISTER ---
admin.site.register(VehicleType, VehicleTypeAdmin)
admin.site.register(VinPrefix, VinPrefixAdmin)
admin.site.register(YearCode, YearCodeAdmin)
admin.site.register(VinRecord, VinRecordAdmin)
# Variant & Color tidak wajib diregister terpisah jika sudah ada Inline di VehicleType,
# tapi jika mau tetap bisa diakses terpisah, silakan register:
admin.site.register(VehicleVariant)
admin.site.register(VehicleColor)