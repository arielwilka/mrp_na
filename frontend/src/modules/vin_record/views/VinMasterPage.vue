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
        <button :class="{ active: activeTab === 'prefixes' }" @click="activeTab = 'prefixes'">Aturan Prefix</button>
        <button :class="{ active: activeTab === 'years' }" @click="activeTab = 'years'">Tahun Produksi</button>
      </div>

      <div v-if="activeTab === 'prefixes'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Mapping Prefix VIN</h3>
            <button v-if="canCreate" @click="openModal('addPrefix')" class="btn-sm">+ Rule Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Produk</th> <th>Tahun</th>
                  <th>WMI + VDS</th>
                  <th class="text-center">Check Digit (Static)</th> 
                  <th>Plant</th>
                  <th>Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="prefixes.length === 0"><td colspan="6" class="text-center">Belum ada rule.</td></tr>
                <tr v-for="p in prefixes" :key="p.id">
                  <td data-label="Produk"><strong>{{ p.product_type_name }}</strong></td>
                  <td data-label="Tahun">{{ p.year_code_label }}</td>
                  <td data-label="WMI+VDS" class="code-cell">{{ p.wmi_vds }}</td>
                  
                  <td data-label="Static Digit" class="text-center">
                    <span v-if="p.static_ninth_digit !== null && p.static_ninth_digit !== ''" class="badge-static">
                      {{ p.static_ninth_digit }}
                    </span>
                    <span v-else class="text-muted text-xs">Auto (ISO)</span>
                  </td>

                  <td data-label="Plant" class="code-cell">{{ p.plant_code }}</td>
                  <td data-label="Aksi">
                    <button v-if="canDelete" @click="deleteItem('prefixes', p.id)" class="btn-danger-text">Hapus</button>
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
    </div>

    <div v-if="modal.isOpen" class="modal-overlay" @click.self="modal.isOpen = false">
      <div class="modal-card">
        <div class="modal-header">
            <h3>{{ modal.title }}</h3>
            <button @click="modal.isOpen = false" class="btn-close">×</button>
        </div>
        
        <div class="modal-body">
            <div v-if="modal.type === 'addYear'">
                <label>Tahun (Angka)</label>
                <input type="number" v-model="form.year" placeholder="2025" />
                <label>Kode VIN (1 Karakter)</label>
                <input v-model="form.code" maxlength="1" style="text-transform:uppercase" placeholder="S" />
            </div>

            <div v-if="modal.type === 'addPrefix'">
                <label>Tipe Produk</label>
                <select v-model="form.product_type">
                    <option :value="null" disabled>-- Pilih Produk (Hanya Traceable) --</option>
                    <option v-for="t in traceableTypes" :key="t.id" :value="t.id">
                        {{ t.brand_code }} - {{ t.name }}
                    </option>
                </select>
                <p v-if="traceableTypes.length === 0" class="hint-text text-danger">
                    Tidak ada produk yang diset "Wajib VIN Trace". Silakan atur di Master Product.
                </p>

                <label>Tahun</label>
                <select v-model="form.year_code">
                    <option :value="null" disabled>-- Pilih Tahun --</option>
                    <option v-for="y in years" :key="y.id" :value="y.id">{{ y.year }} ({{ y.code }})</option>
                </select>

                <label>WMI + VDS (8 Karakter)</label>
                <input v-model="form.wmi_vds" placeholder="Misal: MH1DD182" maxlength="8" style="text-transform:uppercase"/>
                
                <label>Digit Ke-9 (Static)</label>
                <input v-model="form.static_ninth_digit" placeholder="Kosongkan jika Auto Check Digit" maxlength="1" style="text-transform:uppercase"/>
                <p class="hint-text">Isi hanya jika VIN tidak menggunakan rumus Check Digit ISO 3779.</p>

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
import { useAuthStore } from '../../../stores/auth'; 

const BASE_API = 'http://127.0.0.1:8000/api';
const PRODUCT_API = `${BASE_API}/product`;
// Pastikan URL menggunakan tanda strip (-) sesuai urls.py backend
const VIN_API = `${BASE_API}/vin-record`; 

const authStore = useAuthStore();

// RBAC
const canCreate = computed(() => authStore.can('vin_master', 'create'));
const canDelete = computed(() => authStore.can('vin_master', 'delete'));

// State
const isLoading = ref(true);
const activeTab = ref('prefixes'); 
const types = ref<any[]>([]);
const years = ref<any[]>([]);
const prefixes = ref<any[]>([]);

