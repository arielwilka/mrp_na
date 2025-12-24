from rest_framework import serializers
from .models import Role, RolePermission, SystemModule, UserRole
from django.contrib.auth.models import User
from .models import PrintTemplate, LabelModule, LabelField
class SystemModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemModule
        fields = '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    module_code = serializers.ReadOnlyField(source='module.code')
    module_name = serializers.ReadOnlyField(source='module.name')

    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'module', 'module_name', 'module_code', 
                  'can_create', 'can_read', 'can_update', 'can_delete']

class RoleSerializer(serializers.ModelSerializer):
    # Nested permission agar saat ambil Role, permissions-nya ikut terbawa
    permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']

# Serializer untuk UserRole (Jembatan User -> Role)
class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='role.name')
    
    class Meta:
        model = UserRole
        fields = '__all__'

# Serializer User (Tampilkan role yang dimiliki)
class UserSerializer(serializers.ModelSerializer):
    # Kita gunakan nested serializer agar frontend tahu user ini role-nya apa
    user_roles = UserRoleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'user_roles']
        extra_kwargs = {'password': {'write_only': True}}

class LabelFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelField
        fields = ['id', 'field_key', 'field_label', 'dummy_data']

class LabelModuleSerializer(serializers.ModelSerializer):
    fields = LabelFieldSerializer(many=True, read_only=True) # Nested fields

    class Meta:
        model = LabelModule
        fields = ['id', 'name', 'code', 'fields']

class PrintTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintTemplate
        fields = '__all__'