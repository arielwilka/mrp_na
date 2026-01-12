<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>📋 Production Work Order (Hybrid Monitor)</h2>
        <p>Monitoring Serialized Unit (VIN) dan Batch Order (Qty) dalam satu view.</p>
      </div>
      <div class="header-actions">
        <button @click="loadData" class="btn-icon bg-white" title="Refresh Data">🔄</button>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-group">
        <label>Cari (VIN / Batch No)</label>
        <input 
            v-model="filters.search" 
            @keyup.enter="handleFilterChange" 
            class="form-input" 
            placeholder="Ketik VIN atau Batch..." 
        />
      </div>
      
      <div class="filter-group">
        <label>Filter SPK / Order</label>
        <select v-model="filters.order" @change="handleFilterChange" class="form-select">
          <option :value="null">Semua Order</option>
          <option v-for="o in orders" :key="o.id" :value="o.id">{{ o.order_number }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Posisi Station</label>
        <select v-model="filters.station" @change="handleFilterChange" class="form-select">
          <option :value="null">Semua Station</option>
          <option v-for="s in stations" :key="s.id" :value="s.id">{{ s.code }} - {{ s.name }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status" @change="handleFilterChange" class="form-select">
          <option value="">Semua Status</option>
          <option value="PLANNED">PLANNED</option>
          <option value="WIP">WIP (In Progress)</option>
          <option value="PAUSED">PAUSED</option>
          <option value="FINISH_PROD">FINISH</option>
        </select>
      </div>
    </div>

    <div class="card mt-4">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Tipe</th>
              <th>Identitas (VIN / Batch)</th>
              <th>Produk / Model</th>
              <th>Posisi / Progress</th>
              <th class="text-center">Status</th>
              <th class="text-right" width="220">Aksi Supervisor</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
               <td colspan="6" class="text-center py-8 text-muted"><span class="spinner">⏳</span> Memuat data...</td>
            </tr>
            
            <tr v-else v-for="unit in units" :key="unit.id">
              <td>
                <span v-if="unit.tracking_mode === 'SERIALIZED'" class="badge-type serial">🚗 UNIT</span>
                <span v-else class="badge-type batch">📦 BATCH</span>
              </td>

              <td>
                <div v-if="unit.tracking_mode === 'SERIALIZED'">
                    <div class="font-mono font-bold text-primary text-sm">{{ unit.identity_label }}</div>
                    <div class="text-xs text-muted">{{ unit.internal_id }}</div>
                </div>
                <div v-else>
                    <div class="font-mono font-bold text-purple-700 text-sm">{{ unit.batch_number }}</div>
                    <div class="text-xs text-muted">Plan: <strong>{{ unit.qty_plan }}</strong> Pcs</div>
                </div>
              </td>

              <td>
                <div class="font-bold text-sm">{{ unit.variant_name }}</div>
                <div class="text-xs text-muted">{{ unit.color_name }}</div>
              </td>

              <td>
                <div v-if="unit.tracking_mode === 'SERIALIZED'">
                    <span class="badge-station" v-if="unit.current_station">
                        📍 {{ unit.current_station_name }}
                    </span>
                    <span v-else class="text-xs text-muted italic">Belum masuk line</span>
                </div>
                
                <div v-else class="w-full" style="min-width: 140px;">
                    <div v-if="unit.status !== 'PLANNED'">
                        <div class="flex justify-between text-xs mb-1">
                            <span>Output: <b>{{ unit.qty_actual }}</b></span>
                            <span class="text-muted">{{ Math.round((unit.qty_actual / unit.qty_plan) * 100) }}%</span>
                        </div>
                        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div class="h-full bg-purple-500" :style="{ width: (unit.qty_actual / unit.qty_plan * 100) + '%' }"></div>
                        </div>
                        <div class="text-[10px] text-gray-400 mt-1">Station: {{ unit.current_station_name }}</div>
                    </div>
                    <div v-else class="text-xs text-gray-400 italic">Menunggu Start</div>
                </div>
              </td>

              <td class="text-center">
                <span :class="['badge-status', unit.status]">{{ unit.status }}</span>
                <div v-if="unit.is_paused" class="text-xs text-red-500 font-bold mt-1">⚠️ PAUSED</div>
              </td>

              <td class="text-right">
                <div class="flex justify-end gap-2">
                    
                    <button 
                        v-if="!unit.current_station && unit.status !== 'FINISH_PROD' && unit.origin_order_status !== 'CLOSED'" 
                        @click="startManual(unit)" 
                        class="btn-action-sm btn-start"
                    >
                        ▶ Start
                    </button>

                    <button 
                        v-if="unit.tracking_mode === 'SERIALIZED' && unit.current_station && unit.status === 'WIP'" 
                        @click="openProcessModal(unit)" 
                        class="btn-action-sm"
                    >
                        ⚙️ Proses
                    </button>

                    <button 
                        v-if="unit.tracking_mode === 'BATCH' && unit.status === 'WIP'" 
                        @click="openProcessModal(unit)" 
                        class="btn-action-sm btn-batch"
                    >
                        🔢 Update Qty
                    </button>
                </div>
              </td>
            </tr>
            <tr v-if="!isLoading && units.length === 0">
                <td colspan="6" class="text-center py-8 text-muted">Data tidak ditemukan sesuai filter.</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="pagination-bar" v-if="pagination.total > 0">
          <div class="text-sm text-muted">
              Total: <strong>{{ pagination.total }}</strong> Record
              (Hal. {{ pagination.current }})
          </div>
          <div class="flex gap-2">
              <button :disabled="!pagination.previous" @click="changePage(pagination.current - 1)" class="btn-ghost">Previous</button>
              <button :disabled="!pagination.next" @click="changePage(pagination.current + 1)" class="btn-ghost">Next</button>
          </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      
      <div class="modal-content" :class="activeUnit?.tracking_mode === 'BATCH' ? 'max-w-md' : 'max-w-5xl'">
        
        <div class="modal-header">
          <div>
            <h3 class="text-lg font-bold text-gray-800">
                {{ activeUnit?.tracking_mode === 'BATCH' ? '🔢 Update Batch Output' : '⚙️ Station Process' }}
            </h3>
            <p class="text-xs text-gray-500 font-mono">
                {{ activeUnit?.current_station_name }} | {{ activeUnit?.identity_label || activeUnit?.batch_number }}
            </p>
          </div>
          <button @click="closeModal" class="close-btn">✕</button>
        </div>

        <div class="modal-body">
          
          <div v-if="isModalLoading" class="loading-state">
             <span class="spinner w-10 h-10 text-blue-500 mb-4"></span>
             <p class="text-gray-500">Menyiapkan data...</p>
          </div>

          <div v-else-if="activeUnit?.tracking_mode === 'SERIALIZED'" class="grid-layout">
            
            <div class="col-left space-y-6">
              <div class="info-panel">
                <h4 class="panel-title">Unit Information</h4>
                <div class="space-y-4">
                  <div>
                    <span class="label-text">Variant</span>
                    <span class="value-text">{{ activeUnit?.variant_name }}</span>
                  </div>
                  <div>
                    <span class="label-text">Color</span>
                    <span class="value-text">{{ activeUnit?.color_name }}</span>
                  </div>
                </div>
              </div>

              <div v-if="warningMessage" class="warning-alert">
                 <strong class="block mb-1">⚠️ System Warning</strong>
                 {{ warningMessage }}
              </div>

              <div class="decision-panel">
                <h4 class="panel-title">Final Decision</h4>
                <div class="grid-buttons">
                   <button @click="submitResult('REJECT')" class="btn-decision reject">
                      <span class="text-xl mb-1">❌</span>
                      <span class="font-bold text-xs">REJECT</span>
                   </button>
                   <button 
                      @click="submitResult('PASS')"
                      :disabled="requirements.length > 0 && !allReqMet"
                      :class="['btn-decision pass', (requirements.length > 0 && !allReqMet) ? 'disabled' : '']"
                    >
                      <span class="text-xl mb-1">✅</span>
                      <span class="font-bold text-xs">PASS / OK</span>
                   </button>
                </div>
              </div>
            </div>

            <div class="col-right flex flex-col gap-6">
              <div class="scan-panel">
                 <div v-if="isScanning" class="scan-overlay"><span class="spinner text-blue-600 w-6 h-6"></span></div>
                 <label class="block text-sm font-semibold text-gray-700 mb-2">Scan Part Barcode</label>
                 <div class="flex gap-2">
                    <input ref="modalInput" v-model="scanBuffer" @keyup.enter="scanPart" class="scan-input" placeholder="Scan part..." autocomplete="off">
                    <button @click="scanPart" class="btn-scan">SCAN</button>
                 </div>
                 <p v-if="scanError" class="mt-2 text-sm font-bold text-red-600">🚫 {{ scanError }}</p>
              </div>

              <div class="bom-panel flex-1 flex flex-col">
                <div class="bom-header">
                  <h4 class="font-bold text-gray-700">Required Traceability (BOM)</h4>
                  <div class="flex flex-col items-end" v-if="requirements.length > 0">
                    <span class="font-mono font-bold text-blue-700">{{ scannedCount }} / {{ requirements.length }} Parts</span>
                    <div class="progress-bar-bg mt-1"><div class="progress-bar-fill" :style="{ width: progressPercentage + '%' }"></div></div>
                  </div>
                </div>
                <div class="bom-list-container">
                  <ul v-if="requirements.length > 0" class="bom-list">
                    <li v-for="(part, idx) in requirements" :key="idx" :class="['bom-item', part.is_scanned ? 'scanned' : 'pending']">
                      <div class="flex items-start gap-3">
                          <div :class="['status-dot', part.is_scanned ? 'bg-green' : 'bg-gray']"></div>
                          <div>
                            <p :class="['part-name', part.is_scanned ? 'text-green' : 'text-gray']">{{ part.part_name }}</p>
                            <p class="part-number">{{ part.part_number }}</p>
                          </div>
                      </div>
                      <span v-if="part.is_scanned" class="badge-scanned">INSTALLED</span>
                    </li>
                  </ul>
                  <div v-else class="text-center py-8 text-gray-500">No parts required.</div>
                </div>
              </div>
            </div>

          </div>

          <div v-else-if="activeUnit?.tracking_mode === 'BATCH'" class="p-4">
             <div class="bg-blue-50 p-4 rounded-lg mb-6 flex justify-between items-center border border-blue-100">
                <div>
                    <span class="block text-xs text-blue-600 font-bold uppercase">Total Plan</span>
                    <span class="text-xl font-mono">{{ activeUnit?.qty_plan }}</span>
                </div>
                <div class="text-right">
                    <span class="block text-xs text-green-600 font-bold uppercase">Current Good</span>
                    <span class="text-xl font-mono font-bold text-green-700">{{ activeUnit?.qty_actual }}</span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="label-text mb-2">Tambah Good Qty</label>
                    <input type="number" v-model.number="batchInput.good" class="scan-input text-center text-lg font-bold" min="0">
                </div>
                <div>
                    <label class="label-text mb-2">Tambah Reject</label>
                    <input type="number" v-model.number="batchInput.reject" class="scan-input text-center text-lg font-bold text-red-600 border-red-200" min="0">
                </div>
            </div>

            <button @click="submitBatchUpdate" class="w-full mt-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-lg shadow transition-colors">
                💾 Simpan Update Output
            </button>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue';
import api from '../api'; 

// --- STATE DATA ---
const units = ref<any[]>([]);
const orders = ref<any[]>([]);
const stations = ref<any[]>([]);
const isLoading = ref(false);

const pagination = reactive({
    current: 1,
    total: 0,
    next: null as string | null,
    previous: null as string | null
});

const filters = reactive({
    search: '',
    order: null,
    station: null,
    status: '' 
});

// Modal State Shared
const isModalOpen = ref(false);
const isModalLoading = ref(false);
const activeUnit = ref<any>(null);

// Serialized Specific State
const isScanning = ref(false);
const requirements = ref<any[]>([]);
const warningMessage = ref('');
const scanBuffer = ref('');
const scanError = ref('');
const modalInput = ref<HTMLInputElement|null>(null);

// Batch Specific State
const batchInput = reactive({ good: 0, reject: 0 });

// --- COMPUTED ---
const allReqMet = computed(() => {
    if(requirements.value.length === 0) return true;
    return requirements.value.every(r => r.is_scanned);
});

const scannedCount = computed(() => {
    if(!requirements.value) return 0;
    return requirements.value.filter(r => r.is_scanned).length;
});

const progressPercentage = computed(() => {
    if(!requirements.value || requirements.value.length === 0) return 0;
    return (scannedCount.value / requirements.value.length) * 100;
});

// --- LOAD DATA ---
const loadData = async () => {
    isLoading.value = true;
    try {
        // Load Master Data
        if(orders.value.length === 0) {
            const [ordRes, stRes] = await Promise.all([api.getOrders(), api.getStations()]);
            orders.value = Array.isArray(ordRes.data) ? ordRes.data : (ordRes.data.results || []);
            stations.value = Array.isArray(stRes.data) ? stRes.data : (stRes.data.results || []);
        }

        // Request data (Include tracking_mode di backend jika ada filter)
        const res = await api.getProductionUnits({
            page: pagination.current, 
            search: filters.search,
            origin_order: filters.order,
            current_station: filters.station,
            status: filters.status
        });

        const rawData = res.data.results || res.data;
        units.value = rawData.map((u:any) => ({
             ...u,
             // Normalisasi field agar aman untuk hybrid
             tracking_mode: u.tracking_mode || 'SERIALIZED', // Default Serialized jika null
             current_station_name: u.current_station_name || stations.value.find(s=>s.id == u.current_station)?.name || 'Unknown',
             variant_name: u.variant_name || '-',
             color_name: u.color_name || '-',
             qty_plan: u.qty_plan || 0,
             qty_actual: u.qty_actual || 0
        }));

        pagination.total = res.data.count || units.value.length;
        pagination.next = res.data.next;
        pagination.previous = res.data.previous;

    } catch(e) { console.error(e); } 
    finally { isLoading.value = false; }
};

const changePage = (page: number) => {
    pagination.current = page;
    loadData();
};

const handleFilterChange = () => {
    pagination.current = 1;
    loadData();
};

onMounted(loadData);

// --- START MANUAL LOGIC ---
const startManual = async (unit: any) => {
    const label = unit.tracking_mode === 'SERIALIZED' ? unit.identity_label : `Batch ${unit.batch_number}`;
    if(!confirm(`Start ${label} secara manual?`)) return;
    
    isLoading.value = true;
    try {
        await api.startManualUnit(unit.id); 
        alert("Unit/Batch berhasil di-start!");
        loadData();
    } catch(e: any) {
        alert("Gagal: " + (e.response?.data?.detail || "Error Server"));
    } finally {
        isLoading.value = false;
    }
}

// --- MODAL LOGIC (HYBRID) ---
const openProcessModal = async (unit: any) => {
    activeUnit.value = unit;
    isModalOpen.value = true;
    
    // CASE BATCH: Simple Setup
    if (unit.tracking_mode === 'BATCH') {
        batchInput.good = 0;
        batchInput.reject = 0;
        isModalLoading.value = false;
        return;
    }

    // CASE SERIALIZED: Load BOM Info
    isModalLoading.value = true;
    requirements.value = [];
    warningMessage.value = '';
    scanBuffer.value = '';
    scanError.value = '';

    try {
        const res = await api.shopFloorScan(unit.identity_label, unit.current_station);
        if (res.data.warning) warningMessage.value = res.data.warning;
        requirements.value = res.data.job_info?.bom_requirements || [];
    } catch(e) {
        console.error(e);
        alert("Gagal memuat detail unit.");
        closeModal();
    } finally {
        isModalLoading.value = false;
        nextTick(() => modalInput.value?.focus());
    }
};

const closeModal = () => {
    isModalOpen.value = false;
    activeUnit.value = null;
};

// --- ACTION: BATCH UPDATE ---
const submitBatchUpdate = async () => {
    if(batchInput.good === 0 && batchInput.reject === 0) return alert("Mohon isi Qty Good atau Reject.");
    
    if(!confirm(`Simpan Output? Good: ${batchInput.good}, Reject: ${batchInput.reject}`)) return;

    try {
        await api.updateBatchOutput({
            unit_id: activeUnit.value.id,
            added_good: batchInput.good,
            added_reject: batchInput.reject
        });
        alert("Batch output updated!");
        closeModal();
        loadData();
    } catch(e: any) {
         alert("Error update batch: " + (e.response?.data?.detail || "Unknown error"));
    }
};

// --- ACTION: SERIALIZED SCAN & SUBMIT ---
const scanPart = async () => {
    if(!scanBuffer.value) return;
    isScanning.value = true;
    scanError.value = '';

    try {
        const res = await api.shopFloorScanPart({
            unit_id: activeUnit.value.id,
            station_id: activeUnit.value.current_station,
            part_barcode: scanBuffer.value
        });

        const matched = res.data.matched_part_name; 
        const req = requirements.value.find(r => r.part_name === matched && !r.is_scanned);
        if(req) req.is_scanned = true;
        
        scanBuffer.value = ''; 
    } catch(e: any) {
        scanError.value = e.response?.data?.detail || "Barcode Salah / Tidak Sesuai.";
        scanBuffer.value = ''; 
    } finally {
        isScanning.value = false;
        nextTick(() => modalInput.value?.focus());
    }
};

const submitResult = async (action: 'PASS' | 'REJECT') => {
    const verb = action === 'PASS' ? 'meloloskan' : 'me-reject';
    if(!confirm(`Konfirmasi ${verb} unit ini?`)) return;

    try {
        await api.shopFloorProcess({
            unit_id: activeUnit.value.id,
            station_id: activeUnit.value.current_station,
            action: action
        });
        closeModal();
        loadData(); 
    } catch(e: any) {
        alert("Gagal memproses: " + (e.response?.data?.detail || "Error server"));
    }
};
</script>

<style scoped>
/* PAGE & UTILS */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }
.text-muted { color: #64748b; }
.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.font-bold { font-weight: 700; }
.flex { display: flex; }
.gap-2 { gap: 8px; }
.text-right { text-align: right; }
.text-center { text-align: center; }

/* FILTERS */
.filter-card { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; background: white; padding: 16px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.filter-group label { display: block; font-size: 0.75rem; font-weight: 700; color: #64748b; margin-bottom: 4px; text-transform: uppercase; }
.form-input, .form-select { width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 0.9rem; }

/* TABLE */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-top: 16px; }
.table-responsive { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; min-width: 900px; }
.table th { background: #f8fafc; padding: 12px 16px; text-align: left; font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; border-bottom: 1px solid #e2e8f0; }
.table td { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; }

/* BADGES & BUTTONS */
.badge-type { padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; border: 1px solid transparent; }
.badge-type.serial { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
.badge-type.batch { background: #f3e8ff; color: #6b21a8; border-color: #d8b4fe; }

.badge-station { background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; border: 1px solid #bae6fd; }

.badge-status { padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
.badge-status.WIP { background: #fef3c7; color: #b45309; }
.badge-status.PLANNED { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.badge-status.FINISH_PROD { background: #dcfce7; color: #166534; }
.badge-status.PAUSED { background: #fee2e2; color: #991b1b; }

.btn-action-sm { background: white; border: 1px solid #cbd5e1; color: #334155; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-action-sm:hover { background: #f1f5f9; border-color: #3b82f6; color: #2563eb; }
.btn-start { color: #15803d; border-color: #bbf7d0; }
.btn-batch { color: #7e22ce; border-color: #d8b4fe; background: #faf5ff; }
.btn-icon { width: 36px; height: 36px; border-radius: 8px; border: 1px solid #e2e8f0; cursor: pointer; display: flex; align-items: center; justify-content: center; }

/* PAGINATION */
.pagination-bar { padding: 16px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; background: #fafbfc; }
.btn-ghost { padding: 6px 16px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; cursor: pointer; font-size: 0.85rem; color: #475569; }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }

/* MODAL STYLES */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); z-index: 50; display: flex; justify-content: center; align-items: center; padding: 16px; }
.modal-content { background: white; border-radius: 12px; width: 100%; max-height: 90vh; display: flex; flex-direction: column; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); overflow: hidden; transition: max-width 0.2s; }

.modal-header { padding: 16px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }
.modal-body { flex: 1; overflow-y: auto; padding: 24px; background: #f8fafc; }
.loading-state { height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; }

/* GRID LAYOUT (SERIALIZED) */
.grid-layout { display: grid; grid-template-columns: 1fr; gap: 24px; }
@media (min-width: 1024px) {
    .grid-layout { grid-template-columns: 4fr 8fr; }
}

/* PANELS */
.info-panel, .decision-panel, .bom-panel { background: white; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.panel-title { font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; }
.label-text { display: block; font-size: 0.75rem; color: #64748b; }
.value-text { display: block; font-weight: 500; color: #0f172a; }
.warning-alert { background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; padding: 12px; border-radius: 8px; font-size: 0.875rem; }

/* DECISION BUTTONS */
.grid-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.btn-decision { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px; border-radius: 8px; border: 1px solid transparent; cursor: pointer; transition: 0.2s; }
.btn-decision.reject { background: #fef2f2; border-color: #fecaca; color: #dc2626; }
.btn-decision.pass { background: #f0fdf4; border-color: #bbf7d0; color: #15803d; }
.btn-decision.disabled { background: #f3f4f6; border-color: #e5e7eb; color: #9ca3af; cursor: not-allowed; }

/* SCAN AREA */
.scan-panel { background: white; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; position: relative; box-shadow: 0 0 0 4px #eff6ff; }
.scan-overlay { position: absolute; inset: 0; background: rgba(255,255,255,0.8); z-index: 10; display: flex; justify-content: center; align-items: center; border-radius: 8px; }
.scan-input { flex: 1; padding: 12px 16px; font-size: 1.1rem; border: 1px solid #cbd5e1; border-radius: 8px; outline: none; }
.scan-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.btn-scan { background: #2563eb; color: white; border: none; padding: 0 24px; border-radius: 8px; font-weight: bold; cursor: pointer; }

/* BOM LIST */
.bom-header { padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px; }
.progress-bar-bg { width: 120px; height: 6px; background: #e2e8f0; border-radius: 10px; overflow: hidden; }
.progress-bar-fill { height: 100%; background: #3b82f6; transition: width 0.5s ease; }
.bom-list-container { max-height: 350px; overflow-y: auto; }
.bom-list { list-style: none; padding: 0; margin: 0; }
.bom-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 6px; margin-bottom: 4px; transition: background 0.2s; }
.bom-item.scanned { background: #f0fdf4; }
.bom-item.pending:hover { background: #f8fafc; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 6px; }
.bg-green { background: #22c55e; }
.bg-gray { background: #cbd5e1; }
.part-name { font-size: 0.875rem; font-weight: 700; margin: 0; }
.part-name.text-green { color: #15803d; }
.part-name.text-gray { color: #1f2937; }
.badge-scanned { background: #bbf7d0; color: #14532d; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px; font-weight: 700; border: 1px solid #86efac; }
.spinner { display: inline-block; border: 3px solid currentColor; border-radius: 50%; border-right-color: transparent; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>