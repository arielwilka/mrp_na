<template>
  <div class="shop-floor">
    
    <div class="top-bar">
      <div class="station-info">
        <span class="label">STATION:</span>
        <span class="value">{{ activeStation?.code }} - {{ activeStation?.name || 'Loading...' }}</span>
      </div>
      <div class="user-info">
        <span class="user-badge">👤 {{ currentUser }}</span>
        <button @click="logout" class="btn-logout" title="Keluar">⏻</button>
      </div>
    </div>

    <div class="workspace">
      
      <div class="left-panel">
        
        <div class="scan-box" :class="scanBoxClass">
          <label>{{ inputLabel }}</label>
          <div class="input-wrapper">
            <input 
              ref="scanInput"
              v-model="scanBuffer"
              @keyup.enter="handleInput"
              @focus="isFocused = true"
              @blur="isFocused = false"
              :placeholder="inputPlaceholder"
              :disabled="isInputDisabled"
              autocomplete="off"
            />
            <div class="disabled-overlay" v-if="isInputDisabled">
                🚫 SCAN TIDAK DIPERLUKAN
            </div>
            <div class="focus-indicator" v-else-if="!isFocused" @click="focusInput">⚠️ KLIK DISINI UNTUK SCAN</div>
          </div>
          
          <div class="status-indicator" :class="statusClass">
            <span class="status-icon" v-if="statusClass === 'loading'">⏳</span>
            <span class="status-icon" v-else-if="statusClass === 'success'">🎉</span>
            <span class="status-icon" v-else-if="statusClass === 'error'">⚠️</span>
            <span class="status-text">{{ statusMessage }}</span>
          </div>
        </div>

        <div v-if="isBatchMode && batchData" class="unit-card fade-in batch-mode">
            <div class="unit-header batch">
                <div class="unit-id">{{ batchData.order_number }}</div>
                <div class="unit-sub">{{ batchData.product_name }}</div>
            </div>

            <div class="batch-counter-area">
                <div class="counter-display">
                    <span class="label">OUTPUT (GOOD)</span>
                    <span class="value big">{{ batchData.current_output }}</span>
                    <span class="target">Target: {{ batchData.target_qty }}</span>
                </div>
                
                <div class="counter-display reject">
                    <span class="label">REJECT (NG)</span>
                    <span class="value">{{ batchData.current_reject }}</span>
                </div>
            </div>

            <div class="batch-controls-hint">
                <p>Gunakan tombol di panel kanan untuk update quantity.</p>
            </div>
        </div>

        <div v-else-if="unit" class="unit-card fade-in">
          <div class="unit-header">
            <div class="unit-id">{{ unit.vin }}</div>
            <div class="unit-sub">Internal ID: {{ unit.internal_id }}</div>
          </div>
          
          <div class="job-section">
             <div class="job-header">
                <span class="title">📋 INSTRUKSI KERJA</span>
                <span class="weight-badge" v-if="jobInfo?.weight > 0">Bobot: {{ jobInfo.weight }}%</span>
             </div>
             <div class="job-desc">
                {{ jobInfo?.description || 'Tidak ada instruksi khusus.' }}
             </div>
          </div>

          <div v-if="requirements.length > 0" class="requirements-list">
             <div class="req-header">
                <span>🔧 TRACEABILITY PART</span>
                <span class="count-badge" :class="{'complete': scannedCount === requirements.length}">
                    {{ scannedCount }} / {{ requirements.length }}
                </span>
             </div>

             <ul class="req-items">
                <li v-for="(req, idx) in requirements" :key="idx" :class="{ 'done': req.is_scanned }">
                   <div class="check-icon">
                      <span v-if="req.is_scanned">✅</span>
                      <span v-else>⭕</span>
                   </div>
                   <div class="part-info">
                      <div class="p-name">{{ req.part_name }}</div>
                      <div class="p-code">{{ req.part_number }}</div>
                   </div>
                   <div class="scan-val" v-if="req.is_scanned">OK</div>
                </li>
             </ul>
          </div>

          <div v-else class="no-req-state">
             <div class="icon">✨</div>
             <h3>TIDAK ADA TRACEABILITY</h3>
             <p>Unit ini tidak memerlukan scan part.</p>
             <div class="hint">Silakan cek fisik lalu tekan tombol <strong>PASS</strong>.</div>
          </div>

        </div>

        <div v-else class="idle-illustration fade-in">
            <div class="icon">🔍</div>
            <h3>Menunggu Scan...</h3>
            <p>Scan <strong>VIN Unit</strong> atau <strong>No. SPK (Batch)</strong>.</p>
        </div>

      </div>

      <div class="right-panel">
         
         <div v-if="isBatchMode" class="action-grid fade-in">
             <button @click="processBatch('GOOD', 1)" class="btn-action pass">
                <span class="emoji">➕ 1</span>
                <span class="text">GOOD OK</span>
                <span class="sub">Tambah Output</span>
             </button>

             <button @click="processBatch('REJECT', 1)" class="btn-action reject">
                <span class="emoji">🗑️ 1</span>
                <span class="text">REJECT</span>
                <span class="sub">Barang NG</span>
             </button>

             <button @click="resetSession" class="btn-action cancel">
                <span class="emoji">🏁</span>
                <span class="text">SELESAI</span>
                <span class="sub">Ganti Order / Batch</span>
             </button>
         </div>

         <div v-else-if="unit" class="action-grid fade-in">
            <button 
              @click="processUnit('PASS')" 
              class="btn-action pass" 
              :disabled="!isAllRequirementsMet"
              :class="{ 'disabled': !isAllRequirementsMet }"
            >
               <span class="emoji">✅</span>
               <span class="text">PASS / OK</span>
               <span class="sub" v-if="isAllRequirementsMet">Simpan & Lanjut</span>
               <span class="sub warning" v-else>Part Belum Lengkap!</span>
            </button>

            <button @click="processUnit('REJECT')" class="btn-action reject">
               <span class="emoji">❌</span>
               <span class="text">REJECT</span>
               <span class="sub">Unit Cacat / NG</span>
            </button>

            <button @click="resetSession" class="btn-action cancel">
               <span class="emoji">🔄</span>
               <span class="text">RESET</span>
               <span class="sub">Batal / Scan Ulang</span>
            </button>
         </div>
         
         <div v-else class="waiting-state">
            <div class="pulse-ring"></div>
            <p>Station Ready</p>
         </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import api from '../api';

