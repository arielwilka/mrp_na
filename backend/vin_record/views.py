from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.throttling import ScopedRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction, IntegrityError

# Import Model
from .models import VehicleType, YearCode, VinRecord, VinPrefix, VehicleVariant, VehicleColor
from core.models import RolePermission 

# Import Serializer
from .serializers import (
    VehicleTypeSerializer, YearCodeSerializer, VinRecordSerializer,
    VinPrefixSerializer, VehicleVariantSerializer, VehicleColorSerializer
)

# --- PAGINATION ---
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# --- PERMISSION: SEPARATION OF DUTIES ---
class IsVinMasterOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
            
        return RolePermission.objects.filter(
            role__user_roles__user=request.user,
            module__code='vin_master',
            can_read=True
        ).exists()

# ==========================================
# GROUP 1: MASTER DATA (CRUD Protected)
# ==========================================

class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [IsVinMasterOrReadOnly]
    pagination_class = None

class YearCodeViewSet(viewsets.ModelViewSet):
    queryset = YearCode.objects.all()
    serializer_class = YearCodeSerializer
    permission_classes = [IsVinMasterOrReadOnly]
    pagination_class = None

class VinPrefixViewSet(viewsets.ModelViewSet):
    queryset = VinPrefix.objects.select_related('vehicle_type', 'year_code').all() # Optimize Query
    serializer_class = VinPrefixSerializer
    permission_classes = [IsVinMasterOrReadOnly]
    pagination_class = None

class VehicleVariantViewSet(viewsets.ModelViewSet):
    queryset = VehicleVariant.objects.all()
    serializer_class = VehicleVariantSerializer
    permission_classes = [IsVinMasterOrReadOnly]
    pagination_class = None

class VehicleColorViewSet(viewsets.ModelViewSet):
    queryset = VehicleColor.objects.all()
    serializer_class = VehicleColorSerializer
    permission_classes = [IsVinMasterOrReadOnly]
    pagination_class = None


# ==========================================
# GROUP 2: VIN RECORD (Operational)
# ==========================================

class VinRecordViewSet(viewsets.ModelViewSet):
    queryset = VinRecord.objects.select_related(
        'vehicle_type', 'production_year', 'variant', 'color', 'created_by'
    ).order_by('-id')
    
    serializer_class = VinRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['vehicle_type', 'production_year']
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

                # Locking
                try:
                    vehicle_type = VehicleType.objects.select_for_update().get(pk=data['vehicle_type'])
                except VehicleType.DoesNotExist:
                     return Response({'detail': 'Tipe Kendaraan tidak ditemukan'}, status=404)

                production_year = YearCode.objects.get(pk=data['production_year'])
                
                variant_id = data.get('variant')
                color_id = data.get('color')
                
                variant = VehicleVariant.objects.get(pk=variant_id) if variant_id else None
                color = VehicleColor.objects.get(pk=color_id) if color_id else None

                # Prefix Rule
                try:
                    prefix_rule = VinPrefix.objects.get(vehicle_type=vehicle_type, year_code=production_year)
                except VinPrefix.DoesNotExist:
                    return Response({'detail': 'Prefix belum disetting untuk tipe & tahun ini.'}, status=400)

                # Loop Memory
                vin_objects = []
                check_list = []
                year_char = production_year.code

                for i in range(qty):
                    current_num = start_serial + i
                    serial_str = str(current_num).zfill(6)
                    check_list.append(serial_str)
                    
                    full_vin = f"{prefix_rule.wmi_vds}{year_char}{prefix_rule.plant_code}{serial_str}"

                    vin_objects.append(VinRecord(
                        vehicle_type=vehicle_type, production_year=production_year,
                        variant=variant, color=color, serial_number=serial_str,
                        full_vin=full_vin, created_by=request.user
                    ))

                # Pre-flight Check
                existing = VinRecord.objects.filter(
                    vehicle_type=vehicle_type, production_year=production_year,
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