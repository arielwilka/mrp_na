<template>
  <div class="master-page">
    <div class="header">
      <h2>⚙️ Master Konfigurasi VIN</h2>
      <p>Halaman ini hanya dapat diakses oleh Administrator Engineering/IT.</p>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div> Memuat Data Master...
    </div>

    <div v-else>
      <div class="tabs">
        <button :class="{ active: activeTab === 'types' }" @click="activeTab = 'types'">Tipe & Varian</button>
        <button :class="{ active: activeTab === 'years' }" @click="activeTab = 'years'">Tahun Produksi</button>
        <button :class="{ active: activeTab === 'prefixes' }" @click="activeTab = 'prefixes'">Aturan Prefix</button>
      </div>

      <div v-if="activeTab === 'types'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Daftar Tipe Kendaraan</h3>
            <button v-if="canCreate" @click="openModal('addType')" class="btn-sm">+ Tipe Baru</button>
          </div>
          
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th style="width: 30%;">Nama Tipe</th>
                  <th>Daftar Varian</th>
                  <th>Daftar Warna</th>
                  <th style="width: 100px;">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="types.length === 0"><td colspan="4" class="text-center">Belum ada data tipe.</td></tr>
                <tr v-for="t in types" :key="t.id">
                  <td data-label="Nama Tipe">
                      <strong class="type-name">{{ t.name }}</strong>
                  </td>
                  <td data-label="Varian">
                    <div class="tag-container">
                        <span class="badge" v-for="v in t.variants" :key="v.id">
                            {{ v.name }}
                            <span v-if="canDelete" class="del-x" @click="deleteChild('variants', v.id)">×</span>
                        </span>
                        <button v-if="canCreate" @click="openChildModal(t, 'variant')" class="btn-add-tag" title="Tambah Varian">+</button>
                    </div>
                  </td>
                  <td data-label="Warna">
                    <div class="tag-container">
                        <span class="badge color" v-for="c in t.colors" :key="c.id">
                            {{ c.name }}
                            <span v-if="canDelete" class="del-x" @click="deleteChild('colors', c.id)">×</span>
                        </span>
                        <button v-if="canCreate" @click="openChildModal(t, 'color')" class="btn-add-tag" title="Tambah Warna">+</button>
                    </div>
                  </td>
                  <td data-label="Aksi" class="action-cell">
                      <button v-if="canDelete" @click="deleteItem('types', t.id)" class="btn-danger-text">Hapus</button>
                      <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'years'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Kode Tahun Produksi</h3>
            <button v-if="canCreate" @click="openModal('addYear')" class="btn-sm">+ Tahun Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead><tr><th>Tahun</th><th>Kode VIN</th><th>Aksi</th></tr></thead>
              <tbody>
                <tr v-if="years.length === 0"><td colspan="3" class="text-center">Belum ada data.</td></tr>
                <tr v-for="y in years" :key="y.id">
                  <td data-label="Tahun">{{ y.year }}</td>
                  <td data-label="Kode VIN" class="code-cell">{{ y.code }}</td>
                  <td data-label="Aksi">
                    <button v-if="canDelete" @click="deleteItem('years', y.id)" class="btn-danger-text">Hapus</button>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'prefixes'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Mapping Prefix</h3>
            <button v-if="canCreate" @click="openModal('addPrefix')" class="btn-sm">+ Rule Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead><tr><th>Tipe</th><th>Tahun</th><th>WMI + VDS</th><th>Plant</th><th>Aksi</th></tr></thead>
              <tbody>
                <tr v-if="prefixes.length === 0"><td colspan="5" class="text-center">Belum ada rule.</td></tr>
                <tr v-for="p in prefixes" :key="p.id">
                  <td data-label="Tipe">{{ p.vehicle_type_name }}</td>
                  <td data-label="Tahun">{{ p.year_code_label }}</td>
                  <td data-label="WMI+VDS" class="code-cell">{{ p.wmi_vds }}</td>
                  <td data-label="Plant" class="code-cell">{{ p.plant_code }}</td>
                  <td data-label="Aksi">
                    <button v-if="canDelete" @click="deleteItem('vin-prefixes', p.id)" class="btn-danger-text">Hapus</button>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="modal.isOpen" class="modal-overlay" @click.self="modal.isOpen = false">
      <div class="modal-card">
        <div class="modal-header">
            <h3>{{ modal.title }}</h3>
            <button @click="modal.isOpen = false" class="btn-close">×</button>
        </div>
        
        <div class="modal-body">
            <div v-if="modal.type === 'addType'">
                <label>Nama Tipe Mobil</label>
                <input v-model="form.name" placeholder="Contoh: Honda Brio" autofocus />
            </div>

            <div v-if="modal.type === 'addChild'">
                <p class="info-text">Menambah {{ modal.childType }} untuk: <strong>{{ selectedParent?.name }}</strong></p>
                <label>Nama {{ modal.childType === 'variant' ? 'Varian' : 'Warna' }}</label>
                <input v-model="form.childName" placeholder="Contoh: GL / Hitam Metalik" autofocus />
            </div>

            <div v-if="modal.type === 'addYear'">
                <label>Tahun (Angka)</label>
                <input type="number" v-model="form.year" placeholder="2025" />
                <label>Kode VIN (1 Karakter)</label>
                <input v-model="form.code" maxlength="1" style="text-transform:uppercase" placeholder="S" />
            </div>

            <div v-if="modal.type === 'addPrefix'">
                <label>Tipe Kendaraan</label>
                <select v-model="form.vehicle_type">
                    <option :value="null" disabled>-- Pilih Tipe --</option>
                    <option v-for="t in types" :key="t.id" :value="t.id">{{ t.name }}</option>
                </select>

                <label>Tahun</label>
                <select v-model="form.year_code">
                    <option :value="null" disabled>-- Pilih Tahun --</option>
                    <option v-for="y in years" :key="y.id" :value="y.id">{{ y.year }} ({{ y.code }})</option>
                </select>

                <label>WMI + VDS (8-9 Karakter)</label>
                <input v-model="form.wmi_vds" placeholder="Misal: MH1DD1820" maxlength="9" style="text-transform:uppercase"/>
                
                <label>Plant Code (1 Karakter)</label>
                <input v-model="form.plant_code" placeholder="Misal: J" maxlength="1" style="text-transform:uppercase"/>
            </div>
        </div>

        <div class="modal-footer">
           <button @click="modal.isOpen = false" class="btn-secondary">Batal</button>
           <button @click="submitForm" class="btn-primary" :disabled="isSubmitting">
               {{ isSubmitting ? 'Menyimpan...' : 'Simpan' }}
           </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../../../stores/auth'; // Import Auth

