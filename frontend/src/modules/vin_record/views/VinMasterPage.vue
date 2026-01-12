<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>⚙️ Master Konfigurasi VIN</h2>
        <p>Pengaturan kode tahun dan prefix WMI/VDS per model kendaraan.</p>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div> Memuat Data...
    </div>

    <div v-else class="fade-in">
      
      <div class="tabs">
        <button :class="{ active: activeTab === 'prefixes' }" @click="activeTab = 'prefixes'">
          📝 Aturan Prefix (WMI/VDS)
        </button>
        <button :class="{ active: activeTab === 'years' }" @click="activeTab = 'years'">
          📅 Tahun Produksi
        </button>
      </div>

      <div v-if="activeTab === 'prefixes'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Mapping Prefix VIN</h3>
            <button v-if="canCreate" @click="openModal('addPrefix')" class="btn-primary btn-sm">
              + Rule Baru
            </button>
          </div>
          <div class="table-responsive">
            <table class="table table-complex">
              <thead>
                <tr>
                  <th class="col-product">Produk</th>
                  <th class="col-tight text-center">Tahun</th>
                  <th class="col-tight text-center">WMI + VDS</th>
                  <th class="col-tight text-center">Digit 9</th>
                  <th class="col-tight text-center">Plant</th>
                  <th class="col-action text-right">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in prefixes" :key="p.id">
                  <td class="cell-truncate">
                    <div class="product-info" :title="p.product_type_name">
                      <strong class="text-primary">{{ p.product_type_name }}</strong>
                      <span class="mode-badge">{{ p.tracking_mode || 'VIN' }}</span>
                    </div>
                  </td>
                  <td class="text-center"><span class="badge-year">{{ p.year_code_label }}</span></td>
                  <td class="text-center"><span class="code-box">{{ p.wmi_vds }}</span></td>
                  <td class="text-center no-wrap">
                    <span v-if="p.static_ninth_digit && p.static_ninth_digit !== '0'" class="badge-static">
                      Fix: {{ p.static_ninth_digit }}
                    </span>
                    <span v-else class="badge-auto">Auto</span>
                  </td>
                  <td class="text-center"><span class="font-mono font-bold">{{ p.plant_code }}</span></td>
                  <td class="text-right">
                    <button v-if="canDelete" @click="deleteItem('prefixes', p.id)" class="btn-icon danger" title="Hapus">🗑️</button>
                  </td>
                </tr>
                <tr v-if="prefixes.length === 0">
                  <td colspan="6" class="text-center py-8 text-muted">Belum ada rule prefix.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'years'" class="tab-content">
        <div class="card max-w-xl"> <div class="card-header">
            <h3>Kode Tahun Produksi</h3>
            <button v-if="canCreate" @click="openModal('addYear')" class="btn-primary btn-sm">
              + Tahun Baru
            </button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th class="pl-6">Tahun Masehi</th>
                  <th class="text-center w-32">Kode VIN</th>
                  <th class="text-right w-24 pr-6">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="y in years" :key="y.id">
                  <td class="font-bold text-lg pl-6">{{ y.year }}</td>
                  <td class="text-center">
                    <span class="char-box">{{ y.code }}</span>
                  </td>
                  <td class="text-right pr-6">
                    <button v-if="canDelete" @click="deleteItem('years', y.id)" class="btn-icon danger" title="Hapus">🗑️</button>
                  </td>
                </tr>
                <tr v-if="years.length === 0">
                  <td colspan="3" class="text-center py-8 text-muted">Belum ada data tahun.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>

    <Transition name="modal-fade">
      <div v-if="modal.isOpen" class="modal-backdrop" @click.self="modal.isOpen = false">
        <div class="modal-dialog">
          <div class="modal-header">
              <h3>{{ modal.title }}</h3>
              <button @click="modal.isOpen = false" class="btn-close">&times;</button>
          </div>
          <div class="modal-body">
              
              <div v-if="modal.type === 'addYear'">
                  <div class="form-group">
                      <label>Tahun (Angka) <span class="text-red">*</span></label>
                      <input type="number" v-model="form.year" placeholder="Contoh: 2026" class="form-input" />
                  </div>
                  <div class="form-group">
                      <label>Kode Karakter VIN <span class="text-red">*</span></label>
                      <input v-model="form.code" maxlength="1" class="form-input uppercase text-center font-bold text-lg w-24" placeholder="A" />
                      <small class="helper-text">Satu karakter (Angka/Huruf).</small>
                  </div>
              </div>

              <div v-if="modal.type === 'addPrefix'">
                  <div class="form-group">
                      <label>Tipe Produk <span class="text-red">*</span></label>
                      <select v-model="form.product_type" class="form-select">
                          <option :value="null" disabled>-- Pilih Produk --</option>
                          <option v-for="t in traceableTypes" :key="t.id" :value="t.id">{{ t.brand_code }} - {{ t.name }}</option>
                      </select>
                      <p v-if="traceableTypes.length === 0" class="error-text">⚠️ Tidak ada produk mode 'VIN'.</p>
                  </div>
                  <div class="form-group">
                      <label>Untuk Tahun Produksi <span class="text-red">*</span></label>
                      <select v-model="form.year_code" class="form-select">
                          <option :value="null" disabled>-- Pilih Tahun --</option>
                          <option v-for="y in years" :key="y.id" :value="y.id">{{ y.year }} (Kode: {{ y.code }})</option>
                      </select>
                  </div>
                  <div class="row-2-col">
                      <div class="form-group">
                          <label>WMI + VDS (8 Char)</label>
                          <input v-model="form.wmi_vds" placeholder="MH1..." maxlength="8" class="form-input uppercase font-mono"/>
                      </div>
                      <div class="form-group">
                          <label>Plant Code (1 Char)</label>
                          <input v-model="form.plant_code" placeholder="J" maxlength="1" class="form-input uppercase font-mono text-center"/>
                      </div>
                  </div>
                  <div class="form-group bg-slate-50 p-3 rounded border border-slate-200 mt-2">
                      <label>Digit Ke-9 (Override)</label>
                      <div class="flex items-center gap-3">
                        <input v-model="form.static_ninth_digit" placeholder="0" maxlength="1" class="form-input uppercase w-20 text-center"/>
                        <span class="text-xs text-muted leading-tight">Biarkan <strong>'0'</strong> jika ingin Auto Check Digit ISO 3779.</span>
                      </div>
                  </div>
              </div>
          </div>
          <div class="modal-footer">
             <button @click="modal.isOpen = false" class="btn-ghost">Batal</button>
             <button @click="submitForm" class="btn-primary" :disabled="isSubmitting">{{ isSubmitting ? 'Menyimpan...' : 'Simpan Data' }}</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from './api';
