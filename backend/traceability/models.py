from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. GROUP: RULE CODE & COUNTER
# ==========================================
class NumberingRule(models.Model):
    """
    Aturan untuk generate Serial Number otomatis.
    Contoh: 'BAT-{YYYY}{MM}-{SEQ:04d}'
    """
    name = models.CharField(max_length=100, unique=True, help_text="Nama Aturan (ex: Rule Baterai 2024)")
    code = models.CharField(max_length=50, unique=True, help_text="Kode Unik Rule")
    
    prefix = models.CharField(max_length=20, help_text="Awalan (ex: BAT, ECU)")
    
    # Reset Logic
    RESET_CHOICES = [
        ('NEVER', 'Never Reset (Terus bertambah)'),
        ('YEARLY', 'Reset Tiap Tahun'),
        ('MONTHLY', 'Reset Tiap Bulan'),
    ]
    reset_period = models.CharField(max_length=10, choices=RESET_CHOICES, default='NEVER')
    
    digit_length = models.IntegerField(default=4, help_text="Jumlah digit urut (ex: 4 digit = 0001)")
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.prefix})"

class SequenceCounter(models.Model):
    """
    Menyimpan nomor urut terakhir agar tidak bentrok.
    """
    rule = models.ForeignKey(NumberingRule, on_delete=models.CASCADE, related_name='counters')
    year = models.IntegerField(null=True, blank=True)   # Diisi jika reset YEARLY/MONTHLY
    month = models.IntegerField(null=True, blank=True)  # Diisi jika reset MONTHLY
    last_number = models.IntegerField(default=0)

    class Meta:
        unique_together = ('rule', 'year', 'month')

# ==========================================
# 2. GROUP: PART MASTER (Definisi Produk)
# ==========================================
class PartMaster(models.Model):
    """
    Katalog Part (Blueprint).
    Contoh: 'Battery Pack 60Ah Vario', 'ECU Type A'
    """
    part_number = models.CharField(max_length=50, unique=True, help_text="SKU / Kode Part Internal")
    name = models.CharField(max_length=100)
    
    # Relasi ke Rule Code (Setiap jenis part punya aturan SN sendiri)
    numbering_rule = models.ForeignKey(NumberingRule, on_delete=models.SET_NULL, null=True, blank=True)
    
    supplier_code = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.part_number} - {self.name}"

# ==========================================
# 3. GROUP: TRACEABLE ITEM (Barang Fisik)
# ==========================================
class PartItem(models.Model):
    """
    Barang fisik (Instance). Tabel ini akan berisi ribuan/jutaan data.
    Setiap baris mewakili 1 unit barang fisik.
    """
    part_master = models.ForeignKey(PartMaster, on_delete=models.PROTECT, related_name='items')
    
    # Identitas Utama
    serial_number = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Traceability Data
    manufacturing_date = models.DateField(null=True, blank=True)
    batch_no = models.CharField(max_length=50, blank=True, null=True)
    
    # Status Barang
    STATUS_CHOICES = [
        ('GOOD', 'Good / OK'),
        ('NG', 'No Good / Reject'),
        ('INSTALLED', 'Installed on Unit'),
        ('SCRAPPED', 'Scrapped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GOOD')
    
    # Link ke Mobil (VIN)
    # Kita pakai String dulu untuk Loose Coupling, atau bisa FK ke vin_record.VinRecord
    installed_vin = models.CharField(max_length=17, blank=True, null=True, db_index=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.serial_number} ({self.status})"