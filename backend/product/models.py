# product/models.py

from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self): 
        return self.name

class ProductType(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    
    # =========================================================
    # 1. TRACKING MODE (BAGAIMANA BARANG DIIDENTIFIKASI?)
    # =========================================================
    TRACKING_CHOICES = [
        ('VIN', 'By VIN (Strict)'),           # Butuh data VIN Record (Mobil/Motor)
        ('INTERNAL_ID', 'By System ID'),      # Generate ID Otomatis (Bak Mobil/Custom)
        ('BATCH', 'By Qty Counter'),          # Tidak ada ID unik (Baut/Cat/Part Kecil)
    ]
    tracking_mode = models.CharField(
        max_length=20, 
        choices=TRACKING_CHOICES, 
        default='VIN',
        help_text="Menentukan apakah sistem harus men-generate Serial Number unik per unit atau hanya menghitung jumlah."
    )

    # =========================================================
    # 2. SCHEDULING POLICY (BAGAIMANA SIKLUS HIDUP ORDER?)
    # =========================================================
    SCHEDULING_CHOICES = [
        ('DAILY_RESET', 'Daily Reset (Handover Harian)'),         
        # ^ Cocok untuk Mass Production. Sisa WIP hari ini dianggap "utang" produksi besok.
        #   Status Order akan 'CLOSED' tiap sore.
        
        ('CONTINUOUS', 'Continuous (Project Long-Running)'),      
        # ^ Cocok untuk Project Panjang (ex: Bak Mobil 3 Hari).
        #   Status Order tetap 'RELEASED' sampai target tercapai. Tidak ada Handover harian.
    ]
    scheduling_policy = models.CharField(
        max_length=20, 
        choices=SCHEDULING_CHOICES, 
        default='DAILY_RESET',
        help_text="Menentukan apakah SPK harus ditutup harian (Handover) atau berjalan terus sampai target selesai."
    )

    has_check_digit = models.BooleanField(default=True, verbose_name="Use Check Digit (9th)")
    
    def __str__(self): 
        return f"{self.code} - {self.name}"

class ProductVariant(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self): 
        return f"{self.product_type.name} - {self.name}"

class ProductColor(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self): 
        return f"{self.product_type.name} - {self.name}"
