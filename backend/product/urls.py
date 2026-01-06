from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BrandViewSet, ProductTypeViewSet, 
    ProductVariantViewSet, ProductColorViewSet
)

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'types', ProductTypeViewSet)
router.register(r'variants', ProductVariantViewSet)
router.register(r'colors', ProductColorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]