import { useAuthStore } from '@/stores/auth'; 

const authStore = useAuthStore();
const canCreate = computed(() => authStore.can('vin_record', 'create'));
const canDelete = computed(() => authStore.can('vin_record', 'delete'));

const isLoading = ref(true);
const activeTab = ref('prefixes'); 
const types = ref<any[]>([]);
const years = ref<any[]>([]);
const prefixes = ref<any[]>([]);

const modal = reactive({ isOpen: false, type: '', title: '' });
const form = reactive<any>({});
const isSubmitting = ref(false);

const traceableTypes = computed(() => types.value.filter((t: any) => t.tracking_mode === 'VIN'));

const loadData = async () => {
  try {
    const [resT, resY, resP] = await Promise.all([
        api.getTraceableTypes(), api.getYears(), api.getPrefixes()
    ]);
    types.value = Array.isArray(resT.data) ? resT.data : resT.data.results || [];
    years.value = Array.isArray(resY.data) ? resY.data : resY.data.results || [];
    prefixes.value = Array.isArray(resP.data) ? resP.data : resP.data.results || [];
  } catch(e) { console.error("Gagal load master:", e); } 
  finally { isLoading.value = false; }
};

onMounted(loadData);

const openModal = (type: string) => {
    Object.keys(form).forEach(k => delete form[k]);
    if (type === 'addPrefix') form.static_ninth_digit = '0';
    modal.type = type; modal.isOpen = true; 
    modal.title = type === 'addYear' ? "Tambah Tahun Produksi" : "Buat Rule Prefix";
};

const submitForm = async () => {
    isSubmitting.value = true;
    try {
        if(modal.type === 'addYear') await api.createYear(form);
        else if(modal.type === 'addPrefix') await api.createPrefix(form);
        modal.isOpen = false; await loadData();
    } catch(e: any) { alert("Error: " + (e.response?.data?.detail || "Gagal menyimpan")); } 
    finally { isSubmitting.value = false; }
};

const deleteItem = async (type: 'years' | 'prefixes', id: number) => {
    if(!confirm("Yakin hapus data ini?")) return;
    try { 
        if (type === 'years') await api.deleteYear(id);
        else await api.deletePrefix(id);
        loadData(); 
    } catch(e) { alert("Gagal menghapus."); }
};
</script>

<style scoped>
/* PAGE & TABS */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: var(--text-primary); }
.header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: var(--text-secondary); font-size: 0.9rem; }

