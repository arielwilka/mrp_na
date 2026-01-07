<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>🛠️ {{ isEdit ? 'Edit Rule' : 'Buat Rule Baru' }}</h2>
          <p>Konfigurasi pola validasi (segments).</p>
        </div>
        <button @click="router.back()" class="btn-secondary">&larr; Kembali</button>
      </div>
    </div>

    <form @submit.prevent="saveRule">
      <div class="card mb-6">
        <div class="card-header"><h3>Informasi Rule</h3></div>
        <div class="card-body grid-2-col">
          <div class="form-group">
            <label>Kode Rule (Unik)</label>
            <input v-model="form.code" type="text" required placeholder="Ex: R-BAT-V1" />
          </div>
          <div class="form-group">
            <label>Nama Rule</label>
            <input v-model="form.name" type="text" required placeholder="Ex: Rule Baterai 2026" />
          </div>
          <div class="form-group col-span-2">
            <label>Deskripsi</label>
            <input v-model="form.description" type="text" placeholder="Keterangan tambahan..." />
          </div>
        </div>
      </div>

      <div class="card mb-6">
        <div class="card-header flex justify-between items-center">
          <h3>Pattern Segments</h3>
          <button type="button" @click="addSegment" class="btn-sm bg-green">+ Tambah Segmen</button>
        </div>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th width="50">No</th>
                <th>Tipe Validasi</th>
                <th width="100">Start Idx</th>
                <th width="100">Panjang</th>
                <th>Nilai Statis (Jika Static)</th>
                <th width="60" class="text-right">Hapus</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(seg, idx) in form.segments" :key="idx">
                <td class="text-center font-bold text-muted">{{ idx + 1 }}</td>
                <td>
                  <select v-model="seg.segment_type" class="input-flat">
                    <option value="STATIC">STATIC (Teks Tetap)</option>
                    <option value="DIGIT">DIGIT (Angka)</option>
                    <option value="CHAR">CHAR (Huruf)</option>
                    <option value="ALPHANUM">ALPHANUM</option>
                    <option value="YEAR">YEAR (Tahun 2 Digit)</option>
                    <option value="MONTH">MONTH (Bulan 2 Digit)</option>
                  </select>
                </td>
                <td>
                  <input v-model.number="seg.start_index" type="number" placeholder="Auto" class="input-flat text-center" />
                </td>
                <td>
                  <input v-model.number="seg.length" type="number" min="1" class="input-flat text-center" />
                </td>
                <td>
                  <input v-model="seg.static_value" type="text" :disabled="seg.segment_type !== 'STATIC'"
                    :class="{'bg-gray-100': seg.segment_type !== 'STATIC'}" class="input-flat" 
                    placeholder="Contoh: BAT" />
                </td>
                <td class="text-right">
                  <button type="button" @click="removeSegment(idx)" class="btn-icon danger">×</button>
                </td>
              </tr>
              <tr v-if="form.segments.length === 0">
                <td colspan="6" class="text-center py-6 text-muted">Klik "+ Tambah Segmen" untuk memulai.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex gap-3 justify-end">
        <button v-if="isEdit" type="button" @click="showTest = true" class="btn-secondary border-purple text-purple">🧪 Simulasi Test</button>
        <button type="submit" class="btn-primary">Simpan Rule</button>
      </div>
    </form>

    <div v-if="showTest" class="modal-overlay" @click.self="showTest = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3>🧪 Simulasi Validator</h3>
          <button @click="showTest = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Scan Input (Barcode)</label>
            <input v-model="testInput" type="text" placeholder="Scan disini..." @keyup.enter="runTest" />
          </div>
          
          <div v-if="testRes" :class="`p-4 rounded border ${testRes.status === 'OK' ? 'bg-green-50 border-green-200 text-green-800' : 'bg-red-50 border-red-200 text-red-800'}`">
            <strong class="block mb-1">{{ testRes.status === 'OK' ? '✅ VALID' : '❌ INVALID' }}</strong>
            <span class="text-sm">{{ testRes.message }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="runTest" class="btn-primary w-full">Cek Validasi</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../api';
import type { Rule } from '@/types/traceability';

const route = useRoute();
const router = useRouter();
const isEdit = computed(() => !!route.params.id);
const showTest = ref(false);
const testInput = ref('');
const testRes = ref<any>(null);

const form = reactive<Rule>({ code: '', name: '', description: '', segments: [] });

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await api.getRule(Number(route.params.id));
    Object.assign(form, data);
  } else {
    addSegment();
  }
});

const addSegment = () => form.segments.push({ order: 0, segment_type: 'STATIC', length: 1, static_value: '' });
const removeSegment = (i: number) => form.segments.splice(i, 1);

const saveRule = async () => {
  form.segments.forEach((s, i) => s.order = i + 1);
  try {
    if (isEdit.value) await api.updateRule(Number(route.params.id), form);
    else await api.createRule(form);
    router.push('/traceability/rules');
  } catch (e) { alert('Gagal menyimpan rule.'); }
};

const runTest = async () => {
  if (!testInput.value) return;
  try {
    const { data } = await api.testValidate(Number(route.params.id), testInput.value);
    testRes.value = data;
  } catch (e: any) {
    testRes.value = e.response?.data || { status: 'FAIL', message: 'Error System' };
  }
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
.form-group input, .form-group select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; }
.input-flat { width: 100%; padding: 6px; border: 1px solid transparent; border-radius: 4px; background: transparent; transition: all 0.2s; }
.input-flat:hover, .input-flat:focus { border-color: #cbd5e1; background: white; }
.btn-primary { background: #2563eb; color: white; padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }
.btn-sm { padding: 6px 12px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: none; color: white; }
.btn-icon { width: 28px; height: 28px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; color: #ef4444; }
.btn-close { background: none; border: none; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); display: flex; justify-content: center; align-items: center; z-index: 50; backdrop-filter: blur(2px); }
.modal-card { background: white; width: 90%; max-width: 400px; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }
.modal-header { padding: 16px 24px; background: white; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.modal-body { padding: 24px; }
.modal-footer { padding: 16px 24px; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.col-span-2 { grid-column: span 2; }
.bg-green { background-color: #16a34a; }
.bg-gray-100 { background-color: #f3f4f6; }
.mb-6 { margin-bottom: 24px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.items-center { align-items: center; }
.gap-3 { gap: 12px; }
.w-full { width: 100%; }
.border-purple { border: 1px solid #d8b4fe; }
.text-purple { color: #7e22ce; }
</style>