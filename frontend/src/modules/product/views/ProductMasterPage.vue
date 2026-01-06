<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>📦 Master Produk & Kendaraan</h2>
        <p>Kelola data Brand, Tipe, Varian, dan Warna.</p>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'brands' }" @click="activeTab = 'brands'">🏢 Data Brand</button>
      <button :class="{ active: activeTab === 'types' }" @click="activeTab = 'types'">🚙 Tipe & Model</button>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div> Memuat Data...
    </div>

    <div v-else>
      
      <div v-if="activeTab === 'brands'" class="tab-content">
        <div class="card">
          <div class="card-header">
            <h3>Daftar Brand / Merk</h3>
            <button v-if="canCreate" @click="openModal('brand')" class="btn-sm">+ Brand Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead><tr><th>Kode</th><th>Nama Brand</th><th class="text-right">Aksi</th></tr></thead>
              <tbody>
                <tr v-for="b in brands" :key="b.id">
                  <td class="font-mono bold">{{ b.code }}</td>
                  <td>{{ b.name }}</td>
                  <td class="text-right">
                    <button v-if="canDelete" @click="deleteItem('brands', b.id)" class="btn-icon danger">🗑️</button>
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
            <button v-if="canCreate" @click="openModal('type')" class="btn-sm">+ Tipe Baru</button>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Brand</th>
                  <th>Model / Tipe</th>
                  <th>Kode Internal</th>
                  <th class="text-center">VIN Trace</th>
                  <th class="text-center">Check Digit</th>
                  <th class="text-right">Config</th>
                  <th class="text-right">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in types" :key="t.id">
                  <td><span class="badge-brand">{{ t.brand_name }}</span></td>
                  <td><strong>{{ t.name }}</strong></td>
                  <td class="font-mono">{{ t.code }}</td>
                  
                  <td class="text-center">
                    <span v-if="t.is_vin_trace" class="badge-success">✅ Wajib</span>
                    <span v-else class="badge-gray">Non-Trace</span>
                  </td>
                  <td class="text-center">
                    <span v-if="t.has_check_digit" class="badge-info">🧮 Auto (Algo)</span>
                    <span v-else class="badge-warning">Static (0)</span>
                  </td>

                  <td class="text-right">
                    <button @click="openConfigModal(t)" class="btn-config">⚙️ Varian & Warna</button>
                  </td>

                  <td class="text-right">
                    <button v-if="canDelete" @click="deleteItem('types', t.id)" class="btn-icon danger">🗑️</button>
                  </td>
                </tr>
                <tr v-if="types.length === 0"><td colspan="7" class="text-center text-muted">Belum ada data.</td></tr>
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
            <div v-if="modal.type === 'brand'">
                <div class="form-group">
                    <label>Nama Brand</label>
                    <input v-model="form.name" placeholder="Contoh: TOYOTA" />
                </div>
                <div class="form-group">
                    <label>Kode Brand (Singkatan)</label>
                    <input v-model="form.code" placeholder="TYT" class="uppercase" maxlength="10"/>
                </div>
            </div>

            <div v-if="modal.type === 'type'">
                <div class="form-group">
                    <label>Brand</label>
                    <select v-model="form.brand">
                        <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Nama Model</label>
                    <input v-model="form.name" placeholder="Contoh: Fortuner" />
                </div>
                <div class="form-group">
                    <label>Kode Internal</label>
                    <input v-model="form.code" placeholder="FRT-2024" class="uppercase" />
                </div>
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" v-model="form.is_vin_trace">
                        <div><strong>Wajib VIN Trace</strong><small>Produk ini masuk sistem VIN.</small></div>
                    </label>
                </div>
                <div class="checkbox-group">
                    <label class="checkbox-label">
                        <input type="checkbox" v-model="form.has_check_digit">
                        <div><strong>Gunakan Check Digit (Algoritma)</strong><small>Hitung otomatis digit ke-9.</small></div>
                    </label>
                </div>
            </div>
        </div>
        <div class="modal-footer">
           <button @click="modal.isOpen = false" class="btn-secondary">Batal</button>
           <button @click="submitForm" class="btn-primary" :disabled="isSubmitting">Simpan</button>
        </div>
      </div>
    </div>

    <div v-if="configModal.isOpen" class="modal-overlay" @click.self="configModal.isOpen = false">
        <div class="modal-card wide-modal">
            <div class="modal-header">
                <h3>⚙️ Config: {{ configModal.data.name }}</h3>
                <button @click="configModal.isOpen = false" class="btn-close">×</button>
            </div>
            <div class="modal-body grid-2-col">
                <div class="sub-panel">
                    <h4>🏷️ Daftar Varian</h4>
                    <div class="add-row">
                        <input v-model="newVariant" placeholder="Nama Varian (ex: G M/T)" @keyup.enter="addVariant" />
                        <button @click="addVariant" class="btn-add">+</button>
                    </div>
                    <ul class="item-list">
                        <li v-for="v in currentVariants" :key="v.id">
                            <span>{{ v.name }}</span>
                            <button @click="deleteSubItem('variants', v.id)" class="btn-x">×</button>
                        </li>
                        <li v-if="currentVariants.length === 0" class="empty">Belum ada varian.</li>
                    </ul>
                </div>
                <div class="sub-panel">
                    <h4>🎨 Daftar Warna</h4>
                    <div class="add-row">
                        <input v-model="newColorName" placeholder="Nama Warna" class="grow" />
                        <input v-model="newColorCode" placeholder="Kode" class="w-small uppercase" @keyup.enter="addColor" />
                        <button @click="addColor" class="btn-add">+</button>
                    </div>
                    <ul class="item-list">
                        <li v-for="c in currentColors" :key="c.id">
                            <span>{{ c.name }} <small v-if="c.code">({{ c.code }})</small></span>
                            <button @click="deleteSubItem('colors', c.id)" class="btn-x">×</button>
                        </li>
                        <li v-if="currentColors.length === 0" class="empty">Belum ada warna.</li>
                    </ul>
                </div>
            </div>
            <div class="modal-footer">
                <button @click="configModal.isOpen = false" class="btn-primary">Selesai</button>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../../../stores/auth'; // Path relatif dari src/modules/product/views/

