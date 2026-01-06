from rest_framework import viewsets, permissions, parsers, filters
from .models import BatteryRecord
from .serializers import BatteryRecordSerializer

class BatteryRecordViewSet(viewsets.ModelViewSet):
    queryset = BatteryRecord.objects.all()
    serializer_class = BatteryRecordSerializer
    permission_classes = [permissions.IsAuthenticated] # User harus login
    
    # PARSER: Wajib ada untuk handle 'multipart/form-data' (Upload File)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    
    # Fitur Search & Filter bawaan DRF
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['serial_number', 'condition']
    ordering_fields = ['created_at', 'condition']

    # Otomatis isi created_by dengan user yang login
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)