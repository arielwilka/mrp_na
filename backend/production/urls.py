from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkCenterViewSet, 
    StationViewSet, 
    RouteViewSet,               # Perhatikan nama class ini (sesuai views.py terakhir)
    RouteStationConfigViewSet,  # <--- WAJIB ADA (Untuk Tambah Step)
    ProductionPlanViewSet, 
    ProductionOrderViewSet, 
    ShopFloorViewSet
)

router = DefaultRouter()

# Master Data
router.register(r'work-centers', WorkCenterViewSet)
router.register(r'stations', StationViewSet)
router.register(r'routes', RouteViewSet)

# PENTING: Endpoint untuk Konfigurasi Step & Traceability
# Frontend api.ts memanggil '/route-steps/'
router.register(r'route-steps', RouteStationConfigViewSet)

# Planning & Order
router.register(r'plans', ProductionPlanViewSet)
router.register(r'orders', ProductionOrderViewSet)

urlpatterns = [
    # 1. Masukkan semua URL dari Router otomatis
    path('', include(router.urls)),

    # 2. DEFINISI MANUAL SHOP FLOOR (Agar URL sesuai dengan Frontend)
    # Frontend api.ts memanggil URL dengan format "kebab-case" (scan-unit)
    # sedangkan router default kadang membuat "snake_case" (scan_unit).
    path('shop-floor/scan-unit/', ShopFloorViewSet.as_view({'post': 'scan_unit'})),
    path('shop-floor/scan-part/', ShopFloorViewSet.as_view({'post': 'scan_part'})),
    path('shop-floor/process-station/', ShopFloorViewSet.as_view({'post': 'process_station'})),
]