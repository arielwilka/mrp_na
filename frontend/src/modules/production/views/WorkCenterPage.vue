<template>
  <div class="master-page">
    <div class="header">
      <div>
        <h2>🏭 Layout Produksi</h2>
        <p>Atur Work Center (Area) dan Station (Pos Kerja).</p>
      </div>
    </div>

    <div class="layout-grid">
      
      <div class="panel-left card">
        <div class="card-header flex-col items-start gap-3">
          <div class="flex justify-between w-full items-center">
            <h3>Work Centers</h3>
            <button @click="openWcModal" class="btn-icon bg-blue-50 text-blue-600 hover:bg-blue-100" title="Tambah Area">+</button>
          </div>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Cari area..." 
            class="form-input text-sm py-1"
          />
        </div>
        
        <div class="list-container">
          <div v-if="isLoading" class="p-4 text-center text-muted">
            <span class="spinner">⏳</span> Memuat Data...
          </div>
          
          <div 
            v-else 
            v-for="wc in filteredWorkCenters" 
            :key="wc.id"
            :class="['list-item', { active: selectedWc?.id === wc.id }]"
            @click="selectWc(wc)"
          >
            <div class="item-content">
              <div class="flex justify-between items-start">
                  <span class="font-bold text-slate-700">{{ wc.code }}</span>
                  <span v-if="wc.is_continuous" class="badge-continuous">🔄 Cont.</span>
                  <span v-else class="badge-jobshop">🛠️ Stall</span>
              </div>
              <div class="text-sm text-slate-500 mt-1">{{ wc.name }}</div>
            </div>
            <div class="item-actions">
               <span class="badge-count">{{ wc.stations?.length || 0 }} Pos</span>
               <button @click.stop="deleteWc(wc.id)" class="btn-xs danger">×</button>
            </div>
          </div>
        </div>
      </div>

      <div class="panel-right card">
        <div class="card-header">
          <div v-if="selectedWc">
             <h3>Stations di: <span class="text-primary">{{ selectedWc.name }}</span></h3>
             <span class="text-xs text-muted font-mono">{{ selectedWc.code }}</span>
          </div>
          <h3 v-else class="text-muted">Pilih Work Center</h3>
          
          <button v-if="selectedWc" @click="openStationModal" class="btn-primary btn-sm">
            + Tambah Station
          </button>
        </div>

        <div class="table-responsive" v-if="selectedWc">
          <table class="table">
            <thead>
              <tr>
                <th class="w-24">Kode</th>
                <th>Nama Station</th>
                <th class="text-center w-24">Urutan</th>
                <th class="text-center w-32">Fungsi</th>
                <th class="text-right w-20">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="st in selectedWc.stations" :key="st.id">
                <td class="font-mono font-bold">{{ st.code }}</td>
                <td>{{ st.name }}</td>
                <td class="text-center"><span class="badge-seq">{{ st.default_sequence }}</span></td>
                <td class="text-center">
                  <span v-if="st.is_finish_point" class="badge-success">🏁 Finish Point</span>
                  <span v-else class="badge-gray">Process</span>
                </td>
                <td class="text-right">
                  <button @click="deleteStation(st.id)" class="btn-icon danger">🗑️</button>
                </td>
              </tr>
              <tr v-if="!selectedWc.stations || selectedWc.stations.length === 0">
                <td colspan="5" class="text-center py-12 text-muted">
                    <div class="flex flex-col items-center">
                        <span class="text-2xl opacity-50">🏗️</span>
                        <span class="mt-2">Belum ada station di area ini.</span>
                    </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="empty-state-panel">
            <div class="text-center">
                <span class="text-4xl">👈</span>
                <p class="mt-4">Pilih Work Center di sebelah kiri.</p>
            </div>
        </div>
      </div>

    </div>

    <div v-if="modals.wc" class="modal-backdrop" @click.self="modals.wc = false">
       <div class="modal-dialog">
        <div class="modal-header"><h3>Tambah Work Center</h3></div>
        <div class="modal-body">
           <div class="form-group">
              <label>Kode Area <span class="text-red">*</span></label>
              <input v-model="wcForm.code" class="form-input uppercase" />
           </div>
           <div class="form-group">
              <label>Nama Area <span class="text-red">*</span></label>
              <input v-model="wcForm.name" class="form-input" />
           </div>
           <div class="form-group checkbox-wrapper">
              <label class="flex items-center gap-2 cursor-pointer bg-blue-50 p-3 rounded border border-blue-100">
                 <input type="checkbox" v-model="wcForm.is_continuous"> 
                 <div>
                     <span class="font-bold text-sm block">Continuous Flow?</span>
                     <span class="text-xs text-muted">Conveyor line.</span>
                 </div>
              </label>
           </div>
        </div>
        <div class="modal-footer">
           <button @click="modals.wc = false" class="btn-ghost">Batal</button>
           <button @click="saveWc" class="btn-primary" :disabled="isSubmitting">Simpan</button>
        </div>
      </div>
    </div>

    <div v-if="modals.st" class="modal-backdrop" @click.self="modals.st = false">
      <div class="modal-dialog">
        <div class="modal-header"><h3>Tambah Station</h3></div>
        <div class="modal-body">
           <div class="form-group">
              <label>Kode Station <span class="text-red">*</span></label>
              <input v-model="stForm.code" class="form-input uppercase" placeholder="POS-01" maxlength="20" />
              <small v-if="codeError" class="text-red-500 text-xs block mt-1">{{ codeError }}</small>
           </div>
           <div class="form-group">
              <label>Nama Station <span class="text-red">*</span></label>
              <input v-model="stForm.name" class="form-input" placeholder="Front Bumper Assy" />
           </div>
           
           <div class="grid-2-col">
             <div class="form-group">
                <label>Urutan Default</label>
                <input type="number" v-model="stForm.default_sequence" class="form-input text-center" />
             </div>
             <div class="form-group checkbox-wrapper">
                <label class="flex items-center gap-2 cursor-pointer h-full pt-6">
                   <input type="checkbox" v-model="stForm.is_finish_point"> 
                   <span class="font-bold text-sm">🏁 Finish Point?</span>
                </label>
             </div>
           </div>
        </div>
        <div class="modal-footer">
           <button @click="modals.st = false" class="btn-ghost">Batal</button>
           <button @click="saveStation" class="btn-primary" :disabled="isSubmitting || !!codeError">Simpan Station</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import api from '../api';

