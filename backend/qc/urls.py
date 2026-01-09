from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QCTemplateViewSet, SubmitQCResultView, QCInspectionViewSet,SecureImageView

router = DefaultRouter()
router.register(r'templates', QCTemplateViewSet)
router.register(r'inspections', QCInspectionViewSet)

urlpatterns = [
    
    path('submit-result/', SubmitQCResultView.as_view(), name='submit-qc'),
    path('evidence/<str:filename>', SecureImageView.as_view(), name='secure-image'),
    path('', include(router.urls)),
]