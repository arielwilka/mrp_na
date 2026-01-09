<template>
  <div class="shop-floor">
    
    <div class="top-bar">
      <div class="station-info">
        <span class="label">STATION:</span>
        <span class="value">{{ activeStation?.name || 'Loading...' }}</span>
      </div>
      <div class="user-info">
        User: {{ currentUser }} | <button @click="logout" class="btn-logout">Keluar</button>
      </div>
    </div>

    <div class="workspace">
      
      <div class="left-panel">
        
        <div class="scan-box" :class="scanBoxClass">
          <label>{{ inputLabel }}</label>
          <input 
            ref="scanInput"
            v-model="scanBuffer"
            @keyup.enter="handleInput"
            @focus="isFocused = true"
            @blur="isFocused = false"
            :placeholder="inputPlaceholder"
            autocomplete="off"
          />
          <div class="status-indicator" :class="statusClass">
            {{ statusMessage }}
          </div>
        </div>

        <div v-if="unit" class="unit-card fade-in">
          <div class="unit-header">
            <div class="unit-id">{{ unit.identity_label }}</div>
            <div class="unit-desc">
                {{ unit.variant_name }} <span v-if="unit.color_name !== '-'">- {{ unit.color_name }}</span>
            </div>
            </div>
          
          <div class="requirements-list">
             <div class="req-header">
                <span>📋 PART CHECKLIST</span>
                <span class="count-badge">{{ scannedCount }} / {{ requirements.length }}</span>
             </div>

             <div v-if="requirements.length === 0" class="empty-req">
                <p>Tidak ada part wajib di station ini.</p>
                <p class="text-xs">Silakan tekan PASS.</p>
             </div>

             <ul v-else class="req-items">
                <li v-for="(req, idx) in requirements" :key="idx" :class="{ 'done': req.is_scanned }">
                   <div class="icon">
                      <span v-if="req.is_scanned">✅</span>
                      <span v-else>⭕</span>
                   </div>
                   <div class="info">
                      <div class="p-name">{{ req.part_name }}</div>
                      <div class="p-val">{{ req.scanned_value }}</div>
                   </div>
                </li>
             </ul>
          </div>
        </div>
      </div>

      <div class="right-panel">
         <div v-if="unit" class="action-grid fade-in">
            
            <button 
              @click="processUnit('PASS')" 
              class="btn-action pass" 
              :disabled="!isAllRequirementsMet"
              :class="{ 'disabled': !isAllRequirementsMet }"
            >
               <span class="emoji">✅</span>
               <span class="text">PASS / OK</span>
               <span class="sub" v-if="isAllRequirementsMet">Simpan & Lanjut</span>
               <span class="sub" v-else>Part Belum Lengkap!</span>
            </button>

            <button @click="processUnit('REJECT')" class="btn-action reject">
               <span class="emoji">❌</span>
               <span class="text">REJECT</span>
               <span class="sub">Unit Cacat / NG</span>
            </button>

            <button @click="resetSession" class="btn-action cancel">
               <span class="emoji">🔄</span>
               <span class="text">RESET</span>
            </button>

         </div>
         
         <div v-else class="waiting-state">
            <div class="icon">🔍</div>
            <p>Scan Barcode Unit...</p>
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

const unit = ref<any>(null);
const requirements = ref<any[]>([]);

// UI STATUS
const statusMessage = ref('READY');
const statusClass = ref('ready'); // ready, loading, success, error

// COMPUTED
const isAllRequirementsMet = computed(() => {
   if (!requirements.value || requirements.value.length === 0) return true;
   return requirements.value.every(r => r.is_scanned);
});

const scannedCount = computed(() => requirements.value.filter(r => r.is_scanned).length);

const inputLabel = computed(() => unit.value ? 'SCAN PART' : 'SCAN UNIT');
const inputPlaceholder = computed(() => unit.value ? 'Scan barcode part...' : 'Scan VIN / Body ID...');

const scanBoxClass = computed(() => ({
   'focused': isFocused.value,
   'mode-part': !!unit.value
}));

// LIFECYCLE
onMounted(() => {
   const stored = localStorage.getItem('active_station');
   if (!stored) { router.push({ name: 'StationLogin' }); return; }
   activeStation.value = JSON.parse(stored);
   focusInput();
});

const focusInput = () => nextTick(() => scanInput.value?.focus());

// MAIN LOGIC
const handleInput = async () => {
   const val = scanBuffer.value;
   scanBuffer.value = ''; // Clear ASAP
   if (!val) return;

   if (!unit.value) {
      await scanUnit(val);
   } else {
      await scanPart(val);
   }
};

