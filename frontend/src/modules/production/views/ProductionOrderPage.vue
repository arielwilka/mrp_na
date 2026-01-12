<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>📋 Production Orders (SPK)</h2>
        <p>Kelola siklus produksi, pemenuhan target, dan handover harian.</p>
      </div>
      <button @click="openModal" class="btn-primary">
        <span>+</span> Buat SPK Baru
      </button>
    </div>

    <div class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>No. Order</th>
              <th>Plan / Produk</th>
              <th class="text-center">Mode</th> 
              <th class="text-center bg-gray-50" title="Target Total Hari Ini">Target</th>
              <th class="text-center" title="Sisa kemarin">WIP Awal</th>
              <th class="text-center" title="Input Baru">New In</th>
              <th class="text-center" title="Sedang di Line">WIP Aktif</th>
              <th class="text-center">Output</th>
              <th class="text-center">Status</th>
              <th class="text-center">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td>
                <div class="font-mono font-bold text-primary">{{ o.order_number }}</div>
                <div class="text-xs text-muted">{{ formatDate(o.created_at) }}</div>
              </td>
              
              <td>
                <div class="font-bold text-sm">{{ o.product_variant_name }}</div>
                <div class="text-xs text-muted">{{ o.plan_code }}</div>
              </td>

              <td class="text-center">
                <span :class="['badge-mode', o.tracking_mode_snapshot]">
                    {{ o.tracking_mode_snapshot }}
                </span>
              </td>
              
              <td class="text-center font-bold text-lg bg-gray-50 border-x">
                {{ o.target_total_qty }}
              </td>
              
              <td class="text-center text-muted">
                {{ o.carried_over_wip_qty }}
              </td>
              <td class="text-center text-blue-600 font-bold bg-blue-50">
                {{ o.new_material_qty }}
              </td>
              <td class="text-center font-mono font-bold text-orange-600 border-l">
                {{ o.current_wip_qty }}
              </td>
              
              <td class="text-center">
                <div class="flex flex-col gap-1 items-center justify-center text-xs">
                    <span class="badge-success">{{ o.actual_finish_qty }} OK</span>
                    <span v-if="o.actual_reject_qty > 0" class="badge-danger">{{ o.actual_reject_qty }} NG</span>
                </div>
              </td>
              
              <td class="text-center">
                <span :class="['badge-status', o.status]">{{ o.status }}</span>
                <div v-if="o.closed_at" class="text-[10px] text-muted mt-1">
                    {{ formatTime(o.closed_at) }}
                </div>
              </td>

              <td class="text-center">
                <button 
                    v-if="o.status === 'RELEASED'" 
                    @click="handoverOrder(o)" 
                    class="btn-handover"
                    :disabled="processingId === o.id"
                    title="Tutup Harian / Handover Shift"
                >
                    <span v-if="processingId === o.id">⏳</span>
                    <span v-else>🏁 Close</span>
                </button>
                <span v-else class="text-xs text-muted italic">-</span>
              </td>
            </tr>

            <tr v-if="orders.length === 0">
                <td colspan="10" class="text-center py-12 text-muted">
                    <div class="flex flex-col items-center">
                        <span class="text-3xl grayscale opacity-50">🏭</span>
                        <span class="mt-2">Belum ada order produksi hari ini.</span>
                    </div>
                </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isOpen" class="modal-backdrop" @click.self="isOpen = false">
      <div class="modal-dialog">
        <div class="modal-header">
            <h3>🚀 Rilis SPK Produksi</h3>
            <button class="close-btn" @click="isOpen = false">&times;</button>
        </div>
        
        <div class="modal-body">
            
            <div v-if="errorMessage" class="alert-error mb-4">
               {{ errorMessage }}
            </div>

            <div class="form-group">
                <label>Pilih Production Plan</label>
                <select v-model="selectedPlanId" class="form-select">
                    <option :value="null" disabled>-- Pilih Plan Aktif --</option>
                    <option v-for="p in plans" :key="p.id" :value="p.id">
                        {{ p.plan_code }} - {{ p.product_name }} ({{ p.color_name }})
                    </option>
                </select>
                <div v-if="selectedPlan" class="text-xs text-blue-600 mt-1">
                   Sisa Kuota Plan: <strong>{{ selectedPlan.target_qty }} Unit</strong> (Total)
                </div>
            </div>

            <div class="form-group">
                <label>Target Total Qty (Shift Ini)</label>
                <div class="input-wrapper">
                    <input type="number" v-model="form.target_total_qty" class="form-input text-center text-xl font-bold" min="1" />
                    <span class="unit">Unit</span>
                </div>
                
                <div class="bg-blue-50 p-3 rounded mt-3 text-sm text-blue-800 border border-blue-100">
                    <strong>💡 Auto Calculation:</strong>
                    <ul class="list-disc pl-4 mt-1 space-y-1 text-xs">
                        <li><strong>WIP Gantung</strong> dari shift sebelumnya otomatis dihitung.</li>
                        <li>Kekurangannya akan dihitung sebagai <strong>New Input (Booking Material/VIN)</strong>.</li>
                        <li>Sistem otomatis menolak jika melebihi kuota Plan.</li>
                    </ul>
                </div>
            </div>

        </div>
        <div class="modal-footer">
            <button @click="isOpen = false" class="btn-secondary">Batal</button>
            <button @click="save" class="btn-primary flex-1" :disabled="isSubmitting">
                {{ isSubmitting ? 'Memproses...' : 'Rilis Order' }}
            </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../api'; 

