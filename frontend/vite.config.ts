import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // Otomatis deteksi IP komputer (0.0.0.0)
    port: 5173, 
    
    // --- FITUR "FORWARD" (PROXY) ---
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // Forward ke Django Localhost
        changeOrigin: true,
        secure: false,
        // Opsional: jika di django url-nya tidak pakai /api, bisa di-rewrite
        // rewrite: (path) => path.replace(/^\/api/, '') 
      }
    },
    hmr: {
      // clientPort memberitahu browser: "Hubungi aku di port ini,
      // di IP manapun kamu membuka web ini."
      clientPort: 5173, 
    }
  },
  
  resolve: {
    alias: {
      // Baris ini kuncinya: Mapping '@' ke folder './src'
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})