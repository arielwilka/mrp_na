<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>📦 Master Produk & Kendaraan</h2>
        <p>Kelola data Brand, Tipe, Varian, dan Strategi Produksi.</p>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'brands' }" @click="activeTab = 'brands'">🏢 Data Brand</button>
      <button :class="{ active: activeTab === 'types' }" @click="activeTab = 'types'">🚙 Tipe & Model</button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div> Memuat Data...
    </div>

    <div v-else class="fade-in">
      
      <div v-if="activeTab === 'brands'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Daftar Brand / Merk</h3>
            <button v-if="canCreate" @click="openModal('brand')" class="btn-primary btn-sm">+ Brand Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th class="col-tight">Kode</th>
                  <th class="col-auto">Nama Brand</th>
                  <th class="col-tight text-right">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="b in brands" :key="b.id">
                  <td class="font-mono bold">{{ b.code }}</td>
                  <td>{{ b.name }}</td>
                  <td class="text-right">
                    <button v-if="canDelete" @click="deleteItem('brands', b.id!)" class="btn-icon danger" title="Hapus">🗑️</button>
                  </td>
                </tr>
                <tr v-if="brands.length === 0"><td colspan="3" class="text-center text-muted">Belum ada data.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'types'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Daftar Tipe Kendaraan</h3>
            <button v-if="canCreate" @click="openModal('type')" class="btn-primary btn-sm">+ Tipe Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th class="col-tight">Brand</th>
                  <th class="col-auto">Model / Tipe</th>
                  <th class="col-tight">Kode Internal</th>
                  <th class="text-center col-tight">Tracking Mode</th>
                  <th class="text-center col-tight">Schedule</th>
                  <th class="col-action">Config</th>
                  <th class="col-tight text-right">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in types" :key="t.id">
                  <td><span class="badge-brand">{{ t.brand_name }}</span></td>
                  <td><strong>{{ t.name }}</strong></td>
                  <td class="font-mono">{{ t.code }}</td>
                  
                  <td class="text-center">
                    <span :class="['badge-mode', t.tracking_mode]">
                        {{ t.tracking_mode_display }}
                    </span>
                  </td>

                  <td class="text-center">
                    <span v-if="t.scheduling_policy === 'CONTINUOUS'" class="badge-purple">Continuous</span>
                    <span v-else class="badge-blue">Daily Reset</span>
                  </td>

                  <td class="text-right">
                    <button @click="openConfigModal(t)" class="btn-config">⚙️ Detail</button>
                  </td>

                  <td class="text-right">
                    <button v-if="canDelete" @click="deleteItem('types', t.id!)" class="btn-icon danger">🗑️</button>
                  </td>
                </tr>
                <tr v-if="types.length === 0"><td colspan="7" class="text-center text-muted">Belum ada data.</td></tr>
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
              <button @click="modal.isOpen = false" class="btn-close">
                <span class="close-icon">&times;</span>
              </button>
          </div>
          
          <div class="modal-body">
              <div v-if="modal.type === 'brand'">
                  <div class="form-group">
                      <label>Nama Brand <span class="required">*</span></label>
                      <input v-model="form.name" placeholder="Contoh: TOYOTA" class="form-input" />
                  </div>
                  <div class="form-group">
                      <label>Kode Brand <span class="required">*</span></label>
                      <input v-model="form.code" placeholder="TYT" class="form-input uppercase" maxlength="10"/>
                      <small class="helper-text">Singkatan unik, maksimal 10 karakter.</small>
                  </div>
              </div>

              <div v-if="modal.type === 'type'">
                  <div class="form-group">
                      <label>Brand <span class="required">*</span></label>
                      <div class="select-wrapper">
                        <select v-model="form.brand" class="form-select">
                            <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
                        </select>
                      </div>
                  </div>
                  
                  <div class="row-2-col">
                    <div class="form-group">
                        <label>Nama Model <span class="required">*</span></label>
                        <input v-model="form.name" placeholder="Contoh: Fortuner" class="form-input" />
                    </div>
                    <div class="form-group">
                        <label>Kode Internal <span class="required">*</span></label>
                        <input v-model="form.code" placeholder="FRT-2024" class="form-input uppercase" />
                    </div>
                  </div>
                  
                  <div class="form-group">
                      <label>Strategi Produksi (Tracking) <span class="required">*</span></label>
                      <div class="tracking-options">
                          <label :class="['radio-card', { active: form.tracking_mode === 'VIN' }]">
                              <input type="radio" v-model="form.tracking_mode" value="VIN">
                              <div class="radio-content">
                                  <span class="radio-title">Strict VIN</span>
                                  <span class="radio-desc">Mobil / Motor (Wajib VIN Record)</span>
                              </div>
                          </label>
                          <label :class="['radio-card', { active: form.tracking_mode === 'INTERNAL_ID' }]">
                              <input type="radio" v-model="form.tracking_mode" value="INTERNAL_ID">
                              <div class="radio-content">
                                  <span class="radio-title">Internal ID</span>
                                  <span class="radio-desc">Karoseri / Custom (Auto Generated ID)</span>
                              </div>
                          </label>
                          <label :class="['radio-card', { active: form.tracking_mode === 'BATCH' }]">
                              <input type="radio" v-model="form.tracking_mode" value="BATCH">
                              <div class="radio-content">
                                  <span class="radio-title">Batch Qty</span>
                                  <span class="radio-desc">Baut / Part Kecil (Counter Only)</span>
                              </div>
                          </label>
                      </div>
                  </div>

                  <div class="form-group mt-4">
                      <label>Kebijakan Jadwal (Handover)</label>
                      <div class="toggle-group">
                          <label class="toggle-switch">
                              <input type="checkbox" v-model="isContinuous">
                              <span class="slider round"></span>
                          </label>
                          <div class="toggle-label">
                              <strong v-if="isContinuous">Mode: CONTINUOUS (Project)</strong>
                              <strong v-else>Mode: DAILY RESET (Mass Prod)</strong>
                              <small v-if="isContinuous">SPK tidak ditutup harian. Progress berjalan terus.</small>
                              <small v-else>Sisa unit hari ini akan di-handover ke besok sore hari.</small>
                          </div>
                      </div>
                  </div>

                  <div class="toggle-group compact" v-if="form.tracking_mode === 'VIN'">
                      <label class="toggle-switch small">
                          <input type="checkbox" v-model="form.has_check_digit">
                          <span class="slider round"></span>
                      </label>
                      <span class="ml-2 text-sm">Gunakan Check Digit (VIN Algorithm)</span>
                  </div>
              </div>
          </div>
          
          <div class="modal-footer">
             <button @click="modal.isOpen = false" class="btn-ghost">Batal</button>
             <button @click="submitForm" class="btn-primary" :disabled="isSubmitting">
                {{ isSubmitting ? 'Menyimpan...' : 'Simpan Data' }}
             </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal-fade">
      <div v-if="configModal.isOpen" class="modal-backdrop" @click.self="configModal.isOpen = false">
          <div class="modal-dialog wide-dialog">
              <div class="modal-header">
                  <div>
                    <h3>Konfigurasi Produk</h3>
                    <p class="subtitle">{{ configModal.data?.brand_name }} - {{ configModal.data?.name }}</p>
                  </div>
                  <button @click="configModal.isOpen = false" class="btn-close"><span class="close-icon">&times;</span></button>
              </div>
              
              <div class="modal-body">
                <div class="config-grid">
                  
                  <div class="config-panel">
                      <div class="panel-header">
                        <h4>🏷️ Daftar Varian</h4>
                        <span class="badge-count">{{ currentVariants.length }}</span>
                      </div>
                      
                      <div class="input-group-row">
                          <input v-model="newVariant" placeholder="Nama Varian (ex: G M/T)" @keyup.enter="addVariant" class="form-input" />
                          <button @click="addVariant" class="btn-add" title="Tambah Varian"><span>+</span></button>
                      </div>

                      <ul class="styled-list">
                          <li v-for="v in currentVariants" :key="v.id">
                              <span class="item-text">{{ v.name }}</span>
                              <button @click="deleteSubItem('variants', v.id!)" class="btn-remove">&times;</button>
                          </li>
                          <li v-if="currentVariants.length === 0" class="empty-state">Belum ada varian.</li>
                      </ul>
                  </div>

                  <div class="config-panel">
                      <div class="panel-header">
                        <h4>🎨 Daftar Warna</h4>
                        <span class="badge-count">{{ currentColors.length }}</span>
                      </div>
                      
                      <div class="input-group-row">
                          <input v-model="newColorName" placeholder="Nama Warna" class="form-input" />
                          <input v-model="newColorCode" placeholder="Kode" class="form-input w-20 uppercase" @keyup.enter="addColor" />
                          <button @click="addColor" class="btn-add" title="Tambah Warna"><span>+</span></button>
                      </div>

                      <ul class="styled-list">
                          <li v-for="c in currentColors" :key="c.id">
                              <div class="color-item">
                                <span class="item-text">{{ c.name }}</span>
                                <span v-if="c.code" class="code-tag">{{ c.code }}</span>
                              </div>
                              <button @click="deleteSubItem('colors', c.id!)" class="btn-remove">&times;</button>
                          </li>
                          <li v-if="currentColors.length === 0" class="empty-state">Belum ada warna.</li>
                      </ul>
                  </div>

                </div>
              </div>
              
              <div class="modal-footer">
                  <button @click="configModal.isOpen = false" class="btn-primary">Selesai</button>
              </div>
          </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '../api';
