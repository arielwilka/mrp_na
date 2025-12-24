import { defineStore } from 'pinia';

interface UiState {
  isSidebarCollapsed: boolean;
  theme: 'light' | 'dark';
}

export const useUiStore = defineStore('ui', {
  state: (): UiState => ({
    isSidebarCollapsed: localStorage.getItem('sidebarCollapsed') === 'true',
    theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  }),

  actions: {
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
      localStorage.setItem('sidebarCollapsed', String(this.isSidebarCollapsed));
    },

    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', this.theme);
      this.applyTheme();
    },

    // Apply theme ke tag <body> agar CSS Variable global berubah
    applyTheme() {
      document.body.setAttribute('data-theme', this.theme);
    }
  }
});