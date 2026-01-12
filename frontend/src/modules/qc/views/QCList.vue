<template>
  <div class="master-page">
    <div class="header">
      <div class="header-content">
        <div>
          <h2>📜 Riwayat Pemeriksaan QC</h2>
          <p>Daftar hasil inspeksi kualitas barang masuk.</p>
        </div>
        <router-link to="/qc/station" class="btn-primary">
          🛡️ Buka QC Station
        </router-link>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Tanggal</th>
              <th>Serial Number</th>
              <th>Part Info</th>
              <th class="text-center">Status</th>
              <th>Inspector</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="text-muted font-mono">
                {{ formatDate(item.inspection_date) }}
              </td>
              
              <td>
                <span class="sn-badge">{{ item.serial_number }}</span>
              </td>
              
              <td>
                <div class="font-bold">{{ item.part_number }}</div>
                <div class="text-sm text-muted">{{ item.part_name }}</div>
              </td>
              
              <td class="text-center">
                <span :class="['status-badge', item.judge_decision === 'PASS' ? 'status-pass' : 'status-fail']">
                  {{ item.judge_decision }}
                </span>
              </td>

              <td>👤 {{ item.inspector_name || 'System' }}</td>

              <td class="text-right">
                <button 
                  @click="openDetail(item)" 
                  class="btn-icon-small" 
                  title="Lihat Detail Lengkap"
                >
                  🔍
                </button>
              </td>
            </tr>
            
            <tr v-if="items.length === 0">
              <td colspan="6" class="text-center py-5 text-muted">
                Belum ada data riwayat QC.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="selectedItem" class="modal-overlay" @click.self="closeDetail">
        <div class="modal-card">
          
          <div class="modal-header">
            <div>
              <h3>Detail Inspeksi #{{ selectedItem.id }}</h3>
              <small class="text-muted">Dibuat pada: {{ formatDate(selectedItem.inspection_date) }}</small>
            </div>
            <button @click="closeDetail" class="btn-close">&times;</button>
          </div>

          <div class="modal-body">
            
            <div class="summary-grid">
              <div class="summary-box">
                <label>Identitas Barang</label>
                <div class="value font-mono">{{ selectedItem.serial_number }}</div>
                <div class="sub-value">{{ selectedItem.part_name }}</div>
              </div>

              <div class="summary-box center">
                <label>Keputusan Akhir</label>
                <div :class="['decision-text', selectedItem.judge_decision === 'PASS' ? 'text-pass' : 'text-fail']">
                  {{ selectedItem.judge_decision }}
                </div>
              </div>
            </div>

            <div class="param-container">
              <div class="param-header">📋 Parameter Pengukuran</div>
              
              <div v-for="(val, key) in selectedItem.qc_result_data" :key="key" class="param-row">
                
                <div class="param-label">
                  {{ formatKey(key) }}
                </div>

                <div class="param-value">
                  
                  <div v-if="isImage(val)" class="image-wrapper">
                    <span style="display:none">{{ loadImage(key, val) }}</span>

                    <div v-if="imageCache[key]">
                      <a :href="imageCache[key]" target="_blank" class="img-thumbnail" title="Klik untuk Zoom">
                        <img :src="imageCache[key]" alt="Bukti QC" />
                      </a>
                    </div>
                    <div v-else class="text-muted text-sm loading-text">
                      Memuat Gambar...
                    </div>
                  </div>

                  <span v-else-if="typeof val === 'boolean'" :class="['bool-badge', val ? 'bool-ok' : 'bool-ng']">
                     {{ val ? '✅ OK' : '❌ NG' }}
                  </span>

                  <span v-else class="font-mono font-bold">
                    {{ val !== null ? val : '-' }}
                  </span>

                </div>
              </div>
            </div>

          </div>

          <div class="modal-footer">
            <button @click="closeDetail" class="btn-secondary">Tutup</button>
          </div>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../api';

// --- STATE ---
const items = ref<any[]>([]);
const selectedItem = ref<any | null>(null);
const imageCache = ref<Record<string, string>>({}); // Menyimpan Blob URL gambar

// --- DATA LOADING ---
const loadData = async () => {
  try {
    const res = await api.getHistory();
    // Handle pagination DRF
    const rawData: any = res.data;
    items.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
  } catch (e) {
    console.error("Gagal load history", e);
  }
};

