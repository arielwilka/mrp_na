<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📑 Form BOM Version</h2>
          <p>{{ isEdit ? 'Edit Versi BOM' : 'Buat Versi BOM Baru' }} untuk Traceability.</p>
        </div>
        <button @click="router.back()" class="btn-secondary">&larr; Kembali</button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">Loading...</div>

    <form v-else @submit.prevent="save" class="fade-in">
      <div class="card mb-6">
        <div class="card-header"><h3>Informasi Versi</h3></div>
        <div class="card-body grid-2-col">
          <div class="form-group">
            <label>Tipe Produk (FG) <span class="text-red">*</span></label>
            <select v-model="form.product_type" required class="form-select">
              <option :value="null" disabled>-- Pilih Produk --</option>
              <option v-for="p in products" :key="p.id" :value="p.id">
                {{ p.name }} ({{ p.code }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Kode Versi <span class="text-red">*</span></label>
            <input v-model="form.version_code" type="text" class="form-input" placeholder="Contoh: V1.0-JAN2026" required />
          </div>
          <div class="form-group">
            <label>Berlaku Mulai <span class="text-red">*</span></label>
            <input v-model="form.valid_from" type="date" class="form-input" required />
          </div>
          <div class="form-group checkbox-wrapper">
             <label class="flex items-center cursor-pointer h-full">
                <input type="checkbox" v-model="form.is_active" class="mr-3 h-5 w-5">
                <div>
                    <strong class="text-slate-700">Set sebagai Versi AKTIF</strong>
                    <p class="text-xs text-muted">Versi aktif lain akan otomatis non-aktif.</p>
                </div>
             </label>
          </div>
        </div>
      </div>

      <div class="card mb-6">
        <div class="card-header flex justify-between items-center">
          <h3>Daftar Part Traceability (Requirements)</h3>
          <button type="button" @click="addReq" class="btn-sm btn-primary">+ Tambah Part</button>
        </div>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th width="50">No</th>
                <th>Part Master <span class="text-red">*</span></th>
                <th width="120">Qty / Unit</th>
                <th width="150" class="text-center">Wajib Scan?</th>
                <th width="80" class="text-right">Hapus</th>
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
                </td>
                <td class="text-right">
                  <button type="button" @click="removeReq(index)" class="btn-icon danger text-red">&times;</button>
                </td>
              </tr>
              <tr v-if="form.requirements.length === 0">
                <td colspan="5" class="text-center py-6 text-muted italic">Belum ada part. Klik "+ Tambah Part".</td>
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
import type { Version, Part } from '@/types/traceability';
import type { ProductType } from '@/types/product';

const route = useRoute();
const router = useRouter();
const isEdit = computed(() => !!route.params.id);
const isLoading = ref(false);
const isSubmitting = ref(false);

const products = ref<ProductType[]>([]);
const partsList = ref<Part[]>([]);

const form = reactive<Version>({
  product_type: null, version_code: '', 
  valid_from: new Date().toISOString().slice(0, 10), 
  is_active: true, requirements: []
});

onMounted(async () => {
  isLoading.value = true;
  try {
    const [prodRes, partRes] = await Promise.all([api.getProductTypes(), api.getParts()]);
    
    const rawProds = prodRes.data;
    products.value = Array.isArray(rawProds) ? rawProds : (rawProds['results'] || []);

    const rawParts = partRes.data;
    partsList.value = Array.isArray(rawParts) ? rawParts : (rawParts['results'] || []);

    if (isEdit.value) {
      const { data } = await api.getVersion(Number(route.params.id));
      form.product_type = data.product_type;
      form.version_code = data.version_code;
      form.valid_from = data.valid_from;
      form.is_active = data.is_active;
      form.requirements = data.requirements.map((r: any) => ({
        part_master: r.part_master, qty: r.qty, is_mandatory: r.is_mandatory
      }));
    } else {
        addReq();
    }
  } catch (err) { alert("Gagal memuat data."); } 
  finally { isLoading.value = false; }
});

const addReq = () => form.requirements.push({ part_master: null, qty: 1, is_mandatory: true });
const removeReq = (index: number) => form.requirements.splice(index, 1);

const save = async () => {
  if(!form.product_type) return alert("Pilih tipe produk!");
  isSubmitting.value = true;
  try {
    if (isEdit.value) await api.updateVersion(Number(route.params.id), form);
    else await api.createVersion(form);
    router.push('/traceability/bom');
  } catch (e: any) {
    alert('Error: ' + (e.response?.data?.detail || JSON.stringify(e.response?.data)));
  } finally { isSubmitting.value = false; }
};
</script>

<style scoped>
/* Gunakan Style yang sama dengan PartForm */
.master-page { padding: 24px; max-width: 1000px; margin: 0 auto; color: var(--text-primary); }
.header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: var(--text-secondary); }

.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: var(--shadow-sm); overflow: hidden; }
.card-header { padding: 16px 24px; background: #f8fafc; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: var(--text-primary); font-weight: 600; }
.card-body { padding: 24px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; }

.input-flat { width: 100%; padding: 8px; border: 1px solid transparent; border-radius: 6px; background: transparent; transition: 0.2s; }
.input-flat:hover, .input-flat:focus { border-color: var(--border-color); background: white; }

.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 10px 16px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.75rem; text-transform: uppercase; color: var(--text-secondary); }
.table td { padding: 10px 16px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }

.btn-primary { background: var(--primary-color); color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; }
.btn-secondary { background: white; border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 8px; cursor: pointer; color: var(--text-secondary); }
.btn-sm { padding: 6px 12px; font-size: 0.8rem; }
.btn-icon { width: 28px; height: 28px; background: transparent; border: none; cursor: pointer; font-size: 1.2rem; }

.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.checkbox-wrapper { display: flex; align-items: center; background: #f8fafc; border: 1px solid var(--border-color); padding: 10px; border-radius: 8px; }
.text-red { color: #ef4444; }
.mb-6 { margin-bottom: 24px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.gap-3 { gap: 12px; }

/* Toggle Switch */
.toggle-switch { position: relative; display: inline-block; width: 34px; height: 20px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 14px; width: 14px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--primary-color); }
input:checked + .slider:before { transform: translateX(14px); }
</style>