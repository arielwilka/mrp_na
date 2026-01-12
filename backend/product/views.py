from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Brand, ProductType, ProductVariant, ProductColor
from .serializers import (
    BrandSerializer, ProductTypeSerializer, 
    ProductVariantSerializer, ProductColorSerializer
)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.select_related('brand').prefetch_related('variants', 'colors').all().order_by('name')
    serializer_class = ProductTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    # UPDATE: Tambahkan 'tracking_mode' dan 'scheduling_policy' ke filter
    filterset_fields = ['brand', 'tracking_mode', 'scheduling_policy']

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product_type').all().order_by('product_type', 'name')
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_type']

class ProductColorViewSet(viewsets.ModelViewSet):
    queryset = ProductColor.objects.select_related('product_type').all().order_by('name')
    serializer_class = ProductColorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_type']