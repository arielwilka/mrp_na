<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📏 Rules Engine</h2>
          <p>Daftar aturan validasi barcode (Format Logic).</p>
        </div>
        <router-link to="/traceability/rules/create" class="btn-primary">
          + Buat Rule Baru
        </router-link>
      </div>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Kode Rule</th>
              <th>Nama Rule</th>
              <th>Deskripsi</th>
              <th class="text-center">Jml Segmen</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rule in rules" :key="rule.id">
              <td class="font-mono font-bold text-blue-600">{{ rule.code }}</td>
              <td>
                <div class="font-bold">{{ rule.name }}</div>
              </td>
              <td class="text-muted text-sm">{{ rule.description || '-' }}</td>
              <td class="text-center">
                <span class="badge-info">{{ rule.segments.length }} Steps</span>
              </td>
              <td class="text-right">
                <router-link :to="`/traceability/rules/${rule.id}/edit`" class="btn-icon mr-2" title="Edit">✏️</router-link>
                <button @click="deleteItem(rule.id!)" class="btn-icon danger" title="Hapus">🗑️</button>
              </td>
            </tr>
            <tr v-if="rules.length === 0">
              <td colspan="5" class="text-center py-8 text-muted">Belum ada data rule.</td>
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
import type { Rule } from '@/types/traceability';

const rules = ref<Rule[]>([]);

const loadData = async () => {
  try {
    const res = await api.getRules();
    // LOGIC FIX: Handle Array vs Pagination
    const rawData = res.data;
    rules.value = Array.isArray(rawData) ? rawData : (rawData['results'] || []);
  } catch (e) { console.error(e); }
};

const deleteItem = async (id: number) => {
  if (confirm('Yakin hapus rule ini? Part yang menggunakan rule ini mungkin akan error.')) {
    await api.deleteRule(id);
    loadData();
  }
};

onMounted(loadData);
</script>

<style scoped>
/* Gunakan Style Global yang sama */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; }
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; display: inline-block; }
.btn-icon { width: 32px; height: 32px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; }
.badge-info { background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-mono { font-family: monospace; }
.text-blue-600 { color: #2563eb; }
.text-muted { color: #94a3b8; }
.mr-2 { margin-right: 8px; }
</style>