const router = useRouter();
const authStore = useAuthStore();

// STATE
const activeStation = ref<any>(null);
const currentUser = computed(() => authStore.user?.username || 'Operator');

const scanInput = ref<HTMLInputElement | null>(null);
const scanBuffer = ref('');
const isFocused = ref(false);

// State Unit (Single Piece Flow)
const unit = ref<any>(null);
const jobInfo = ref<any>(null);
const requirements = ref<any[]>([]);

// State Batch (Bulk Flow)
const isBatchMode = ref(false);
const batchData = ref<any>(null);

// UI STATUS HELPERS
const statusMessage = ref('READY TO SCAN');
const statusClass = ref('ready'); 

// COMPUTED PROPERTIES
const isAllRequirementsMet = computed(() => {
   if (!requirements.value || requirements.value.length === 0) return true;
   return requirements.value.every((r: any) => r.is_scanned);
});

const scannedCount = computed(() => {
    return requirements.value ? requirements.value.filter((r: any) => r.is_scanned).length : 0;
});

// IMPROVEMENT: Disable input jika Unit ada TAPI req kosong
const isInputDisabled = computed(() => {
    return unit.value && requirements.value.length === 0;
});

// Dynamic Label & Placeholder
const inputLabel = computed(() => {
    if (isBatchMode.value) return 'BATCH MODE AKTIF';
    // IMPROVEMENT: Label berubah jika tidak perlu scan part
    if (unit.value && requirements.value.length === 0) return 'READY TO PASS';
    return unit.value ? 'SCAN PART BARCODE' : 'SCAN UNIT / SPK';
});

