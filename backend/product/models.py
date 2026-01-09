# product/models.py

from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    def __str__(self): return self.name

class ProductType(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    
    # --- UPDATE: PILIHAN STRATEGI PRODUKSI ---
    TRACKING_CHOICES = [
        ('VIN', 'By VIN (Strict)'),           # Mobil/Motor (Wajib VIN)
        ('INTERNAL_ID', 'By System ID'),      # Karoseri/Custom (Generate ID)
        ('BATCH', 'By Qty Counter'),          # Komponen Kecil (Hitung Jumlah)
    ]
    tracking_mode = models.CharField(
        max_length=20, 
        choices=TRACKING_CHOICES, 
        default='VIN',
        help_text="Menentukan cara tracking di lantai produksi"
    )
    # -----------------------------------------

    has_check_digit = models.BooleanField(default=True, verbose_name="Use Check Digit (9th)")
    
    def __str__(self): return f"{self.code} - {self.name}"

class ProductVariant(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    class Meta:
        ordering = ['name']
    def __str__(self): return f"{self.product_type.name} - {self.name}"

class ProductColor(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)
    class Meta:
        ordering = ['name']
    def __str__(self): return f"{self.product_type.name} - {self.name}"