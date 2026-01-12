// Permission per modul
export interface ModulePermission {
    create: boolean;
    read: boolean;
    update: boolean;
    delete: boolean;
}

// Map: "vin_record": { create: true ... }
export interface PermissionMap {
    [moduleCode: string]: ModulePermission;
}

// Respon Login (Sesuai punya Anda)
export interface LoginResponse {
    token: string;
    user_id: number;
    username: string;
    is_superuser: boolean;
    permissions: PermissionMap;
}

// [TAMBAHAN BARU] Interface User untuk State Pinia
export interface User {
    id: number;
    username: string;
    email?: string; // Optional
}

// Untuk Halaman Admin Role Manager
export interface RoleData {
    id: number;
    name: string;
    description: string;
    permissions: RolePermissionData[];
}

export interface RolePermissionData {
    id: number;
    module_code: string;
    module_name: string;
    can_create: boolean;
    can_read: boolean;
    can_update: boolean;
    can_delete: boolean;
}