const inputPlaceholder = computed(() => {
    if (isBatchMode.value) return 'Scan SPK lain untuk ganti batch...';
    // IMPROVEMENT: Placeholder kosong jika disabled
    if (unit.value && requirements.value.length === 0) return '';
    return unit.value ? 'Scan part...' : 'Scan VIN atau No. SPK...';
});

const scanBoxClass = computed(() => ({
   'focused': isFocused.value,
   'mode-part': !!unit.value,
   'mode-batch': isBatchMode.value,
   'error-shake': statusClass.value === 'error',
   'disabled': isInputDisabled.value // Class tambahan untuk styling
}));

// LIFECYCLE
onMounted(() => {
   const stored = localStorage.getItem('active_station');
   if (!stored) { 
       alert("Sesi Station tidak ditemukan. Mohon Login Station.");
       router.push({ name: 'StationLogin' }); 
       return; 
   }
   activeStation.value = JSON.parse(stored);
   focusInput();
});

const focusInput = () => nextTick(() => {
    if(!isInputDisabled.value) scanInput.value?.focus();
});

// --- MAIN LOGIC ---

const handleInput = async () => {
   if (isInputDisabled.value) return; // Prevent input if disabled

   const val = scanBuffer.value.trim();
   scanBuffer.value = ''; 
   if (!val) return;

   if (unit.value) {
      await scanPart(val);
   } else {
      await scanUnitOrBatch(val);
   }
};

const scanUnitOrBatch = async (code: string) => {
   setStatus('MENCARI...', 'loading');
   try {
      const res = await api.shopFloorScan(code, activeStation.value.id);
      
      if (res.data.mode === 'BATCH') {
          // --- MASUK MODE BATCH ---
          isBatchMode.value = true;
          batchData.value = res.data;
          unit.value = null;
          jobInfo.value = null;
          setStatus('MODE BATCH AKTIF', 'success');
      } else {
          // --- MASUK MODE UNIT ---
          isBatchMode.value = false;
          batchData.value = null;
          
          unit.value = res.data;
          jobInfo.value = res.data.job_info || {};
          requirements.value = jobInfo.value.bom_requirements || [];
          
          // IMPROVEMENT: Cek jumlah requirements untuk set status awal
          if (requirements.value.length === 0) {
              setStatus('UNIT OK. SIAP PASS.', 'success');
          } else {
              setStatus('UNIT DITEMUKAN', 'success');
              setTimeout(() => setStatus('MENUNGGU SCAN PART...', 'ready'), 1500);
          }
      }
   } catch (e: any) {
      console.error(e);
      const msg = e.response?.data?.detail || 'DATA TIDAK DITEMUKAN';
      setStatus(msg, 'error');
   }
};

const scanPart = async (code: string) => {
   // Safety check
   if (requirements.value.length === 0) return;

   setStatus('VALIDASI PART...', 'loading');
   try {
      const res = await api.shopFloorScanPart({
         unit_id: unit.value.id,
         station_id: activeStation.value.id,
         part_barcode: code
      });
      
      const matchedName = res.data.matched_part_name;
      const targetReq = requirements.value.find((r: any) => r.part_name === matchedName && !r.is_scanned);
      
      if (targetReq) {
         targetReq.is_scanned = true;
         setStatus(`OK: ${matchedName}`, 'success');
      } else {
         setStatus('PART OK (EXTRA/MULTI)', 'success');
      }

      if (isAllRequirementsMet.value) {
         setTimeout(() => setStatus('SEMUA PART LENGKAP. TEKAN PASS.', 'success'), 1000);
      } else {
         setTimeout(() => setStatus('SCAN PART BERIKUTNYA...', 'ready'), 1000);
      }

   } catch (e: any) {
      const msg = e.response?.data?.detail || 'PART SALAH / TIDAK SESUAI BOM';
      setStatus(msg, 'error');
   }
};

