<template>
  <div class="login-container">
    <div class="card login-card">
      <div class="header">
        <h1>🏭 Station Setup</h1>
        <p>Pilih lokasi kerja Anda sebelum memulai.</p>
      </div>

      <div class="form-body">
        <div v-if="isLoading" class="loading">Memuat Data Station...</div>
        
        <div v-else>
          <label>Pilih Work Center (Area)</label>
          <div class="grid-options">
            <button 
              v-for="wc in workCenters" :key="wc.id"
              :class="['option-btn', { active: selectedWcId === wc.id }]"
              @click="selectWc(wc.id)"
            >
              {{ wc.code }}
            </button>
          </div>

          <div v-if="selectedWcId" class="mt-6 fade-in">
            <label>Pilih Station (Pos Kerja)</label>
            <select v-model="selectedStationId" class="station-select">
              <option :value="null" disabled>-- Pilih Station --</option>
              <option v-for="st in availableStations" :key="st.id" :value="st.id">
                {{ st.code }} - {{ st.name }}
              </option>
            </select>
          </div>

          <button 
            v-if="selectedStationId" 
            @click="enterShopFloor" 
            class="btn-enter"
          >
            MASUK KE SHOP FLOOR ➜
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const isLoading = ref(true);
const workCenters = ref<any[]>([]);
const selectedWcId = ref<number | null>(null);
const selectedStationId = ref<number | null>(null);

onMounted(async () => {
  try {
    // Cek jika sudah login sebelumnya
    const savedStation = localStorage.getItem('active_station');
    if (savedStation) {
       // Opsional: Auto redirect atau biarkan user reset
    }

    const res = await api.getWorkCenters();
    workCenters.value = res.data.results || res.data || [];
  } catch (e) { console.error(e); } 
  finally { isLoading.value = false; }
});

const availableStations = computed(() => {
  const wc = workCenters.value.find(w => w.id === selectedWcId.value);
  return wc ? wc.stations : [];
});

const selectWc = (id: number) => {
  selectedWcId.value = id;
  selectedStationId.value = null;
};

const enterShopFloor = () => {
  // FIX: Tambahkan (s: any) agar TypeScript tidak komplain
  const station = availableStations.value.find((s: any) => s.id === selectedStationId.value);
  
  if (station) {
    localStorage.setItem('active_station', JSON.stringify(station));
    router.push({ name: 'ShopFloorInterface' }); // Pastikan nama route ini benar di router/index.ts
  }
};
</script>

<style scoped>
.login-container { height: 100vh; display: flex; align-items: center; justify-content: center; background: #f1f5f9; }
.login-card { width: 100%; max-width: 500px; padding: 30px; background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; }
.header h1 { margin: 0; color: #1e293b; }
.header p { margin: 5px 0 20px; color: #64748b; }

.grid-options { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; margin-top: 10px; }
.option-btn { padding: 15px; border: 2px solid #e2e8f0; background: white; border-radius: 8px; font-weight: bold; cursor: pointer; color: #64748b; transition: 0.2s; }
.option-btn:hover { border-color: #3b82f6; }
.option-btn.active { background: #eff6ff; border-color: #2563eb; color: #1e40af; }

.station-select { width: 100%; padding: 15px; font-size: 1.1rem; border-radius: 8px; border: 2px solid #cbd5e1; margin-top: 10px; font-weight: bold; }
.btn-enter { margin-top: 30px; width: 100%; padding: 15px; background: #2563eb; color: white; font-size: 1.1rem; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3); }
.btn-enter:hover { background: #1d4ed8; transform: translateY(-2px); }

label { display: block; text-align: left; font-weight: 600; color: #475569; margin-bottom: 5px; }
.fade-in { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>