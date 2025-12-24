from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# --- HANYA IMPORT VIEWSETS MILIK CORE ---
from .views import (
    CustomAuthToken, 
    RoleViewSet, 
    RolePermissionViewSet, 
    SystemModuleViewSet, 
    UserViewSet, 
    UserRoleViewSet,
    LabelModuleViewSet,
    PrintTemplateViewSet
)

# [HAPUS BAGIAN INI] - Jangan import view vin_record disini lagi!
# from vin_record.views import ... (HAPUS)

router = DefaultRouter()

# --- REGISTER HANYA MODUL CORE ---
router.register(r'roles', RoleViewSet)
router.register(r'role-permissions', RolePermissionViewSet)
router.register(r'system-modules', SystemModuleViewSet)
router.register(r'users', UserViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'templates', PrintTemplateViewSet)
router.register(r'label-modules', LabelModuleViewSet)

# [HAPUS BAGIAN INI] - Jangan register vin disini!
# router.register(r'types', VehicleTypeViewSet) ... (HAPUS)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', CustomAuthToken.as_view()), 
    
    # 1. URL untuk Modul Core (User, Role, dll)
    path('api/', include(router.urls)), 

    # 2. URL untuk Modul VIN RECORD (PENTING!)
    # Django akan membaca file backend/vin_record/urls.py
    # dan menggabungkannya ke bawah prefix 'api/'
    path('api/', include('vin_record.urls')), 
]