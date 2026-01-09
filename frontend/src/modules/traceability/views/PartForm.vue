<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>{{ isEdit ? 'Edit Part' : 'Tambah Part Baru' }}</h2>
          <p>Detail informasi komponen, aturan validasi, dan konfigurasi stok.</p>
        </div>
        <button @click="router.back()" class="btn-secondary">&larr; Kembali</button>
      </div>
    </div>

    <form @submit.prevent="save">
      <div class="card max-w-3xl">
        <div class="card-header"><h3>Form Part Data</h3></div>
        <div class="card-body">
          
          <div class="grid-2-col">
            <div class="form-group">
                <label>Part Number (SKU) <span class="text-red">*</span></label>
                <input v-model="form.part_number" type="text" required class="form-input font-mono" placeholder="Ex: 31500-K0J-N01" />
            </div>
            <div class="form-group">
                <label>Nama Part <span class="text-red">*</span></label>
                <input v-model="form.part_name" type="text" required class="form-input" placeholder="Ex: BATTERY ASSY" />
            </div>
          </div>

          <div class="form-group">
            <label>Aturan Validasi (Barcode Rule)</label>
            <select v-model="form.validation_rule" class="form-select">
              <option :value="null">-- Tanpa Validasi (Scan Bebas) --</option>
              <option v-for="rule in rules" :key="rule.id" :value="rule.id">
                {{ rule.code }} - {{ rule.name }}
              </option>
            </select>
            <small class="text-muted">Menentukan format barcode yang valid saat discan.</small>
          </div>

          <div class="grid-2-col my-4">
            <label class="config-card">
                <div class="flex items-start">
                    <input type="checkbox" v-model="form.is_qc_required" class="mt-1 mr-3" />
                    <div>
                        <span class="font-bold text-slate-700">Wajib QC (Receiving)</span>
                        <p class="text-sm text-muted mt-1">Barang masuk harus via inspeksi QC sebelum stok menjadi Available.</p>
                    </div>
                </div>
            </label>

            <label class="config-card">
                <div class="flex items-start">
                    <input type="checkbox" v-model="form.is_unique_serial" class="mt-1 mr-3" />
                    <div>
                        <span class="font-bold text-slate-700">Serial Number Unik</span>
                        <p class="text-sm text-muted mt-1">Sistem akan menolak jika ada SN yang sama persis dalam database.</p>
                    </div>
                </div>
            </label>
          </div>

          <div class="form-group">
            <label>Supplier / Vendor</label>
            <input v-model="form.supplier" type="text" class="form-input" placeholder="Ex: PT. GS Battery" />
          </div>

          <div class="flex justify-end pt-4 border-t mt-6">
             <button type="submit" class="btn-primary">Simpan Part</button>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import type { Part, Rule } from '@/types/traceability';

const route = useRoute();
const router = useRouter();
const isEdit = computed(() => !!route.params.id);

const form = reactive<Part>({ 
  part_number: '', part_name: '', validation_rule: null,
  is_qc_required: true, is_unique_serial: true, supplier: ''
});

const rules = ref<Rule[]>([]);

onMounted(async () => {
  try {
    const ruleRes = await api.getRules();
    const rawData = ruleRes.data;
    rules.value = Array.isArray(rawData) ? rawData : (rawData['results'] || []); 

    if (isEdit.value) {
      const { data } = await api.getPart(Number(route.params.id));
      Object.assign(form, data);
    }
  } catch (err) { console.error(err); }
});

const save = async () => {
  try {
    if (isEdit.value) await api.updatePart(Number(route.params.id), form);
    else await api.createPart(form);
    router.push('/traceability/parts');
  } catch (e) { alert('Error saat menyimpan data.'); }
};
</script>

<style scoped>
.master-page { padding: 24px; max-width: 1000px; margin: 0 auto; }
.header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: var(--text-secondary); }

.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: var(--shadow-sm); overflow: hidden; }
.card-header { padding: 16px 24px; background: #f8fafc; border-bottom: 1px solid var(--border-color); }
.card-header h3 { margin: 0; font-size: 1.1rem; color: var(--text-primary); font-weight: 600; }
.card-body { padding: 24px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.95rem; box-sizing: border-box; }
.form-input:focus, .form-select:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

.config-card { display: block; padding: 16px; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; transition: 0.2s; background: #f8fafc; }
.config-card:hover { border-color: var(--primary-color); background: #eff6ff; }
.config-card input { width: 18px; height: 18px; }

.btn-primary { background: var(--primary-color); color: white; padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.2s; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-secondary { background: white; color: var(--text-secondary); padding: 8px 16px; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; font-weight: 500; }
.btn-secondary:hover { background: #f1f5f9; color: var(--text-primary); }

.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.text-red { color: #ef4444; }
.text-muted { color: var(--text-secondary); }
.max-w-3xl { max-width: 800px; }
.my-4 { margin-top: 16px; margin-bottom: 16px; }
.mr-3 { margin-right: 12px; }
.mt-1 { margin-top: 4px; }
.pt-4 { padding-top: 16px; }
.border-t { border-top: 1px solid var(--border-color); }
.font-mono { font-family: monospace; }
</style>