<template>
  <div class="page-container">
    
    <div class="page-header">
       <div>
         <h2 class="title">📋 Riwayat Battery QC</h2>
         <p class="subtitle">Data hasil pengecekan baterai masuk.</p>
       </div>
       <div class="filter-group">
            <input 
            v-model="search" 
            @keyup.enter="fetchData()" 
            placeholder="Cari Serial Number..." 
            class="search-input"
            />
            <button @click="fetchData()" class="btn-refresh">🔄 Refresh</button>
        </div>
    </div>

    <div class="card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Serial Number</th>
              <th>Kondisi</th>
              <th>Voltage</th>
              <th>Waktu Cek</th>
              <th>Petugas</th>
              <th class="text-right">Bukti Foto</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
               <td colspan="6" class="text-center">Memuat data...</td>
            </tr>
            <tr v-else-if="records.length === 0">
               <td colspan="6" class="text-center empty-state">Tidak ada data ditemukan.</td>
            </tr>
            <tr v-else v-for="item in records" :key="item.id">
              <td class="font-mono bold">{{ item.serial_number }}</td>
              <td><span :class="['badge', item.condition]">{{ item.condition }}</span></td>
              <td>{{ item.voltage ? item.voltage + ' V' : '-' }}</td>
              <td class="text-secondary">{{ item.created_at_fmt || item.created_at }}</td>
              <td>{{ item.created_by_name || 'System' }}</td>
              <td class="text-right">
                <a :href="item.screenshot" target="_blank" class="btn-link">🖼️ Lihat</a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination">
         <span class="info">Total: {{ totalRecords }} data</span>
         <div class="nav-buttons">
            <button :disabled="!prevUrl" @click="changePage(prevUrl)">Prev</button>
            <button :disabled="!nextUrl" @click="changePage(nextUrl)">Next</button>
         </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../../../stores/auth';

const API_URL = 'http://127.0.0.1:8000/api';
const authStore = useAuthStore();

const loading = ref(false);
const records = ref<any[]>([]);
const search = ref('');

// Pagination State
const nextUrl = ref<string|null>(null);
const prevUrl = ref<string|null>(null);
const totalRecords = ref(0);

const canRead = computed(() => authStore.can('battery_record', 'read'));

const fetchData = async (urlOverride?: string) => {
  if (!canRead.value) return;
  loading.value = true;
  
  try {
    const url = urlOverride || `${API_URL}/battery/records/`;
    const params = !urlOverride ? { search: search.value, limit: 10 } : {}; // Param search hanya utk url awal
    
    const res = await axios.get(url, { params });
    records.value = res.data.results;
    nextUrl.value = res.data.next;
    prevUrl.value = res.data.previous;
    totalRecords.value = res.data.count;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const changePage = (url: string | null) => {
    if (url) fetchData(url);
}

onMounted(() => fetchData());
</script>

<style scoped>
.page-container { padding: 24px; max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 15px; }
.title { margin: 0; color: var(--text-primary); }
.subtitle { margin: 0; color: var(--text-secondary); font-size: 0.9rem; }

.filter-group { display: flex; gap: 10px; }
.search-input { padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; width: 250px; }
.btn-refresh { padding: 10px 15px; cursor: pointer; background: white; border: 1px solid var(--border-color); border-radius: 6px; }

.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); overflow: hidden; }
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 15px; border-bottom: 1px solid var(--border-color); text-align: left; vertical-align: middle; }
th { background: var(--bg-body); font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); }

.badge { padding: 5px 10px; border-radius: 15px; font-size: 0.75rem; font-weight: 800; }
.badge.OK { background: #dcfce7; color: #15803d; }
.badge.NG { background: #fee2e2; color: #b91c1c; }
.badge.RECHECK { background: #fef3c7; color: #b45309; }

.btn-link { text-decoration: none; color: var(--primary-color); font-weight: 600; font-size: 0.9rem; padding: 6px 10px; background: var(--bg-body); border-radius: 6px; }
.text-right { text-align: right; }
.text-center { text-align: center; }

.pagination { padding: 15px; display: flex; justify-content: space-between; align-items: center; background: var(--bg-body); border-top: 1px solid var(--border-color); }
.nav-buttons button { padding: 6px 12px; margin-left: 5px; cursor: pointer; }
.nav-buttons button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>