from django.contrib import admin
from .models import SystemModule, Role, RolePermission, UserRole
from .models import LabelModule, LabelField, PrintTemplate
# 1. Konfigurasi Role Permission di dalam halaman Role
class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0 # Tidak perlu baris kosong berlebih
    can_delete = True

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [RolePermissionInline] # Edit permission langsung di halaman Role

# 2. Konfigurasi User Role di dalam halaman User (Opsional, tapi lebih rapi terpisah)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role', 'user')
# Tampilan agar Field bisa diinput langsung di dalam Modul
class LabelFieldInline(admin.TabularInline):
    model = LabelField
    extra = 1 # Menyiapkan 1 baris kosong default

@admin.register(LabelModule)
class LabelModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    inlines = [LabelFieldInline] # Pasang inline di sini

@admin.register(LabelField)
class LabelFieldAdmin(admin.ModelAdmin):
    list_display = ('field_label', 'field_key', 'module', 'dummy_data')
    list_filter = ('module',)

@admin.register(PrintTemplate)
class PrintTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'module_scope', 'created_at')

# 3. Register Model
admin.site.register(SystemModule)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRole, UserRoleAdmin)
# RolePermission tidak perlu diregister terpisah karena sudah ada di dalam RoleAdmin (inline)