import type { Brand, ProductType, ProductVariant, ProductColor } from '@/types/product';

const authStore = useAuthStore();
const canCreate = computed(() => authStore.can('product_master', 'create')); 
const canDelete = computed(() => authStore.can('product_master', 'delete'));

const activeTab = ref('brands');
const isLoading = ref(false);
const isSubmitting = ref(false);

const brands = ref<Brand[]>([]);
const types = ref<ProductType[]>([]);

const modal = reactive({ isOpen: false, type: '', title: '' });
const form = reactive<any>({});
const isContinuous = ref(false); // Helper state for toggle

// Sync toggle UI to form model
watch(isContinuous, (val) => {
    form.scheduling_policy = val ? 'CONTINUOUS' : 'DAILY_RESET';
});

const configModal = reactive({ isOpen: false, data: {} as any });
const currentVariants = ref<ProductVariant[]>([]);
const currentColors = ref<ProductColor[]>([]);
const newVariant = ref('');
const newColorName = ref('');
const newColorCode = ref('');

onMounted(() => { loadData(); });

const loadData = async () => {
    isLoading.value = true;
    try {
        const [resB, resT] = await Promise.all([
            api.getBrands(),
            api.getTypes()
        ]);
        const rawBrands = resB.data;
        brands.value = Array.isArray(rawBrands) ? rawBrands : (rawBrands['results'] || []);
        
        const rawTypes = resT.data;
        const typesList = Array.isArray(rawTypes) ? rawTypes : (rawTypes['results'] || []);
        
        // Map brand name manually if not populated by backend
        types.value = typesList.map((t: any) => {
            const brand = brands.value.find(b => b.id === t.brand);
            // Backup check jika backend sudah kirim brand_name via serializer
            return { ...t, brand_name: t.brand_name || (brand ? brand.name : '-') };
        });
    } catch(e) { console.error(e); } 
    finally { isLoading.value = false; }
};

