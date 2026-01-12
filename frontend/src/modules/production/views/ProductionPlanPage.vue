<template>
  <div class="master-page">
    <div class="header">
      <div>
        <h2>📅 Production Planning</h2>
        <p>Kelola rencana produksi, varian, dan warna.</p>
      </div>
      <button @click="openModal" class="btn-primary">+ Buat Plan Baru</button>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Kode Plan</th>
              <th>Produk</th>
              <th class="text-center">Warna</th> <th class="text-center">Periode</th>
              <th class="text-center">Target</th>
              <th class="text-center">Progress</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in plans" :key="p.id">
              <td class="font-mono font-bold text-primary">{{ p.plan_code }}</td>
              <td>
                <div class="font-bold">{{ p.product_name }}</div>
                <div class="text-xs text-muted">{{ p.description || '-' }}</div>
              </td>
              <td class="text-center">
                 <span class="badge-color">{{ p.color_name }}</span>
              </td>
              <td class="text-center text-sm">
                 <div>{{ formatDate(p.start_date) }}</div>
                 <div class="text-xs text-muted">s/d {{ formatDate(p.end_date) }}</div>
              </td>
              <td class="text-center">
                <span class="badge-qty">{{ p.target_qty }}</span>
              </td>
              <td class="text-center">
                <div class="progress-wrapper">
                    <div class="progress-bar" :style="{ width: Math.min((p.realized_qty / p.target_qty * 100), 100) + '%' }"></div>
                    <span class="progress-text">{{ p.realized_qty }} / {{ p.target_qty }}</span>
                </div>
              </td>
              <td class="text-right">
                <button @click="deletePlan(p.id)" class="btn-icon danger" title="Hapus Plan">🗑️</button>
              </td>
            </tr>
            <tr v-if="plans.length === 0">
                <td colspan="7" class="text-center py-8 text-muted">Belum ada planning aktif.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isOpen" class="modal-backdrop" @click.self="isOpen = false">
      <div class="modal-dialog">
        <div class="modal-header"><h3>Buat Production Plan</h3></div>
        <div class="modal-body">
            
            <div class="form-group">
                <label>Kode Plan (Auto/Manual)</label>
                <input v-model="form.plan_code" placeholder="PLN-YYYY-XXX" class="form-input uppercase font-mono" />
            </div>

            <div class="form-group">
                <label>Pilih Tipe Produk <span class="text-red-500">*</span></label>
                <select v-model="selectedType" @change="onTypeChange" class="form-select">
                    <option :value="null" disabled>-- Pilih Tipe --</option>
                    <option v-for="t in productTypes" :key="t.id" :value="t.id">{{ t.name }}</option>
                </select>
            </div>

            <div class="grid-2-col">
                <div class="form-group">
                    <label>Varian <span class="text-red-500">*</span></label>
                    <select v-model="form.product_variant" :disabled="!selectedType" class="form-select">
                        <option :value="null">-- Pilih Varian --</option>
                        <option v-for="v in variants" :key="v.id" :value="v.id">{{ v.name }}</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Warna <span class="text-red-500">*</span></label>
                    <select v-model="form.color" :disabled="!selectedType" class="form-select">
                        <option :value="null">-- Pilih Warna --</option>
                        <option v-for="c in colors" :value="c.id" :key="c.id">{{ c.name }} ({{ c.code }})</option>
                    </select>
                </div>
            </div>

            <div class="grid-2-col">
                <div class="form-group">
                    <label>Tanggal Mulai</label>
                    <input type="date" v-model="form.start_date" class="form-input" />
                </div>
                <div class="form-group">
                    <label>Tanggal Selesai</label>
                    <input type="date" v-model="form.end_date" class="form-input" />
                </div>
            </div>

            <div class="form-group">
                <label>Target Quantity</label>
                <input type="number" v-model="form.target_qty" class="form-input text-center font-bold text-lg" min="1" />
            </div>

            <div class="form-group">
                <label>Keterangan</label>
                <textarea v-model="form.description" class="form-input" rows="2"></textarea>
            </div>

        </div>
        <div class="modal-footer">
            <button @click="isOpen = false" class="btn-ghost">Batal</button>
            <button @click="save" class="btn-primary" :disabled="isSubmitting">Simpan Plan</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';

// State Data
const plans = ref<any[]>([]);
const productTypes = ref<any[]>([]);
const variants = ref<any[]>([]);
const colors = ref<any[]>([]); 

// State UI
const selectedType = ref<number | null>(null);
const isOpen = ref(false);
const isLoading = ref(false);
const isSubmitting = ref(false);

