from django.db import models
from django.contrib.auth.models import User
# Import rumus dari utils agar rapi
from .utils import calculate_vin_check_digit 
from product.models import ProductType, ProductVariant, ProductColor

class YearCode(models.Model):
    year = models.IntegerField(unique=True)
    code = models.CharField(max_length=1)
    def __str__(self): return f"{self.year} ({self.code})"

class VinPrefix(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='vin_prefixes')
    year_code = models.ForeignKey(YearCode, on_delete=models.CASCADE, related_name='prefixes')
    
    wmi_vds = models.CharField(max_length=8, help_text="Masukan 8 Karakter pertama (WMI + VDS)")
    plant_code = models.CharField(max_length=1, help_text="Kode Pabrik (1 Digit)")
    static_ninth_digit = models.CharField(
        max_length=1, default='0', help_text="Dipakai jika Check Digit dimatikan."
    )
    class Meta:
        unique_together = ('product_type', 'year_code') 

    def __str__(self):
        return f"{self.product_type.code} / {self.year_code.year}"

class VinRecord(models.Model):
    # --- UPDATE STATUS ---
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),  
        ('RESERVED', 'Reserved'),    # Sedang dipakai produksi
        ('USED', 'Used / Assembled'),# Sudah jadi Finish Good
        ('SCRAPPED', 'Scrapped'),    
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE', db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    booking_reference = models.CharField(max_length=100, null=True, blank=True)
    # ---------------------

    product_type = models.ForeignKey(ProductType, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    color = models.ForeignKey(ProductColor, on_delete=models.PROTECT)
    production_year = models.ForeignKey(YearCode, on_delete=models.PROTECT)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    serial_number = models.CharField(max_length=6) 
    full_vin = models.CharField(max_length=17, unique=True, db_index=True)

    class Meta:
        ordering = ['serial_number']
        unique_together = ('product_type', 'production_year', 'serial_number')

    def save(self, *args, **kwargs):
        # LOGIC FIX: Hapus pengecekan "if not full_vin".
        # Backend harus menjadi Source of Truth. Selalu generate ulang VIN
        # berdasarkan komponen agar Check Digit terjamin benar.
        
        if self.product_type and self.production_year and self.serial_number:
            try:
                # 1. Ambil Rule Prefix
                prefix = VinPrefix.objects.get(
                    product_type=self.product_type,
                    year_code=self.production_year
                )
                
                wmi_vds = prefix.wmi_vds
                plant = prefix.plant_code
                year_char = self.production_year.code
                serial = self.serial_number.zfill(6) # Pastikan 6 digit
                
                # 2. Cek Config Product (Sesuai model Anda: has_check_digit)
                use_algo = self.product_type.has_check_digit
                ninth_digit = prefix.static_ninth_digit or '0'

                # 3. Hitung Digit 9
                if use_algo:
                    # Susun dummy VIN dengan '0' di digit 9
                    temp_vin = f"{wmi_vds}0{year_char}{plant}{serial}"
                    calc = calculate_vin_check_digit(temp_vin)
                    if calc != '?':
                        ninth_digit = calc
                
                # 4. Set VIN Final (Overwrite inputan frontend)
                self.full_vin = f"{wmi_vds}{ninth_digit}{year_char}{plant}{serial}"
                
            except VinPrefix.DoesNotExist:
                pass # Biarkan error validasi database menangani jika full_vin kosong

        super().save(*args, **kwargs)

    def __str__(self): return f"{self.full_vin} [{self.status}]"