const openModal = (type: string) => {
    Object.keys(form).forEach(k => delete form[k]);
    
    // Default values
    form.tracking_mode = 'VIN'; 
    form.has_check_digit = false;
    form.scheduling_policy = 'DAILY_RESET';
    isContinuous.value = false;
    
    modal.type = type;
    modal.title = type === 'brand' ? 'Tambah Brand Baru' : 'Tambah Tipe Kendaraan';
    modal.isOpen = true;
};

const submitForm = async () => {
    isSubmitting.value = true;
    try {
        if (modal.type === 'brand') await api.createBrand(form);
        else await api.createType(form);
        modal.isOpen = false; loadData();
    } catch(e: any) { 
        alert("Gagal: " + (e.response?.data?.detail || "Error")); 
    } finally { isSubmitting.value = false; }
};

const deleteItem = async (type: 'brands' | 'types', id: number) => {
    if(!confirm("Yakin hapus?")) return;
    try { 
        if (type === 'brands') await api.deleteBrand(id);
        else await api.deleteType(id);
        loadData(); 
    } catch(e) { alert("Gagal hapus (Data terpakai?)"); }
};

const openConfigModal = async (typeObj: any) => {
    configModal.data = typeObj; configModal.isOpen = true;
    newVariant.value = ''; newColorName.value = ''; newColorCode.value = '';
    currentVariants.value = []; currentColors.value = [];
    await loadSubItems(typeObj.id);
};

