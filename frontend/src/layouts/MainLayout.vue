<template>
  <div class="layout-wrapper">
    <AppSidebar />
    <div class="main-content">
      <AppNavbar />
      <div class="content-body">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppNavbar from '@/components/layout/AppNavbar.vue';
</script>

<style scoped>
.layout-wrapper { 
  display: flex; 
  height: 100vh; 
  overflow: hidden; 
  background-color: var(--bg-body); 
}
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* Penting agar scroll ada di content-body */
}
.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg-body);
}

/* Animasi Transisi Halaman */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>