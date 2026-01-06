from django.db import models

# 1. MODEL BRAND (Baru)
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True) # Misal: TYT, HND
    
    def __str__(self):
        return self.name

# 2. MODEL TIPE KENDARAAN (Pindahan dari vin_record)
class ProductType(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=100) # Misal: Fortuner, Brio
    code = models.CharField(max_length=50, unique=True) # Kode internal
    has_check_digit = models.BooleanField(default=True, verbose_name="Use Check Digit (9th)")
    is_vin_trace = models.BooleanField(default=True, verbose_name="Wajib VIN Trace")
    def __str__(self):
        return f"{self.brand.code} - {self.name}"

# 3. MODEL VARIAN (Pindahan + Fitur VIN Trace)
class ProductVariant(models.Model):
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100) # Misal: G M/T, E CVT
    # --- FITUR BARU ---
    # Jika True: Varian ini adalah Finish Good yang butuh VIN.
    # Jika False: Mungkin ini varian prototype/display yang tidak masuk database VIN.
    class Meta:
        ordering = ['name']
    

    def __str__(self):
        return f"{self.product_type.name} - {self.name}"

# 4. MODEL WARNA (Pindahan)
class ProductColor(models.Model):
    # Warna biasanya nempel ke Tipe (karena beda tipe beda katalog warna)
    # Atau bisa nempel ke Brand jika warnanya global. Kita ikuti struktur lama (nempel ke Type).
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True) # Kode cat
    class Meta:
        ordering = ['name']
    def __str__(self):
        return f"{self.product_type.name} - {self.name}"