// --- HELPERS ---
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('id-ID', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

const formatKey = (key: string | number) => {
  // Ubah "battery_voltage" -> "Battery Voltage"
  return String(key).replace(/_/g, ' ');
};

// Cek apakah value adalah marker gambar
const isImage = (val: any): boolean => {
  if (typeof val !== 'string') return false;
  // Support Base64 lama DAN format baru SECURE_IMG
  return val.startsWith('data:image') || val.startsWith('SECURE_IMG:');
};

// --- SECURE IMAGE LOADER ---
// --- SECURE IMAGE LOADER ---
// Ubah parameter agar menerima (string | number) dan (any)
const loadImage = async (key: string | number, val: any) => {
  // 1. Konversi Key & Val ke String agar aman
  const sKey = String(key);
  const sVal = String(val);

  // 2. Jika sudah ada di cache, stop
  if (imageCache.value[sKey]) return;

  // 3. Jika format Secure Image (Path di server)
  if (sVal.startsWith('SECURE_IMG:')) {
    const filename = sVal.split('/').pop();
    
    if (filename) {
      try {
        const res = await api.getSecureImage(filename);
        const url = URL.createObjectURL(res.data);
        imageCache.value[sKey] = url;
      } catch (e) {
        console.error("Gagal load gambar secure:", e);
        imageCache.value[sKey] = ''; 
      }
    }
  } 
  // 4. Jika format Base64 (Legacy data)
  else {
    imageCache.value[sKey] = sVal;
  }
};

// --- ACTIONS ---
const openDetail = (item: any) => {
  selectedItem.value = item;
};

const closeDetail = () => {
  selectedItem.value = null;
  // Opsional: Bersihkan cache gambar saat modal ditutup untuk hemat memori
  // Object.values(imageCache.value).forEach(url => URL.revokeObjectURL(url));
  // imageCache.value = {};
};

onMounted(loadData);
</script>

<style scoped>
/* --- LAYOUT UTAMA --- */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; }

.header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: var(--text-secondary); font-size: 0.9rem; }

/* --- CARD & TABLE --- */
.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; box-shadow: var(--shadow-sm); overflow: hidden; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th { background: rgba(0,0,0,0.03); padding: 12px 16px; text-align: left; font-weight: 600; font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; border-bottom: 1px solid var(--border-color); }
.table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; vertical-align: middle; color: var(--text-primary); }

/* --- BADGES & STATUS --- */
.status-badge { padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
.status-pass { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.status-fail { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.sn-badge { background: rgba(0,0,0,0.05); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-weight: bold; font-size: 0.85rem; }

/* --- BUTTONS --- */
.btn-primary { background: var(--primary-color); color: white; padding: 10px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; border: none; cursor: pointer; transition: opacity 0.2s; }
.btn-primary:hover { opacity: 0.9; }

.btn-secondary { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; }
.btn-secondary:hover { background: rgba(0,0,0,0.05); }

.btn-icon-small { width: 32px; height: 32px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--primary-color); transition: all 0.2s; }
.btn-icon-small:hover { border-color: var(--primary-color); background: rgba(59, 130, 246, 0.05); }
.btn-close { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-secondary); line-height: 1; }

/* --- MODAL (OVERLAY & CARD) --- */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.6); /* Backdrop gelap */
  backdrop-filter: blur(3px); /* Efek Blur modern */
  z-index: 9999; /* Pastikan di atas segalanya */
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}

.modal-card {
  background: var(--bg-card);
  width: 100%; max-width: 600px;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  display: flex; flex-direction: column;
  max-height: 90vh; /* Agar tidak melebihi tinggi layar */
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header { padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: flex-start; background: rgba(0,0,0,0.02); }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: var(--text-primary); }
.modal-body { padding: 24px; overflow-y: auto; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border-color); text-align: right; background: var(--bg-card); }

/* --- MODAL CONTENT STYLES --- */
.summary-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.summary-box { border: 1px solid var(--border-color); padding: 12px; border-radius: 8px; background: rgba(0,0,0,0.01); }
.summary-box.center { text-align: center; }
.summary-box label { font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); display: block; margin-bottom: 6px; letter-spacing: 0.5px; }
.summary-box .value { font-weight: bold; font-size: 1.1rem; color: var(--text-primary); }
.summary-box .sub-value { font-size: 0.85rem; color: var(--text-secondary); }

.decision-text { font-size: 1.25rem; font-weight: 800; padding: 2px 10px; border-radius: 4px; display: inline-block; }
.text-pass { color: #166534; background: #dcfce7; }
.text-fail { color: #991b1b; background: #fee2e2; }

.param-container { border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }
.param-header { background: rgba(0,0,0,0.03); padding: 10px 16px; font-weight: 600; font-size: 0.9rem; color: var(--text-primary); border-bottom: 1px solid var(--border-color); }
.param-row { display: grid; grid-template-columns: 1fr 2fr; padding: 12px 16px; border-bottom: 1px solid var(--border-color); align-items: center; }
.param-row:last-child { border-bottom: none; }
.param-label { text-transform: capitalize; color: var(--text-secondary); font-size: 0.9rem; }
.param-value { text-align: right; }

.image-wrapper { display: flex; justify-content: flex-end; }
.img-thumbnail { display: block; width: 100px; height: 75px; border-radius: 6px; overflow: hidden; border: 1px solid var(--border-color); background: #eee; cursor: zoom-in; }
.img-thumbnail img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.2s; }
.img-thumbnail:hover img { transform: scale(1.1); }
.loading-text { font-style: italic; font-size: 0.8rem; }

.bool-badge { padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; border: 1px solid transparent; }
.bool-ok { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.bool-ng { background: #fee2e2; color: #991b1b; border-color: #fecaca; }

/* UTILS */
.text-muted { color: var(--text-secondary); }
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 600; }
</style>