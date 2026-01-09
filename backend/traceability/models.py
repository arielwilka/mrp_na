from django.db import models, transaction
from django.contrib.auth.models import User
from product.models import ProductType
# ==========================================
# 1. RULE ENGINE (The Validator)
# ==========================================
class SerialRule(models.Model):
    """
    Header untuk aturan validasi.
    Misal: "Rule Validasi Baterai Vendor A"
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Kode Rule Internal")
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.name

class RuleSegment(models.Model):
    """
    Baris-baris aturan (Child).
    Urutan sangat penting (order).
    """
    rule = models.ForeignKey(SerialRule, related_name='segments', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)
    
    TYPE_CHOICES = [
        ('STATIC', 'Karakter Tetap (Ex: BAT)'),
        ('DIGIT', 'Angka (0-9)'),
        ('CHAR', 'Huruf (A-Z)'),
        ('ALPHANUM', 'Huruf & Angka'),
        ('YEAR', 'Tahun (2 Digit)'),
        ('MONTH', 'Bulan (2 Digit)'),
    ]
    segment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_index = models.IntegerField(
        null=True, blank=True, 
        help_text="Posisi mulai (Index 1). Jika kosong, akan lanjut dari segmen sebelumnya."
    )
    
    # Konfigurasi
    length = models.PositiveIntegerField(default=1, help_text="Jumlah karakter/digit")
    static_value = models.CharField(max_length=50, blank=True, null=True, help_text="Isi jika tipe STATIC")
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        pos_info = f"@{self.start_index}" if self.start_index else "Next"
        return f"#{self.order} [{pos_info}] {self.segment_type}"

# ==========================================
# 2. PART MASTER (The Object)
# ==========================================
class PartMaster(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    part_name = models.CharField(max_length=100)
    
    validation_rule = models.ForeignKey('SerialRule', on_delete=models.SET_NULL, null=True, blank=True)
    
    # --- UPDATE: CONFIG QC ---
    is_qc_required = models.BooleanField(
        default=True, 
        help_text="TRUE: Wajib di-scan di Modul QC (Receiving). FALSE: Langsung ke Produksi."
    )
    is_unique_serial = models.BooleanField(
        default=True, 
        help_text="TRUE: Serial Number Global Unik. FALSE: Batch based."
    )
    # -------------------------

    supplier = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.part_number} - {self.part_name}"

# ==========================================
# 3. TRACEABILITY VERSION (HEADER)
# ==========================================
class TraceabilityVersion(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='trace_versions')
    version_code = models.CharField(max_length=50, help_text="Ex: REV-001 or V1.0")
    
    valid_from = models.DateField(help_text="Tanggal mulai berlaku")
    is_active = models.BooleanField(default=True, help_text="Versi yang sedang digunakan saat ini")
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product_type', 'version_code')
        verbose_name = "Traceability Version / BOM Header"
        ordering = ['-valid_from'] # Urutkan dari yang terbaru

    def __str__(self):
        status = "ACTIVE" if self.is_active else "INACTIVE"
        return f"{self.product_type.name} [{self.version_code}] - {status}"

    # --- LOGIC PENJAGAAN (AUTO-SWITCH) ---
    def save(self, *args, **kwargs):
        # Jika versi ini diset AKTIF
        if self.is_active:
            with transaction.atomic():
                # Cari versi lain milik Product yang sama, yang juga Aktif
                # Exclude diri sendiri (agar tidak mematikan diri sendiri saat update)
                TraceabilityVersion.objects.filter(
                    product_type=self.product_type, 
                    is_active=True
                ).exclude(pk=self.pk).update(is_active=False)

        # Lanjutkan proses save yang sebenarnya
        super(TraceabilityVersion, self).save(*args, **kwargs)

# ==========================================
# 4. TRACEABILITY REQUIREMENT (DETAIL)
# ==========================================
class TraceabilityRequirement(models.Model):
    """
    Isi detail dari versi tersebut.
    """
    # Link ke Version (Header), BUKAN langsung ke ProductType
    version = models.ForeignKey(TraceabilityVersion, on_delete=models.CASCADE, related_name='requirements')
    
    part_master = models.ForeignKey(PartMaster, on_delete=models.PROTECT)
    
    qty = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    
    class Meta:
        # Dalam 1 versi, tidak boleh ada part yang sama double
        unique_together = ('version', 'part_master')

    def __str__(self):
        return f"{self.part_master.part_name} (Qty: {self.qty})"