// --- TYPES ---
interface ProductionPlan {
    id: number;
    plan_code: string;
    product_name: string;
    color_name: string;
    target_qty: number;
}

interface ProductionOrder {
    id: number;
    order_number: string;
    plan_code: string;
    product_variant_name: string;
    tracking_mode_snapshot: 'VIN' | 'BATCH' | 'INTERNAL_ID';
    target_total_qty: number;
    carried_over_wip_qty: number;
    new_material_qty: number;
    current_wip_qty: number;
    actual_finish_qty: number;
    actual_reject_qty: number;
    status: string;
    created_at: string;
    closed_at?: string;
}

// --- STATE ---
const orders = ref<ProductionOrder[]>([]);
const plans = ref<ProductionPlan[]>([]);
const isOpen = ref(false);
const isSubmitting = ref(false);
const processingId = ref<number | null>(null); // Untuk loading per baris (handover)
const selectedPlanId = ref<number|null>(null);
const errorMessage = ref<string>("");

const form = reactive({
    target_total_qty: 50
});

// --- COMPUTED ---
const selectedPlan = computed(() => {
    return plans.value.find(p => p.id === selectedPlanId.value);
});

// --- LIFECYCLE ---
onMounted(() => {
    loadData();
});

const loadData = async () => {
    try {
        const [ordRes, planRes] = await Promise.all([
            api.getOrders(),
            api.getPlans()
        ]);

        // --- FIX: Type Casting ---
        // Kita paksa data dari API dianggap sebagai 'any' dulu, 
        // lalu di-cast ke interface local 'ProductionOrder[]'
        const rawOrderData = ordRes.data as any;
        
        const results = Array.isArray(rawOrderData) 
            ? rawOrderData 
            : (rawOrderData.results || []);

        // Assign ke state dengan casting eksplisit
        orders.value = results as ProductionOrder[];

        // Handle Plans
        const planData = planRes.data as any;
        plans.value = Array.isArray(planData) ? planData : (planData.results || []);
    } catch (e) { 
        console.error("Gagal load data", e); 
    }
};

// --- HELPERS ---
const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('id-ID', {
        day: '2-digit', month: 'short'
    });
};

const formatTime = (dateStr: string) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleTimeString('id-ID', {
        hour: '2-digit', minute: '2-digit'
    });
};

const openModal = () => {
    selectedPlanId.value = null;
    form.target_total_qty = 50;
    errorMessage.value = "";
    isOpen.value = true;
};

// --- ACTION 1: BUAT ORDER BARU ---
const save = async () => {
    if(!selectedPlanId.value) {
        errorMessage.value = "Harap pilih Production Plan terlebih dahulu.";
        return;
    }
    
    isSubmitting.value = true;
    errorMessage.value = "";

    try {
        await api.createOrder({
            plan: selectedPlanId.value,
            target_total_qty: form.target_total_qty
        });
        
        isOpen.value = false;
        await loadData();
        alert("✅ Order Berhasil Dirilis!");
    } catch(e: any) {
        console.error(e);
        // Parsing error message dari DRF
        if (e.response && e.response.data) {
             const d = e.response.data;
             // Cek jika error validasi field
             if (d.target_total_qty) {
                 errorMessage.value = Array.isArray(d.target_total_qty) ? d.target_total_qty[0] : d.target_total_qty;
             } else if (d.detail) {
                 errorMessage.value = d.detail;
             } else {
                 errorMessage.value = "Gagal membuat order. Cek data input.";
             }
        } else {
             errorMessage.value = "Terjadi kesalahan koneksi server.";
        }
    } finally {
        isSubmitting.value = false;
    }
};

