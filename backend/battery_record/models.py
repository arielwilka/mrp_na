from django.db import models
from django.conf import settings # Mengambil User Model yg aktif
import os
import uuid
from datetime import datetime

# Helper: Rename file upload agar unik & rapi
def battery_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    # File tersimpan di: media/battery_qc/2024/12/unik.jpg
    return os.path.join('battery_qc', datetime.now().strftime('%Y/%m'), filename)

class BatteryRecord(models.Model):
    CONDITION_CHOICES = [
        ('OK', 'OK (Pass)'),
        ('NG', 'NG (Reject)'),
        ('RECHECK', 'Re-Check'),
    ]

    # Serial Number Unik
    serial_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Kondisi & Data Teknis
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='OK')
    voltage = models.CharField(max_length=10, blank=True, null=True, help_text="Contoh: 12.4 V")
    
    # File Bukti (Screen Capture)
    screenshot = models.ImageField(upload_to=battery_file_path)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-created_at'] # Data terbaru di atas
        verbose_name = "Battery QC Record"

    def __str__(self):
        return f"{self.serial_number} - {self.condition}"