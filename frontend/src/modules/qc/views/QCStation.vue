<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h2>🛡️ QC Workstation</h2>
          <p>Scan barcode, input parameter fisik, dan tentukan kualitas (OK/NG).</p>
        </div>
        
        <div v-if="submitStatus" :class="['status-badge', statusColor]">
          {{ submitStatus }}
        </div>
      </div>
    </div>

    
    <div class="workstation-grid">
      
      <div class="left-panel">
        
        <div class="card mb-4">
          <div class="card-header">
            <h3>1. Setup Barang</h3>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label>Pilih Part / Komponen</label>
              <select 
                v-model="selectedPartId" 
                @change="fetchTemplates" 
                class="input-field"
                :disabled="isLoading"
              >
                <option :value="null">-- Pilih Part --</option>
                <option v-for="part in parts" :key="part.id" :value="part.id">
                  {{ part.part_number }} - {{ part.part_name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="card mb-4" v-if="selectedPartId">
          <div class="card-header">
            <h3>2. Identifikasi Fisik</h3>
          </div>
          <div class="card-body">
            <div class="form-group">
              <label>Scan Serial Number</label>
              <input 
                ref="snInput"
                v-model="serialNumber" 
                type="text" 
                class="input-field font-mono font-bold text-lg" 
                placeholder="Scan Barcode here..."
                @keyup.enter="focusToForm"
              />
              <small class="text-muted mt-2 block">Tekan Enter untuk pindah ke form parameter.</small>
            </div>
          </div>
        </div>

        <div class="info-box">
          <strong>💡 Instruksi Kerja:</strong>
          <ul class="info-list">
            <li>Pastikan Serial Number sesuai fisik.</li>
            <li>Gunakan <strong>Kamera</strong> untuk foto fisik barang.</li>
            <li>Gunakan <strong>Screen</strong> untuk capture bukti software.</li>
            <li>Tekan tombol PASS atau FAIL sesuai hasil.</li>
          </ul>
        </div>
      </div>

      <div class="right-panel">
        
        <div class="card h-full" v-if="selectedPartId && templates.length > 0">
          <div class="card-header flex-between">
            <h3>📋 Parameter Pemeriksaan</h3>
            <span class="badge badge-blue">{{ selectedPartName }}</span>
          </div>
          
          <div class="card-body">
            <div class="form-container">
              <div v-for="tpl in templates" :key="tpl.id" class="form-item">
                <label class="field-label">
                  {{ tpl.field_label }} 
                  <span v-if="tpl.is_mandatory" class="text-red">*</span>
                </label>

                <div v-if="tpl.field_type === 'NUMBER'">
                  <div class="input-wrapper">
                    <input 
                      v-model.number="formValues[tpl.field_key]" 
                      type="number" 
                      step="0.01"
                      class="input-field"
                      :class="{'input-error': isOutOfRange(tpl)}"
                    />
                    <span class="suffix-text">
                      (Std: {{ tpl.min_val }} - {{ tpl.max_val }})
                    </span>
                  </div>
                  <small v-if="isOutOfRange(tpl)" class="error-text">
                    ⚠️ Nilai di luar standar!
                  </small>
                </div>

                <div v-else-if="tpl.field_type === 'TEXT'">
                  <input v-model="formValues[tpl.field_key]" type="text" class="input-field" />
                </div>

                <div v-else-if="tpl.field_type === 'BOOLEAN'">
                  <div class="radio-group">
                    <label class="radio-label pass">
                      <input type="radio" :name="tpl.field_key" :value="true" v-model="formValues[tpl.field_key]"> 
                      <span>OK</span>
                    </label>
                    <label class="radio-label fail">
                      <input type="radio" :name="tpl.field_key" :value="false" v-model="formValues[tpl.field_key]"> 
                      <span>NG</span>
                    </label>
                  </div>
                </div>

                <div v-else-if="tpl.field_type === 'IMAGE'">
                  
                  <div v-if="!formValues[tpl.field_key]" class="media-actions">
                    <button @click="openCamera(tpl.field_key)" class="btn-tool btn-camera">
                      📷 Kamera
                    </button>

                    <button @click="captureScreen(tpl.field_key)" class="btn-tool btn-screen">
                      🖥️ Screen
                    </button>

                    <label class="btn-tool btn-upload">
                      📂 Upload
                      <input type="file" accept="image/*" class="hidden" @change="handleFileUpload($event, tpl.field_key)" />
                    </label>
                  </div>

                  <div v-else class="image-preview-container">
                    <img 
                      :src="formValues[tpl.field_key]" 
                      class="image-preview" 
                      alt="Bukti QC" 
                    />
                    <button @click="removePhoto(tpl.field_key)" class="btn-remove-photo" title="Hapus Foto">
                      &times;
                    </button>
                    <span class="image-tag">Captured</span>
                  </div>
                </div>

              </div>
            </div>

            <div class="action-area">
              <button 
                @click="submit('FAIL')" 
                class="btn-big btn-fail"
                :disabled="isSubmitting"
              >
                🚫 REJECT
              </button>
              
              <button 
                @click="submit('PASS')" 
                class="btn-big btn-pass"
                :disabled="isSubmitting"
              >
                ✅ ACCEPT
              </button>
            </div>
          </div>
        </div>

        <div v-else class="card h-full empty-state-card">
          <div class="text-muted text-center">
            <div class="empty-icon">👈</div>
            <p v-if="!selectedPartId" class="text-lg">Silakan pilih part di panel kiri.</p>
            <p v-else class="text-lg">Tidak ada template parameter untuk part ini.</p>
          </div>
        </div>

      </div>
    </div>

    <CameraCapture 
      :isOpen="isCameraOpen" 
      @close="closeCamera" 
      @capture="handleCapture" 
    />

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import api from '../api';
import CameraCapture from '@/components/CameraCapture.vue';

// --- STATE ---
const parts = ref<any[]>([]);
const templates = ref<any[]>([]);
const selectedPartId = ref<number | null>(null);
const serialNumber = ref('');
const formValues = reactive<Record<string, any>>({});
const snInput = ref<HTMLInputElement | null>(null);

// UI State
const isLoading = ref(false);
const isSubmitting = ref(false);
const submitStatus = ref<string | null>(null);

// Camera State
const isCameraOpen = ref(false);
const activePhotoKey = ref<string | null>(null);

// --- COMPUTED ---
const selectedPartName = computed(() => {
  const p = parts.value.find(x => x.id === selectedPartId.value);
  return p ? p.part_number : '';
});

const statusColor = computed(() => {
  if (submitStatus.value?.includes('PASS')) return 'status-pass';
  if (submitStatus.value?.includes('FAIL')) return 'status-fail';
  return '';
});

// --- LIFECYCLE ---
onMounted(async () => {
  try {
    const res = await api.getParts();
    const rawData: any = res.data;
    parts.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
  } catch (e) { console.error(e); }
});

// --- METHODS: LOAD DATA ---
const fetchTemplates = async () => {
  if (!selectedPartId.value) {
    templates.value = [];
    return;
  }
  
  isLoading.value = true;
  formValues.value = {}; 
  
  try {
    const res = await api.getTemplatesByPart(selectedPartId.value);
    const rawData: any = res.data;
    templates.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
    
    // Init Model Kosong
    templates.value.forEach((t: any) => {
      formValues[t.field_key] = null;
    });

    nextTick(() => snInput.value?.focus());

  } catch (e) {
    console.error("Gagal load template", e);
  } finally {
    isLoading.value = false;
  }
};

// --- METHODS: VALIDATION ---
const isOutOfRange = (tpl: any) => {
  const val = formValues[tpl.field_key];
  if (val === null || val === '') return false;
  if (tpl.min_val !== null && val < tpl.min_val) return true;
  if (tpl.max_val !== null && val > tpl.max_val) return true;
  return false;
};

// --- METHODS: MEDIA (Camera, Screen, Upload) ---
const openCamera = (key: string) => {
  activePhotoKey.value = key;
  isCameraOpen.value = true;
};

const closeCamera = () => {
  isCameraOpen.value = false;
  activePhotoKey.value = null;
};

const handleCapture = (base64Image: string) => {
  if (activePhotoKey.value) {
    formValues[activePhotoKey.value] = base64Image;
  }
  closeCamera();
};

const captureScreen = async (key: string) => {
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { cursor: 'always' } as any, 
      audio: false
    });
    const video = document.createElement('video');
    video.srcObject = stream;
    await video.play(); 

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const base64Image = canvas.toDataURL('image/jpeg', 0.8);
        formValues[key] = base64Image;
        stream.getTracks().forEach(track => track.stop());
    }
  } catch (err) {
    console.log("Screen capture cancelled");
  }
};

