<template>
  <div class="error-page">
    <h1>404</h1>
    <p>Halaman tidak ditemukan.</p>
    <router-link to="/" class="btn">Kembali ke Dashboard</router-link>
  </div>
</template>
<style scoped>
.error-page { text-align: center; padding-top: 100px; }
h1 { font-size: 5rem; margin: 0; color: #cbd5e1; }
.btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; }
</style>