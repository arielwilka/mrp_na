<template>
  <router-view></router-view>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useUiStore } from './stores/ui';

const uiStore = useUiStore();

onMounted(() => {
  uiStore.applyTheme(); // Set tema sesuai localStorage saat reload
});
</script>