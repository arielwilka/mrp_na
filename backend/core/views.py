from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import Role, RolePermission, UserRole, SystemModule
from .serializers import RoleSerializer, RolePermissionSerializer, SystemModuleSerializer
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserRoleSerializer
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet
from .models import PrintTemplate, LabelModule
from .serializers import PrintTemplateSerializer, LabelModuleSerializer
from django.db import transaction
from rest_framework.throttling import ScopedRateThrottle
# --- 1. Custom Login (Return Permissions) ---
class CustomAuthToken(ObtainAuthToken):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login_attempt'
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # Merge Permissions Logic
        final_permissions = {}
        user_roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
        perms = RolePermission.objects.filter(role__in=user_roles).select_related('module')

        for p in perms:
            code = p.module.code
            if code not in final_permissions:
                final_permissions[code] = {'create': False, 'read': False, 'update': False, 'delete': False}
            
            # OR Logic (Jika salah satu role boleh, maka boleh)
            final_permissions[code]['create'] |= p.can_create
            final_permissions[code]['read']   |= p.can_read
            final_permissions[code]['update'] |= p.can_update
            final_permissions[code]['delete'] |= p.can_delete

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_superuser': user.is_superuser, # Flag untuk akses menu setting
            'permissions': final_permissions
        })

# --- 2. API untuk Halaman Setting Role (Admin Only) ---
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAdminUser]
    # PENTING: Matikan Pagination agar logic 'find()' di frontend berjalan lancar
    pagination_class = None

    # --- FITUR 1: BATCH UPDATE (Tombol Simpan) ---
    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update_permissions(self, request):
        """
        Menerima List Permission yang sudah diedit user, lalu update ke DB sekaligus.
        """
        updates = request.data
        if not isinstance(updates, list):
            return Response({'detail': 'Data harus berupa list array.'}, status=400)

        try:
            with transaction.atomic():
                for item in updates:
                    p_id = item.get('id')
                    if p_id:
                        # Update hanya field boolean
                        RolePermission.objects.filter(id=p_id).update(
                            can_read=item.get('can_read', False),
                            can_create=item.get('can_create', False),
                            can_update=item.get('can_update', False),
                            can_delete=item.get('can_delete', False)
                        )
            
            return Response({'status': 'success', 'message': 'Permissions updated successfully'})
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    # --- FITUR 2: SYNC MATRIX (Tombol Fix Checkbox) ---
    @action(detail=False, methods=['post'], url_path='sync-matrix')
    def sync_matrix(self, request):
        """
        Memastikan setiap Role memiliki pasangan Permission untuk setiap Modul.
        """
        roles = Role.objects.all()
        modules = SystemModule.objects.all()
        created_count = 0
        
        with transaction.atomic():
            for role in roles:
                for module in modules:
                    _, created = RolePermission.objects.get_or_create(role=role, module=module)
                    if created:
                        created_count += 1

        return Response({'status': 'success', 'message': f'Matrix synced. {created_count} missing permissions created.'})

class SystemModuleViewSet(viewsets.ModelViewSet): 
    queryset = SystemModule.objects.all()
    serializer_class = SystemModuleSerializer
    permission_classes = [permissions.IsAdminUser] # Hanya Admin yang boleh edit modul
    pagination_class = None
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password=request.data['password']
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAdminUser]


class LabelModuleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API untuk mengambil list Modul beserta Field-nya.
    """
    queryset = LabelModule.objects.prefetch_related('fields').all()
    serializer_class = LabelModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

class PrintTemplateViewSet(viewsets.ModelViewSet):
    queryset = PrintTemplate.objects.all()
    serializer_class = PrintTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None