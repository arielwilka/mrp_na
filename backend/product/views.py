from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Brand, ProductType, ProductVariant, ProductColor
from .serializers import (
    BrandSerializer, ProductTypeSerializer, 
    ProductVariantSerializer, ProductColorSerializer
)
# Asumsi Anda menggunakan permission class yang sama (bisa diimport dari core/utils)
from rest_framework.permissions import IsAuthenticatedOrReadOnly 
# Atau pakai custom permission 'IsVinMasterOrReadOnly' jika sudah dipindahkan ke module global/core

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated]
class ProductTypeViewSet(viewsets.ModelViewSet):
    # Prefetch variants & colors agar query efisien saat nested serializer
    queryset = ProductType.objects.select_related('brand').prefetch_related('variants', 'colors').all().order_by('name')
    serializer_class = ProductTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['brand']

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