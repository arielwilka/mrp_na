<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📜 Riwayat Pemeriksaan QC</h2>
          <p>Daftar hasil inspeksi kualitas barang masuk.</p>
        </div>
        <router-link to="/qc/station" class="btn-primary">🛡️ Buka QC Station</router-link>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Tanggal</th>
              <th>Serial Number</th>
              <th>Nama Part</th>
              <th>Status</th>
              <th>Inspector</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="text-sm text-slate-600 font-mono">
                {{ formatDate(item.inspection_date) }}
              </td>
              
              <td class="font-mono font-bold">{{ item.serial_number }}</td>
              
              <td>
                <div class="font-semibold text-slate-700">{{ item.part_number }}</div>
                <div class="text-xs text-slate-500">{{ item.part_name }}</div>
              </td>
              
              <td>
                <span v-if="item.judge_decision === 'PASS'" class="badge badge-green">PASS (OK)</span>
                <span v-else class="badge badge-red">FAIL (NG)</span>
              </td>

              <td class="text-sm">{{ item.inspector_name || 'System' }}</td>

              <td class="text-right">
                <button 
                  @click="openDetail(item)" 
                  class="btn-icon bg-blue-50 border-blue-200 text-blue-600 hover:bg-blue-100"
                  title="Lihat Detail"
                >
                  🔍
                </button>
              </td>
            </tr>
            
            <tr v-if="items.length === 0">
              <td colspan="6" class="text-center py-8 text-muted">Belum ada data riwayat QC.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedItem" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="closeDetail">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in">
        
        <div class="p-5 border-b flex justify-between items-start bg-slate-50">
          <div>
            <h3 class="text-lg font-bold text-slate-800">Detail Inspeksi #{{ selectedItem.id }}</h3>
            <p class="text-sm text-slate-500 mt-1">
              Serial Number: <span class="font-mono font-bold text-slate-800">{{ selectedItem.serial_number }}</span>
            </p>
          </div>
          <button @click="closeDetail" class="text-slate-400 hover:text-red-500 text-2xl font-bold leading-none">&times;</button>
        </div>

        <div class="p-6 overflow-y-auto">
          
          <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="p-3 bg-slate-50 rounded border">
              <span class="text-xs text-slate-500 uppercase block">Part Name</span>
              <span class="font-semibold text-slate-800">{{ selectedItem.part_name }}</span>
            </div>
            <div class="p-3 bg-slate-50 rounded border">
              <span class="text-xs text-slate-500 uppercase block">Keputusan Akhir</span>
              <span 
                class="font-bold text-lg"
                :class="selectedItem.judge_decision === 'PASS' ? 'text-green-600' : 'text-red-600'"
              >
                {{ selectedItem.judge_decision }}
              </span>
            </div>
          </div>

          <h4 class="font-bold text-slate-700 mb-3 border-b pb-2">📋 Hasil Pengukuran</h4>
          
          <div class="space-y-4">
            <div v-for="(val, key) in selectedItem.qc_result_data" :key="key" class="group">
              
              <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start text-sm">
                <span class="font-medium text-slate-600 capitalize mb-1 sm:mb-0 w-1/3">
                  {{ formatKey(key) }}
                </span>

                <div class="w-full sm:w-2/3 sm:text-right">
                  
                  <div v-if="isImage(val)" class="mt-2 sm:mt-0 flex justify-end">
                    <a :href="val" target="_blank" title="Klik untuk memperbesar">
                      <img 
                        :src="val" 
                        class="h-32 w-auto rounded border shadow-sm hover:scale-105 transition-transform cursor-zoom-in bg-gray-100" 
                        alt="Bukti Foto"
                      />
                    </a>
                  </div>

                  <span v-else-if="typeof val === 'boolean'" :class="val ? 'badge-green' : 'badge-red'" class="badge">
                    {{ val ? 'OK' : 'NG' }}
                  </span>

                  <span v-else class="font-mono font-bold text-slate-800 break-words">
                    {{ val !== null ? val : '-' }}
                  </span>

                </div>
              </div>
              <hr class="border-slate-100 mt-3 group-last:hidden" />
            </div>
          </div>

        </div>

        <div class="p-4 border-t bg-slate-50 text-right">
          <button @click="closeDetail" class="btn-secondary">Tutup</button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../api';

const items = ref<any[]>([]);
const selectedItem = ref<any | null>(null);

// --- LOAD DATA ---
const loadData = async () => {
  try {
    const res = await api.getHistory();
    const rawData: any = res.data;
    items.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
  } catch (e) {
    console.error("Gagal load history", e);
  }
};

// --- HELPERS ---
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  // Format: 07/01/2026 14:30
  return d.toLocaleString('id-ID', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

// Ubah "voltage_val" -> "Voltage Val"
const formatKey = (key: string | number) => {
  return String(key).replace(/_/g, ' ');
};

// Deteksi apakah value adalah string base64 gambar
const isImage = (val: any): boolean => {
  if (typeof val !== 'string') return false;
  // Ciri khas base64 image dari canvas/upload
  return val.startsWith('data:image');
};

// --- ACTIONS ---
const openDetail = (item: any) => {
  selectedItem.value = item;
};

const closeDetail = () => {
  selectedItem.value = null;
};

onMounted(loadData);
</script>

<style scoped>
/* Reuse Global Style */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* TABLE STYLE */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; }

/* BUTTONS */
.btn-primary { background: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: background 0.2s; }
.btn-primary:hover { background: #1d4ed8; }

.btn-secondary { background: white; color: #334155; border: 1px solid #cbd5e1; padding: 8px 20px; border-radius: 6px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-secondary:hover { background: #f1f5f9; }

.btn-icon { width: 32px; height: 32px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; cursor: pointer; border-width: 1px; transition: all 0.2s; }

/* BADGES */
.badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
.badge-green { background: #dcfce7; color: #166534; }
.badge-red { background: #fee2e2; color: #991b1b; }

/* UTILS */
.text-right { text-align: right; }
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.capitalize { text-transform: capitalize; }
.animate-fade-in { animation: fadeIn 0.2s ease-out; }

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>