const isLoading = ref(false);
const isSubmitting = ref(false);
const searchQuery = ref('');

const workCenters = ref<any[]>([]);
const selectedWc = ref<any>(null); // Object WC yang sedang dipilih (lengkap dengan stations)

const modals = reactive({ wc: false, st: false });
const wcForm = reactive({ code: '', name: '', description: '', is_continuous: false });
const stForm = reactive({ code: '', name: '', default_sequence: 10, is_finish_point: false });
const codeError = ref('');

// Computed Filter untuk Search Area
const filteredWorkCenters = computed(() => {
    if (!searchQuery.value) return workCenters.value;
    const q = searchQuery.value.toLowerCase();
    return workCenters.value.filter(w => 
        w.name.toLowerCase().includes(q) || 
        w.code.toLowerCase().includes(q)
    );
});

// Load Data Utama (Master + Nested Stations)
const loadData = async () => {
  isLoading.value = true;
  try {
    const res = await api.getWorkCenters();
    // Asumsi: Backend mengembalikan data nested: [{ id:1, stations: [...] }, ...]
    workCenters.value = res.data.results || res.data || [];
    
    // Logic Smart Refresh:
    // Jika user sedang memilih WC, kita update datanya agar list station di kanan ikut ter-refresh
    if(selectedWc.value) {
       const updated = workCenters.value.find(w => w.id === selectedWc.value.id);
       if(updated) selectedWc.value = updated;
       else selectedWc.value = null; 
    }
  } catch(e) { console.error(e); } 
  finally { isLoading.value = false; }
};

onMounted(loadData);

const selectWc = (wc: any) => {
    selectedWc.value = wc;
    // Tidak perlu loadStations terpisah karena data sudah ada di dalam object wc
};

// --- WORK CENTER ACTIONS ---
const openWcModal = () => { 
    Object.assign(wcForm, { code: '', name: '', description: '', is_continuous: false });
    modals.wc = true; 
};

const saveWc = async () => {
   if(!wcForm.code || !wcForm.name) return alert("Wajib diisi.");
   isSubmitting.value = true;
   try { 
       await api.createWorkCenter(wcForm); 
       modals.wc = false; 
       loadData(); 
   } catch(e: any) { handleError(e); } 
   finally { isSubmitting.value = false; }
};

