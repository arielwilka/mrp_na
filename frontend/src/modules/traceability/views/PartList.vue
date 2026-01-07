<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>⚙️ Part Master</h2>
          <p>Database part, aturan validasi, dan konfigurasi QC.</p>
        </div>
        <router-link to="/traceability/parts/create" class="btn-primary">+ Add Part</router-link>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Part Number</th>
              <th>Nama Part</th>
              <th>Rule Validasi</th>
              <th class="text-center">QC Check?</th>
              <th class="text-center">Tipe Stok</th>
              
              <th>Supplier</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="part in parts" :key="part.id">
              <td class="font-mono font-bold">{{ part.part_number }}</td>
              
              <td>{{ part.part_name }}</td>
              
              <td>
                <span v-if="part.rule_code" class="badge badge-blue" :title="part.rule_name">
                  {{ part.rule_code }}
                </span>
                <span v-else class="text-muted text-xs italic">Free Scan</span>
              </td>
              
              <td class="text-center">
                <span v-if="part.is_qc_required" class="badge badge-green">
                  ✅ Wajib
                </span>
                <span v-else class="badge badge-gray">
                  ⏩ Skip
                </span>
              </td>

              <td class="text-center">
                 <span v-if="part.is_unique_serial" class="badge badge-purple">
                  🆔 Unique
                </span>
                <span v-else class="badge badge-orange">
                  📦 Batch
                </span>
              </td>

              <td>{{ part.supplier || '-' }}</td>
              
              <td class="text-right">
                <router-link 
                  :to="`/traceability/parts/${part.id}/template`" 
                  class="btn-icon mr-2 bg-yellow-50 border-yellow-200 hover:bg-yellow-100" 
                  title="Setup QC Template"
                >
                  📋
                </router-link>
                <router-link :to="`/traceability/parts/${part.id}/edit`" class="btn-icon mr-2" title="Edit">✏️</router-link>
                <button @click="deleteItem(part.id!)" class="btn-icon danger" title="Hapus">🗑️</button>
              </td>
            </tr>

            <tr v-if="parts.length === 0">
              <td colspan="7" class="text-center py-8 text-muted">Belum ada data part.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../api';
import type { Part } from '@/types/traceability';

const parts = ref<Part[]>([]);

const loadData = async () => {
  try {
    const res = await api.getParts();
    const rawData = res.data;
    // Handle format pagination Django Rest Framework { count:.., results: [] } atau Array biasa []
    parts.value = Array.isArray(rawData) ? rawData : (rawData['results'] || []);
  } catch (e) { 
    console.error("Gagal load part:", e); 
  }
};

const deleteItem = async (id: number) => {
  if (confirm('Hapus part ini? Konfigurasi QC dan History akan terpengaruh.')) {
    try {
        await api.deletePart(id);
        loadData();
    } catch(e) {
        alert('Gagal menghapus. Mungkin part sudah dipakai di transaksi.');
    }
  }
};

onMounted(loadData);
</script>

<style scoped>
/* --- STYLING YANG SAMA --- */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; }
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; }
.btn-icon { width: 32px; height: 32px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; }

/* BADGES */
.badge { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; }
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-green  { background: #dcfce7; color: #166534; }
.badge-purple { background: #f3e8ff; color: #6b21a8; }
.badge-orange { background: #ffedd5; color: #9a3412; }
.badge-gray   { background: #f1f5f9; color: #64748b; }

/* UTILS */
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 600; }
.text-muted { color: #94a3b8; }
.text-xs { font-size: 0.75rem; }
.italic { font-style: italic; }
.mr-2 { margin-right: 8px; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
</style>