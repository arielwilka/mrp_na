from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from .models import SerialRule, PartMaster, TraceabilityVersion
from .serializers import SerialRuleSerializer, PartMasterSerializer, TraceabilityVersionSerializer
from .utils import validate_serial_number

# ==========================================
# 1. SERIAL RULE VIEWSET
# ==========================================
class SerialRuleViewSet(viewsets.ModelViewSet):
    queryset = SerialRule.objects.prefetch_related('segments').all().order_by('-created_at')
    serializer_class = SerialRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='test-validate')
    def test_validate(self, request, pk=None):
        rule = self.get_object()
        scan_input = request.data.get('scan_input', '')
        
        if not scan_input:
            return Response({'status': 'FAIL', 'message': 'Input scan kosong'}, status=400)

        try:
            validate_serial_number(scan_input, rule)
            return Response({'status': 'OK', 'message': 'Format Sesuai ✅'})
        except ValidationError as e:
            return Response({'status': 'FAIL', 'message': e.message}, status=400)


# ==========================================
# 2. PART MASTER VIEWSET
# ==========================================
class PartMasterViewSet(viewsets.ModelViewSet):
    queryset = PartMaster.objects.select_related('validation_rule').all().order_by('-created_at')
    serializer_class = PartMasterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['part_name', 'part_number']
    
    # [UPDATE] Tambahkan 'compatible_product_types' agar bisa difilter di Frontend
    filterset_fields = ['validation_rule', 'is_qc_required', 'compatible_product_types']


# ==========================================
# 3. TRACEABILITY VERSION VIEWSET (BOM)
# ==========================================
class TraceabilityVersionViewSet(viewsets.ModelViewSet):
    queryset = TraceabilityVersion.objects.select_related('product_type')\
                .prefetch_related('requirements__part_master').all().order_by('-valid_from')
    
    serializer_class = TraceabilityVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['product_type', 'is_active'] 
    search_fields = ['version_code', 'product_type__name']