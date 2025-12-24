<template>
  <div class="layout-wrapper">
    
    <AppSidebar />

    <div class="main-content">
      
      <AppNavbar />

      <div class="content-body">
        <router-view></router-view>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import AppSidebar from '../components/layout/AppSidebar.vue';
import AppNavbar from '../components/layout/AppNavbar.vue';
</script>

<style scoped>
/* HANYA CSS STRUKTUR LAYOUT */
.layout-wrapper { 
  display: flex; 
  height: 100vh; 
  overflow: hidden; 
  background-color: var(--bg-body); 
  color: var(--text-primary); 
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-body);
  transition: background-color 0.3s;
}

.content-body {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}
</style>