const processUnit = async (action: 'PASS' | 'REJECT') => {
   if (action === 'PASS' && !isAllRequirementsMet.value) {
       setStatus('PART BELUM LENGKAP!', 'error');
       return;
   }

   setStatus('MENYIMPAN DATA...', 'loading');
   try {
      await api.shopFloorProcess({
         unit_id: unit.value.id,
         station_id: activeStation.value.id,
         action: action 
      });
      
      setStatus(action === 'PASS' ? 'UNIT FINISH!' : 'UNIT REJECTED', 'success');
      setTimeout(() => resetSession(), 1500);
   } catch (e: any) {
      const msg = e.response?.data?.detail || 'GAGAL MENYIMPAN';
      setStatus(msg, 'error');
   }
};

const processBatch = async (type: 'GOOD' | 'REJECT', qty: number) => {
    if(!batchData.value) return;
    
    if(type === 'GOOD') batchData.value.current_output += qty;
    else batchData.value.current_reject += qty;

    try {
        const res = await api.shopFloorProcessBatch({
            order_id: batchData.value.order_id,
            station_id: activeStation.value.id,
            type: type,
            qty: qty
        });
        batchData.value.current_output = res.data.current_output;
        if(res.data.current_reject !== undefined) 
            batchData.value.current_reject = res.data.current_reject;
    } catch(e) {
        setStatus('GAGAL UPDATE BATCH', 'error');
        if(type === 'GOOD') batchData.value.current_output -= qty;
        else batchData.value.current_reject -= qty;
    }
};

const resetSession = () => {
   unit.value = null;
   batchData.value = null;
   isBatchMode.value = false;
   jobInfo.value = null;
   requirements.value = [];
   setStatus('READY TO SCAN', 'ready');
   focusInput();
};

const setStatus = (msg: string, cls: string) => {
   statusMessage.value = msg;
   statusClass.value = cls;
   
   if(cls === 'error') {
       setTimeout(() => {
           if(statusClass.value === 'error') {
                // Return to appropriate state
                if(unit.value && requirements.value.length === 0) setStatus('UNIT OK. SIAP PASS.', 'success');
                else setStatus('READY TO SCAN', 'ready');
           }
       }, 3000);
   }
};

const logout = () => {
   if(confirm('Keluar dari Station?')) {
      localStorage.removeItem('active_station');
      router.push({ name: 'StationLogin' });
   }
};
</script>

<style scoped>
/* --- LAYOUT UTAMA --- */
.shop-floor { 
    height: 100vh; width: 100vw; 
    display: flex; flex-direction: column; 
    background: #f1f5f9; font-family: 'Segoe UI', sans-serif; 
    overflow: hidden;
}

