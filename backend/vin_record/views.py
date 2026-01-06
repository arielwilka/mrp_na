from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle, ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, IntegrityError
from .pagination import StandardPagination
from .models import VinRecord, VinPrefix, YearCode
from product.models import ProductType, ProductVariant, ProductColor
from product.serializers import ProductTypeSerializer
# Pastikan Anda mengimport semua Serializer di sini
from .serializers import VinRecordSerializer, VinPrefixSerializer, YearCodeSerializer

# Import utils hitung check digit
from .utils import calculate_vin_check_digit

# ==========================================
# 1. VIEWSET TAHUN (YearCode)
# ==========================================
class YearCodeViewSet(viewsets.ModelViewSet):
    queryset = YearCode.objects.all().order_by('-year')
    serializer_class = YearCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None
# ==========================================
# 2. VIEWSET PREFIX (VinPrefix)
# ==========================================
class VinPrefixViewSet(viewsets.ModelViewSet):
    queryset = VinPrefix.objects.select_related('product_type', 'year_code').all()
    serializer_class = VinPrefixSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_type', 'year_code']
    pagination_class = StandardPagination
# ==========================================
# 3. VIEWSET VIN RECORD (Main Logic)
# ==========================================
class VinRecordViewSet(viewsets.ModelViewSet):
    queryset = VinRecord.objects.select_related(
        'product_type', 'production_year', 'variant', 'color', 'created_by'
    ).order_by('-id')
    
    serializer_class = VinRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product_type', 'production_year']
    search_fields = ['full_vin', 'serial_number']

    def get_throttles(self):
        if self.action == 'batch_generate':
            self.throttle_scope = 'batch_vin'
            return [ScopedRateThrottle()]
        return [UserRateThrottle()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        # 1. Manual Duplicate Check
        input_vin = request.data.get('full_vin')
        if input_vin and VinRecord.objects.filter(full_vin=input_vin).exists():
            raise ValidationError({"full_vin": ["GAGAL: Nomor Rangka (VIN) ini sudah terdaftar di sistem."]})

        # 2. Save with Race Condition Protection
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError as e:
            if 'unique constraint' in str(e).lower() or 'full_vin' in str(e).lower():
                raise ValidationError({"full_vin": ["KONFLIK DATA: VIN baru saja didaftarkan oleh user lain."]})
            raise e

    @action(detail=False, methods=['post'], url_path='batch-generate')
    def batch_generate(self, request):
        data = request.data
        try:
            with transaction.atomic():
                qty = int(data.get('quantity', 0))
                start_serial = int(data.get('start_serial', 0))
                
                if qty <= 0 or qty > 5000:
                    return Response({'detail': 'Quantity harus 1 - 5000'}, status=400)

                # Locking Product
                try:
                    product_type = ProductType.objects.select_for_update().get(pk=data['product_type'])
                except ProductType.DoesNotExist:
                      return Response({'detail': 'Tipe Kendaraan tidak ditemukan'}, status=404)
                
                # Cek Trace (Sesuai model Anda: is_vin_trace)
                if not product_type.is_vin_trace:
                    return Response({
                        'detail': f"GAGAL: Tipe '{product_type.name}' dikonfigurasi sebagai Non-VIN Trace."
                    }, status=400)

                production_year = YearCode.objects.get(pk=data['production_year'])
                
                variant_id = data.get('variant')
                color_id = data.get('color')
                
                variant = ProductVariant.objects.get(pk=variant_id) if variant_id else None
                color = ProductColor.objects.get(pk=color_id) if color_id else None
                
                # Prefix Rule
                try:
                    prefix_rule = VinPrefix.objects.get(product_type=product_type, year_code=production_year)
                except VinPrefix.DoesNotExist:
                    return Response({'detail': 'Prefix belum disetting untuk tipe & tahun ini.'}, status=400)

                # Persiapan Variabel Generator
                wmi_vds = prefix_rule.wmi_vds
                plant_code = prefix_rule.plant_code
                year_char = production_year.code
                
                # Cek Config Check Digit (Sesuai model Anda: has_check_digit)
                use_algo = product_type.has_check_digit
                static_ninth = prefix_rule.static_ninth_digit or '0'

                # Loop Generate
                vin_objects = []
                check_list = []

                for i in range(qty):
                    current_num = start_serial + i
                    serial_str = str(current_num).zfill(6)
                    check_list.append(serial_str)
                    
                    # LOGIKA HITUNG DIGIT 9 (Sama persis dengan models.save)
                    final_ninth = static_ninth
                    
                    if use_algo:
                        temp_vin = f"{wmi_vds}0{year_char}{plant_code}{serial_str}"
                        calc = calculate_vin_check_digit(temp_vin)
                        if calc != '?':
                            final_ninth = calc
                            
                    full_vin = f"{wmi_vds}{final_ninth}{year_char}{plant_code}{serial_str}"

                    vin_objects.append(VinRecord(
                        product_type=product_type, production_year=production_year,
                        variant=variant, color=color, serial_number=serial_str,
                        full_vin=full_vin, created_by=request.user
                    ))

                # Pre-flight Check Duplikat
                existing = VinRecord.objects.filter(
                    product_type=product_type, production_year=production_year,
                    serial_number__in=check_list
                ).values_list('serial_number', flat=True)

                if existing:
                    return Response({
                        'detail': 'Serial Number berikut sudah terpakai:',
                        'errors': list(existing)
                    }, status=400)

                VinRecord.objects.bulk_create(vin_objects)

                return Response({
                    'message': f'Sukses generate {len(vin_objects)} record.',
                    'range': f'{str(start_serial).zfill(6)} - {str(start_serial + qty - 1).zfill(6)}'
                }, status=201)

        except IntegrityError:
            return Response({'detail': 'KONFLIK DATA: Terjadi tabrakan saat proses.'}, status=409)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
class TraceableProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint khusus untuk dropdown di modul VIN.
    HANYA menampilkan produk yang wajib ditrace (is_vin_trace=True).
    Pagination dimatikan agar dropdown frontend menerima semua data sekaligus.
    """
    queryset = ProductType.objects.filter(is_vin_trace=True).order_by('name')
    serializer_class = ProductTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None