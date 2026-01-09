from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# --- TAMBAHAN PENTING UNTUK GAMBAR ---
from django.conf import settings
from django.conf.urls.static import static

# --- IMPORT VIEWSETS CORE ---
from core.views import (
    CustomAuthToken, 
    RoleViewSet, 
    RolePermissionViewSet, 
    SystemModuleViewSet, 
    UserViewSet, 
    UserRoleViewSet,
    LabelModuleViewSet,
    PrintTemplateViewSet
)

router = DefaultRouter()

# --- REGISTER MODUL CORE ---
router.register(r'roles', RoleViewSet)
router.register(r'role-permissions', RolePermissionViewSet)
router.register(r'system-modules', SystemModuleViewSet)
router.register(r'users', UserViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'templates', PrintTemplateViewSet)
router.register(r'label-modules', LabelModuleViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', CustomAuthToken.as_view()), 
    
    # 1. URL Modul Core
    path('api/', include(router.urls)), 
    
    # 2. URL Modul Master Product
    path('api/product/', include('product.urls')),

    # 3. URL Modul VIN & Traceability
    path('api/vin-record/', include('vin_record.urls')), 
    path('api/traceability/', include('traceability.urls')),

    # 4. URL Modul QC (Receiving & Inspection)
    path('api/qc/', include('qc.urls')),

    # 5. URL Modul PRODUCTION (BARU - MRP Hybrid)
    # Endpoint utama: http://localhost:8000/api/production/orders/
    # Endpoint operator: http://localhost:8000/api/production/shop-floor/
    path('api/production/', include('production.urls')),

    # 6. URL Modul Battery (Legacy/Eksisting)
    path('api/battery/', include('battery_record.urls')), 
]

# --- KONFIGURASI AGAR GAMBAR BISA DIBUKA (DEV MODE) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)