const scanUnit = async (code: string) => {
   setStatus('MENCARI UNIT...', 'loading');
   try {
      const res = await api.shopFloorScan(code, activeStation.value.id);
      unit.value = res.data.unit;
      requirements.value = res.data.requirements || [];
      
      setStatus('UNIT OK. SCAN PART.', 'scanning');
   } catch (e: any) {
      setStatus(e.response?.data?.detail || 'UNIT TIDAK DITEMUKAN', 'error');
   }
};

const scanPart = async (code: string) => {
   setStatus('CEK PART...', 'loading');
   try {
      const res = await api.shopFloorScanPart({
         unit_id: unit.value.id,
         station_id: activeStation.value.id,
         part_barcode: code
      });
      
      // Update Checklist di UI
      const matchedName = res.data.matched_part_name;
      const targetReq = requirements.value.find(r => r.part_name === matchedName && !r.is_scanned);
      
      if (targetReq) {
         targetReq.is_scanned = true;
         targetReq.scanned_value = code; // Simpan barcode yg discan utk display
         setStatus(`OK: ${matchedName}`, 'success');
      } else {
         setStatus('PART SALAH / SUDAH DISCAN', 'error');
      }

      // Cek Finish
      if (isAllRequirementsMet.value) {
         setStatus('PART LENGKAP. TEKAN PASS.', 'ready');
      }

   } catch (e: any) {
      setStatus(e.response?.data?.detail || 'PART INVALID', 'error');
   }
};

const processUnit = async (action: 'PASS' | 'REJECT' | 'PAUSE') => {
   setStatus('MENYIMPAN...', 'loading');
   try {
      await api.shopFloorProcess({
         unit_id: unit.value.id,
         station_id: activeStation.value.id,
         // TypeScript sekarang tahu action pasti salah satu dari 3 string itu
         action: action 
      });
      
      setStatus(action === 'PASS' ? 'UNIT FINISH!' : 'UNIT REJECT', action === 'PASS' ? 'success' : 'error');
      
      setTimeout(() => resetSession(), 1500);
   } catch (e: any) {
      setStatus('GAGAL PROSES', 'error');
   }
};

const resetSession = () => {
   unit.value = null;
   requirements.value = [];
   setStatus('READY', 'ready');
   focusInput();
};

const setStatus = (msg: string, cls: string) => {
   statusMessage.value = msg;
   statusClass.value = cls;
};

const logout = () => {
   if(confirm('Keluar?')) {
      localStorage.removeItem('active_station');
      router.push({ name: 'StationLogin' });
   }
};
</script>

<style scoped>
/* --- FULL SCREEN LAYOUT --- */
.shop-floor { 
    height: 100vh; width: 100vw; 
    display: flex; flex-direction: column; 
    background: #f1f5f9; font-family: 'Inter', sans-serif; 
    overflow: hidden; /* Mencegah scroll halaman */
}

