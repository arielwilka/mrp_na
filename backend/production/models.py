from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

# Import Cross-App
# Pastikan aplikasi 'product', 'traceability', dan 'vin_record' sudah terinstall di settings.py
from product.models import ProductVariant, ProductType, ProductColor
from traceability.models import PartMaster  # Kita relasikan langsung ke PartMaster
from vin_record.models import VinRecord

# ==========================================
# 1. MASTER LOCATION & STATION
# ==========================================
class WorkCenter(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_continuous = models.BooleanField(default=True, help_text="True=Line Ban Berjalan, False=Custom Bay")
    description = models.TextField(blank=True)
    
    def __str__(self): 
        return f"{self.code} - {self.name}"

class Station(models.Model):
    work_center = models.ForeignKey(WorkCenter, on_delete=models.CASCADE, related_name='stations')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    default_sequence = models.PositiveIntegerField(default=1)
    is_finish_point = models.BooleanField(default=False, help_text="Jika True, unit yang lewat sini dianggap Selesai (Output).")

    class Meta:
        unique_together = ('work_center', 'code')
        ordering = ['work_center', 'default_sequence']

    def __str__(self): 
        return f"[{self.work_center.code}] {self.name}"

# ==========================================
# 2. LOGICAL ROUTE & CONFIG
# ==========================================
class ProductionRoute(models.Model):
    name = models.CharField(max_length=100)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='routes')
    is_active = models.BooleanField(default=True)
    
    def __str__(self): 
        return self.name

class RouteStationConfig(models.Model):
    route = models.ForeignKey(ProductionRoute, on_delete=models.CASCADE, related_name='steps')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()
    
    progress_percentage = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Akumulasi Progres (0-100%) jika lolos station ini"
    )
    
    # UPDATE PENTING: Target ke PartMaster agar fleksibel
    traceability_triggers = models.ManyToManyField(
        PartMaster, 
        blank=True,
        related_name='route_configs',
        help_text="Part yang WAJIB discan di station ini sebelum unit boleh PASS."
    )

    class Meta:
        ordering = ['sequence']
        unique_together = ('route', 'station')
    
    def __str__(self): 
        return f"{self.route.name} - Seq {self.sequence} ({self.station.code})"

# ==========================================
# 3. PLANNING & ORDER
# ==========================================
class ProductionPlan(models.Model):
    plan_code = models.CharField(max_length=50, unique=True)
    
    # Kombinasi Varian + Warna
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    color = models.ForeignKey(ProductColor, on_delete=models.PROTECT, related_name='production_plans') # <--- TAMBAHAN BARU
    
    target_qty = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    realized_qty = models.PositiveIntegerField(default=0)
    
    def __str__(self): 
        return f"{self.plan_code} - {self.product_variant.name} ({self.color.name})"

class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('RELEASED', 'Released'),       
        ('CLOSED', 'Closed/Handover'),  
        ('COMPLETED', 'Completed'),
    ]
    plan = models.ForeignKey(ProductionPlan, on_delete=models.CASCADE, related_name='daily_orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    # Snapshot Tracking Mode saat Order dibuat (penting untuk histori)
    tracking_mode_snapshot = models.CharField(max_length=20, choices=ProductType.TRACKING_CHOICES, blank=True)
    
    target_total_qty = models.PositiveIntegerField()
    
    # Handover Logic
    carried_over_wip_qty = models.PositiveIntegerField(default=0)
    new_material_qty = models.PositiveIntegerField(default=0)
    current_wip_qty = models.PositiveIntegerField(default=0, help_text="Jumlah unit yang sedang berjalan (WIP)")
    # Realisasi
    actual_finish_qty = models.PositiveIntegerField(default=0)
    actual_reject_qty = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.plan:
            self.tracking_mode_snapshot = self.plan.product_variant.product_type.tracking_mode
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.order_number

# ==========================================
# 4. ENGINE A: UNIT TRACKING (VIN/Internal)
# ==========================================
class ProductionUnit(models.Model):
    origin_order = models.ForeignKey(ProductionOrder, on_delete=models.PROTECT, related_name='units')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    
    # Link ke VIN Record jika mode VIN Strict
    vin_record = models.OneToOneField(VinRecord, on_delete=models.PROTECT, null=True, blank=True)
    
    # Internal ID jika mode Custom Body
    internal_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    # Posisi Terkini
    current_station = models.ForeignKey(Station, on_delete=models.PROTECT, null=True, blank=True)
    
    STATUS_UNIT = [
        ('WIP', 'In Progress'),
        ('PAUSED', 'Line Off / Kendala'),
        ('FINISH_PROD', 'Finish Production'),
        ('SCRAPPED', 'Scrapped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_UNIT, default='WIP')
    is_paused = models.BooleanField(default=False)
    pause_reason = models.TextField(blank=True, null=True)

    class Meta:
        # Constraint: Unit ID harus unik dalam 1 order
        unique_together = ('origin_order', 'internal_id') 

    def clean(self):
        # Validasi bisnis logic
        mode = self.origin_order.tracking_mode_snapshot
        if mode == 'VIN' and not self.vin_record:
            raise ValidationError("Mode VIN wajib isi vin_record.")
        if mode == 'INTERNAL_ID' and not self.internal_id:
            raise ValidationError("Mode Internal ID wajib isi internal_id.")

    def __str__(self):
        return self.vin_record.full_vin if self.vin_record else (self.internal_id or "Unknown Unit")

# ==========================================
# 5. ENGINE B: BATCH TRACKING
# ==========================================
class StationBatchRecord(models.Model):
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='batch_records')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    
    opening_wip_qty = models.PositiveIntegerField(default=0)
    input_qty = models.PositiveIntegerField(default=0)
    output_good_qty = models.PositiveIntegerField(default=0)
    output_reject_qty = models.PositiveIntegerField(default=0)
    current_wip_qty = models.PositiveIntegerField(default=0) 

    class Meta:
        unique_together = ('production_order', 'station')

    def save(self, *args, **kwargs):
        # Auto hitung saldo WIP
        self.current_wip_qty = (self.opening_wip_qty + self.input_qty) - (self.output_good_qty + self.output_reject_qty)
        super().save(*args, **kwargs)

# ==========================================
# 6. LOGS & TRACEABILITY HISTORY
# ==========================================
class StationActivityLog(models.Model):
    """Mencatat setiap kali unit di-scan PASS/FAIL di station"""
    unit = models.ForeignKey(ProductionUnit, on_delete=models.CASCADE, related_name='logs')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    
    RESULT_CHOICES = [('PROCESS', 'Processing'), ('PASS', 'OK'), ('REJECT', 'NG'), ('PAUSE', 'Paused')]
    result_status = models.CharField(max_length=20, choices=RESULT_CHOICES, default='PROCESS')
    
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class PartInstallationLog(models.Model):
    """Mencatat pemasangan part (Traceability)"""
    unit = models.ForeignKey(ProductionUnit, on_delete=models.CASCADE, related_name='installed_parts')
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    
    part_master = models.ForeignKey(PartMaster, on_delete=models.PROTECT)
    serial_number_scanned = models.CharField(max_length=100)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    installed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)