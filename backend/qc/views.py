import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import FileResponse, HttpResponseNotFound

from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Import Models & Logic
from traceability.models import PartMaster
from traceability.utils import validate_serial_number  # <--- Logic Validasi Anda
from .models import InventoryItem, QCInspection, QCTemplate
from .serializers import InventoryItemSerializer, QCSubmitSerializer, QCTemplateSerializer, QCInspectionListSerializer

# Import Helper Gambar (Pastikan file utils.py sudah ada)
from .utils import save_base64_image 

# ==============================================================================
# 1. TEMPLATE VIEWSET
# ==============================================================================
class QCTemplateViewSet(viewsets.ModelViewSet):
    queryset = QCTemplate.objects.all().order_by('id')
    serializer_class = QCTemplateSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['part_master']

# ==============================================================================
# 2. SUBMIT QC RESULT (Logic Gabungan)
# ==============================================================================
class SubmitQCResultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QCSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # Ambil Serial Number untuk penamaan file
        # Pastikan SN tidak kosong (fallback ke 'UNKNOWN' jika error)
        current_sn = data.get('serial_number', 'UNKNOWN')

        # ---------------------------------------------------------
        # STEP 1: PRE-PROCESS GAMBAR
        # ---------------------------------------------------------
        raw_qc_data = data.get('qc_data', {})
        processed_qc_data = {}

        for key, value in raw_qc_data.items():
            if isinstance(value, str) and value.startswith('data:image'):
                try:
                    # --- PERUBAHAN DISINI ---
                    # Gabungkan SN dan Nama Field (Key) sebagai identifier
                    # Contoh: "SN12345-visual_check"
                    file_name_identifier = f"{current_sn}-{key}"
                    
                    file_path = save_base64_image(value, file_name_identifier)
                    
                    processed_qc_data[key] = f"SECURE_IMG:{file_path}"
                except Exception as e:
                    print(f"Gagal simpan gambar {key}: {e}")
                    processed_qc_data[key] = None 
            else:
                processed_qc_data[key] = value
        
        # ---------------------------------------------------------
        # STEP 2: AMBIL DATA & VALIDASI RULE
        # ---------------------------------------------------------
        part = get_object_or_404(PartMaster, pk=data['part_id'])
        input_sn = data['serial_number']

        # Cek Rule Code dari Traceability
        if part.validation_rule:
            try:
                # Panggil "Satpam" dari utils.py
                validate_serial_number(input_sn, part.validation_rule)
            except ValidationError as e:
                return Response({
                    "error": "Format Serial Number Tidak Sesuai!",
                    "detail": e.message 
                }, status=status.HTTP_400_BAD_REQUEST)

        # ---------------------------------------------------------
        # STEP 3: DATABASE TRANSACTION (Create Inventory & QC)
        # ---------------------------------------------------------
        try:
                with transaction.atomic():
                    # A. Get or Create Inventory Item
                    inventory_item, created = InventoryItem.objects.get_or_create(
                        part_master=part,
                        serial_number=input_sn,
                        defaults={
                            # PERBAIKAN 1: Nama field 'current_status'
                            # PERBAIKAN 2: Value 'PENDING' sesuai STATUS_CHOICES di models.py
                            'current_status': 'PENDING', 
                            # 'batch_number': '...' (Opsional jika mau diisi)
                        }
                    )

                    # B. Tentukan Status Akhir (PASS->OK, FAIL->NG)
                    # Sesuai STATUS_CHOICES: 'OK' atau 'NG'
                    new_status = 'OK' if data['decision'] == 'PASS' else 'NG'
                    
                    # C. Update Status Inventory
                    inventory_item.current_status = new_status # <--- Pakai current_status
                    inventory_item.save()

                    # D. Simpan Log QC
                    QCInspection.objects.create(
                        inventory_item=inventory_item,
                        inspector=request.user,
                        qc_result_data=processed_qc_data,
                        judge_decision=data['decision']
                    )

                return Response({
                    "message": "QC Result Saved Successfully",
                    "serial_number": inventory_item.serial_number,
                    "final_status": new_status,
                    "is_new_item": created
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
# 3. SECURE IMAGE ACCESS (Pintu Gerbang Gambar)
# ==============================================================================
class SecureImageView(APIView):
    """
    Hanya user login yang bisa akses gambar di folder private.
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request, filename):
        # Folder penyimpanan rahasia (Sama dengan utils.py)
        file_directory = os.path.join(settings.MEDIA_ROOT, 'private_evidence')
        file_path = os.path.join(file_directory, filename)
        
        # Security Check: Cegah Directory Traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(file_directory)):
             return HttpResponseNotFound("Akses file tidak valid.")

        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
        else:
            return HttpResponseNotFound("Gambar tidak ditemukan.")


# ==============================================================================
# 4. HISTORY VIEWSET
# ==============================================================================
class QCInspectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QCInspection.objects.select_related(
        'inventory_item', 
        'inventory_item__part_master', 
        'inspector'
    ).all().order_by('-inspection_date')
    
    serializer_class = QCInspectionListSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['judge_decision', 'inventory_item__part_master']