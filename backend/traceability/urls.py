from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NumberingRuleViewSet, PartMasterViewSet, PartItemViewSet

router = DefaultRouter()
router.register(r'rules', NumberingRuleViewSet, basename='traceability-rules')
router.register(r'parts', PartMasterViewSet, basename='traceability-parts')
router.register(r'items', PartItemViewSet, basename='traceability-items')

urlpatterns = [
    path('', include(router.urls)),
]