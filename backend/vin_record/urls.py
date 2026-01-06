from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VinRecordViewSet, YearCodeViewSet, VinPrefixViewSet,TraceableProductTypeViewSet

router = DefaultRouter()

# Hanya mendaftarkan URL milik domain VIN Record
router.register(r'records', VinRecordViewSet, basename='vin-record')
router.register(r'years', YearCodeViewSet)
router.register(r'prefixes', VinPrefixViewSet)
router.register(r'product-options', TraceableProductTypeViewSet, basename='vin-product-options')
urlpatterns = [
    path('', include(router.urls)),
]