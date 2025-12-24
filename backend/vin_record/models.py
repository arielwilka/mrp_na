from django.db import models
from django.contrib.auth.models import User
# 1. MODEL TAHUN
class YearCode(models.Model):
    year = models.IntegerField(unique=True)
    code = models.CharField(max_length=1)
    def __str__(self): return f"{self.year} ({self.code})"

# 2. MODEL TIPE KENDARAAN
class VehicleType(models.Model):
    name = models.CharField(max_length=100)
    # Field lain dipindah ke VinPrefix
    def __str__(self): return self.name

# 3. MODEL PREFIX (Penghubung Tipe + Tahun)
class VinPrefix(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='prefixes')
    year_code = models.ForeignKey(YearCode, on_delete=models.CASCADE, related_name='prefixes')
    
    wmi_vds = models.CharField(max_length=10, help_text="Contoh: MH1RW")
    plant_code = models.CharField(max_length=1, help_text="Contoh: K")

    class Meta:
        unique_together = ('vehicle_type', 'year_code') 

    def __str__(self):
        return f"{self.vehicle_type.name} - {self.year_code.year}"

# 4. MODEL VARIAN
class VehicleVariant(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

# 5. MODEL WARNA
class VehicleColor(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

# 6. MODEL VIN RECORD (Yang Error Tadi Disini)
class VinRecord(models.Model):
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    production_year = models.ForeignKey(YearCode, on_delete=models.PROTECT)
    variant = models.ForeignKey(VehicleVariant, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(VehicleColor, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    serial_number = models.CharField(max_length=6)
    full_vin = models.CharField(max_length=17, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
        # Opsional: Pastikan serial number unik untuk tiap tipe & tahun
        constraints = [
            models.UniqueConstraint(
                fields=['vehicle_type', 'production_year', 'serial_number'], 
                name='unique_serial_per_type_year'
            )
        ]
    def save(self, *args, **kwargs):
        # Logic Generate Full VIN
        if not self.full_vin:
            try:
                # Ambil rule prefix berdasarkan Tipe & Tahun
                # Note: field di VinPrefix namanya 'year_code', field di sini 'production_year'
                prefix_rule = VinPrefix.objects.get(
                    vehicle_type=self.vehicle_type,
                    year_code=self.production_year 
                )
                
                year_char = self.production_year.code 
                
                # RUMUS: WMI_VDS + YEAR_CODE + PLANT_CODE + SERIAL
                self.full_vin = f"{prefix_rule.wmi_vds}{year_char}{prefix_rule.plant_code}{self.serial_number}"
                
            except VinPrefix.DoesNotExist:
                # Fallback jika admin lupa input prefix
                year_char = self.production_year.code
                self.full_vin = f"UNKNOWN{year_char}?{self.serial_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_vin or self.serial_number