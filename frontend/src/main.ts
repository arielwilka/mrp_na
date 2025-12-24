// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)

// --- 1. CONFIG AXIOS GLOBAL ---
// Set Base URL agar tidak perlu ketik berulang-ulang di component
axios.defaults.baseURL = 'http://127.0.0.1:8000/api';

// --- 2. RESTORE TOKEN (SAAT REFRESH) ---
const token = localStorage.getItem('token');
if (token) {
  axios.defaults.headers.common['Authorization'] = `Token ${token}`;
}

// --- 3. GLOBAL INTERCEPTOR (PENANGKAL ERROR) ---
axios.interceptors.response.use(
  (response) => {
    // Jika sukses (200, 201), loloskan data
    return response;
  },
  (error) => {
    // Jika ada error dari Backend
    if (error.response) {
      
      const status = error.response.status;

      // CASE A: THROTTLING (429) - User terlalu ngebut
      if (status === 429) {
        alert("⚠️ TERLALU BANYAK REQUEST!\n\nSistem mendeteksi aktivitas berlebihan. Mohon tunggu beberapa saat sebelum mencoba lagi.");
      } 
      
      // CASE B: RACE CONDITION / CONFLICT (409) - Data tabrakan
      else if (status === 409) {
        alert("⚠️ KONFLIK DATA!\n\nData yang Anda input bentrok dengan data lain (mungkin baru saja diambil user lain). Silakan refresh dan coba lagi.");
      }

      // CASE C: UNAUTHORIZED (401) - Token Expired / Invalid
      else if (status === 401) {
        // Hapus token sampah
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        delete axios.defaults.headers.common['Authorization'];
        
        // Paksa pindah ke login (jika bukan di halaman login)
        if (router.currentRoute.value.path !== '/login') {
          alert("Sesi Anda telah berakhir. Silakan login kembali.");
          router.push('/login');
        }
      }
      
      // CASE D: SERVER ERROR (500)
      else if (status === 500) {
        console.error("Server Error:", error.response.data);
        alert("Terjadi kesalahan Internal Server (500). Silakan hubungi IT Support.");
      }
    }
    
    // Kembalikan error agar Component pemanggil (misal: VinCreate) 
    // masih bisa menangani error spesifiknya sendiri (misal: validasi form).
    return Promise.reject(error);
  }
);

app.use(createPinia())
app.use(router)

app.mount('#app')