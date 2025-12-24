import { defineStore } from 'pinia';
import axios from 'axios';
import type { LoginResponse, PermissionMap } from '../types';

interface AuthState {
  token: string | null;
  isSuperuser: boolean;
  permissions: PermissionMap;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token') || null,
    isSuperuser: localStorage.getItem('is_superuser') === 'true',
    permissions: JSON.parse(localStorage.getItem('permissions') || '{}'),
  }),

  getters: {
    // --- TAMBAHKAN INI (Solusi Error 2) ---
    isAuthenticated: (state): boolean => !!state.token,
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const res = await axios.post<LoginResponse>('http://127.0.0.1:8000/api/login/', { username, password });
        
        const { token, is_superuser, permissions } = res.data;

        this.token = token;
        this.isSuperuser = is_superuser;
        this.permissions = permissions;

        localStorage.setItem('token', token);
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
        this.isSuperuser = false;
        this.permissions = {};
        localStorage.clear();
        delete axios.defaults.headers.common['Authorization'];
    },

    can(module: string, action: 'create' | 'read' | 'update' | 'delete'): boolean {
        if (this.isSuperuser) return true;
        return this.permissions[module]?.[action] || false;
    }
  }
});