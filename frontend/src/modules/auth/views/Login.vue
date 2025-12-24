<template>
  <div class="login-wrapper">
    <div class="login-card">
      <h2>Production Master</h2>
      <p>Sign in to your account</p>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label>Username</label>
          <input v-model="username" type="text" required />
        </div>
        
        <div class="mb-4">
          <label>Password</label>
          <input v-model="password" type="password" required />
        </div>

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Loading...' : 'Login' }}
        </button>

        <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../../../stores/auth'; // Go up 3 levels
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMsg = ref('');

const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  try {
    await authStore.login(username.value, password.value);
    router.push('/'); // Go to Dashboard
  } catch (err) {
    errorMsg.value = "Login Failed. Check credentials.";
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-wrapper { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f8fafc; }
.login-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 350px; }
h2 { text-align: center; margin-top: 0; color: #0f172a; }
p { text-align: center; color: #64748b; margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 1rem; }
label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.875rem; color: #334155; }
input { width: 100%; padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 4px; box-sizing: border-box; }
button { width: 100%; padding: 0.75rem; background: #2563eb; color: white; border: none; border-radius: 4px; font-weight: 600; cursor: pointer; }
button:disabled { background: #94a3b8; }
.error { color: #dc2626; text-align: center; margin-top: 1rem; font-size: 0.875rem; }
</style>