const API_URL = 'http://127.0.0.1:8000/api/product';
const authStore = useAuthStore();

// Gunakan permission string yang Anda set di backend, misal 'product' atau 'vin_master'
// Sesuaikan dengan logic permission Anda
const canCreate = computed(() => authStore.can('vin_master', 'create')); 
const canDelete = computed(() => authStore.can('vin_master', 'delete'));

const activeTab = ref('brands');
const isLoading = ref(false);
const brands = ref<any[]>([]);
const types = ref<any[]>([]);

const modal = reactive({ isOpen: false, type: '', title: '' });
const form = reactive<any>({});
const isSubmitting = ref(false);

const configModal = reactive({ isOpen: false, data: {} as any });
const currentVariants = ref<any[]>([]);
const currentColors = ref<any[]>([]);
const newVariant = ref('');
const newColorName = ref('');
const newColorCode = ref('');

onMounted(() => { loadData(); });

const loadData = async () => {
    isLoading.value = true;
    try {
        const [resB, resT] = await Promise.all([
            axios.get(`${API_URL}/brands/`),
            axios.get(`${API_URL}/types/`)
        ]);
        brands.value = Array.isArray(resB.data) ? resB.data : (resB.data.results || []);
        const rawTypes = Array.isArray(resT.data) ? resT.data : (resT.data.results || []);
        
        types.value = rawTypes.map((t: any) => {
            const brand = brands.value.find(b => b.id === t.brand);
            return { ...t, brand_name: brand ? brand.name : '-' };
        });
    } catch(e) { console.error(e); } 
    finally { isLoading.value = false; }
};

const openModal = (type: string) => {
    Object.keys(form).forEach(k => delete form[k]);
    form.is_vin_trace = true; form.has_check_digit = true;
    modal.type = type;
    modal.title = type === 'brand' ? 'Tambah Brand' : 'Tambah Tipe';
    modal.isOpen = true;
};

const submitForm = async () => {
    isSubmitting.value = true;
    try {
        const endpoint = modal.type === 'brand' ? 'brands' : 'types';
        await axios.post(`${API_URL}/${endpoint}/`, form);
        modal.isOpen = false; loadData();
    } catch(e: any) { alert("Gagal: " + (e.response?.data?.detail || "Error")); } 
    finally { isSubmitting.value = false; }
};

const deleteItem = async (ep: string, id: number) => {
    if(!confirm("Yakin hapus?")) return;
    try { await axios.delete(`${API_URL}/${ep}/${id}/`); loadData(); } 
    catch(e) { alert("Gagal hapus (Data terpakai?)"); }
};

const openConfigModal = async (typeObj: any) => {
    configModal.data = typeObj; configModal.isOpen = true;
    newVariant.value = ''; newColorName.value = ''; newColorCode.value = '';
    currentVariants.value = []; currentColors.value = [];
    await loadSubItems(typeObj.id);
};

