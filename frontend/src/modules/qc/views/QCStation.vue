<template>
  <div class="master-page">
    <div class="header">
      <div class="flex justify-between items-center">
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
              <select v-model="selectedPartId" @change="fetchTemplates" class="input" :disabled="isLoading">
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
                class="input font-mono font-bold text-lg" 
                placeholder="Scan Barcode here..."
                @keyup.enter="focusToForm"
              />
              <small class="text-muted block mt-1">Tekan Enter untuk pindah ke form parameter.</small>
            </div>
          </div>
        </div>

        <div class="info-box">
          <strong>💡 Instruksi Kerja:</strong>
          <ul class="pl-4 mt-2 list-disc">
            <li>Pastikan Serial Number sesuai fisik.</li>
            <li>Gunakan <strong>Kamera</strong> untuk foto fisik barang.</li>
            <li>Gunakan <strong>Screen</strong> untuk capture bukti software/dokumen di layar.</li>
            <li>Tekan tombol PASS atau FAIL sesuai hasil.</li>
          </ul>
        </div>
      </div>

      <div class="right-panel">
        
        <div class="card h-full" v-if="selectedPartId && templates.length > 0">
          <div class="card-header flex justify-between items-center">
            <h3>📋 Parameter Pemeriksaan</h3>
            <span class="badge badge-blue">{{ selectedPartName }}</span>
          </div>
          
          <div class="card-body">
            <div class="form-container">
              <div v-for="tpl in templates" :key="tpl.id" class="form-group border-b pb-4 mb-4">
                <label>
                  {{ tpl.field_label }} 
                  <span v-if="tpl.is_mandatory" class="text-red-500">*</span>
                </label>

                <div v-if="tpl.field_type === 'NUMBER'">
                  <div class="flex items-center gap-2">
                    <input 
                      v-model.number="formValues[tpl.field_key]" 
                      type="number" step="0.01" class="input"
                      :class="{'border-red': isOutOfRange(tpl)}"
                    />
                    <span class="text-muted text-sm">(Std: {{ tpl.min_val }} - {{ tpl.max_val }})</span>
                  </div>
                  <small v-if="isOutOfRange(tpl)" class="text-red-500 font-bold text-xs mt-1 block">⚠️ Nilai di luar standar!</small>
                </div>

                <div v-else-if="tpl.field_type === 'TEXT'">
                  <input v-model="formValues[tpl.field_key]" type="text" class="input" />
                </div>

                <div v-else-if="tpl.field_type === 'BOOLEAN'">
                  <div class="flex gap-4 mt-2">
                    <label class="radio-label pass">
                      <input type="radio" :name="tpl.field_key" :value="true" v-model="formValues[tpl.field_key]"> <span>OK</span>
                    </label>
                    <label class="radio-label fail">
                      <input type="radio" :name="tpl.field_key" :value="false" v-model="formValues[tpl.field_key]"> <span>NG</span>
                    </label>
                  </div>
                </div>

                <div v-else-if="tpl.field_type === 'IMAGE'">
                  
                  <div v-if="!formValues[tpl.field_key]" class="flex flex-wrap gap-2 mt-2">
                    
                    <button @click="openCamera(tpl.field_key)" class="btn-tool btn-camera" title="Ambil Foto Fisik">
                      📷 Kamera
                    </button>

                    <button @click="captureScreen(tpl.field_key)" class="btn-tool btn-screen" title="Capture Layar Komputer">
                      🖥️ Screen
                    </button>

                    <label class="btn-tool btn-upload" title="Upload File Gambar">
                      📂 Upload
                      <input type="file" accept="image/*" class="hidden" @change="handleFileUpload($event, tpl.field_key)" />
                    </label>

                  </div>

                  <div v-else class="mt-2 relative inline-block group">
                    <img 
                      :src="formValues[tpl.field_key]" 
                      class="h-40 w-auto rounded-lg border shadow-sm object-cover bg-gray-100" 
                    />
                    <button 
                      @click="removePhoto(tpl.field_key)" 
                      class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center shadow hover:bg-red-600 font-bold"
                    >
                      &times;
                    </button>
                    <span class="absolute bottom-1 right-1 bg-black/50 text-white text-[10px] px-2 rounded">
                      Captured
                    </span>
                  </div>
                </div>

              </div>
            </div>

            <div class="action-area mt-6 pt-4 border-t">
              <button @click="submit('FAIL')" class="btn-big btn-fail" :disabled="isSubmitting">🚫 REJECT</button>
              <button @click="submit('PASS')" class="btn-big btn-pass" :disabled="isSubmitting">✅ ACCEPT</button>
            </div>
          </div>
        </div>

        <div v-else class="card h-full flex items-center justify-center p-8 bg-gray-50 text-center border-dashed">
          <div class="text-muted">
            <p v-if="!selectedPartId" class="text-lg">👈 Silakan pilih part di sebelah kiri.</p>
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

const isLoading = ref(false);
const isSubmitting = ref(false);
const submitStatus = ref<string | null>(null);

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

onMounted(async () => {
  try {
    const res = await api.getParts();
    const rawData: any = res.data;
    parts.value = Array.isArray(rawData) ? rawData : (rawData.results || []);
  } catch (e) { console.error(e); }
});