const loadSubItems = async (typeId: number) => {
    try {
        const [resV, resC] = await Promise.all([api.getVariants(typeId), api.getColors(typeId)]);
        const rawV = resV.data;
        currentVariants.value = Array.isArray(rawV) ? rawV : (rawV['results'] || []);
        const rawC = resC.data;
        currentColors.value = Array.isArray(rawC) ? rawC : (rawC['results'] || []);
    } catch(e) {}
};

const addVariant = async () => {
    if(!newVariant.value) return;
    try {
        await api.createVariant({ product_type: configModal.data.id, name: newVariant.value });
        newVariant.value = ''; loadSubItems(configModal.data.id);
    } catch(e) {}
};

const addColor = async () => {
    if(!newColorName.value) return;
    try {
        await api.createColor({ product_type: configModal.data.id, name: newColorName.value, code: newColorCode.value });
        newColorName.value = ''; newColorCode.value = ''; loadSubItems(configModal.data.id);
    } catch(e) {}
};

const deleteSubItem = async (type: 'variants' | 'colors', id: number) => {
    if(!confirm("Hapus?")) return;
    try { 
        if (type === 'variants') await api.deleteVariant(id);
        else await api.deleteColor(id);
        loadSubItems(configModal.data.id); 
    } catch(e) {}
};
</script>

<style scoped>
/* ==========================================================================
   PAGE LAYOUT
   ========================================================================== */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; --primary-color: #2563eb; --primary-hover: #1d4ed8; --text-primary: #1e293b; --text-secondary: #64748b; --border-color: #e2e8f0; --bg-body: #ffffff; --bg-card: #ffffff; }
