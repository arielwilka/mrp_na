from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SerialRuleViewSet, PartMasterViewSet, TraceabilityVersionViewSet

router = DefaultRouter()

router.register(r'rules', SerialRuleViewSet, basename='rules')
router.register(r'parts', PartMasterViewSet, basename='parts')
router.register(r'versions', TraceabilityVersionViewSet, basename='versions')

urlpatterns = [
    path('', include(router.urls)),
]