/* --- HEADER BAR --- */
.top-bar { 
    height: 60px; flex-shrink: 0;
    background: #0f172a; color: white; 
    padding: 0 24px; display: flex; justify-content: space-between; align-items: center; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 10;
}
.station-info { display: flex; align-items: baseline; gap: 8px; }
.station-info .label { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; }
.station-info .value { font-size: 1.25rem; font-weight: 800; color: #fbbf24; text-shadow: 0 0 10px rgba(251, 191, 36, 0.3); }
.btn-logout { 
    background: #334155; border: 1px solid #475569; color: #e2e8f0; 
    padding: 6px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: 0.2s;
}
.btn-logout:hover { background: #ef4444; border-color: #ef4444; color: white; }

/* --- MAIN WORKSPACE GRID --- */
.workspace { 
    flex: 1; display: grid; 
    grid-template-columns: 450px 1fr; /* Kiri Fixed, Kanan Flexible */
    gap: 24px; padding: 24px; 
    overflow: hidden; 
}

/* --- LEFT PANEL (INFO & LIST) --- */
.left-panel { 
    display: flex; flex-direction: column; gap: 20px; 
    height: 100%; overflow: hidden;
}

/* SCAN BOX */
.scan-box { 
    background: white; padding: 20px; border-radius: 12px; 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); 
    border: 3px solid transparent; transition: 0.3s; 
}
.scan-box.focused { border-color: #cbd5e1; }
.scan-box.mode-part { border-color: #3b82f6; background: #eff6ff; }
.scan-box label { display: block; font-weight: 700; color: #64748b; font-size: 0.85rem; margin-bottom: 8px; letter-spacing: 0.5px; }
.scan-box input { 
    width: 100%; padding: 12px; font-size: 1.5rem; font-weight: 600;
    border: 2px solid #e2e8f0; border-radius: 8px; 
    font-family: 'Courier New', monospace; text-transform: uppercase; box-sizing: border-box;
}
.scan-box input:focus { outline: none; border-color: #3b82f6; }

/* STATUS INDICATOR */
.status-indicator { 
    margin-top: 12px; padding: 10px; border-radius: 8px; 
    text-align: center; font-weight: 800; font-size: 1.1rem; 
}
.status-indicator.ready { background: #dcfce7; color: #166534; }
.status-indicator.scanning { background: #e0f2fe; color: #0284c7; }
.status-indicator.success { background: #22c55e; color: white; box-shadow: 0 4px 6px rgba(34, 197, 94, 0.4); }
.status-indicator.error { background: #ef4444; color: white; animation: shake 0.3s; box-shadow: 0 4px 6px rgba(239, 68, 68, 0.4); }

/* UNIT CARD */
.unit-card { 
    flex: 1; background: white; border-radius: 16px; 
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); 
    display: flex; flex-direction: column; overflow: hidden; 
}
.unit-header { background: #1e293b; padding: 20px; text-align: center; color: white; }
.unit-id { font-size: 1.75rem; font-weight: 800; font-family: monospace; letter-spacing: 1px; color: #fbbf24; }
.unit-desc { font-size: 0.95rem; opacity: 0.8; margin-top: 4px; }

/* CHECKLIST AREA */
.requirements-list { 
    flex: 1; display: flex; flex-direction: column; 
    background: #f8fafc; overflow: hidden; 
}
.req-header { 
    padding: 12px 20px; background: #e2e8f0; font-weight: 700; color: #475569; font-size: 0.85rem;
    display: flex; justify-content: space-between; align-items: center;
}
.count-badge { background: #94a3b8; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }

.req-items { list-style: none; padding: 0; margin: 0; overflow-y: auto; flex: 1; }
.req-items li { 
    display: flex; align-items: center; padding: 14px 20px; 
    border-bottom: 1px solid #e2e8f0; background: white; 
}
.req-items li.done { background: #f0fdf4; border-left: 4px solid #22c55e; }
.req-items li .icon { font-size: 1.2rem; margin-right: 16px; min-width: 24px; text-align: center; }
.req-items li .info { display: flex; flex-direction: column; }
.p-name { font-weight: 700; font-size: 1rem; color: #1e293b; }
.p-val { font-size: 0.85rem; color: #64748b; font-family: monospace; margin-top: 2px; }
.req-items li.done .p-val { color: #15803d; font-weight: 700; }
.empty-req { padding: 40px; text-align: center; color: #94a3b8; font-style: italic; }

/* --- RIGHT PANEL (ACTIONS) --- */
.right-panel { height: 100%; }

.action-grid { 
    display: grid; grid-template-rows: 2fr 1fr 1fr; 
    gap: 16px; height: 100%; 
}

.btn-action { 
    border: none; border-radius: 16px; color: white; 
    cursor: pointer; display: flex; flex-direction: column; 
    align-items: center; justify-content: center; 
    transition: transform 0.1s, box-shadow 0.2s; 
    position: relative; overflow: hidden;
}
.btn-action:active { transform: scale(0.98); }

/* PASS BUTTON */
.btn-action.pass { 
    background: linear-gradient(145deg, #22c55e, #16a34a); 
    box-shadow: 0 8px 0 #15803d; 
}
.btn-action.pass:active { box-shadow: 0 4px 0 #15803d; transform: translateY(4px); }
.btn-action.pass.disabled { 
    background: #cbd5e1; box-shadow: none; cursor: not-allowed; opacity: 1; 
}
.btn-action.pass.disabled .text, .btn-action.pass.disabled .emoji { opacity: 0.5; filter: grayscale(1); }

/* REJECT BUTTON */
.btn-action.reject { 
    background: linear-gradient(145deg, #ef4444, #dc2626); 
    box-shadow: 0 8px 0 #b91c1c; 
}
.btn-action.reject:active { box-shadow: 0 4px 0 #b91c1c; transform: translateY(4px); }

/* CANCEL BUTTON */
.btn-action.cancel { 
    background: #fff; border: 2px solid #cbd5e1; color: #64748b; 
    box-shadow: 0 4px 0 #e2e8f0; 
}
.btn-action.cancel:active { box-shadow: none; transform: translateY(4px); }

/* TYPOGRAPHY BUTTONS */
.btn-action .emoji { font-size: 2.5rem; margin-bottom: 8px; }
.btn-action .text { font-size: 2rem; font-weight: 900; letter-spacing: 1px; }
.btn-action .sub { font-size: 1rem; opacity: 0.9; margin-top: 4px; font-weight: 500; }

.waiting-state { 
    height: 100%; display: flex; flex-direction: column; 
    align-items: center; justify-content: center; 
    border: 3px dashed #cbd5e1; border-radius: 16px; 
    background: #f8fafc; color: #94a3b8; 
}
.waiting-state .icon { font-size: 4rem; margin-bottom: 16px; opacity: 0.5; }
.waiting-state p { font-size: 1.25rem; font-weight: 600; }

@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>