// --- METHODS: LOAD ---
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
    templates.value.forEach((t: any) => formValues[t.field_key] = null);
    nextTick(() => snInput.value?.focus());
  } catch (e) { console.error(e); } finally { isLoading.value = false; }
};

const isOutOfRange = (tpl: any) => {
  const val = formValues[tpl.field_key];
  if (val === null || val === '') return false;
  if (tpl.min_val !== null && val < tpl.min_val) return true;
  if (tpl.max_val !== null && val > tpl.max_val) return true;
  return false;
};

// --- METHODS: MEDIA HANDLING ---

// 1. KAMERA (WEBCAM)
const openCamera = (key: string) => {
  activePhotoKey.value = key;
  isCameraOpen.value = true;
};
const closeCamera = () => {
  isCameraOpen.value = false;
  activePhotoKey.value = null;
};
const handleCapture = (base64Image: string) => {
  if (activePhotoKey.value) formValues[activePhotoKey.value] = base64Image;
  closeCamera();
};

// 2. SCREEN CAPTURE (WINDOWS/TAB)
const captureScreen = async (key: string) => {
  try {
    // Minta izin share screen ke browser
    // cursor: 'always' agar cursor terlihat di screenshot
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { cursor: 'always' } as any, 
      audio: false
    });

    // Buat elemen video virtual untuk memutar stream sejenak
    const video = document.createElement('video');
    video.srcObject = stream;
    // Play video agar frame tersedia
    await video.play(); 

    // Capture Frame ke Canvas
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    
    if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert ke Base64 String (JPEG Quality 0.8)
        const base64Image = canvas.toDataURL('image/jpeg', 0.8);
        
        // Simpan ke Form
        formValues[key] = base64Image;
        
        // Matikan sharing screen segera setelah capture
        stream.getTracks().forEach(track => track.stop());
    }
  } catch (err) {
    // User membatalkan dialog share screen
    console.log("Screen capture cancelled or failed", err);
  }
};

// 3. UPLOAD FILE
const handleFileUpload = (event: any, key: string) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => { formValues[key] = e.target?.result; };
    reader.readAsDataURL(file);
  }
};

const removePhoto = (key: string) => { formValues[key] = null; };

// --- SUBMIT ---
const focusToForm = () => { /* Opsional */ };

const submit = async (decision: 'PASS' | 'FAIL') => {
  if (!serialNumber.value) { alert("Serial Number wajib diisi!"); snInput.value?.focus(); return; }

  for (const tpl of templates.value) {
    if (tpl.is_mandatory && !formValues[tpl.field_key]) {
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
    const msg = err.response?.data?.error || "Gagal menyimpan data.";
    alert(`ERROR: ${msg}`);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: #334155; }
.header { margin-bottom: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; }
.header h2 { margin: 0; color: #1e293b; font-size: 1.5rem; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* LAYOUT */
.workstation-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }
@media (max-width: 768px) { .workstation-grid { grid-template-columns: 1fr; } }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.card-header { padding: 12px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 1rem; color: #475569; font-weight: 600; text-transform: uppercase; }
.card-body { padding: 24px; }

/* INPUTS */
.input { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.95rem; }
.input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
.input.border-red { border-color: #ef4444; background-color: #fef2f2; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; font-size: 0.9rem; color: #334155; }

/* BUTTONS TOOLBAR (Camera, Screen, Upload) */
.btn-tool {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 12px; border-radius: 6px; font-weight: 500; font-size: 0.85rem;
  border: none; cursor: pointer; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.btn-camera { background-color: #3b82f6; color: white; }
.btn-camera:hover { background-color: #2563eb; }

/* Tombol Screen Warna Ungu */
.btn-screen { background-color: #9333ea; color: white; } 
.btn-screen:hover { background-color: #7e22ce; }

.btn-upload { background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; }
.btn-upload:hover { background-color: #e2e8f0; }

.hidden { display: none; }
.text-red-500 { color: #ef4444; }
.text-muted { color: #94a3b8; font-size: 0.85rem; }

/* BADGES & RADIO */
.badge-blue { background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
.radio-label { display: flex; align-items: center; padding: 8px 16px; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; background: white; flex: 1; justify-content: center; font-weight: 600; }
.radio-label:hover { background: #f8fafc; }
.radio-label.pass:has(input:checked) { border-color: #16a34a; background: #dcfce7; color: #166534; }
.radio-label.fail:has(input:checked) { border-color: #dc2626; background: #fee2e2; color: #991b1b; }
.radio-label input { margin-right: 8px; }

/* EXECUTION BUTTONS */
.action-area { display: flex; gap: 16px; }
.btn-big { flex: 1; padding: 14px; border-radius: 8px; font-weight: 700; font-size: 1rem; border: none; cursor: pointer; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.btn-pass { background: linear-gradient(to bottom right, #16a34a, #15803d); }
.btn-fail { background: linear-gradient(to bottom right, #dc2626, #b91c1c); }
.status-badge { padding: 8px 16px; border-radius: 6px; font-weight: 700; color: white; font-size: 0.9rem; }
.status-pass { background-color: #16a34a; }
.status-fail { background-color: #dc2626; }
.info-box { background: #eff6ff; border: 1px solid #dbeafe; padding: 16px; border-radius: 8px; color: #1e40af; font-size: 0.9rem; margin-top: 16px; }
.list-disc { margin-left: 20px; }
.border-dashed { border-style: dashed !important; border-width: 2px; }
</style>