.tabs { display: flex; gap: 24px; border-bottom: 2px solid var(--border-color); margin-bottom: 24px; }
.tabs button { padding: 12px 4px; background: none; border: none; font-size: 1rem; font-weight: 600; color: var(--text-secondary); cursor: pointer; border-bottom: 3px solid transparent; margin-bottom: -2px; transition: all 0.3s; }
.tabs button:hover { color: var(--primary-color); }
.tabs button.active { border-bottom-color: var(--primary-color); color: var(--primary-color); }

/* CARDS */
.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: var(--shadow-sm); overflow: hidden; }
.card-header { padding: 16px 24px; background: var(--bg-body); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; font-weight: 600; }

/* TABLE STYLING */
.table-responsive { width: 100%; overflow-x: auto; }
.table { width: 100%; border-collapse: separate; border-spacing: 0; }

/* REVISI CSS TABEL: TIDAK ADA MIN-WIDTH GLOBAL */
.table th { background: #f8fafc; color: var(--text-secondary); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; padding: 14px 20px; text-align: left; border-bottom: 1px solid var(--border-color); white-space: nowrap; }
.table td { padding: 14px 20px; border-bottom: 1px solid var(--border-color); vertical-align: middle; font-size: 0.95rem; color: var(--text-primary); }
.table tr:last-child td { border-bottom: none; }
.table tr:hover { background-color: #f8fafc; }

/* HANYA TABLE PREFIX YANG PUNYA MIN-WIDTH */
.table-complex { min-width: 800px; }

/* COLUMN HELPERS */
.col-tight { width: 1%; white-space: nowrap; }
.col-auto { width: auto; }
.col-action { width: 100px; text-align: right; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; letter-spacing: 0.5px; }
.no-wrap { white-space: nowrap; }
.w-32 { width: 8rem; }
.w-24 { width: 6rem; }
.pl-6 { padding-left: 24px !important; }
.pr-6 { padding-right: 24px !important; }

/* Truncate Product Name */
.cell-truncate { max-width: 250px; }
.product-info strong { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
.mode-badge { font-size: 0.65rem; background: #e0f2fe; color: #0284c7; padding: 1px 6px; border-radius: 4px; font-weight: 600; white-space: nowrap; }

/* BADGES */
.text-primary { color: var(--primary-color); font-weight: 600; }
.text-muted { color: var(--text-secondary); }
.text-xs { font-size: 0.75rem; }
.text-orange { color: #c2410c; }
.code-box { background: #fff7ed; color: #c2410c; padding: 4px 8px; border-radius: 6px; border: 1px solid #ffedd5; font-family: monospace; font-weight: bold; }
.char-box { display: inline-flex; width: 32px; height: 32px; align-items: center; justify-content: center; background: #eff6ff; color: #1d4ed8; border-radius: 8px; font-weight: 800; font-size: 1.1rem; border: 1px solid #dbeafe; }
.badge-year { background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }
.badge-static { background: #fefce8; color: #854d0e; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; border: 1px solid #fde047; white-space: nowrap; }
.badge-auto { background: #f0fdf4; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #bbf7d0; font-weight: 600; }

/* BUTTONS */
.btn-primary { background: var(--primary-color); color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--text-secondary); border: none; padding: 8px 16px; font-weight: 600; cursor: pointer; }
.btn-ghost:hover { background: #f1f5f9; color: var(--text-primary); border-radius: 6px; }
.btn-icon { width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border-color); background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: var(--text-secondary); transition: 0.2s; }
.btn-icon:hover { border-color: var(--primary-color); color: var(--primary-color); }
.btn-icon.danger:hover { background: #fee2e2; border-color: #ef4444; color: #ef4444; }

/* MODAL STYLES */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-dialog { background: var(--bg-card); width: 90%; max-width: 500px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.modal-header { padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: var(--text-primary); }
.btn-close { background: transparent; border: none; font-size: 1.5rem; color: var(--text-secondary); cursor: pointer; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }
.btn-close:hover { background: #f1f5f9; }
.modal-body { padding: 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 12px; background: var(--bg-body); }

/* FORMS */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem; background: var(--bg-body); color: var(--text-primary); box-sizing: border-box; transition: 0.2s; }
.form-input:focus, .form-select:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.row-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.helper-text { display: block; margin-top: 6px; font-size: 0.8rem; color: var(--text-secondary); }
.error-text { color: #ef4444; font-size: 0.8rem; margin-top: 6px; }
.text-red { color: #ef4444; margin-left: 2px; }
.w-20 { width: 80px; }
.uppercase { text-transform: uppercase; }
.bg-slate-50 { background: #f8fafc; }
.flex { display: flex; }
.gap-3 { gap: 12px; }
.items-center { align-items: center; }
.leading-tight { line-height: 1.25; }
.max-w-xl { max-width: 576px; }
</style>