from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SerialRuleViewSet, PartMasterViewSet, TraceabilityVersionViewSet
from .utils import validate_serial_number

router = DefaultRouter()

# Register Endpoint
router.register(r'rules', SerialRuleViewSet, basename='rules')
router.register(r'parts', PartMasterViewSet, basename='parts')
router.register(r'versions', TraceabilityVersionViewSet, basename='versions')

urlpatterns = [
    path('', include(router.urls)),
]