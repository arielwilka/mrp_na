<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-95 p-4">
    
    <div class="relative w-full max-w-md bg-black rounded-2xl overflow-hidden shadow-2xl flex flex-col" style="max-height: 90vh;">
      
      <div class="flex-none flex justify-between items-center p-4 bg-gray-900 border-b border-gray-800 z-20">
        <h3 class="text-white font-bold text-lg flex items-center gap-2">
          📸 Ambil Foto
        </h3>
        <button 
          @click="stopCamera" 
          class="w-8 h-8 flex items-center justify-center rounded-full bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white transition"
        >
          ✕
        </button>
      </div>

      <div class="relative flex-1 bg-black overflow-hidden flex items-center justify-center min-h-0">
        
        <video 
          v-show="!errorMessage && !isLoading" 
          ref="video" 
          autoplay 
          playsinline 
          class="w-full h-full object-contain"
        ></video>
        
        <div v-if="isLoading" class="absolute inset-0 flex flex-col items-center justify-center text-white bg-gray-900 z-10">
          <div class="animate-spin rounded-full h-10 w-10 border-4 border-gray-600 border-t-blue-500 mb-3"></div>
          <span class="text-sm font-medium animate-pulse">Menghubungkan Kamera...</span>
        </div>

        <div v-if="errorMessage" class="absolute inset-0 flex flex-col items-center justify-center text-center p-6 bg-gray-900 z-10">
          <div class="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center mb-4">
            <span class="text-3xl">🚫</span>
          </div>
          <h3 class="text-red-400 font-bold text-lg mb-1">Kamera Error</h3>
          <p class="text-gray-400 text-sm mb-4 max-w-xs">{{ errorMessage }}</p>
          <button @click="stopCamera" class="px-6 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white hover:bg-gray-700 transition">
            Tutup
          </button>
        </div>
      </div>

      <canvas ref="canvas" class="hidden"></canvas>

      <div v-if="!errorMessage" class="flex-none h-32 bg-gray-900 border-t border-gray-800 flex items-center justify-center relative z-30">
        
        <button 
          v-if="hasMultipleCameras" 
          @click.stop="switchCamera" 
          class="absolute left-8 p-3 rounded-full bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white transition shadow-lg border border-gray-700"
          title="Ganti Kamera"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <button 
          @click.stop="takePhoto" 
          class="group relative flex items-center justify-center w-20 h-20 rounded-full border-[5px] border-white/30 hover:border-white/60 transition-all active:scale-95"
          title="Ambil Foto"
        >
          <div class="w-16 h-16 bg-red-600 rounded-full shadow-inner flex items-center justify-center group-hover:bg-red-500 transition-colors">
             <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white drop-shadow-md" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
               <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
               <path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
             </svg>
          </div>
        </button>

        <div v-if="hasMultipleCameras" class="absolute right-8 w-12"></div> 

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

const props = defineProps<{
  isOpen: boolean;
}>();

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
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Browser ini tidak mendukung akses kamera.");
    }

    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(d => d.kind === 'videoinput');
    hasMultipleCameras.value = videoDevices.length > 1;

    // Matikan stream lama
    if (stream.value) {
      stream.value.getTracks().forEach(t => t.stop());
    }

    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode: facingMode.value,
        width: { ideal: 1280 }, // HD 720p
        height: { ideal: 720 } 
      }
    });

    if (video.value) {
      video.value.srcObject = stream.value;
      video.value.onloadedmetadata = () => {
        isLoading.value = false;
        video.value?.play();
      };
    }
  } catch (err: any) {
    console.error("Camera Error:", err);
    isLoading.value = false;
    errorMessage.value = err.name === 'NotFoundError' 
      ? "Perangkat kamera tidak ditemukan." 
      : "Akses kamera ditolak. Mohon izinkan browser mengakses kamera.";
  }
};

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  emit('close');
};

const switchCamera = () => {
  facingMode.value = facingMode.value === 'user' ? 'environment' : 'user';
  startCamera();
};

const takePhoto = () => {
  if (!video.value || !canvas.value) return;
  
  const context = canvas.value.getContext('2d');
  if (context) {
    canvas.value.width = video.value.videoWidth;
    canvas.value.height = video.value.videoHeight;
    
    // Draw image without mirroring
    context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
    
    // Convert to JPG (0.7 Quality)
    const dataUrl = canvas.value.toDataURL('image/jpeg', 0.7);
    
    emit('capture', dataUrl);
    stopCamera();
  }
};

watch(() => props.isOpen, (val) => {
  if (val) startCamera();
  else if (stream.value) stream.value.getTracks().forEach(t => t.stop());
});

onUnmounted(() => {
  if (stream.value) stream.value.getTracks().forEach(t => t.stop());
});
</script>

<style scoped>
.hidden { display: none; }
</style>