const API_URL = 'http://127.0.0.1:8000/api';
const authStore = useAuthStore();

// --- RBAC PERMISSIONS ---
// Cek apakah user punya izin 'create' atau 'delete' di modul 'vin_master'
const canCreate = computed(() => authStore.can('vin_master', 'create'));
const canDelete = computed(() => authStore.can('vin_master', 'delete'));

// State Data
const isLoading = ref(true);
const activeTab = ref('types');
const types = ref<any[]>([]);
const years = ref<any[]>([]);
const prefixes = ref<any[]>([]);

// State Modal
const modal = reactive({ isOpen: false, type: '', title: '', childType: '' });
const form = reactive<any>({});
const selectedParent = ref<any>(null);
const isSubmitting = ref(false);

const loadData = async () => {
  try {
    const [resT, resY, resP] = await Promise.all([
        axios.get(`${API_URL}/types/`),
        axios.get(`${API_URL}/years/`),
        axios.get(`${API_URL}/vin-prefixes/`)
    ]);

    types.value = Array.isArray(resT.data) ? resT.data : resT.data.results || [];
    years.value = Array.isArray(resY.data) ? resY.data : resY.data.results || [];
    prefixes.value = Array.isArray(resP.data) ? resP.data : resP.data.results || [];
  } catch(e) { 
    console.error("Gagal load master:", e);
  } finally {
    isLoading.value = false;
  }
};

onMounted(loadData);

// --- MODAL & ACTIONS ---
const resetForm = () => { Object.keys(form).forEach(k => delete form[k]); };

const openModal = (type: string) => {
    resetForm();
    modal.type = type; modal.isOpen = true; 
    if (type === 'addType') modal.title = "Buat Tipe Baru";
    if (type === 'addYear') modal.title = "Tambah Tahun Produksi";
    if (type === 'addPrefix') modal.title = "Buat Rule Prefix";
};

const openChildModal = (parent: any, childType: string) => {
    resetForm();
    selectedParent.value = parent;
    modal.type = 'addChild'; modal.childType = childType;
    modal.title = `Tambah ${childType === 'variant' ? 'Varian' : 'Warna'}`;
    modal.isOpen = true;
};