// Form Data
const form = reactive({
    plan_code: '',
    product_variant: null as number | null,
    color: null as number | null,
    target_qty: 100,
    start_date: new Date().toISOString().slice(0, 10),
    end_date: new Date().toISOString().slice(0, 10),
    description: ''
});

onMounted(() => {
    loadData();
});

const loadData = async () => {
    isLoading.value = true;
    try {
        // Load Plan & Product Type saja di awal
        const [planRes, typeRes] = await Promise.all([
            api.getPlans(),
            api.getProductTypes()
        ]);

        plans.value = planRes.data.results || planRes.data || [];
        productTypes.value = typeRes.data.results || typeRes.data || [];
    } catch (e) {
        console.error("Gagal load data", e);
    } finally {
        isLoading.value = false;
    }
};

// [LOGIC PENTING] Load Varian & Warna saat Tipe Dipilih
const onTypeChange = async () => {
    variants.value = [];
    colors.value = [];
    form.product_variant = null;
    form.color = null;
    
    if(selectedType.value) {
        try {
            // Load Varian & Warna secara paralel berdasarkan ID Tipe
            const [varRes, colRes] = await Promise.all([
                api.getVariants(selectedType.value),
                api.getColors(selectedType.value)
            ]);
            
            variants.value = varRes.data.results || varRes.data || [];
            colors.value = colRes.data.results || colRes.data || [];
        } catch (e) {
            console.error("Gagal load dependencies", e);
        }
    }
};

const openModal = () => {
    // Generate Random Auto Code sementara
    form.plan_code = `PLN-${new Date().getFullYear()}-${Math.floor(Math.random()*1000).toString().padStart(3, '0')}`;
    
    // Reset Form
    form.product_variant = null;
    form.color = null;
    form.target_qty = 100;
    form.description = '';
    
    selectedType.value = null;
    variants.value = [];
    colors.value = [];
    
    isOpen.value = true;
};

const save = async () => {
    if(!form.product_variant) return alert("Pilih Varian Produk!");
    if(!form.color) return alert("Pilih Warna Produk!"); 

    isSubmitting.value = true;
    try {
        await api.createPlan(form);
        isOpen.value = false;
        loadData(); 
    } catch(e:any) { 
        alert("Gagal simpan: " + (e.response?.data?.detail || JSON.stringify(e.response?.data) || "Error Server")); 
    } finally {
        isSubmitting.value = false;
    }
};

const deletePlan = async (id: number) => {
    if(confirm("Hapus plan ini? Data order terkait mungkin akan error.")) { 
        try {
            await api.deletePlan(id); 
            loadData(); 
        } catch(e:any) {
            alert("Gagal hapus: " + (e.response?.data?.detail || "Error Server"));
        }
    }
};

const formatDate = (dateStr: string) => {
    if(!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: '2-digit' });
};
</script>

<style scoped>
/* Reuse Global Styles */
.master-page { padding: 24px; max-width: 1100px; margin: 0 auto; color: #1e293b; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; font-size: 1.5rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
.table td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }

.badge-qty { background: #eff6ff; color: #1e40af; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
.badge-color { background: #f3f4f6; color: #374151; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; border: 1px solid #e5e7eb; }

.progress-wrapper { background: #f1f5f9; height: 20px; border-radius: 10px; width: 120px; margin: 0 auto; position: relative; overflow: hidden; }
.progress-bar { background: #10b981; height: 100%; transition: width 0.3s; }
.progress-text { position: absolute; top: 0; left: 0; width: 100%; text-align: center; font-size: 0.7rem; line-height: 20px; color: #334155; font-weight: bold; text-shadow: 0 0 2px white; }

/* Modal */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(2px); display: flex; justify-content: center; align-items: center; z-index: 50; }
.modal-dialog { background: white; width: 90%; max-width: 500px; border-radius: 12px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.modal-header { margin-bottom: 20px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }
.modal-header h3 { margin: 0; font-size: 1.2rem; }
.modal-footer { margin-top: 24px; padding-top: 16px; border-top: 1px solid #f1f5f9; display: flex; justify-content: flex-end; gap: 10px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; }
.form-input, .form-select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
.form-select:disabled { background-color: #f1f5f9; cursor: not-allowed; }

.btn-primary { background: #2563eb; color: white; padding: 10px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }
.btn-primary:hover { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

.btn-ghost { background: transparent; color: #64748b; padding: 10px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }
.btn-ghost:hover { background: #f1f5f9; }

.btn-icon { width: 30px; height: 30px; border-radius: 6px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-icon:hover { background: #fee2e2; border-color: #ef4444; }

.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.text-primary { color: #2563eb; }
.text-muted { color: #64748b; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-red-500 { color: #ef4444; }
.text-sm { font-size: 0.85rem; }
</style>