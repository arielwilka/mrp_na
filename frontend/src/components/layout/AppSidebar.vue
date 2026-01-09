<template>
  <aside :class="['sidebar', { collapsed: uiStore.isSidebarCollapsed }]">
    
    <div class="sidebar-header">
      <span class="brand-text" v-if="!uiStore.isSidebarCollapsed">PT. N A</span>
      <span class="brand-icon" v-else>NA</span>
    </div>

    <nav class="sidebar-nav">
      
      <template v-for="(item, index) in filteredMenu" :key="index">
        
        <router-link 
          v-if="!item.children" 
          :to="item.to!" 
          class="nav-item"
          :title="uiStore.isSidebarCollapsed ? item.label : ''"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="label">{{ item.label }}</span>
        </router-link>

        <div v-else class="nav-group">
          <div 
            class="nav-group-label" 
            :class="{ 'admin-group': item.adminOnly }" 
            v-if="!uiStore.isSidebarCollapsed"
          >
            {{ item.label }}
          </div>

          <router-link 
            v-for="(child, cIndex) in item.children" 
            :key="cIndex" 
            :to="child.to!" 
            class="nav-item sub-item"
            :title="uiStore.isSidebarCollapsed ? child.label : ''"
          >
            <span class="icon">{{ child.icon }}</span>
            <span class="label">{{ child.label }}</span>
          </router-link>
        </div>

      </template>

    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUiStore } from '../../stores/ui';
import { useAuthStore } from '../../stores/auth';
import { menuItems } from '../../router/menu'; 

const uiStore = useUiStore();
const authStore = useAuthStore();

const filteredMenu = computed(() => {
  const isSuperuser = authStore.isSuperuser;
  
  return menuItems.map(item => {
    // 1. Cek Permission Module (Parent)
    if (item.moduleName && !authStore.can(item.moduleName, 'read')) return null;
    
    // 2. Cek Superuser Only (Parent)
    if (item.adminOnly && !isSuperuser) return null;

    // 3. Cek Children
    if (item.children) {
      const visibleChildren = item.children.filter(child => {
         if (child.adminOnly && !isSuperuser) return false;
         if (child.moduleName && !authStore.can(child.moduleName, 'read')) return false;
         return true;
      });
      
      // Jika semua anak difilter (kosong), parent juga disembunyikan
      if (visibleChildren.length === 0) return null;
      
      return { ...item, children: visibleChildren };
    }
    
    return item;
  }).filter(item => item !== null);
});
</script>

<style scoped>
/* KONTAINER UTAMA SIDEBAR */
.sidebar { 
  width: var(--sidebar-width); 
  background-color: var(--bg-sidebar); 
  color: var(--text-sidebar); 
  display: flex; 
  flex-direction: column; 
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
  box-shadow: 2px 0 10px rgba(0,0,0,0.1); 
  z-index: 10; 
  white-space: nowrap; 
  height: 100vh; /* Wajib full height agar bisa scroll */
}

.sidebar.collapsed { 
  width: var(--sidebar-width-collapsed); 
}

/* HEADER SIDEBAR */
.sidebar-header { 
  flex-shrink: 0; /* Header jangan ikut mengecil */
  height: var(--header-height); 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: 800; 
  font-size: 1.25rem; 
  letter-spacing: 1px; 
  color: white; 
  background-color: rgba(0,0,0,0.1); 
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

/* AREA NAVIGASI (SCROLLABLE) */
.sidebar-nav {
  flex: 1;              /* Isi sisa ruang kosong */
  overflow-y: auto;     /* Scroll vertikal aktif */
  overflow-x: hidden;   /* Hilangkan scroll horizontal */
  padding-bottom: 20px;
}

/* Kustomisasi Scrollbar (Agar elegan di background gelap) */
.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-track { background: transparent; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }

/* ITEM NAVIGASI */
.nav-item { 
  display: flex; 
  align-items: center; 
  padding: 12px 24px; 
  color: var(--text-sidebar); 
  text-decoration: none; 
  font-weight: 500; 
  border-left: 3px solid transparent; 
  transition: all 0.2s; 
  font-size: 0.95rem;
}

.nav-item:hover { 
  background-color: rgba(255,255,255,0.05); 
  color: white; 
}

/* State Aktif (Menggunakan var primary-color) */
.nav-item.router-link-active { 
  background-color: rgba(255, 255, 255, 0.08); 
  color: white; 
  border-left-color: var(--primary-color); /* Garis indikator kiri */
}

/* Ikon */
.nav-item .icon { 
  font-size: 1.2rem; 
  margin-right: 12px; 
  min-width: 24px; 
  text-align: center;
  transition: margin 0.3s;
}

/* Perilaku saat Collapsed */
.sidebar.collapsed .label, 
.sidebar.collapsed .nav-group-label { 
  display: none; 
}

.sidebar.collapsed .nav-item { 
  justify-content: center; 
  padding: 16px 0; 
}

.sidebar.collapsed .nav-item .icon { 
  margin-right: 0; 
}

/* GROUP LABEL */
.nav-group { margin-top: 5px; }

.nav-group-label { 
  padding: 15px 24px 8px; 
  font-size: 0.7rem; 
  text-transform: uppercase; 
  color: var(--text-secondary); /* Pakai variabel agar konsisten */
  font-weight: 700; 
  letter-spacing: 0.5px; 
  opacity: 0.7;
}

.nav-group-label.admin-group {
  margin-top: 10px;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 15px;
  color: #fbbf24; /* Emas khusus admin */
  opacity: 1;
}

/* Sub Item Indentation */
.sub-item { 
  padding-left: 35px; 
  font-size: 0.9rem; 
}

.sidebar.collapsed .sub-item { 
  padding-left: 0; 
}
</style>