<template>
  <div class="master-page">
    <div class="header">
      <div>
        <h2>⚙️ Part Master</h2>
        <p>Database part, aturan validasi, dan konfigurasi QC.</p>
      </div>
      <router-link to="/traceability/parts/create" class="btn-primary">+ Add Part</router-link>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th class="col-tight">Part Number</th>
              <th class="col-auto">Nama Part</th>
              <th>Rule Validasi</th>
              <th class="text-center">QC Check?</th>
              <th class="text-center">Tipe Stok</th>
              <th>Supplier</th>
              <th class="col-action">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="part in parts" :key="part.id">
              <td class="font-mono font-bold">{{ part.part_number }}</td>
              
              <td>{{ part.part_name }}</td>
              
              <td>
                <span v-if="part.rule_code" class="badge-info" :title="part.rule_name">
                  {{ part.rule_code }}
                </span>
                <span v-else class="text-muted text-xs italic">Free Scan</span>
              </td>
              
              <td class="text-center">
                <span v-if="part.is_qc_required" class="badge-success">✅ Wajib</span>
                <span v-else class="badge-gray">⏩ Skip</span>
              </td>

              <td class="text-center">
                 <span v-if="part.is_unique_serial" class="badge-purple">🆔 Unique</span>
                <span v-else class="badge-warning">📦 Batch</span>
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
    parts.value = Array.isArray(rawData) ? rawData : (rawData['results'] || []);
  } catch (e) { console.error(e); }
};

const deleteItem = async (id: number) => {
  if (confirm('Hapus part ini? Konfigurasi QC dan History akan terpengaruh.')) {
    try {
        await api.deletePart(id);
        loadData();
    } catch(e) { alert('Gagal menghapus. Mungkin part sudah dipakai.'); }
  }
};

onMounted(loadData);
</script>

<style scoped>
/* Copy Style Global dari ProductMasterPage agar konsisten */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; }
.header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: var(--text-secondary); font-size: 0.9rem; }

.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: var(--shadow-sm); overflow: hidden; }
.table-responsive { width: 100%; overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.75rem; text-transform: uppercase; font-weight: 600; color: var(--text-secondary); }
.table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); vertical-align: middle; color: var(--text-primary); font-size: 0.9rem; }

.btn-primary { background: var(--primary-color); color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: 0.2s; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid var(--border-color); background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: 0.2s; }
.btn-icon:hover { border-color: var(--primary-color); color: var(--primary-color); }
.btn-icon.danger:hover { background: #fee2e2; border-color: #ef4444; color: #ef4444; }

/* Badges */
.badge-info { background: #eff6ff; color: #1e40af; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
.badge-success { background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid #bbf7d0; }
.badge-warning { background: #ffedd5; color: #9a3412; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid #fed7aa; }
.badge-purple { background: #f3e8ff; color: #6b21a8; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1px solid #e9d5ff; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; }

.col-tight { width: 1%; white-space: nowrap; }
.col-auto { width: auto; }
.col-action { width: 140px; text-align: right; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; }
.mr-2 { margin-right: 8px; }
</style>