// --- ACTION 2: HANDOVER ORDER ---
const handoverOrder = async (order: ProductionOrder) => {
    // 1. Pesan konfirmasi
    let confirmMsg = `🏁 Handover Order: ${order.order_number}?\n\n` +
                     `Status saat ini:\n` +
                     `- Target: ${order.target_total_qty}\n` +
                     `- Finish OK: ${order.actual_finish_qty}\n` + 
                     `- Sisa WIP: ${order.current_wip_qty} Unit\n\n`;

    if (order.tracking_mode_snapshot === 'VIN' || order.tracking_mode_snapshot === 'BATCH') {
        confirmMsg += `PERHATIAN: WIP unit yang tersisa akan dilepas (Unassign) untuk dilanjutkan order shift berikutnya.`;
    } else {
        confirmMsg += `PERHATIAN: Pastikan semua aktivitas fisik di line sudah berhenti sebelum Close Order.`;
    }
    
    if(!confirm(confirmMsg)) return;

    // 2. Eksekusi API
    processingId.value = order.id;
    try {
        const res = await api.handoverOrder(order.id);
        await loadData(); // Refresh table
        alert(`✅ Sukses: ${res.data.message || 'Order berhasil di-close.'}`);
    } catch(e: any) {
        const errorMsg = e.response?.data?.detail || "Gagal melakukan handover.";
        alert(`⚠️ Info: ${errorMsg}`);
    } finally {
        processingId.value = null;
    }
};
</script>

<style scoped>
/* --- LAYOUT UTILS --- */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; font-family: 'Inter', sans-serif; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; color: #0f172a; font-size: 1.5rem; font-weight: 700; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* --- TABLE --- */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 12px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; white-space: nowrap; }
.table td { padding: 12px 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; }
.table tr:last-child td { border-bottom: none; }
.table tr:hover td { background-color: #f8fafc; transition: background 0.2s; }

/* --- BADGES --- */
.badge-mode { padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; border: 1px solid transparent; }
.badge-mode.VIN { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.badge-mode.BATCH { background: #ffedd5; color: #9a3412; border-color: #fed7aa; }
.badge-mode.INTERNAL_ID { background: #e0f2fe; color: #075985; border-color: #bae6fd; }

.badge-success { background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; }
.badge-danger { background: #fee2e2; color: #b91c1c; padding: 2px 8px; border-radius: 99px; font-size: 0.7rem; font-weight: 700; }

.badge-status { padding: 4px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; }
.badge-status.RELEASED { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
.badge-status.CLOSED { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }
.badge-status.CANCELLED { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* --- BUTTONS --- */
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.2s; box-shadow: 0 2px 4px rgba(37,99,235,0.2); }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; transform: translateY(-1px); }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; opacity: 0.7; }

.btn-secondary { background: white; border: 1px solid #cbd5e1; color: #475569; padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; margin-right: 8px; }
.btn-secondary:hover { background: #f1f5f9; }

.btn-handover { background: white; border: 1px solid #cbd5e1; color: #475569; padding: 6px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; cursor: pointer; transition: 0.2s; display: inline-flex; align-items: center; gap: 4px; min-width: 80px; justify-content: center; }
.btn-handover:hover:not(:disabled) { background: #fef2f2; border-color: #fca5a5; color: #dc2626; box-shadow: 0 2px 4px rgba(220,38,38,0.1); }
.btn-handover:disabled { opacity: 0.5; cursor: wait; }

/* --- MODAL --- */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 50; }
.modal-dialog { background: white; width: 90%; max-width: 480px; border-radius: 16px; padding: 0; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-direction: column; }
.modal-header { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border-top-left-radius: 16px; border-top-right-radius: 16px; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }
.modal-body { padding: 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid #f1f5f9; background: #f8fafc; display: flex; justify-content: flex-end; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px; }

/* --- FORM & ALERTS --- */
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; color: #334155; }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; transition: border 0.2s; box-sizing: border-box; }
.form-input:focus, .form-select:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2); }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-wrapper .unit { position: absolute; right: 12px; color: #64748b; font-size: 0.9rem; font-weight: 500; }

.alert-error { background-color: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; padding: 12px; border-radius: 8px; font-size: 0.9rem; }

/* --- UTILS --- */
.text-primary { color: #2563eb; }
.text-muted { color: #94a3b8; }
.text-blue-600 { color: #2563eb; }
.text-orange-600 { color: #ea580c; }
.bg-blue-50 { background-color: #eff6ff; }
.bg-gray-50 { background-color: #f8fafc; }
.border-x { border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9; }
.border-l { border-left: 1px solid #f1f5f9; }
.font-bold { font-weight: 600; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.text-center { text-align: center; }
.flex { display: flex; }
.flex-col { flex-direction: column; }
.gap-1 { gap: 4px; }
</style>