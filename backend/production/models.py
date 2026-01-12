from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime 

# Import Cross-App
# Pastikan app 'product', 'traceability', dan 'vin_record' sudah ada dan terdaftar di INSTALLED_APPS
from product.models import ProductVariant, ProductType, ProductColor
from traceability.models import PartMaster
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
    route = models.ForeignKey('ProductionRoute', on_delete=models.CASCADE, related_name='steps')
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField(default=1)
    
    # --- FIELD BOBOT & DESKRIPSI ---
    job_description = models.TextField(blank=True, help_text="Instruksi kerja untuk operator")
    job_weight = models.FloatField(default=0, help_text="Bobot pekerjaan dalam % (Total harus 100)")
    progress_percentage = models.FloatField(default=0) 

    # BOM Traceability
    traceability_triggers = models.ManyToManyField(
        'traceability.PartMaster', 
        blank=True, 
        related_name='route_configs'
    )

    class Meta:
        ordering = ['route', 'sequence']
        unique_together = ('route', 'station')

    def __str__(self):
        return f"{self.route.name} - {self.station.name} (Seq: {self.sequence})"

# ==========================================
# 3. PLANNING & ORDER
# ==========================================
class ProductionPlan(models.Model):
    plan_code = models.CharField(max_length=50, unique=True)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    color = models.ForeignKey(ProductColor, on_delete=models.PROTECT, related_name='production_plans')
    
    target_qty = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    realized_qty = models.PositiveIntegerField(default=0)
    
    # Timestamp plan dibuat
    created_at = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self): 
        return f"{self.plan_code} - {self.product_variant.name} ({self.color.name})"

class ProductionOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('RELEASED', 'Released'),       
        ('CLOSED', 'Closed/Handover'),  
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    plan = models.ForeignKey(ProductionPlan, on_delete=models.CASCADE, related_name='daily_orders')
    
    # [FIX] Blank=True agar validasi form lolos, nanti diisi otomatis di save()
    order_number = models.CharField(max_length=50, unique=True, blank=True) 
    
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
    # [BARU] Waktu Closing / Handover
    closed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. AUTO GENERATE NOMOR ORDER (Format: SPK-YYYYMMDD-XXX)
        if not self.order_number:
            today_str = timezone.now().strftime('%Y%m%d')
            prefix = f"SPK-{today_str}"
            
            # Cari nomor urut terakhir hari ini
            last_order = ProductionOrder.objects.filter(
                order_number__startswith=prefix
            ).order_by('order_number').last()

            if last_order:
                # Ambil 3 digit terakhir, convert int, tambah 1
                try:
                    last_seq = int(last_order.order_number.split('-')[-1])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1

            self.order_number = f"{prefix}-{new_seq:03d}"

        # 2. Snapshot Tracking Mode
        if not self.pk and self.plan:
            # Mengambil tracking mode dari ProductType via Variant -> Plan
            # Pastikan relasi di models Product sudah benar
            self.tracking_mode_snapshot = self.plan.product_variant.product_type.tracking_mode
        
        # 3. [FIX SAFETY] Auto-fill WIP Qty untuk order baru
        if not self.pk and self.current_wip_qty == 0 and self.target_total_qty > 0:
            self.current_wip_qty = self.target_total_qty
            
        super().save(*args, **kwargs)
    
    def __str__(self): 
        return self.order_number

