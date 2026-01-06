from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BatteryRecordViewSet

router = DefaultRouter()
router.register(r'records', BatteryRecordViewSet) 
# Akses nanti: /api/battery/records/

urlpatterns = [
    path('', include(router.urls)),
]