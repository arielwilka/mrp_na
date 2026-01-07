<template>
  <div class="master-page">
    
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📑 Form BOM Version</h2>
          <p>{{ isEdit ? 'Edit Versi BOM' : 'Buat Versi BOM Baru' }} untuk Traceability.</p>
        </div>
        <button @click="router.back()" class="btn-secondary">
          &larr; Kembali
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div> Memuat Data...
    </div>

    <form v-else @submit.prevent="save" class="fade-in">
      
      <div class="card mb-6">
        <div class="card-header">
          <h3>Informasi Versi</h3>
        </div>
        <div class="card-body grid-2-col">
          
          <div class="form-group">
            <label>Tipe Produk (FG) <span class="text-red-500">*</span></label>
            <select v-model="form.product_type" required>
              <option :value="null" disabled>-- Pilih Produk --</option>
              <option v-for="p in products" :key="p.id" :value="p.id">
                {{ p.name }} ({{ p.code }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Kode Versi <span class="text-red-500">*</span></label>
            <input v-model="form.version_code" type="text" placeholder="Contoh: V1.0-JAN2026" required />
          </div>

          <div class="form-group">
            <label>Berlaku Mulai <span class="text-red-500">*</span></label>
            <input v-model="form.valid_from" type="date" required />
          </div>

          <div class="form-group checkbox-wrapper">
             <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" v-model="form.is_active">
                    <div>
                        <strong>Set sebagai Versi AKTIF</strong>
                        <small>Versi aktif lain untuk produk ini akan otomatis non-aktif.</small>
                    </div>
                </label>
            </div>
          </div>

        </div>
      </div>

      <div class="card mb-6">
        <div class="card-header flex justify-between items-center">
          <h3>Daftar Part Traceability (Requirements)</h3>
          <button type="button" @click="addReq" class="btn-sm bg-green text-white">
            + Tambah Part
          </button>
        </div>
        
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th style="width: 50px">No</th>
                <th>Part Master <span class="text-red-500">*</span></th>
                <th style="width: 120px">Qty / Unit</th>
                <th style="width: 150px" class="text-center">Wajib Scan?</th>
                <th style="width: 80px" class="text-right">Hapus</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(req, index) in form.requirements" :key="index">
                <td class="text-center font-bold text-muted">{{ index + 1 }}</td>
                
                <td>
                  <select v-model="req.part_master" required class="input-flat">
                    <option :value="null">-- Pilih Part --</option>
                    <option v-for="part in partsList" :key="part.id" :value="part.id">
                      {{ part.part_number }} - {{ part.part_name }}
                    </option>
                  </select>
                </td>

                <td>
                  <input v-model.number="req.qty" type="number" min="1" class="input-flat text-center" />
                </td>

                <td class="text-center">
                   <label class="toggle-switch">
                      <input type="checkbox" v-model="req.is_mandatory">
                      <span class="slider round"></span>
                   </label>
                   <div class="text-xs mt-1 text-muted">{{ req.is_mandatory ? 'Ya' : 'Opsional' }}</div>
                </td>

                <td class="text-right">
                  <button type="button" @click="removeReq(index)" class="btn-icon danger">×</button>
                </td>
              </tr>
              
              <tr v-if="form.requirements.length === 0">
                <td colspan="5" class="text-center py-6 text-muted italic">
                  Belum ada part yang didaftarkan. Klik tombol "+ Tambah Part".
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex gap-3 justify-end">
        <button type="button" @click="router.back()" class="btn-secondary">Batal</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Menyimpan...' : 'Simpan Perubahan' }}
        </button>
      </div>

    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api'; 
// Pastikan path ini sesuai
import type { Version, Part } from '@/types/traceability';
import type { ProductType } from '@/types/product';

const route = useRoute();
const router = useRouter();
const isEdit = computed(() => !!route.params.id);

const isLoading = ref(false);
const isSubmitting = ref(false);

// Dropdown Data
const products = ref<ProductType[]>([]);
const partsList = ref<Part[]>([]);

// Form State
const form = reactive<Version>({
  product_type: null, 
  version_code: '', 
  // GANTI BARIS INI:
  // valid_from: new Date().toISOString().split('T')[0], 
  
  // MENJADI INI (Ambil 10 karakter pertama: YYYY-MM-DD):
  valid_from: new Date().toISOString().slice(0, 10), 

  is_active: true, 
  requirements: []
});

onMounted(async () => {
  isLoading.value = true;
  try {
    // 1. Load Dropdowns (Product & Parts)
    const [prodRes, partRes] = await Promise.all([
      api.getProductTypes(), 
      api.getParts()
    ]);
    
    // LOGIC FIX: Handle Pagination di Dropdown
    const rawProds = prodRes.data;
    products.value = Array.isArray(rawProds) ? rawProds : (rawProds['results'] || []);

    const rawParts = partRes.data;
    partsList.value = Array.isArray(rawParts) ? rawParts : (rawParts['results'] || []);

    // 2. Load Data if Edit
    if (isEdit.value) {
      const { data } = await api.getVersion(Number(route.params.id));
      form.product_type = data.product_type;
      form.version_code = data.version_code;
      form.valid_from = data.valid_from;
      form.is_active = data.is_active;
      
      form.requirements = data.requirements.map((r: any) => ({
        part_master: r.part_master, 
        qty: r.qty, 
        is_mandatory: r.is_mandatory
      }));
    } else {
        addReq();
    }
  } catch (err) {
    console.error(err);
    alert("Gagal memuat data.");
  } finally {
    isLoading.value = false;
  }
});

const addReq = () => {
  form.requirements.push({ part_master: null, qty: 1, is_mandatory: true });
};

const removeReq = (index: number) => {
  form.requirements.splice(index, 1);
};

const save = async () => {
  if(!form.product_type) return alert("Pilih tipe produk!");
  
  isSubmitting.value = true;
  try {
    if (isEdit.value) {
        await api.updateVersion(Number(route.params.id), form);
    } else {
        await api.createVersion(form);
    }
    router.push('/traceability/bom'); // Redirect ke list page
  } catch (e: any) {
    alert('Error: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data)));
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* --- STYLING MENGACU PADA VIN/PRODUCT MASTER PAGE --- */

.master-page { padding: 24px; max-width: 1000px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 16px 24px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: #334155; }
.card-body { padding: 24px; }

.mb-6 { margin-bottom: 24px; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.gap-3 { gap: 12px; }
.justify-end { justify-content: flex-end; }

/* FORMS */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 500; font-size: 0.9rem; color: #334155; }
.form-group input, .form-group select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; }
.form-group input:focus, .form-group select:focus { border-color: #2563eb; outline: none;  }

/* CHECKBOX GROUP (STYLE SAMA DENGAN VIN MASTER) */
.checkbox-wrapper { display: flex; align-items: flex-end; height: 100%; }
.checkbox-group { border: 1px solid #e2e8f0; padding: 12px; border-radius: 8px; background: #f8fafc; width: 100%; }
.checkbox-label { display: flex; gap: 12px; align-items: flex-start; cursor: pointer; }
.checkbox-label input { margin-top: 4px; width: 16px; height: 16px; }
.checkbox-label div { display: flex; flex-direction: column; }
.checkbox-label small { color: #64748b; font-size: 0.8rem; margin-top: 2px; }

/* TABLE STYLES */
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }

/* INPUT DALAM TABEL (FLAT) */
.input-flat { width: 100%; padding: 6px; border: 1px solid transparent; border-radius: 4px; background: transparent; transition: all 0.2s; }
.input-flat:hover, .input-flat:focus { border-color: #cbd5e1; background: white; }

/* BUTTONS */
.btn-primary { background: #2563eb; color: white; padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 0.95rem; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.btn-sm { padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: none; }
.btn-icon { width: 28px; height: 28px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #64748b; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; color: #ef4444; }
.bg-green { background-color: #16a34a; }

/* TOGGLE SWITCH */
.toggle-switch { position: relative; display: inline-block; width: 34px; height: 20px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(14px); }

/* UTILS */
.text-red-500 { color: #ef4444; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-muted { color: #94a3b8; }
.font-bold { font-weight: 600; }
.italic { font-style: italic; }

.loading-state { text-align: center; padding: 50px; color: #64748b; font-weight: 500; }
.spinner { border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; display: inline-block; margin-right: 10px; vertical-align: middle; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 768px) { .grid-2-col { grid-template-columns: 1fr; } }
</style>