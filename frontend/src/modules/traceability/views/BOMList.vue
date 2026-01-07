<template>
  <div class="master-page">
    
    <div class="header">
      <div class="flex justify-between items-center">
        <div>
          <h2>📑 BOM Versions</h2>
          <p>Konfigurasi traceability per model produk (Bill of Materials).</p>
        </div>
        <router-link to="/traceability/bom/create" class="btn-primary">
          + Buat Versi Baru
        </router-link>
      </div>
    </div>

    <div class="card">
      
      <div v-if="isLoading" class="text-center py-8 text-muted">
        Loading data...
      </div>

      <div v-else class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Produk (FG)</th>
              <th>Kode Versi</th>
              <th>Berlaku Mulai</th>
              <th class="text-center">Status</th>
              <th class="text-center">Jml Part</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ver in versions" :key="ver.id || Math.random()">
              <td>
                <span class="font-bold text-slate-700">{{ ver.product_name || '-' }}</span>
              </td>
              <td class="font-mono text-sm font-bold text-blue-600">
                {{ ver.version_code }}
              </td>
              <td>{{ ver.valid_from }}</td>
              <td class="text-center">
                <span v-if="ver.is_active" class="badge-success">Active</span>
                <span v-else class="badge-gray">Inactive</span>
              </td>
              <td class="text-center">
                <span class="badge-gray">{{ ver.requirements?.length || 0 }} Item</span>
              </td>
              <td class="text-right">
                <router-link :to="`/traceability/bom/${ver.id}/edit`" class="btn-icon mr-2" title="Edit">
                  ✏️
                </router-link>
                <button @click="deleteItem(ver.id!)" class="btn-icon danger" title="Hapus">
                  🗑️
                </button>
              </td>
            </tr>

            <tr v-if="versions.length === 0">
              <td colspan="6" class="text-center py-8 text-muted italic">
                Belum ada versi BOM yang dibuat.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../api'; // Import API Module Lokal
import type { Version } from '@/types/traceability'; // Import Global Types

const versions = ref<Version[]>([]);
const isLoading = ref(false);

const loadData = async () => {
  isLoading.value = true;
  try {
    const res = await api.getVersions();
    
    // --- LOGIC FIX: Handle Array vs Pagination ---
    // Mencegah error "map is not a function" jika backend mengirim object pagination
    const rawData = res.data;
    
    if (Array.isArray(rawData)) {
      versions.value = rawData;
    } else {
      // Jika formatnya { count: ..., results: [...] }
      versions.value = rawData['results'] || [];
    }

  } catch (e) { 
    console.error("Gagal load BOM:", e);
    // Optional: Tambahkan notifikasi error user disini
  } finally {
    isLoading.value = false;
  }
};

const deleteItem = async (id: number) => {
  if (!confirm('Hapus BOM Version ini? Data produksi terkait mungkin akan kehilangan referensi.')) return;
  
  try {
    await api.deleteVersion(id);
    loadData(); // Refresh table setelah hapus
  } catch (e) {
    alert('Gagal menghapus data.');
  }
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
/* --- STYLE GLOBAL KONSISTEN --- */

.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }

/* Header Section */
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* Card & Table */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }
.table th { background: #f1f5f9; font-weight: 600; color: #475569; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
.table tr:last-child td { border-bottom: none; }
.table tr:hover { background-color: #f8fafc; }

/* Buttons */
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 0.9rem; display: inline-block; transition: background 0.2s; }
.btn-primary:hover { background: #1d4ed8; }

.btn-icon { width: 32px; height: 32px; border-radius: 4px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all 0.2s; color: #64748b; }
.btn-icon:hover { background: #f1f5f9; color: #0f172a; border-color: #cbd5e1; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; color: #ef4444; }

/* Badges */
.badge-success { background: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; border: 1px solid #bbf7d0; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; border: 1px solid #e2e8f0; }

/* Utilities */
.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-bold { font-weight: 600; }
.font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
.text-slate-700 { color: #334155; }
.text-blue-600 { color: #2563eb; }
.text-muted { color: #94a3b8; }
.italic { font-style: italic; }
.py-8 { padding-top: 2rem; padding-bottom: 2rem; }
.mr-2 { margin-right: 8px; }

</style>