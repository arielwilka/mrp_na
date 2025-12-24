<template>
  <div class="layout-page">
    <h2>Print Layout Designer</h2>
    <div class="designer-container">
      <div class="editor-pane">
        <label v-pre>HTML Template (Gunakan {{ full_vin }} untuk data dinamis)</label>
        <textarea v-model="templateHtml" class="code-editor"></textarea>
        <button @click="saveTemplate" class="btn-primary">Simpan Layout</button>
      </div>

      <div class="preview-pane">
        <h4>Preview Live</h4>
        <div id="print-canvas" class="label-canvas" v-html="compiledHtml"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import QRCode from 'qrcode';

// Template Default
const defaultTemplate = `
<div style="width: 300px; height: 150px; border: 2px solid black; padding: 10px; font-family: Arial; display: flex;">
  <div style="flex: 1;">
    <h3 style="margin: 0;">HONDA PART</h3>
    <p style="font-size: 12px;">VIN RECORD:</p>
    <h2 style="margin: 5px 0;">{{ full_vin }}</h2>
    <small>Date: {{ date }}</small>
  </div>
  <div style="width: 80px;">
    <img src="{{ qr_code }}" width="80" />
  </div>
</div>
`;

const templateHtml = ref(localStorage.getItem('vin_print_template') || defaultTemplate);
const dummyData = { full_vin: 'MH1RWK000123', date: '2025-12-17' };
const qrDataUrl = ref('');

// Generate QR Dummy
onMounted(async () => {
  qrDataUrl.value = await QRCode.toDataURL(dummyData.full_vin);
});

// Replace Placeholder
const compiledHtml = computed(() => {
  let html = templateHtml.value;
  html = html.replace('{{ full_vin }}', dummyData.full_vin);
  html = html.replace('{{ date }}', dummyData.date);
  html = html.replace('{{ qr_code }}', qrDataUrl.value);
  return html;
});

const saveTemplate = () => {
  localStorage.setItem('vin_print_template', templateHtml.value);
  alert("Layout tersimpan!");
};
</script>

<style scoped>
.designer-container { display: flex; gap: 20px; }
.editor-pane { flex: 1; }
.code-editor { width: 100%; height: 300px; font-family: monospace; }
.label-canvas { background: white; border: 1px dashed #ccc; display: inline-block; }
</style>