const handleFileUpload = (event: any, key: string) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      formValues[key] = e.target?.result; 
    };
    reader.readAsDataURL(file);
  }
};

const removePhoto = (key: string) => {
  formValues[key] = null;
};

// --- METHODS: SUBMIT ---
const focusToForm = () => { /* Logic focus jika diperlukan */ };

const submit = async (decision: 'PASS' | 'FAIL') => {
  if (!serialNumber.value) {
    alert("Serial Number wajib diisi!");
    snInput.value?.focus();
    return;
  }

  for (const tpl of templates.value) {
    if (tpl.is_mandatory && (formValues[tpl.field_key] === null || formValues[tpl.field_key] === '')) {
      alert(`Field "${tpl.field_label}" wajib diisi!`);
      return;
    }
  }

  isSubmitting.value = true;
  submitStatus.value = null;

  const payload = {
    part_id: selectedPartId.value as number,
    serial_number: serialNumber.value,
    decision: decision,
    qc_data: { ...formValues }
  };

  try {
    await api.submitResult(payload);
    submitStatus.value = `HASIL DISIMPAN: ${decision}`;
    serialNumber.value = '';
    Object.keys(formValues).forEach(k => formValues[k] = null);
    nextTick(() => snInput.value?.focus()); 
    setTimeout(() => submitStatus.value = null, 3000);
  } catch (err: any) {
    console.error(err);
    const msg = err.response?.data?.error || "Gagal menyimpan data.";
    alert(`ERROR: ${msg}`);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
/* ========================================= */
/* LAYOUT GLOBAL (Mengikuti style.css)       */
/* ========================================= */
.page-container { padding: 24px; max-width: 1400px; margin: 0 auto; color: var(--text-primary); }

.page-header { margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px; }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { margin: 0; color: var(--text-primary); font-size: 1.5rem; }
.page-header p { margin: 4px 0 0; color: var(--text-secondary); font-size: 0.9rem; }

/* GRID SYSTEM */
.workstation-grid { display: grid; grid-template-columns: 350px 1fr; gap: 24px; }
@media (max-width: 900px) { .workstation-grid { grid-template-columns: 1fr; } }

/* CARD STYLES */
.card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: var(--shadow-sm); overflow: hidden; }
.card-header { padding: 16px 20px; background: rgba(0,0,0,0.02); border-bottom: 1px solid var(--border-color); }
.card-header h3 { margin: 0; font-size: 1rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.card-body { padding: 24px; }
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.mb-4 { margin-bottom: 16px; }
.h-full { height: 100%; }

/* FORM ELEMENTS */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 0.9rem; color: var(--text-primary); }

.input-field { 
  width: 100%; padding: 10px 12px; 
  border: 1px solid var(--border-color); 
  border-radius: 6px; 
  background: var(--bg-body); 
  color: var(--text-primary);
  font-size: 0.95rem; 
  transition: all 0.2s; 
}
.input-field:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.input-field:disabled { background: rgba(0,0,0,0.05); color: var(--text-secondary); cursor: not-allowed; }
.input-error { border-color: #ef4444; background-color: #fef2f2; }

/* UTILS */
.text-muted { color: var(--text-secondary); font-size: 0.85rem; }
.text-red { color: #ef4444; }
.mt-2 { margin-top: 8px; }
.font-mono { font-family: monospace; }
.font-bold { font-weight: 700; }
.text-lg { font-size: 1.125rem; }

/* FORM ITEMS LAYOUT */
.form-item { border-bottom: 1px solid var(--border-color); padding-bottom: 20px; margin-bottom: 20px; }
.form-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.field-label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--text-primary); font-size: 0.95rem; }

.input-wrapper { display: flex; align-items: center; gap: 12px; }
.suffix-text { color: var(--text-secondary); font-size: 0.85rem; white-space: nowrap; }
.error-text { color: #ef4444; font-weight: bold; font-size: 0.75rem; margin-top: 4px; display: block; }

/* BADGES */
.badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
.badge-blue { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }

.status-badge { padding: 8px 16px; border-radius: 6px; font-weight: 700; color: white; font-size: 0.9rem; box-shadow: var(--shadow-md); }
.status-pass { background-color: #16a34a; }
.status-fail { background-color: #dc2626; }

/* INFO BOX */
.info-box { background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); padding: 16px; border-radius: 8px; color: var(--primary-color); font-size: 0.9rem; }
.info-list { padding-left: 20px; margin-top: 8px; list-style-type: disc; }

/* RADIO BUTTONS (OK/NG) */
.radio-group { display: flex; gap: 16px; }
.radio-label { flex: 1; display: flex; align-items: center; justify-content: center; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; cursor: pointer; transition: all 0.2s; background: var(--bg-body); font-weight: 600; color: var(--text-secondary); }
.radio-label input { margin-right: 8px; }
.radio-label:hover { border-color: var(--text-secondary); }

/* Active States for Radio */
.radio-label.pass:has(input:checked) { background: #dcfce7; color: #166534; border-color: #16a34a; }
.radio-label.fail:has(input:checked) { background: #fee2e2; color: #991b1b; border-color: #dc2626; }

/* MEDIA BUTTONS */
.media-actions { display: flex; flex-wrap: wrap; gap: 10px; }
.btn-tool { display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 6px; font-weight: 500; font-size: 0.85rem; border: none; cursor: pointer; transition: all 0.2s; color: white; }
.btn-tool:hover { transform: translateY(-1px); opacity: 0.9; }

.btn-camera { background-color: var(--primary-color); }
.btn-screen { background-color: #9333ea; }
.btn-upload { background-color: var(--bg-body); color: var(--text-primary); border: 1px solid var(--border-color); }
.btn-upload:hover { background-color: rgba(0,0,0,0.05); }
.hidden { display: none; }

/* IMAGE PREVIEW */
.image-preview-container { position: relative; display: inline-block; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }
.image-preview { height: 160px; width: auto; display: block; background: #000; }
.btn-remove-photo { position: absolute; top: 4px; right: 4px; background: rgba(239, 68, 68, 0.9); color: white; border: none; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: bold; }
.image-tag { position: absolute; bottom: 4px; right: 4px; background: rgba(0,0,0,0.6); color: white; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; }

/* ACTION AREA (PASS/FAIL) */
.action-area { margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--border-color); display: flex; gap: 16px; }
.btn-big { flex: 1; padding: 16px; border-radius: 8px; font-weight: 800; font-size: 1.1rem; border: none; cursor: pointer; color: white; transition: transform 0.1s; display: flex; align-items: center; justify-content: center; box-shadow: var(--shadow-md); }
.btn-big:active { transform: scale(0.98); }
.btn-big:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-pass { background: linear-gradient(135deg, #16a34a, #15803d); }
.btn-fail { background: linear-gradient(135deg, #dc2626, #b91c1c); }

/* EMPTY STATE */
.empty-state-card { display: flex; align-items: center; justify-content: center; border-style: dashed; border-width: 2px; background: transparent; }
.empty-icon { font-size: 3rem; margin-bottom: 10px; }
</style>