from django.db import models
from django.contrib.auth.models import User

# IMPORT PENTING: Mengambil PartMaster dari modul traceability
from traceability.models import PartMaster 

# ==========================================
# 1. QC TEMPLATE (Soal Ujian)
# ==========================================
class QCTemplate(models.Model):
    """
    Settingan parameter QC (Voltage, Fisik, Foto).
    Berelasi ke PartMaster di modul Traceability.
    """
    FIELD_TYPES = [
        ('NUMBER', 'Angka'),
        ('TEXT', 'Teks'),
        ('BOOLEAN', 'OK/NG Check'),
        ('IMAGE', 'Foto/Upload'),
    ]

    part_master = models.ForeignKey(PartMaster, on_delete=models.CASCADE, related_name='qc_templates')
    
    field_key = models.CharField(max_length=50, help_text="Key JSON (ex: voltage)")
    field_label = models.CharField(max_length=100, help_text="Label di UI")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    
    # Validasi angka
    min_val = models.FloatField(null=True, blank=True)
    max_val = models.FloatField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"Template {self.part_master.part_name}: {self.field_key}"


# ==========================================
# 2. INVENTORY ITEM (Barang Fisik)
# ==========================================
class InventoryItem(models.Model):
    """
    Stok barang yang ada di pabrik (Instance dari PartMaster).
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending QC'),     # Baru masuk, belum dicek
        ('OK', 'OK (Ready Stock)'),    # Lolos QC
        ('NG', 'Not Good (Reject)'),   # Gagal QC
        ('USED', 'Used (Installed)'),  # Disiapkan untuk masa depan (modul produksi)
        ('SCRAPPED', 'Scrapped'),      # Dibuang
    ]

    part_master = models.ForeignKey(PartMaster, on_delete=models.PROTECT, related_name='inventory_items')
    serial_number = models.CharField(max_length=100, db_index=True)
    
    # Status Lifecycle
    current_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING', 
        db_index=True
    )
    
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Kombinasi Part + Serial harus unik
        unique_together = ('part_master', 'serial_number')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.part_master.part_number} - {self.serial_number} [{self.current_status}]"


# ==========================================
# 3. QC INSPECTION (Log History)
# ==========================================
class QCInspection(models.Model):
    """
    Menyimpan hasil tes (Voltage, Foto) dalam JSON.
    """
    JUDGEMENT_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Data Dinamis (Menyimpan hasil input form QC)
    qc_result_data = models.JSONField(default=dict) 
    
    judge_decision = models.CharField(max_length=10, choices=JUDGEMENT_CHOICES)
    notes = models.TextField(blank=True)
    inspection_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log QC {self.inventory_item.serial_number}: {self.judge_decision}"