# ==========================================
# 4. ENGINE A: UNIT TRACKING (VIN/Internal)
# ==========================================
class ProductionUnit(models.Model):
    # [PENTING] related_name='units' ditambahkan agar Serializer ProductionOrder bisa akses data ini
    origin_order = models.ForeignKey(ProductionOrder, on_delete=models.PROTECT, related_name='units', null=True, blank=True)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    
    vin_record = models.OneToOneField(VinRecord, on_delete=models.PROTECT, null=True, blank=True)
    internal_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    current_station = models.ForeignKey(Station, on_delete=models.PROTECT, null=True, blank=True)
    
    STATUS_UNIT = [
        ('PLANNED', 'Planned'), # Tambahan status awal
        ('WIP', 'In Progress'),
        ('PAUSED', 'Line Off / Kendala'),
        ('FINISH_PROD', 'Finish Production'),
        ('SCRAPPED', 'Scrapped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_UNIT, default='PLANNED')
    is_paused = models.BooleanField(default=False)
    pause_reason = models.TextField(blank=True, null=True)

    # [PENTING] Tambahan Timestamps agar tidak error di Serializer
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('origin_order', 'internal_id') 

    def clean(self):
        if self.origin_order:
            mode = self.origin_order.tracking_mode_snapshot
            if mode == 'VIN' and not self.vin_record:
                raise ValidationError("Mode VIN wajib isi vin_record.")
            if mode == 'INTERNAL_ID' and not self.internal_id:
                raise ValidationError("Mode Internal ID wajib isi internal_id.")

    def __str__(self):
        label = self.vin_record.full_vin if self.vin_record else (self.internal_id or "Unknown Unit")
        return f"{label} [{self.status}]"

# ==========================================
# 5. ENGINE B: BATCH TRACKING (Total Progress)
# ==========================================
class StationBatchRecord(models.Model):
    """
    Menyimpan progres AKUMULATIF (Total) dari sebuah Order di tiap Stasiun.
    Digunakan untuk melihat saldo WIP (Antrian) di setiap pos.
    """
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='station_records')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    
    opening_wip_qty = models.PositiveIntegerField(default=0)
    input_qty = models.PositiveIntegerField(default=0)
    output_good_qty = models.PositiveIntegerField(default=0)
    output_reject_qty = models.PositiveIntegerField(default=0)
    current_wip_qty = models.PositiveIntegerField(default=0) 

    class Meta:
        unique_together = ('production_order', 'station')

    # --- LOGIKA KALKULASI WIP DI SINI ---
    def save(self, *args, **kwargs):
        # 1. Hitung total output
        total_out = self.output_good_qty + self.output_reject_qty
        
        # 2. Hitung total input (saldo awal + input masuk)
        total_in = self.opening_wip_qty + self.input_qty
        
        # 3. KOREKSI INPUT OTOMATIS (Self-Healing Data)
        if total_out > total_in:
            diff = total_out - total_in
            self.input_qty += diff
            total_in += diff # Update total_in agar balance
        
        # 4. Hitung Saldo Akhir (Gunakan max 0 untuk safety net terakhir)
        self.current_wip_qty = max(0, total_in - total_out)
        
        super().save(*args, **kwargs)

# ==========================================
# 6. ENGINE C: DAILY REPORTING (Output Harian)
# ==========================================
class DailyStationOutput(models.Model):
    """
    [BARU] Mencatat output HANYA pada tanggal tertentu.
    Ini memisahkan 'Total Order Progress' dengan 'Kinerja Harian'.
    Sangat berguna untuk Order Long-Running (Continuous) yang tidak di-handover tiap hari.
    """
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='daily_outputs')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    
    qty_good = models.PositiveIntegerField(default=0)
    qty_reject = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('production_order', 'station', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.station.name} - OK: {self.qty_good}"

# ==========================================
# 7. LOGS & TRACEABILITY HISTORY
# ==========================================
class StationActivityLog(models.Model):
    unit = models.ForeignKey(ProductionUnit, on_delete=models.CASCADE, related_name='logs')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    
    # [UPDATE] Tambahkan START_MANUAL untuk logic Supervisor
    RESULT_CHOICES = [
        ('PROCESS', 'Processing'), 
        ('PASS', 'OK'), 
        ('REJECT', 'NG'), 
        ('PAUSE', 'Paused'),
        ('START_MANUAL', 'Force Start by Supervisor')
    ]
    result_status = models.CharField(max_length=30, choices=RESULT_CHOICES, default='PROCESS')
    
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class PartInstallationLog(models.Model):
    unit = models.ForeignKey(ProductionUnit, on_delete=models.CASCADE, related_name='installed_parts')
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    
    part_master = models.ForeignKey(PartMaster, on_delete=models.PROTECT)
    serial_number_scanned = models.CharField(max_length=100)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    installed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)