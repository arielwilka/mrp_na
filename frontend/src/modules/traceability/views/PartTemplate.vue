<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📋 QC Parameters</h2>
          <p>Atur poin-poin pemeriksaan untuk part: <strong>{{ partName }}</strong></p>
        </div>
        <button @click="$router.push('/traceability/parts')" class="btn-secondary">&larr; Kembali ke Part List</button>
      </div>
    </div>

    <div class="grid-layout">
      
      <div class="left-col">
        <div class="card">
          <div class="card-header">
            <h3>+ Tambah Parameter Baru</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="addTemplate">
              
              <div class="form-group">
                <label>Label (Pertanyaan) <span class="text-red">*</span></label>
                <input v-model="form.field_label" type="text" class="input" placeholder="Contoh: Tegangan Baterai" required />
              </div>

              <div class="form-group">
                <label>Key (Variable) <span class="text-red">*</span></label>
                <input v-model="form.field_key" type="text" class="input font-mono" placeholder="Contoh: voltage_val" required />
                <small class="text-muted">Gunakan huruf kecil & underscore (_). Tanpa spasi.</small>
              </div>

              <div class="form-group">
                <label>Tipe Input</label>
                <select v-model="form.field_type" class="input">
                  <option value="NUMBER">Angka (Pengukuran)</option>
                  <option value="TEXT">Teks Bebas</option>
                  <option value="BOOLEAN">Pilihan (OK / NG)</option>
                  <option value="IMAGE">Upload Foto</option>
                </select>
              </div>

              <div v-if="form.field_type === 'NUMBER'" class="p-3 bg-slate-50 border rounded mb-4">
                <p class="text-sm font-bold mb-2 text-slate-700">Batasan Nilai (Range)</p>
                <div class="flex gap-2">
                  <div class="w-full">
                    <label class="text-xs">Min</label>
                    <input v-model.number="form.min_val" type="number" step="0.01" class="input" />
                  </div>
                  <div class="w-full">
                    <label class="text-xs">Max</label>
                    <input v-model.number="form.max_val" type="number" step="0.01" class="input" />
                  </div>
                </div>
              </div>

              <div class="form-group mt-4">
                <label class="flex items-center cursor-pointer">
                  <input type="checkbox" v-model="form.is_mandatory" class="mr-2" />
                  <span>Wajib Diisi? (Mandatory)</span>
                </label>
              </div>

              <div class="pt-4 border-t">
                <button type="submit" class="btn-primary w-full" :disabled="isSubmitting">Simpan Parameter</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div class="right-col">
        <div class="card h-full">
          <div class="card-header">
            <h3>Daftar Parameter Aktif</h3>
          </div>
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Label</th>
                  <th>Key</th>
                  <th>Type</th>
                  <th>Range</th>
                  <th>Wajib?</th>
                  <th class="text-right">Aksi</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tpl in templates" :key="tpl.id">
                  <td class="font-bold">{{ tpl.field_label }}</td>
                  <td class="font-mono text-sm">{{ tpl.field_key }}</td>
                  <td>
                    <span class="badge badge-blue">{{ tpl.field_type }}</span>
                  </td>
                  <td>
                    <span v-if="tpl.field_type === 'NUMBER'" class="text-sm">
                      {{ tpl.min_val }} - {{ tpl.max_val }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span v-if="tpl.is_mandatory" class="badge badge-red">YES</span>
                    <span v-else class="badge badge-gray">OPT</span>
                  </td>
                  <td class="text-right">
                    <button @click="deleteItem(tpl.id)" class="btn-icon danger" title="Hapus">🗑️</button>
                  </td>
                </tr>
                <tr v-if="templates.length === 0">
                  <td colspan="6" class="text-center py-8 text-muted">Belum ada parameter. Part ini akan lolos QC tanpa cek nilai.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute } from 'vue-router';

// Gunakan @ untuk path absolute yang lebih aman
import apiQC from '@/modules/qc/api';      
import apiTrace from '@/modules/traceability/api'; 

const route = useRoute();
const partId = Number(route.params.id);

const partName = ref('');
const templates = ref<any[]>([]); 
const isSubmitting = ref(false);

// Form Default
const defaultForm = {
  part_master: partId,
  field_label: '',
  field_key: '',
  field_type: 'NUMBER',
  min_val: null,
  max_val: null,
  is_mandatory: true
};

const form = reactive({ ...defaultForm });

// --- LOAD DATA ---
const loadData = async () => {
  try {
    const partRes = await apiTrace.getPart(partId);
    partName.value = partRes.data.part_name;

    const tplRes = await apiQC.getTemplatesByPart(partId);
    const rawData: any = tplRes.data;
    templates.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
    
  } catch (e) {
    console.error("Error loading data", e);
  }
};

// --- ACTIONS ---
const addTemplate = async () => {
  isSubmitting.value = true;
  try {
    const keyRegex = /^[a-z0-9_]+$/;
    if (!keyRegex.test(form.field_key)) {
      alert("Field Key hanya boleh huruf kecil, angka, dan underscore (_).");
      isSubmitting.value = false;
      return;
    }

    // Menggunakan 'as any' untuk bypass validasi strict typescript sementara
    await apiQC.createTemplate(form as any);
    
    // Reset form
    Object.assign(form, defaultForm); 
    form.field_label = '';
    form.field_key = '';
    form.field_type = 'NUMBER';
    form.min_val = null;
    form.max_val = null;
    form.is_mandatory = true;
    
    await loadData();
  } catch (e: any) {
    alert("Gagal menyimpan: " + (e.response?.data?.detail || "Server Error"));
  } finally {
    isSubmitting.value = false;
  }
};

const deleteItem = async (id: number) => {
  if (confirm("Hapus parameter ini? Data history lama tetap aman.")) {
    try {
      await apiQC.deleteTemplate(id);
      await loadData();
    } catch (e) { alert("Gagal menghapus."); }
  }
};

onMounted(loadData);
</script>

<style scoped>
/* Reuse Style Global */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* Grid 2 Kolom */
.grid-layout { display: grid; grid-template-columns: 350px 1fr; gap: 24px; }
@media (max-width: 768px) { .grid-layout { grid-template-columns: 1fr; } }

/* Card & Form */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; height: fit-content; }
.card-header { padding: 12px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.card-header h3 { margin: 0; font-size: 1rem; color: #475569; font-weight: 600; }
.card-body { padding: 20px; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 500; font-size: 0.9rem; color: #334155; }
.input { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; }
.input:focus { outline: 2px solid #3b82f6; border-color: #3b82f6; }

/* Table */
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 10px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; font-size: 0.75rem; text-transform: uppercase; }

/* Buttons & Badges */
.btn-primary { background: #2563eb; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; }
.btn-secondary { background: #f1f5f9; color: #475569; padding: 8px 16px; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; }
.btn-icon { width: 28px; height: 28px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.btn-icon:hover { background: #fee2e2; border-color: #fca5a5; }

.badge { padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }
.badge-blue { background: #dbeafe; color: #1e40af; }
.badge-red { background: #fee2e2; color: #991b1b; }
.badge-gray { background: #f1f5f9; color: #64748b; }

.text-red { color: #ef4444; }
.text-muted { color: #94a3b8; font-size: 0.8rem; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 600; }
.flex { display: flex; }
.gap-2 { gap: 8px; }
.w-full { width: 100%; }
.h-full { height: 100%; }
</style>