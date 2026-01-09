import { defineStore } from 'pinia';
import axios from 'axios';
// Import type dari file types Anda
import type { LoginResponse, PermissionMap, User } from '../types';

interface AuthState {
  token: string | null;
  user: User | null; // <--- State User Object
  isSuperuser: boolean;
  permissions: PermissionMap;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token') || null,
    // Load user object dari localStorage
    user: JSON.parse(localStorage.getItem('user') || 'null'), 
    isSuperuser: localStorage.getItem('is_superuser') === 'true',
    permissions: JSON.parse(localStorage.getItem('permissions') || '{}'),
  }),

  getters: {
    isAuthenticated: (state): boolean => !!state.token,
    // Helper username aman
    username: (state): string => state.user?.username || 'Guest',
  },

  actions: {
    async login(username: string, password: string) {
      try {
        // Gunakan relative path (axios base url sudah di-set di main.ts)
        const res = await axios.post<LoginResponse>('/login/', { username, password });
        
        // Destructure response sesuai interface LoginResponse Anda
        const { token, is_superuser, permissions, user_id, username: resUsername } = res.data;

        // BENTUK MANUAL OBJECT USER DARI RESPONSE FLAT
        const userData: User = {
            id: user_id,
            username: resUsername
        };

        // Simpan ke State
        this.token = token;
        this.user = userData;
        this.isSuperuser = is_superuser;
        this.permissions = permissions;

        // Simpan ke LocalStorage
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData)); // Simpan object user
        localStorage.setItem('is_superuser', String(is_superuser));
        localStorage.setItem('permissions', JSON.stringify(permissions));
        
        axios.defaults.headers.common['Authorization'] = `Token ${token}`;
        return true;
      } catch (err) {
        throw err;
      }
    },

    logout() {
        this.token = null;
        this.user = null;
        this.isSuperuser = false;
        this.permissions = {};
        
        localStorage.clear();
        delete axios.defaults.headers.common['Authorization'];
    },

    can(module: string, action: 'create' | 'read' | 'update' | 'delete'): boolean {
        if (this.isSuperuser) return true;
        // Optional chaining untuk keamanan jika permissions null/undefined
        return this.permissions?.[module]?.[action] || false;
    }
  }
});