from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VinRecordViewSet, 
    VehicleTypeViewSet, 
    YearCodeViewSet, 
    VinPrefixViewSet,        # <--- Sudah ada
    VehicleVariantViewSet,   # <--- Sudah ada
    VehicleColorViewSet      # <--- Sudah ada
)

router = DefaultRouter()

# Daftarkan semua URL milik modul VIN disini
router.register(r'records', VinRecordViewSet, basename='vin-record')
router.register(r'types', VehicleTypeViewSet)
router.register(r'years', YearCodeViewSet)
router.register(r'vin-prefixes', VinPrefixViewSet)
router.register(r'variants', VehicleVariantViewSet)
router.register(r'colors', VehicleColorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]