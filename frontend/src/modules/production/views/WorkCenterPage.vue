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
        <div class="card-header">
          <h3>Work Centers</h3>
          <button @click="openWcModal" class="btn-icon bg-blue-50 text-blue-600 hover:bg-blue-100" title="Tambah Area">+</button>
        </div>
        <div class="list-container">
          <div v-if="isLoading" class="p-4 text-center text-muted">Loading...</div>
          <div 
            v-else 
            v-for="wc in workCenters" 
            :key="wc.id"
            :class="['list-item', { active: selectedWc?.id === wc.id }]"
            @click="selectWc(wc)"
          >
            <div>
              <div class="font-bold text-slate-700">{{ wc.code }}</div>
              <div class="text-sm text-slate-500">{{ wc.name }}</div>
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
          <h3 v-if="selectedWc">Stations di: <span class="text-primary">{{ selectedWc.name }}</span></h3>
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
                <td class="text-center">{{ st.default_sequence }}</td>
                <td class="text-center">
                  <span v-if="st.is_finish_point" class="badge-success">🏁 Finish Point</span>
                  <span v-else class="badge-gray">Process</span>
                </td>
                <td class="text-right">
                  <button @click="deleteStation(st.id)" class="btn-icon danger" title="Hapus">🗑️</button>
                </td>
              </tr>
              <tr v-if="!selectedWc.stations || selectedWc.stations.length === 0">
                <td colspan="5" class="text-center py-8 text-muted">Belum ada station di area ini.</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="empty-state-panel">
           👈 Pilih Work Center di sebelah kiri untuk melihat detail.
        </div>
      </div>

    </div>

    <div v-if="modals.wc" class="modal-backdrop" @click.self="modals.wc = false">
      <div class="modal-dialog">
        <div class="modal-header"><h3>Tambah Work Center</h3></div>
        <div class="modal-body">
           <div class="form-group">
              <label>Kode Area</label>
              <input v-model="wcForm.code" class="form-input uppercase" placeholder="BODY-SHOP" />
           </div>
           <div class="form-group">
              <label>Nama Area</label>
              <input v-model="wcForm.name" class="form-input" placeholder="Body Welding Area" />
           </div>
           <div class="form-group">
              <label class="flex items-center gap-2 cursor-pointer">
                 <input type="checkbox" v-model="wcForm.is_continuous"> 
                 <span>Continuous Flow (Conveyor)?</span>
              </label>
           </div>
        </div>
        <div class="modal-footer">
           <button @click="saveWc" class="btn-primary w-full">Simpan</button>
        </div>
      </div>
    </div>

    <div v-if="modals.st" class="modal-backdrop" @click.self="modals.st = false">
      <div class="modal-dialog">
        <div class="modal-header"><h3>Tambah Station</h3></div>
        <div class="modal-body">
           <div class="form-group">
              <label>Kode Station</label>
              <input v-model="stForm.code" class="form-input uppercase" placeholder="POS-01" />
           </div>
           <div class="form-group">
              <label>Nama Station</label>
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
           <small class="text-muted block mt-2">Finish Point = Titik dimana unit dihitung sebagai "Barang Jadi" (Output).</small>
        </div>
        <div class="modal-footer">
           <button @click="saveStation" class="btn-primary w-full">Simpan</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';

const isLoading = ref(false);
const workCenters = ref<any[]>([]);
const selectedWc = ref<any>(null);

const modals = reactive({ wc: false, st: false });
const wcForm = reactive({ code: '', name: '', is_continuous: false });
const stForm = reactive({ code: '', name: '', default_sequence: 10, is_finish_point: false });

const loadData = async () => {
  isLoading.value = true;
  try {
    const res = await api.getWorkCenters();
    workCenters.value = res.data.results || res.data || [];
    // Refresh selected WC data if exists
    if(selectedWc.value) {
       const updated = workCenters.value.find(w => w.id === selectedWc.value.id);
       if(updated) selectedWc.value = updated;
    }
  } catch(e) { console.error(e); } 
  finally { isLoading.value = false; }
};

onMounted(loadData);

const selectWc = (wc: any) => selectedWc.value = wc;

// Work Center Actions
const openWcModal = () => { wcForm.code = ''; wcForm.name = ''; wcForm.is_continuous = false; modals.wc = true; };
const saveWc = async () => {
   try { await api.createWorkCenter(wcForm); modals.wc = false; loadData(); } catch(e) { alert("Error Save"); }
};
const deleteWc = async (id: number) => {
   if(confirm("Hapus Area ini? Semua station di dalamnya akan terhapus.")) {
      await api.deleteWorkCenter(id); selectedWc.value = null; loadData();
   }
};

// Station Actions
const openStationModal = () => { 
   stForm.code = ''; stForm.name = ''; stForm.default_sequence = (selectedWc.value.stations.length + 1) * 10; 
   stForm.is_finish_point = false; 
   modals.st = true; 
};
const saveStation = async () => {
   try { 
      await api.createStation({ ...stForm, work_center: selectedWc.value.id }); 
      modals.st = false; loadData(); 
   } catch(e) { alert("Error Save Station"); }
};
const deleteStation = async (id: number) => {
   if(confirm("Hapus Station ini?")) { await api.deleteStation(id); loadData(); }
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
</style>