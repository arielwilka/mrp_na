<template>
  <header class="navbar">
    <div class="navbar-left">
      <button @click="uiStore.toggleSidebar" class="btn-icon">
          <span v-if="uiStore.isSidebarCollapsed">➡️</span>
          <span v-else>⬅️</span>
      </button>
      <h3 class="page-title">Dashboard</h3> 
      </div>

    <div class="navbar-right">
      <div class="printer-selector">
        <span class="status-dot" :class="{ online: printStore.isAgentConnected }" title="Status Agent">●</span>
        <select :value="printStore.selectedPrinter" @change="handlePrinterChange">
          <option value="" disabled>-- Pilih Printer --</option>
          <option v-for="p in printStore.availablePrinters" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>

      <button @click="uiStore.toggleTheme" class="btn-icon" title="Ubah Tema">
        <span v-if="uiStore.theme === 'light'">🌙</span>
        <span v-else>☀️</span>
      </button>
      
      <div class="profile-menu">
        <div class="avatar">U</div>
        <button @click="handleLogout" class="btn-logout">Logout</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUiStore } from '../../stores/ui';
import { useAuthStore } from '../../stores/auth';
import { usePrintStore } from '../../stores/print';

const uiStore = useUiStore();
const authStore = useAuthStore();
const printStore = usePrintStore();
const router = useRouter();

onMounted(() => {
  printStore.checkAgent();
});

const handlePrinterChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  printStore.setPrinter(target.value);
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
/* CSS KHUSUS NAVBAR */
.navbar {
  height: var(--header-height);
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  z-index: 5;
}

.navbar-left, .navbar-right { display: flex; align-items: center; gap: 16px; }
.page-title { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.btn-icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-primary); }

.printer-selector { display: flex; align-items: center; gap: 8px; }
.printer-selector select { padding: 5px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-body); color: var(--text-primary); }
.status-dot { font-size: 1.5rem; color: #ef4444; line-height: 0; }
.status-dot.online { color: #22c55e; }

.profile-menu { display: flex; align-items: center; gap: 10px; }
.avatar { 
  width: 32px; height: 32px; background: var(--primary-color); 
  color: white; border-radius: 50%; display: flex; 
  align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;
}
.btn-logout { font-size: 0.8rem; color: #ef4444; background: none; border: none; cursor: pointer; font-weight: 600; }
.btn-logout:hover { text-decoration: underline; }
</style>