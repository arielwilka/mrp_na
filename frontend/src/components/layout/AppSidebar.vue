<template>
  <aside :class="['sidebar', { collapsed: uiStore.isSidebarCollapsed }]">
    
    <div class="sidebar-header">
      <span class="brand-text" v-if="!uiStore.isSidebarCollapsed">PRO MASTER</span>
      <span class="brand-icon" v-else>PM</span>
    </div>

    <nav class="sidebar-nav">
      
      <template v-for="(item, index) in filteredMenu" :key="index">
        
        <router-link v-if="!item.children" :to="item.to!" class="nav-item">
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

          <router-link v-for="(child, cIndex) in item.children" :key="cIndex" :to="child.to!" class="nav-item sub-item">
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
.sidebar { width: var(--sidebar-width); background-color: var(--bg-sidebar); color: var(--text-sidebar); display: flex; flex-direction: column; transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 2px 0 10px rgba(0,0,0,0.1); z-index: 10; white-space: nowrap; }
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }

.sidebar-header { height: var(--header-height); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.25rem; letter-spacing: 1px; color: white; background-color: rgba(0,0,0,0.1); }

.nav-item { display: flex; align-items: center; padding: 14px 24px; color: var(--text-sidebar); text-decoration: none; font-weight: 500; border-left: 3px solid transparent; transition: all 0.2s; }
.nav-item:hover { background-color: rgba(255,255,255,0.05); color: white; }
.nav-item.router-link-active { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border-left-color: #60a5fa; }
.nav-item .icon { font-size: 1.2rem; margin-right: 12px; min-width: 24px; text-align: center;}

.sidebar.collapsed .label, .sidebar.collapsed .nav-group-label { display: none; }
.sidebar.collapsed .nav-item { justify-content: center; padding: 16px 0; }
.sidebar.collapsed .nav-item .icon { margin: 0; }

.nav-group { margin-top: 10px; }
.nav-group-label { padding: 10px 24px 5px; font-size: 0.7rem; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.5px; }

/* Style Khusus Header Group Admin (Opsional, agar terlihat beda seperti sebelumnya) */
.nav-group-label.admin-group {
  margin-top: 15px;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 15px;
  color: #fbbf24; /* Warna Emas */
}

.sub-item { padding-left: 35px; font-size: 0.95rem; }
.sidebar.collapsed .sub-item { padding-left: 0; }
</style>