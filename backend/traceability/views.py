from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import SerialRule, PartMaster, TraceabilityVersion
from .serializers import SerialRuleSerializer, PartMasterSerializer, TraceabilityVersionSerializer

# ==========================================
# 1. SERIAL RULE VIEWSET (Dengan Logic Validator)
# ==========================================
class SerialRuleViewSet(viewsets.ModelViewSet):
    queryset = SerialRule.objects.prefetch_related('segments').all().order_by('-created_at')
    serializer_class = SerialRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']

    # --- ACTION: TEST VALIDATOR (POST) ---
    # URL: /api/traceability/rules/{id}/test-validate/
    @action(detail=True, methods=['post'], url_path='test-validate')
    def test_validate(self, request, pk=None):
        rule = self.get_object()
        scan_input = request.data.get('scan_input', '')
        
        if not scan_input:
            return Response({'status': 'FAIL', 'message': 'Input scan kosong'}, status=400)

        is_valid, message = self._validate_rule(rule, scan_input)
        
        if is_valid:
            return Response({'status': 'OK', 'message': 'Format Sesuai ✅'})
        else:
            return Response({'status': 'FAIL', 'message': message}, status=400)

    # --- LOGIC CORE VALIDASI ---
    def _validate_rule(self, rule, text):
        segments = rule.segments.order_by('order')
        
        # Cursor default (0-based index)
        current_cursor = 0 
        
        for seg in segments:
            # 1. Tentukan Posisi Awal (Start)
            if seg.start_index is not None and seg.start_index > 0:
                # User input 1-based, kita convert ke 0-based
                start_pos = seg.start_index - 1
            else:
                # Mode Relative: Lanjut dari posisi terakhir
                start_pos = current_cursor

            # 2. Tentukan Posisi Akhir (End)
            end_pos = start_pos + seg.length

            # 3. Cek Batas String (Safety Check)
            if len(text) < end_pos:
                return False, f"Error Segmen #{seg.order}: String terlalu pendek. Mencoba baca index {start_pos}-{end_pos}, panjang input cuma {len(text)}."

            # 4. Ambil Potongan String (Slicing)
            chunk = text[start_pos : end_pos]

            # 5. Validasi Berdasarkan Tipe
            err_prefix = f"Posisi {start_pos+1}-{end_pos} (Segmen #{seg.order})"
            
            if seg.segment_type == 'STATIC':
                if chunk != seg.static_value:
                    return False, f"{err_prefix}: Harusnya '{seg.static_value}', terbaca '{chunk}'."
            
            elif seg.segment_type == 'DIGIT':
                if not chunk.isdigit():
                    return False, f"{err_prefix}: Harusnya Angka, terbaca '{chunk}'."
            
            elif seg.segment_type == 'CHAR':
                if not chunk.isalpha():
                    return False, f"{err_prefix}: Harusnya Huruf, terbaca '{chunk}'."
                    
            elif seg.segment_type == 'ALPHANUM':
                if not chunk.isalnum():
                    return False, f"{err_prefix}: Harusnya Alfanumerik, terbaca '{chunk}'."

            elif seg.segment_type == 'YEAR':
                if not chunk.isdigit() or len(chunk) != 2:
                     return False, f"{err_prefix}: Harusnya 2 digit Tahun."

            elif seg.segment_type == 'MONTH':
                if not chunk.isdigit() or not (1 <= int(chunk) <= 12):
                     return False, f"{err_prefix}: Harusnya Bulan (01-12)."

            # Update cursor untuk segmen berikutnya (jika mode relative)
            current_cursor = end_pos
            
        return True, "Validasi OK"


# ==========================================
# 2. PART MASTER VIEWSET
# ==========================================
class PartMasterViewSet(viewsets.ModelViewSet):
    queryset = PartMaster.objects.select_related('validation_rule').all().order_by('-created_at')
    serializer_class = PartMasterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['part_name', 'part_number']
    filterset_fields = ['validation_rule'] # Agar bisa filter "Mana part yang pakai rule X?"


# ==========================================
# 3. TRACEABILITY VERSION VIEWSET (BOM)
# ==========================================
class TraceabilityVersionViewSet(viewsets.ModelViewSet):
    # Optimasi query: join product_type dan prefetch requirements+part
    queryset = TraceabilityVersion.objects.select_related('product_type')\
                .prefetch_related('requirements__part_master').all().order_by('-valid_from')
    
    serializer_class = TraceabilityVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # Filter Penting: 
    # Frontend bisa request: /api/traceability/versions/?product_type=1&is_active=True
    filterset_fields = ['product_type', 'is_active'] 
    search_fields = ['version_code', 'product_type__name']