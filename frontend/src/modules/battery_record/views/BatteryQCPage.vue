<template>
  <div class="page-container">
    
    <div class="page-header center-header">
      <h2 class="title">🔋 Input Battery QC</h2>
      <p class="subtitle">Scan barcode dan capture aplikasi tester.</p>
    </div>

    <div v-if="!canCreate" class="alert-box error">
      ⛔ <strong>Akses Terbatas</strong><br>Anda tidak memiliki izin membuat data QC.
    </div>

    <div v-else class="form-container">
      <div class="card">
        <div class="card-header">
           <h3 class="card-title">📝 Form Pengecekan</h3>
        </div>
        
        <form @submit.prevent="submitQC" class="card-body">
          <div class="form-group">
            <label>Serial Number (Scan Barcode)</label>
            <input 
              v-model="form.serial_number" 
              ref="snInput"
              placeholder="Scan atau ketik SN..." 
              class="input-lg font-mono"
              required 
            />
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label>Kondisi Fisik</label>
              <select v-model="form.condition" :class="['select-status', form.condition]" required>
                <option value="OK">✅ OK (Pass)</option>
                <option value="NG">❌ NG (Reject)</option>
                <option value="RECHECK">⚠️ Re-Check</option>
              </select>
            </div>
            <div class="form-group">
              <label>Voltage (Volt)</label>
              <div class="input-suffix">
                <input v-model="form.voltage" type="text" placeholder="12.4" />
                <span>V</span>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Bukti Screenshot</label>
            <div class="capture-area">
                <div v-if="!form.file" class="empty-capture">
                    <p class="capture-hint">Klik tombol, lalu pilih Window Aplikasi Tester.</p>
                    <button type="button" @click="captureWindow" class="btn-capture">
                        🖥️ PILIH WINDOW & CAPTURE
                    </button>
                </div>
                <div v-else class="preview-capture">
                    <img :src="previewUrl" class="img-result" />
                    <div class="capture-actions">
                        <span class="file-info">Captured</span>
                        <button type="button" @click="captureWindow" class="btn-retake">🔄 Ulangi</button>
                    </div>
                </div>
            </div>
          </div>

          <div class="form-actions">
             <button type="submit" class="btn-save" :disabled="loading">
               {{ loading ? 'Mengirim Data...' : 'SIMPAN DATA' }}
             </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../../../stores/auth';

const API_URL = 'http://127.0.0.1:8000/api'; 
const authStore = useAuthStore();
const loading = ref(false);
const snInput = ref<HTMLInputElement|null>(null);
const previewUrl = ref('');

const form = reactive({
  serial_number: '',
  condition: 'OK',
  voltage: '',
  file: null as File | null
});

// Permission hanya cek CREATE
const canCreate = computed(() => authStore.can('battery_record', 'create'));

// --- LOGIKA CAPTURE (Sama seperti sebelumnya) ---
const captureWindow = async () => {
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: { cursor: 'always' } as any, 
      audio: false
    });
    const video = document.createElement('video');
    video.srcObject = stream;
    await video.play(); 

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => {
            if (blob) {
                const filename = `screen_${form.serial_number || 'capture'}_${Date.now()}.jpg`;
                form.file = new File([blob], filename, { type: 'image/jpeg' });
                previewUrl.value = URL.createObjectURL(blob);
                stream.getTracks().forEach(track => track.stop());
            }
        }, 'image/jpeg', 0.9);
    }
  } catch (err) { console.log("Capture cancelled"); }
};

const submitQC = async () => {
  if (!form.file) { alert("Bukti screenshot wajib ada!"); return; }
  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('serial_number', form.serial_number);
    formData.append('condition', form.condition);
    formData.append('voltage', form.voltage);
    formData.append('screenshot', form.file); 

    await axios.post(`${API_URL}/battery/records/`, formData);
    
    // Reset Form
    form.serial_number = ''; form.condition = 'OK'; form.voltage = ''; 
    form.file = null; previewUrl.value = '';
    
    alert("✅ Data Tersimpan!");
    setTimeout(() => snInput.value?.focus(), 100);

  } catch (error: any) {
    const detail = error.response?.data?.serial_number ? "Serial Number Duplikat!" : "Gagal simpan.";
    alert(`❌ ${detail}`);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Simplified Style for Single Column */
.page-container { padding: 40px 20px; max-width: 600px; margin: 0 auto; } /* Lebih ramping */
.center-header { text-align: center; margin-bottom: 30px; }
.title { font-size: 1.8rem; color: var(--text-primary); margin: 0; font-weight: 800; }
.subtitle { color: var(--text-secondary); margin-top: 5px; }

.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); overflow: hidden; }
.card-header { padding: 15px 25px; border-bottom: 1px solid var(--border-color); background: var(--bg-body); }
.card-title { margin: 0; font-size: 1rem; color: var(--text-primary); font-weight: 700; text-transform: uppercase; }
.card-body { padding: 30px; }

.form-group { margin-bottom: 20px; display: flex; flex-direction: column; gap: 8px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
label { font-weight: 600; font-size: 0.9rem; color: var(--text-secondary); }

input, select { 
    padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; 
    font-size: 1rem; width: 100%; box-sizing: border-box; background: var(--bg-input, #fff); color: var(--text-primary);
}
.input-lg { padding: 14px; font-size: 1.2rem; text-align: center; letter-spacing: 1px; font-weight: bold; }
.input-suffix { position: relative; display: flex; align-items: center; }
.input-suffix span { position: absolute; right: 15px; color: var(--text-secondary); font-weight: bold; }

/* Capture Area (Sama seperti sebelumnya) */
.capture-area { border: 2px dashed var(--border-color); background: var(--bg-body); border-radius: 8px; padding: 15px; text-align: center; }
.btn-capture { background: #0f172a; color: white; padding: 12px 20px; border-radius: 6px; border: none; font-weight: 700; cursor: pointer; }
.img-result { width: 100%; max-height: 250px; object-fit: contain; border: 1px solid var(--border-color); border-radius: 4px; background: #000; }
.capture-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
.btn-retake { background: white; border: 1px solid var(--border-color); padding: 5px 10px; cursor: pointer; border-radius: 4px; }

.btn-save { 
    width: 100%; background: var(--primary-color); color: white; padding: 16px; 
    border: none; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 1.1rem; 
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); 
}
.alert-box.error { background: #fee2e2; color: #991b1b; padding: 20px; text-align: center; border-radius: 8px; }
</style>