// Modal
const modal = reactive({ isOpen: false, type: '', title: '' });
const form = reactive<any>({});
const isSubmitting = ref(false);

// --- REVISI: COMPUTED FILTER ---
// Memfilter tipe produk, hanya menampilkan yang is_vin_trace == true
const traceableTypes = computed(() => {
    if (!types.value) return [];
    return types.value.filter((t: any) => t.is_vin_trace === true);
});

const loadData = async () => {
  try {
    const [resT, resY, resP] = await Promise.all([
        axios.get(`${PRODUCT_API}/types/`), 
        axios.get(`${VIN_API}/years/`),
        axios.get(`${VIN_API}/prefixes/`)
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

// Actions
const resetForm = () => { Object.keys(form).forEach(k => delete form[k]); };

const openModal = (type: string) => {
    resetForm();
    modal.type = type; modal.isOpen = true; 
    if (type === 'addYear') modal.title = "Tambah Tahun Produksi";
    if (type === 'addPrefix') modal.title = "Buat Rule Prefix";
};

const submitForm = async () => {
    isSubmitting.value = true;
    try {
        if(modal.type === 'addYear') {
            await axios.post(`${VIN_API}/years/`, { 
                year: form.year, 
                code: form.code 
            });
        }
        else if(modal.type === 'addPrefix') {
            await axios.post(`${VIN_API}/prefixes/`, {
                product_type: form.product_type, // Field disesuaikan
                year_code: form.year_code,
                wmi_vds: form.wmi_vds,
                plant_code: form.plant_code,
                static_ninth_digit: form.static_ninth_digit 
            });
        }
        
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
    try { 
        await axios.delete(`${VIN_API}/${endpoint}/${id}/`); 
        loadData(); 
    } catch(e) { 
        alert("Gagal menghapus."); 
    }
};
</script>

<style scoped>
/* CSS Styles Tetap Sama */
.master-page { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header { margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
.header h2 { margin: 0; color: #1e293b; }
.header p { margin: 5px 0 0; color: #64748b; font-size: 0.9rem; }

.loading-state { text-align: center; padding: 50px; color: #64748b; }

.tabs { display: flex; gap: 10px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; overflow-x: auto; white-space: nowrap; }
.tabs button { padding: 10px 15px; background: none; border: none; font-weight: 600; color: #64748b; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; white-space: nowrap; }
.tabs button.active { border-bottom-color: #2563eb; color: #2563eb; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }

.table-responsive { width: 100%; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 600px; }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: top; }
th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px; }

.code-cell { font-family: monospace; font-weight: bold; color: #d97706; }
.text-center { text-align: center; }
.text-muted { color: #cbd5e1; }
.text-xs { font-size: 0.75rem; }
.hint-text { font-size: 0.75rem; color: #64748b; margin-top: -5px; margin-bottom: 15px; }
.text-danger { color: #ef4444; font-size: 0.8rem; margin-top: -5px; margin-bottom: 10px; }

.badge-static { background: #fef3c7; color: #d97706; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-family: monospace; border: 1px solid #fde68a; }

.btn-sm { background: #2563eb; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.btn-danger-text { background: none; border: none; color: #ef4444; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.btn-danger-text:hover { text-decoration: underline; }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(2px); padding: 20px; box-sizing: border-box; }
.modal-card { background: white; width: 100%; max-width: 450px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); overflow: hidden; animation: popIn 0.2s ease; display: flex; flex-direction: column; max-height: 90vh; }
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.btn-close { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-body { padding: 20px; overflow-y: auto; }
.modal-footer { padding: 15px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; }

label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.85rem; color: #475569; margin-top: 15px; }
label:first-child { margin-top: 0; }
input, select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; outline: none; box-sizing: border-box; }
input:focus, select:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
.btn-primary { background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }

@media (max-width: 768px) {
    .master-page { padding: 10px; }
    .card-header { flex-direction: column; align-items: flex-start; gap: 10px; }
    .card-header button { width: 100%; }
    thead { display: none; }
    tr { display: block; margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    td { display: block; text-align: right; padding: 8px 0; border: none; position: relative; padding-left: 40%; }
    td::before { content: attr(data-label); position: absolute; left: 0; top: 8px; width: 40%; text-align: left; font-weight: 700; color: #64748b; font-size: 0.85rem; }
}
</style>