/* --- TOP BAR --- */
.top-bar { 
    height: 64px; flex-shrink: 0;
    background: #1e293b; color: white; 
    padding: 0 24px; display: flex; justify-content: space-between; align-items: center; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); z-index: 10;
}
.station-info .label { font-size: 0.75rem; color: #94a3b8; letter-spacing: 1px; font-weight: 600; margin-right: 8px; }
.station-info .value { font-size: 1.25rem; font-weight: 700; color: #fbbf24; }
.user-info { display: flex; align-items: center; gap: 16px; }
.user-badge { font-weight: 600; color: #e2e8f0; }
.btn-logout { background: #334155; border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; transition: 0.2s; font-size: 1rem; display: flex; align-items: center; justify-content: center; }
.btn-logout:hover { background: #ef4444; }

/* --- WORKSPACE GRID --- */
.workspace { 
    flex: 1; display: grid; 
    grid-template-columns: 1fr 400px; 
    gap: 20px; padding: 20px; 
    overflow: hidden; 
}

/* --- LEFT PANEL --- */
.left-panel { display: flex; flex-direction: column; gap: 16px; height: 100%; overflow: hidden; }

/* SCAN BOX */
.scan-box { 
    background: white; padding: 20px; border-radius: 12px; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
    border: 2px solid transparent; transition: 0.3s; 
}
.scan-box.focused { border-color: #94a3b8; }
.scan-box.mode-part { border-color: #3b82f6; background: #eff6ff; }
.scan-box.mode-batch { border-color: #6366f1; background: #eef2ff; }
.scan-box.error-shake { animation: shake 0.4s cubic-bezier(.36,.07,.19,.97) both; border-color: #ef4444; }

/* Styles for Disabled Input */
.scan-box.disabled { background: #f1f5f9; border-color: #e2e8f0; opacity: 0.8; }
.disabled-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(241, 245, 249, 0.7);
    display: flex; align-items: center; justify-content: center;
    color: #64748b; font-weight: 700; letter-spacing: 1px;
    border-radius: 8px;
    cursor: not-allowed;
}

.scan-box label { display: block; font-weight: 700; font-size: 0.8rem; color: #64748b; margin-bottom: 8px; letter-spacing: 0.5px; }
.input-wrapper { position: relative; }
.scan-box input { 
    width: 100%; padding: 14px; font-size: 1.5rem; font-weight: 600; 
    border: 2px solid #e2e8f0; border-radius: 8px; box-sizing: border-box;
    font-family: monospace; text-transform: uppercase;
}
.scan-box input:focus { outline: none; border-color: #3b82f6; }
.scan-box input:disabled { background: #e2e8f0; cursor: not-allowed; color: transparent; } /* Text hidden by overlay */

.focus-indicator { 
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
    background: rgba(255,255,255,0.8); backdrop-filter: blur(2px);
    display: flex; align-items: center; justify-content: center; 
    font-weight: 700; color: #ef4444; cursor: pointer; border-radius: 8px;
    border: 2px dashed #ef4444;
}

/* STATUS */
.status-indicator { 
    margin-top: 12px; padding: 12px; border-radius: 8px; 
    display: flex; align-items: center; justify-content: center; gap: 10px;
    font-weight: 700; font-size: 1.1rem; transition: 0.3s;
}
.status-indicator.ready { background: #f1f5f9; color: #64748b; }
.status-indicator.loading { background: #e0f2fe; color: #0284c7; }
.status-indicator.success { background: #dcfce7; color: #166534; }
.status-indicator.error { background: #fee2e2; color: #991b1b; }

/* UNIT CARD */
.unit-card { 
    flex: 1; background: white; border-radius: 12px; 
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
    display: flex; flex-direction: column; overflow: hidden; 
}
.unit-header { background: #0f172a; padding: 16px 20px; color: white; }
.unit-header.batch { background: #4f46e5; }
.unit-id { font-size: 1.5rem; font-weight: 800; font-family: monospace; color: #fbbf24; }
.unit-sub { font-size: 0.9rem; color: #94a3b8; margin-top: 2px; }

/* BATCH STYLES */
.batch-counter-area {
    padding: 30px; display: flex; gap: 20px;
    justify-content: center; background: #f8fafc; flex: 1; align-items: flex-start;
}
.counter-display {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;
    display: flex; flex-direction: column; align-items: center; flex: 1;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
}
.counter-display .value.big { font-size: 5rem; font-weight: 800; color: #16a34a; line-height: 1; margin: 10px 0; }
.counter-display .label { font-weight: 700; color: #64748b; letter-spacing: 1px; }
.counter-display .target { background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; }
.counter-display.reject .value { font-size: 3rem; color: #dc2626; margin: 26px 0; }
.batch-controls-hint { padding: 16px; text-align: center; color: #64748b; border-top: 1px solid #e2e8f0; font-style: italic; }

/* JOB SECTION */
.job-section { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; background: #fffbeb; }
.job-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.job-header .title { font-weight: 700; font-size: 0.85rem; color: #92400e; }
.weight-badge { background: #fcd34d; color: #78350f; font-weight: 700; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
.job-desc { font-size: 1rem; color: #1e293b; line-height: 1.5; font-weight: 500; }

/* REQUIREMENTS LIST */
.requirements-list { flex: 1; display: flex; flex-direction: column; background: #f8fafc; overflow: hidden; }
.req-header { 
    padding: 12px 20px; background: #e2e8f0; 
    display: flex; justify-content: space-between; align-items: center;
    font-weight: 700; color: #475569; font-size: 0.8rem; letter-spacing: 0.5px;
}
.count-badge { background: #cbd5e1; color: #475569; padding: 2px 8px; border-radius: 12px; }
.count-badge.complete { background: #22c55e; color: white; }

.req-items { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1; }
.req-items li { 
    display: flex; align-items: center; padding: 12px 20px; 
    border-bottom: 1px solid #f1f5f9; background: white; transition: 0.2s;
}
.req-items li.done { background: #f0fdf4; border-left: 4px solid #22c55e; }
.check-icon { font-size: 1.2rem; margin-right: 12px; width: 24px; text-align: center; }
.part-info { flex: 1; }
.p-name { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
.p-code { font-size: 0.8rem; color: #64748b; font-family: monospace; }
.scan-val { font-weight: 700; color: #166534; font-size: 0.9rem; }

/* NO REQUIREMENTS STATE (New) */
.no-req-state {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: #f0fdf4; /* Light Green */
    color: #166534;
    padding: 20px;
}
.no-req-state .icon { font-size: 4rem; margin-bottom: 10px; }
.no-req-state h3 { margin: 0; font-size: 1.4rem; font-weight: 800; }
.no-req-state p { margin: 4px 0 16px; opacity: 0.8; }
.no-req-state .hint { 
    background: white; padding: 8px 16px; border-radius: 20px; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size: 0.9rem;
}

/* IDLE STATE */
.idle-illustration { 
    flex: 1; display: flex; flex-direction: column; 
    align-items: center; justify-content: center; 
    background: white; border-radius: 12px; border: 2px dashed #cbd5e1; 
    color: #64748b;
}
.idle-illustration .icon { font-size: 4rem; margin-bottom: 16px; opacity: 0.6; }
.idle-illustration h3 { margin: 0 0 8px; font-size: 1.5rem; color: #334155; }

/* --- RIGHT PANEL --- */
.right-panel { height: 100%; }
.action-grid { display: grid; grid-template-rows: 2fr 1fr 1fr; gap: 16px; height: 100%; }

.btn-action { 
    border: none; border-radius: 16px; color: white; cursor: pointer; 
    display: flex; flex-direction: column; align-items: center; justify-content: center; 
    transition: all 0.2s; position: relative; overflow: hidden;
}
.btn-action:active { transform: scale(0.98); }

.btn-action.pass { background: linear-gradient(145deg, #16a34a, #15803d); box-shadow: 0 6px 0 #14532d; }
.btn-action.pass:active { box-shadow: 0 2px 0 #14532d; transform: translateY(4px); }
.btn-action.pass.disabled { background: #cbd5e1; box-shadow: none; cursor: not-allowed; opacity: 0.8; }
.btn-action.pass.disabled .text { color: #64748b; }

.btn-action.reject { background: linear-gradient(145deg, #dc2626, #b91c1c); box-shadow: 0 6px 0 #7f1d1d; }
.btn-action.reject:active { box-shadow: 0 2px 0 #7f1d1d; transform: translateY(4px); }

.btn-action.cancel { background: #fff; border: 2px solid #cbd5e1; color: #64748b; box-shadow: 0 4px 0 #e2e8f0; }
.btn-action.cancel:active { box-shadow: none; transform: translateY(4px); }

.btn-action .emoji { font-size: 2.5rem; margin-bottom: 4px; }
.btn-action .text { font-size: 1.75rem; font-weight: 800; letter-spacing: 1px; }
.btn-action .sub { font-size: 0.9rem; font-weight: 600; opacity: 0.9; margin-top: 4px; }
.btn-action .sub.warning { color: #7f1d1d; background: #fee2e2; padding: 2px 8px; border-radius: 4px; }

.waiting-state { 
    height: 100%; display: flex; flex-direction: column; 
    align-items: center; justify-content: center; color: #94a3b8; 
}
.pulse-ring { width: 60px; height: 60px; border: 4px solid #cbd5e1; border-radius: 50%; animation: pulse 2s infinite; margin-bottom: 16px; }

@keyframes pulse { 0% { transform: scale(0.9); opacity: 1; } 100% { transform: scale(1.5); opacity: 0; } }
@keyframes shake { 10%, 90% { transform: translate3d(-1px, 0, 0); } 20%, 80% { transform: translate3d(2px, 0, 0); } 30%, 50%, 70% { transform: translate3d(-4px, 0, 0); } 40%, 60% { transform: translate3d(4px, 0, 0); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>