const deleteWc = async (id: number) => {
   if(confirm("Hapus Area ini beserta semua station di dalamnya?")) {
      try {
          await api.deleteWorkCenter(id); 
          loadData();
      } catch(e: any) { handleError(e); }
   }
};

// --- STATION ACTIONS ---
const openStationModal = () => { 
   Object.assign(stForm, { code: '', name: '', is_finish_point: false });
   codeError.value = '';
   
   // Auto Sequence Logic
   // Ambil sequence dari data lokal (selectedWc.stations)
   const currentStations = selectedWc.value.stations || [];
   const maxSeq = currentStations.length > 0 
        ? Math.max(...currentStations.map((s:any) => s.default_sequence)) 
        : 0;
   stForm.default_sequence = maxSeq + 10;
   
   modals.st = true; 
};

// Validasi Duplikat: Cek apakah kode station sudah ada di Work Center INI
watch(() => stForm.code, (newVal) => {
    if(!newVal || !selectedWc.value) {
        codeError.value = '';
        return;
    }
    const currentStations = selectedWc.value.stations || [];
    const exists = currentStations.some((s:any) => s.code.toUpperCase() === newVal.toUpperCase());
    codeError.value = exists ? 'Kode station ini sudah digunakan di area ini.' : '';
});

const saveStation = async () => {
   if(codeError.value) return;
   if(!stForm.code || !stForm.name) return alert("Wajib diisi.");

   isSubmitting.value = true;
   try { 
      // Kita kirim work_center_id agar backend tahu station ini milik siapa
      await api.createStation({ ...stForm, work_center: selectedWc.value.id }); 
      modals.st = false; 
      
      // Refresh Full Data agar struktur nested terupdate
      loadData(); 
   } catch(e: any) { handleError(e); } 
   finally { isSubmitting.value = false; }
};

const deleteStation = async (id: number) => {
   if(confirm("Hapus Station ini?")) { 
       try {
           await api.deleteStation(id); 
           loadData(); 
       } catch(e: any) { handleError(e); }
   }
};

const handleError = (e: any) => {
    const msg = e.response?.data?.detail || "Terjadi kesalahan server.";
    alert("Gagal: " + msg);
};
</script>

<style scoped>
/* Reuse global styles, add specific grid layout */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; }

.layout-grid { display: grid; grid-template-columns: 300px 1fr; gap: 24px; align-items: start; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.card-header { padding: 16px; border-bottom: 1px solid #e2e8f0; background: #f8fafc; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1rem; color: #334155; font-weight: 600; }

/* Left Panel List */
.list-container { max-height: 70vh; overflow-y: auto; }
.list-item { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
.list-item:hover { background: #f8fafc; }
.list-item.active { background: #eff6ff; border-left: 3px solid #2563eb; }
.item-actions { display: flex; gap: 8px; align-items: center; }
.badge-count { background: #e2e8f0; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; color: #64748b; }
.btn-xs { font-size: 1rem; line-height: 1; padding: 0 4px; background: none; border: none; cursor: pointer; color: #94a3b8; }
.btn-xs:hover { color: #ef4444; }

/* Right Panel Table */
.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 10px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
.table td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
.empty-state-panel { padding: 40px; text-align: center; color: #94a3b8; font-style: italic; }

/* Badges */
.badge-success { background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid #bbf7d0; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; }

/* Form & Modal (Standard) */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(2px); display: flex; justify-content: center; align-items: center; z-index: 50; }
.modal-dialog { background: white; width: 90%; max-width: 400px; border-radius: 12px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.modal-header h3 { margin: 0 0 16px; font-size: 1.2rem; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; color: #334155; }
.form-input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
.btn-primary { background: #2563eb; color: white; padding: 10px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }
.btn-sm { font-size: 0.85rem; padding: 6px 12px; }
.btn-icon { width: 30px; height: 30px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #e2e8f0; background: white; cursor: pointer; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #ef4444; color: #ef4444; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.text-primary { color: #2563eb; }
.flex-col { flex-direction: column; }
.w-full { width: 100%; }
.gap-3 { gap: 12px; }
.text-xs { font-size: 0.75rem; }
.mt-1 { margin-top: 0.25rem; }
.text-red-500 { color: #ef4444; }
.badge-count { background: #e2e8f0; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; color: #64748b; font-weight: 600; }
</style>