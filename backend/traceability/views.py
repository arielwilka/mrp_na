from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import NumberingRule, PartMaster, PartItem
from .serializers import NumberingRuleSerializer, PartMasterSerializer, PartItemSerializer

class NumberingRuleViewSet(viewsets.ModelViewSet):
    queryset = NumberingRule.objects.all()
    serializer_class = NumberingRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

class PartMasterViewSet(viewsets.ModelViewSet):
    queryset = PartMaster.objects.select_related('numbering_rule').all()
    serializer_class = PartMasterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'part_number']
    filterset_fields = ['numbering_rule'] # Bisa filter by rule

class PartItemViewSet(viewsets.ModelViewSet):
    queryset = PartItem.objects.select_related('part_master', 'created_by').all().order_by('-id')
    serializer_class = PartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Filter Penting
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['serial_number', 'installed_vin', 'batch_no']
    filterset_fields = ['part_master', 'status', 'installed_vin'] # Filter by Part Type atau Status
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)