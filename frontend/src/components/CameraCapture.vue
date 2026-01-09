<template>
  <Teleport to="body">
    <div v-if="isOpen" class="camera-overlay">
      
      <div class="camera-modal">
        <div class="camera-header">
          <h3>📸 Ambil Foto</h3>
          <button @click="stopCamera" class="btn-close">&times;</button>
        </div>

        <div class="camera-body">
          <video v-show="!errorMessage && !isLoading" ref="video" autoplay playsinline></video>
          
          <div v-if="isLoading" class="state-msg">
            <div class="spinner"></div>
            <span>Menghubungkan...</span>
          </div>

          <div v-if="errorMessage" class="state-msg error">
            <span class="icon">🚫</span>
            <p>{{ errorMessage }}</p>
            <button @click="stopCamera" class="btn-secondary">Tutup</button>
          </div>
        </div>

        <canvas ref="canvas" style="display: none;"></canvas>

        <div v-if="!errorMessage" class="camera-footer">
          <button v-if="hasMultipleCameras" @click.stop="switchCamera" class="btn-switch" title="Ganti Kamera">
            🔄
          </button>

          <button @click.stop="takePhoto" class="btn-shutter" title="Jepret"></button>
          
          <div v-if="hasMultipleCameras" style="width: 40px;"></div>
        </div>
      </div>

    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

const props = defineProps<{ isOpen: boolean }>();
const emit = defineEmits(['close', 'capture']);

const video = ref<HTMLVideoElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);
const stream = ref<MediaStream | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const hasMultipleCameras = ref(false);
const facingMode = ref<'user' | 'environment'>('environment');

const startCamera = async () => {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) throw new Error("Browser tidak support.");
    const devices = await navigator.mediaDevices.enumerateDevices();
    hasMultipleCameras.value = devices.filter(d => d.kind === 'videoinput').length > 1;

    if (stream.value) stream.value.getTracks().forEach(t => t.stop());

    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: facingMode.value, width: { ideal: 1280 }, height: { ideal: 720 } }
    });

    if (video.value) {
      video.value.srcObject = stream.value;
      video.value.onloadedmetadata = () => { isLoading.value = false; video.value?.play(); };
    }
  } catch (err: any) {
    isLoading.value = false;
    errorMessage.value = "Gagal akses kamera.";
  }
};

const stopCamera = () => {
  if (stream.value) { stream.value.getTracks().forEach(t => t.stop()); stream.value = null; }
  emit('close');
};

const switchCamera = () => {
  facingMode.value = facingMode.value === 'user' ? 'environment' : 'user';
  startCamera();
};

const takePhoto = () => {
  if (!video.value || !canvas.value) return;
  const ctx = canvas.value.getContext('2d');
  if (ctx) {
    canvas.value.width = video.value.videoWidth;
    canvas.value.height = video.value.videoHeight;
    ctx.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
    emit('capture', canvas.value.toDataURL('image/jpeg', 0.7));
    stopCamera();
  }
};

watch(() => props.isOpen, (val) => { if (val) startCamera(); else if (stream.value) stopCamera(); });
onUnmounted(() => stopCamera());
</script>

<style scoped>
.camera-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}

.camera-modal {
  width: 100%; max-width: 500px;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  max-height: 90vh;
}

.camera-header {
  padding: 15px; background: #111; color: white;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid #333;
}
.camera-header h3 { margin: 0; font-size: 1rem; }
.btn-close { background: none; border: none; color: #888; font-size: 1.5rem; cursor: pointer; }

.camera-body {
  position: relative; flex: 1; background: #000;
  display: flex; align-items: center; justify-content: center;
  min-height: 300px; overflow: hidden;
}

video { width: 100%; height: 100%; object-fit: contain; }

.state-msg {
  position: absolute; color: white; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}

.camera-footer {
  padding: 20px; background: #111;
  display: flex; justify-content: center; align-items: center; gap: 20px;
}

.btn-shutter {
  width: 70px; height: 70px;
  border-radius: 50%;
  background: #ef4444;
  border: 4px solid white;
  cursor: pointer;
  transition: transform 0.1s;
}
.btn-shutter:active { transform: scale(0.9); }

.btn-switch {
  width: 40px; height: 40px; border-radius: 50%;
  background: #333; border: 1px solid #555; color: white; cursor: pointer;
}

.spinner {
  width: 30px; height: 30px; border: 3px solid #FFF;
  border-bottom-color: transparent; border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>