from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WorkCenterViewSet, 
    StationViewSet, 
    RouteViewSet, 
    RouteStationConfigViewSet, 
    ProductionPlanViewSet, 
    ProductionOrderViewSet,
    ProductionUnitViewSet, # ✅ VIEWSET BARU
    ShopFloorViewSet
)

router = DefaultRouter()

# Master Data
router.register(r'work-centers', WorkCenterViewSet)
router.register(r'stations', StationViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'route-steps', RouteStationConfigViewSet)

# Planning & Order
router.register(r'plans', ProductionPlanViewSet)
router.register(r'orders', ProductionOrderViewSet)

# ✅ Monitoring WIP (Memperbaiki 404 pada Frontend)
router.register(r'units', ProductionUnitViewSet, basename='production-unit')

urlpatterns = [
    # 1. URL Otomatis dari Router
    path('', include(router.urls)),

    # 2. DEFINISI MANUAL SHOP FLOOR (Endpoint khusus non-CRUD standar)
    path('shop-floor/scan-unit/', ShopFloorViewSet.as_view({'post': 'scan_unit'})),
    path('shop-floor/scan-part/', ShopFloorViewSet.as_view({'post': 'scan_part'})),
    path('shop-floor/process-station/', ShopFloorViewSet.as_view({'post': 'process_station'})),
    path('shop-floor/process-batch/', ShopFloorViewSet.as_view({'post': 'process_batch'})),
]