from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QCTemplateViewSet, SubmitQCResultView, QCInspectionViewSet

router = DefaultRouter()
router.register(r'templates', QCTemplateViewSet)
router.register(r'inspections', QCInspectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('submit-result/', SubmitQCResultView.as_view(), name='qc-submit'),
]