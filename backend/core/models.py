from django.db import models
from django.contrib.auth.models import User

# 1. Master Modul (Daftar Modul yang ada di sistem)
class SystemModule(models.Model):
    name = models.CharField(max_length=100) # Cth: "VIN Record System"
    code = models.SlugField(max_length=50, unique=True) # Cth: "vin_record"

    def __str__(self):
        return self.name

# 2. Master Role (Jabatan/Group)
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True) # Cth: "Admin", "Operator"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# 3. Relasi User ke Role (User bisa punya banyak role)
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

# 4. Matrix Permission (CRUD per Modul per Role)
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module = models.ForeignKey(SystemModule, on_delete=models.CASCADE)
    
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module')

    def __str__(self):
        return f"{self.role.name} on {self.module.code}"

class LabelModule(models.Model):
    name = models.CharField(max_length=100, help_text="Nama Modul (Contoh: VIN Record)")
    code = models.SlugField(max_length=50, unique=True, help_text="Kode unik (Contoh: vin_record)")
    
    def __str__(self):
        return self.name

class LabelField(models.Model):
    module = models.ForeignKey(LabelModule, on_delete=models.CASCADE, related_name='fields')
    field_key = models.CharField(max_length=100, help_text="Contoh: {{ full_vin }}")
    field_label = models.CharField(max_length=100, help_text="Contoh: No. Rangka Lengkap")
    dummy_data = models.CharField(max_length=100, blank=True, help_text="Contoh data untuk preview (MH1RW...)")

    def __str__(self):
        return f"{self.field_label} ({self.module.code})"

# Update PrintTemplate agar module_scope tidak lagi hardcoded choices
# Hapus MODULE_CHOICES yang lama
class PrintTemplate(models.Model):
    name = models.CharField(max_length=100)
    # Kita ubah jadi CharField biasa, validasinya nanti via Frontend dropdown
    module_scope = models.CharField(max_length=50, default='vin_record') 
    
    width_mm = models.FloatField(default=100)
    height_mm = models.FloatField(default=50)
    design_schema = models.JSONField(default=dict) 
    html_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name