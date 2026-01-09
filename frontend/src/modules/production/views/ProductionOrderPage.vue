<template>
  <div class="master-page">
    <div class="header">
      <div>
        <h2>📋 Production Orders (SPK)</h2>
        <p>Rilis perintah kerja ke lantai produksi.</p>
      </div>
      <button @click="openModal" class="btn-primary">+ Buat SPK Baru</button>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>No. Order</th>
              <th>Plan Reff</th>
              <th>Produk</th>
              <th class="text-center">Target</th>
              <th class="text-center">WIP Lama</th>
              <th class="text-center">New Mat.</th>
              <th class="text-center">Output</th>
              <th class="text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td class="font-mono font-bold text-primary">{{ o.order_number }}</td>
              <td class="text-sm">{{ o.plan_code }}</td>
              <td>{{ o.product_variant_name }}</td>
              
              <td class="text-center font-bold">{{ o.target_total_qty }}</td>
              <td class="text-center text-muted">{{ o.carried_over_wip_qty }}</td>
              <td class="text-center text-blue-600 font-bold bg-blue-50 rounded">{{ o.new_material_qty }}</td>
              
              <td class="text-center">
                <span class="badge-success">{{ o.actual_finish_qty }} OK</span>
                <span v-if="o.actual_reject_qty > 0" class="badge-danger ml-1">{{ o.actual_reject_qty }} NG</span>
              </td>
              
              <td class="text-center">
                <span :class="['badge-status', o.status]">{{ o.status }}</span>
              </td>
            </tr>
            <tr v-if="orders.length === 0">
                <td colspan="8" class="text-center py-8 text-muted">Belum ada order produksi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isOpen" class="modal-backdrop" @click.self="isOpen = false">
      <div class="modal-dialog">
        <div class="modal-header"><h3>Rilis SPK Produksi</h3></div>
        <div class="modal-body">
            
            <div class="form-group">
                <label>Pilih Production Plan</label>
                <select v-model="selectedPlanId" class="form-select">
                    <option :value="null" disabled>-- Pilih Plan Aktif --</option>
                    <option v-for="p in plans" :key="p.id" :value="p.id">
                        {{ p.plan_code }} - {{ p.product_name }}
                    </option>
                </select>
            </div>

            <div class="form-group">
                <label>Target Total Qty (Hari Ini)</label>
                <input type="number" v-model="form.target_total_qty" class="form-input text-center text-xl font-bold" min="1" />
                <small class="text-muted block mt-2">
                    Sistem akan otomatis menghitung <strong>WIP Gantung</strong> dan memotong sisa kuota dari stok <strong>VIN Available</strong>.
                </small>
            </div>

            <div v-if="selectedPlanId" class="info-box">
                <p>⚠️ <strong>Perhatian:</strong></p>
                <ul class="text-sm list-disc pl-4 mt-1">
                    <li>Jika Mode = VIN, sistem akan membooking VIN sejumlah (Target - WIP).</li>
                    <li>Pastikan stok VIN tersedia di modul VIN Record.</li>
                </ul>
            </div>

        </div>
        <div class="modal-footer">
            <button @click="save" class="btn-primary w-full" :disabled="isSubmitting">
                {{ isSubmitting ? 'Memproses...' : 'Rilis Order' }}
            </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';

const orders = ref<any[]>([]);
const plans = ref<any[]>([]);
const isOpen = ref(false);
const isSubmitting = ref(false);
const selectedPlanId = ref<number|null>(null);

const form = reactive({
    plan: null as number|null,
    target_total_qty: 50
});

onMounted(() => {
    loadData();
});

const loadData = async () => {
    const [ordRes, planRes] = await Promise.all([
        api.getOrders(),
        api.getPlans()
    ]);
    orders.value = ordRes.data.results || ordRes.data || [];
    plans.value = planRes.data.results || planRes.data || [];
};

const openModal = () => {
    selectedPlanId.value = null;
    form.target_total_qty = 50;
    isOpen.value = true;
};

const save = async () => {
    if(!selectedPlanId.value) return alert("Pilih Plan dulu!");
    
    isSubmitting.value = true;
    try {
        await api.createOrder({
            plan: selectedPlanId.value,
            target_total_qty: form.target_total_qty
        });
        isOpen.value = false;
        loadData();
        alert("Sukses! Order dirilis & Material/VIN ter-booking.");
    } catch(e: any) {
        // Tampilkan pesan error dari backend (misal: Stok VIN Habis)
        const msg = e.response?.data?.detail || e.response?.data?.[0] || "Gagal Rilis Order";
        alert("Gagal: " + msg);
    } finally {
        isSubmitting.value = false;
    }
};
</script>

<style scoped>
/* Reuse style global yang konsisten */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: var(--text-primary); }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
.table td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; vertical-align: middle; }

.badge-success { background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
.badge-danger { background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }

.badge-status { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }
.badge-status.RELEASED { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.badge-status.CLOSED { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(2px); display: flex; justify-content: center; align-items: center; z-index: 50; }
.modal-dialog { background: white; width: 90%; max-width: 450px; border-radius: 12px; padding: 24px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; }
.form-input, .form-select { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
.btn-primary { background: #2563eb; color: white; padding: 10px 16px; border-radius: 6px; border: none; cursor: pointer; font-weight: 600; }
.info-box { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; padding: 12px; border-radius: 6px; margin-top: 16px; }

.text-primary { color: #2563eb; }
.text-muted { color: #64748b; }
.text-blue-600 { color: #2563eb; }
.bg-blue-50 { background-color: #eff6ff; }
.ml-1 { margin-left: 4px; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-bold { font-weight: 600; }
.font-mono { font-family: monospace; }
</style>