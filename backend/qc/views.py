from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

# Import Logic & Models
from traceability.models import PartMaster
from traceability.utils import validate_serial_number  # <--- IMPORT PENTING
from .models import InventoryItem, QCInspection, QCTemplate
from .serializers import InventoryItemSerializer, QCSubmitSerializer, QCTemplateSerializer, QCInspectionListSerializer

# Viewset Read-Only untuk cek Template apa saja yg harus diisi
class QCTemplateViewSet(viewsets.ModelViewSet):
    queryset = QCTemplate.objects.all()
    serializer_class = QCTemplateSerializer
    filterset_fields = ['part_master']

# API Endpoint Utama: Submit Hasil QC
class SubmitQCResultView(APIView):
    """
    Endpoint ini melakukan 3 hal:
    1. VALIDASI Serial Number sesuai Rule (jika ada).
    2. Mendaftarkan Barang ke Inventory (jika belum ada).
    3. Menyimpan Hasil QC & Update Status.
    """
    def post(self, request):
        serializer = QCSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        # 1. Ambil PartMaster & Serial Number
        part = get_object_or_404(PartMaster, pk=data['part_id'])
        input_sn = data['serial_number']

        # --- [START] LOGIC VALIDASI RULE ---
        # Sebelum masuk database, cek dulu apakah format SN sesuai aturan?
        if part.validation_rule:
            try:
                # Panggil "Satpam" dari utils.py
                validate_serial_number(input_sn, part.validation_rule)
            except ValidationError as e:
                # Jika tidak lolos validasi, return 400 Bad Request
                return Response({
                    "error": "Format Serial Number Tidak Sesuai!",
                    "detail": e.message  # Pesan detail dari utils (misal: "Harusnya Angka")
                }, status=status.HTTP_400_BAD_REQUEST)
        # --- [END] LOGIC VALIDASI RULE ---

        try:
            with transaction.atomic():
                # 2. Get or Create Inventory Item (Receiving Logic)
                # Jika barang baru discan pertama kali, dia otomatis dibuat.
                inventory_item, created = InventoryItem.objects.get_or_create(
                    part_master=part,
                    serial_number=input_sn
                )

                # 3. Tentukan Status Baru
                # Logic: Jika PASS -> OK, Jika FAIL -> NG
                new_status = 'OK' if data['decision'] == 'PASS' else 'NG'
                
                # Update Status Inventory
                inventory_item.current_status = new_status
                inventory_item.save()

                # 4. Simpan Log Detail (History)
                QCInspection.objects.create(
                    inventory_item=inventory_item,
                    inspector=request.user if request.user.is_authenticated else None,
                    qc_result_data=data['qc_data'], # JSON disimpan mentah
                    judge_decision=data['decision']
                )

            return Response({
                "message": "QC Result Saved Successfully",
                "serial_number": inventory_item.serial_number,
                "final_status": new_status
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class QCInspectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API untuk melihat riwayat inspeksi.
    ReadOnly karena history tidak boleh diedit manual, hanya boleh dibaca.
    """
    queryset = QCInspection.objects.select_related(
        'inventory_item', 
        'inventory_item__part_master', 
        'inspector'
    ).all().order_by('-inspection_date')
    
    serializer_class = QCInspectionListSerializer
    filterset_fields = ['judge_decision', 'inventory_item__part_master']