const loadSubItems = async (typeId: number) => {
    try {
        const [resV, resC] = await Promise.all([
            axios.get(`${API_URL}/variants/?product_type=${typeId}`),
            axios.get(`${API_URL}/colors/?product_type=${typeId}`)
        ]);
        currentVariants.value = Array.isArray(resV.data) ? resV.data : (resV.data.results || []);
        currentColors.value = Array.isArray(resC.data) ? resC.data : (resC.data.results || []);
    } catch(e) { console.error(e); }
};

const addVariant = async () => {
    if(!newVariant.value) return;
    try {
        await axios.post(`${API_URL}/variants/`, { product_type: configModal.data.id, name: newVariant.value });
        newVariant.value = ''; loadSubItems(configModal.data.id);
    } catch(e) { alert("Gagal simpan"); }
};

const addColor = async () => {
    if(!newColorName.value) return;
    try {
        await axios.post(`${API_URL}/colors/`, { product_type: configModal.data.id, name: newColorName.value, code: newColorCode.value });
        newColorName.value = ''; newColorCode.value = ''; loadSubItems(configModal.data.id);
    } catch(e) { alert("Gagal simpan"); }
};

const deleteSubItem = async (ep: string, id: number) => {
    if(!confirm("Hapus?")) return;
    try { await axios.delete(`${API_URL}/${ep}/${id}/`); loadSubItems(configModal.data.id); } catch(e) {}
};
</script>

<style scoped>
.master-page { padding: 20px; max-width: 1100px; margin: 0 auto; }
.header { margin-bottom: 20px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
.header h2 { margin: 0; color: #1e293b; }
.header p { margin: 5px 0 0; color: #64748b; font-size: 0.9rem; }
.tabs { display: flex; gap: 10px; border-bottom: 2px solid #e2e8f0; margin-bottom: 20px; }
.tabs button { padding: 10px 15px; background: none; border: none; font-weight: 600; color: #64748b; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tabs button.active { border-bottom-color: #2563eb; color: #2563eb; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.card-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; }
.badge-brand { background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem; }
.badge-success { background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #bbf7d0; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
.badge-info { background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #bfdbfe; }
.badge-warning { background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; border: 1px solid #fde68a; }
.btn-sm { background: #2563eb; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; }
.btn-config { background: #fff; border: 1px solid #cbd5e1; color: #334155; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
.btn-icon { background: none; border: 1px solid #e2e8f0; width: 30px; height: 30px; border-radius: 4px; cursor: pointer; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-card { background: white; width: 100%; max-width: 450px; border-radius: 8px; overflow: hidden; display: flex; flex-direction: column; max-height: 90vh; animation: popIn 0.2s ease; }
.modal-card.wide-modal { max-width: 800px; height: 500px; }
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal-header { padding: 15px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 20px; overflow-y: auto; }
.modal-footer { padding: 15px 20px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.85rem; color: #475569; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
.checkbox-group { margin-bottom: 10px; border: 1px solid #e2e8f0; padding: 10px; border-radius: 6px; background: #f8fafc; }
.checkbox-label { display: flex; gap: 10px; align-items: flex-start; cursor: pointer; }
.checkbox-label input { margin-top: 4px; }
.checkbox-label div { display: flex; flex-direction: column; }
.checkbox-label small { color: #64748b; font-size: 0.8rem; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; height: 100%; }
.sub-panel { border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; background: #fcfcfc; display: flex; flex-direction: column; }
.sub-panel h4 { margin: 0 0 15px 0; font-size: 0.95rem; color: #475569; padding-bottom: 8px; border-bottom: 1px dashed #e2e8f0; }
.add-row { display: flex; gap: 5px; margin-bottom: 10px; }
.add-row input { padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; flex: 1; }
.add-row .w-small { width: 60px; flex: none; text-align: center; }
.btn-add { background: #16a34a; color: white; border: none; width: 32px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.item-list { list-style: none; padding: 0; margin: 0; flex: 1; overflow-y: auto; border: 1px solid #f1f5f9; border-radius: 4px; background: white; }
.item-list li { display: flex; justify-content: space-between; padding: 8px 10px; border-bottom: 1px solid #f1f5f9; align-items: center; font-size: 0.9rem; }
.item-list li:last-child { border-bottom: none; }
.btn-x { background: none; border: none; color: #ef4444; font-weight: bold; cursor: pointer; padding: 0 5px; }
.btn-primary { background: #2563eb; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-close { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
@media (max-width: 768px) { .grid-2-col { grid-template-columns: 1fr; } .table-responsive table { min-width: 800px; } }
</style>