.header { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
.header h2 { margin: 0; font-size: 1.5rem; color: var(--text-primary); }
.header p { margin: 4px 0 0; color: var(--text-secondary); }

/* Tabs */
.tabs { display: flex; gap: 20px; border-bottom: 2px solid var(--border-color); margin-bottom: 24px; }
.tabs button { 
    padding: 12px 20px; background: none; border: none; font-size: 1rem;
    font-weight: 600; color: var(--text-secondary); cursor: pointer; 
    border-bottom: 2px solid transparent; margin-bottom: -2px; transition: 0.3s;
}
.tabs button:hover { color: var(--primary-color); }
.tabs button.active { border-bottom-color: var(--primary-color); color: var(--primary-color); }

/* ==========================================================================
   TABLE STYLES
   ========================================================================== */
.card-header { padding: 16px 24px; background: var(--bg-body); border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.table-responsive { width: 100%; overflow-x: auto; border-radius: 0 0 12px 12px; }
.table { width: 100%; border-collapse: separate; border-spacing: 0; }
.table th { background: #f8fafc; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; padding: 16px 20px; text-align: left; border-bottom: 2px solid var(--border-color); white-space: nowrap; }
.table td { padding: 16px 20px; border-bottom: 1px solid var(--border-color); vertical-align: middle; color: var(--text-primary); font-size: 0.95rem; }

/* Column Width Helpers */
.col-tight { width: 1%; white-space: nowrap; }
.col-auto { width: auto; }
.col-action { width: 140px; text-align: right; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-muted { color: var(--text-secondary); }
.font-mono { font-family: monospace; }
.bold { font-weight: 600; }

/* Badges */
.badge-brand { background: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
.badge-mode { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid transparent; display: inline-flex; justify-content: center; }
.badge-mode.VIN { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.badge-mode.INTERNAL_ID { background: #e0f2fe; color: #075985; border-color: #bae6fd; }
.badge-mode.BATCH { background: #ffedd5; color: #9a3412; border-color: #fed7aa; }
.badge-purple { background: #f3e8ff; color: #7e22ce; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-blue { background: #eff6ff; color: #1d4ed8; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

/* ==========================================================================
   MODAL STYLES
   ========================================================================== */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-dialog { background: var(--bg-card); width: 100%; max-width: 500px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column; max-height: 90vh; animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.modal-dialog.wide-dialog { max-width: 900px; height: 650px; }
.modal-header { padding: 20px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: flex-start; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 700; color: var(--text-primary); }
.btn-close { background: transparent; border: none; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background 0.2s; }
.btn-close:hover { background: #f1f5f9; }
.close-icon { font-size: 1.5rem; line-height: 1; color: var(--text-secondary); }
.modal-body { padding: 24px; overflow-y: auto; flex: 1; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 0.9rem; color: var(--text-primary); }
.required { color: #ef4444; margin-left: 2px; }
.helper-text { display: block; margin-top: 6px; font-size: 0.8rem; color: var(--text-secondary); }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-body); font-size: 0.95rem; color: var(--text-primary); transition: all 0.2s; box-sizing: border-box; }
.form-input:focus, .form-select:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.row-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* Radio Cards */
.tracking-options { display: flex; flex-direction: column; gap: 10px; }
.radio-card { display: flex; align-items: center; gap: 12px; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; transition: all 0.2s; }
.radio-card:hover { background: #f8fafc; }
.radio-card.active { border-color: var(--primary-color); background: #eff6ff; }
.radio-content { display: flex; flex-direction: column; }
.radio-title { font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.radio-desc { font-size: 0.8rem; color: var(--text-secondary); }

/* Toggle */
.toggle-group { display: flex; gap: 12px; align-items: flex-start; padding: 16px; background: #f8fafc; border-radius: 8px; border: 1px dashed var(--border-color); }
.toggle-group.compact { padding: 0; border: none; background: none; margin-top: 8px; align-items: center; }
.toggle-switch { position: relative; display: inline-block; width: 44px; height: 24px; flex-shrink: 0; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .4s; border-radius: 24px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--primary-color); }
input:checked + .slider:before { transform: translateX(20px); }
.toggle-label { display: flex; flex-direction: column; font-size: 0.9rem; }

.modal-footer { padding: 20px 24px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 12px; background: var(--bg-body); border-radius: 0 0 16px 16px; }

/* Buttons */
.btn-sm { padding: 8px 16px; font-size: 0.85rem; }
.btn-primary { background: var(--primary-color); color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-ghost { background: transparent; color: var(--text-secondary); border: none; padding: 10px 20px; font-weight: 600; cursor: pointer; }
.btn-ghost:hover { background: rgba(0,0,0,0.05); border-radius: 8px; color: var(--text-primary); }
.btn-config { background: white; border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: 0.2s; }
.btn-config:hover { border-color: var(--primary-color); color: var(--primary-color); box-shadow: 0 2px 4px rgba(0,0,0,0.05); }

/* Config Grid */
.config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; height: 100%; }
.config-panel { background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px dashed var(--border-color); padding-bottom: 8px; }
.panel-header h4 { margin: 0; font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }
.badge-count { background: #e2e8f0; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); }
.input-group-row { display: flex; gap: 8px; margin-bottom: 12px; }
.w-20 { width: 80px; text-align: center; }
.btn-add { background: #10b981; color: white; border: none; width: 40px; border-radius: 8px; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.btn-add:hover { background: #059669; }
.styled-list { list-style: none; padding: 0; margin: 0; flex: 1; overflow-y: auto; }
.styled-list li { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: white; border: 1px solid var(--border-color); border-radius: 8px; margin-bottom: 8px; transition: 0.2s; }
.styled-list li:hover { border-color: #cbd5e1; transform: translateX(2px); }
.item-text { font-weight: 500; font-size: 0.9rem; color: var(--text-primary); }
.code-tag { font-family: monospace; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; margin-left: 8px; }
.btn-remove { background: none; border: none; color: #cbd5e1; font-size: 1.2rem; cursor: pointer; transition: 0.2s; }
.btn-remove:hover { color: #ef4444; }
.empty-state { padding: 20px; text-align: center; color: var(--text-secondary); font-style: italic; font-size: 0.9rem; }

/* Animation */
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>