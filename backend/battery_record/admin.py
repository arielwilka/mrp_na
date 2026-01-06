from django.contrib import admin
from .models import BatteryRecord

@admin.register(BatteryRecord)
class BatteryRecordAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'condition', 'created_at', 'created_by')
    list_filter = ('condition', 'created_at')
    search_fields = ('serial_number',)
    readonly_fields = ('created_at',)