const submitForm = async () => {
    isSubmitting.value = true;
    try {
        if(modal.type === 'addType') await axios.post(`${API_URL}/types/`, { name: form.name });
        else if(modal.type === 'addChild') {
            const endpoint = modal.childType === 'variant' ? 'variants' : 'colors';
            await axios.post(`${API_URL}/${endpoint}/`, { vehicle_type: selectedParent.value.id, name: form.childName });
        }
        else if(modal.type === 'addYear') await axios.post(`${API_URL}/years/`, { year: form.year, code: form.code });
        else if(modal.type === 'addPrefix') await axios.post(`${API_URL}/vin-prefixes/`, form);
        
        modal.isOpen = false;
        await loadData();
    } catch(e: any) {
        alert("Error: " + (e.response?.data?.detail || "Gagal menyimpan"));
    } finally {
        isSubmitting.value = false;
    }
};

const deleteItem = async (endpoint: string, id: number) => {
    if(!confirm("Yakin hapus data ini?")) return;
    try { await axios.delete(`${API_URL}/${endpoint}/${id}/`); loadData(); } catch(e) { alert("Gagal menghapus."); }
};

const deleteChild = async (endpoint: string, id: number) => {
    if(!confirm("Hapus item ini?")) return;
    try { await axios.delete(`${API_URL}/${endpoint}/${id}/`); loadData(); } catch(e) { alert("Gagal menghapus."); }
};
</script>

<style scoped>
.master-page { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header { margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
.header h2 { margin: 0; color: #1e293b; }
.header p { margin: 5px 0 0; color: #64748b; font-size: 0.9rem; }

/* LOADING */
.loading-state { text-align: center; padding: 50px; color: #64748b; }

/* TABS */
.tabs { display: flex; gap: 10px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; overflow-x: auto; white-space: nowrap; }
.tabs button { padding: 10px 15px; background: none; border: none; font-weight: 600; color: #64748b; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; white-space: nowrap; }
.tabs button.active { border-bottom-color: #2563eb; color: #2563eb; }

/* CARD */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }

/* TABLE STYLING */
.table-responsive { width: 100%; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 600px; /* Force scroll on really small screens if table view kept */ }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: top; }
th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }

.type-name { color: #334155; font-size: 1rem; }
.code-cell { font-family: monospace; font-weight: bold; color: #d97706; }
.text-center { text-align: center; color: #94a3b8; }
.text-muted { color: #cbd5e1; }

/* TAGS */
.tag-container { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.badge { background: #e0f2fe; color: #0284c7; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; display: flex; align-items: center; gap: 5px; }
.badge.color { background: #fce7f3; color: #be185d; }
.del-x { cursor: pointer; font-weight: bold; opacity: 0.6; }
.del-x:hover { opacity: 1; color: #ef4444; }

/* BUTTONS */
.btn-sm { background: #2563eb; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.btn-add-tag { background: #f1f5f9; border: 1px dashed #cbd5e1; border-radius: 4px; width: 24px; height: 24px; cursor: pointer; color: #64748b; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; line-height: 1; }
.btn-add-tag:hover { border-color: #2563eb; color: #2563eb; background: #eff6ff; }
.btn-danger-text { background: none; border: none; color: #ef4444; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.btn-danger-text:hover { text-decoration: underline; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(2px); padding: 20px; box-sizing: border-box; }
.modal-card { background: white; width: 100%; max-width: 450px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); overflow: hidden; animation: popIn 0.2s ease; display: flex; flex-direction: column; max-height: 90vh; }
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.btn-close { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 20px; overflow-y: auto; }
.modal-footer { padding: 15px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; }

/* FORMS */
label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.85rem; color: #475569; margin-top: 15px; }
label:first-child { margin-top: 0; }
input, select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; outline: none; box-sizing: border-box; }
input:focus, select:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
.info-text { background: #eff6ff; color: #1e40af; padding: 10px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 15px; border: 1px solid #dbeafe; }
.btn-primary { background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }

/* =========================================
   MOBILE RESPONSIVE (CARD VIEW)
   ========================================= */
@media (max-width: 768px) {
    .master-page { padding: 10px; }
    
    /* Header Stack */
    .card-header { flex-direction: column; align-items: flex-start; gap: 10px; }
    .card-header button { width: 100%; }

    /* Hide Table Header */
    thead { display: none; }

    /* Table Rows as Cards */
    tr { display: block; margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    tr:last-child { margin-bottom: 0; }
    
    td { display: block; text-align: right; padding: 8px 0; border: none; position: relative; padding-left: 40%; }
    
    /* Label Pseudo-element (Requires data-label in HTML) */
    td::before { 
        content: attr(data-label); 
        position: absolute; left: 0; top: 8px; 
        width: 40%; text-align: left; 
        font-weight: 700; color: #64748b; font-size: 0.85rem; 
    }

    /* Adjust Tag Container for Mobile */
    .tag-container { justify-content: flex-end; }
    .action-cell { text-align: right; }
    
    /* Reset min-width for mobile */
    table { min-width: 100%; }
}
</style>