<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>{{ isEdit ? 'Edit Part' : 'Tambah Part Baru' }}</h2>
          <p>Detail informasi komponen dan aturan validasi.</p>
        </div>
        <button @click="router.back()" class="btn-secondary">&larr; Kembali</button>
      </div>
    </div>

    <form @submit.prevent="save">
      <div class="card max-w-2xl">
        <div class="card-header"><h3>Form Part Data</h3></div>
        <div class="card-body">
          
          <div class="form-group">
            <label>Part Number (SKU) <span class="text-red-500">*</span></label>
            <input v-model="form.part_number" type="text" required class="input" placeholder="Ex: 31500-K0J-N01" />
          </div>

          <div class="form-group">
            <label>Nama Part <span class="text-red-500">*</span></label>
            <input v-model="form.part_name" type="text" required class="input" placeholder="Ex: BATTERY ASSY" />
          </div>

          <div class="form-group">
            <label>Aturan Validasi (Barcode Rule)</label>
            <select v-model="form.validation_rule" class="input">
              <option :value="null">-- Tanpa Validasi (Scan Bebas) --</option>
              <option v-for="rule in rules" :key="rule.id" :value="rule.id">
                {{ rule.code }} - {{ rule.name }}
              </option>
            </select>
            <small class="text-muted block mt-1">Jika kosong, part ini bisa discan dengan barcode apapun.</small>
          </div>

          <div class="form-group">
            <label>Supplier / Vendor</label>
            <input v-model="form.supplier" type="text" class="input" place
            holder="Ex: PT. GS Battery" />
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

const form = reactive<Part>({ part_number: '', part_name: '', validation_rule: null });
const rules = ref<Rule[]>([]);

onMounted(async () => {
  try {
    // 1. Load Dropdown Rules
    const ruleRes = await api.getRules();
    
    // --- PERBAIKAN LOGIC DATA (Handling Pagination) ---
    const rawData = ruleRes.data;
    if (Array.isArray(rawData)) {
        rules.value = rawData;
    } else {
        // Jika format { results: [...] }
        rules.value = rawData['results'] || []; 
    }

    // 2. Load Data Part (Jika Mode Edit)
    if (isEdit.value) {
      const { data } = await api.getPart(Number(route.params.id));
      Object.assign(form, data);
    }
  } catch (err) {
    console.error("Gagal memuat data:", err);
  }
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
/* Gunakan Style Global yang sama */
.master-page { padding: 24px; max-width: 1000px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 16px 24px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.card-header h3 { margin: 0; font-size: 1.1rem; color: #334155; }
.card-body { padding: 24px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 500; font-size: 0.9rem; color: #334155; }
.input { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; }
.btn-primary { background: #2563eb; color: white; padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.items-center { align-items: center; }
.text-red-500 { color: #ef4444; }
.text-muted { color: #94a3b8; }
.max-w-2xl { max-width: 672px; }
</style>