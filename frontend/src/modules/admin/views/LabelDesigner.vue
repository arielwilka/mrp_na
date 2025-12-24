<template>
  <div class="designer-page">
    
    <div class="header-section">
      <div class="header-top">
        <h2>🎨 Label Designer (Admin)</h2>
        <button @click="resetWorkspace" class="btn-secondary">
          📄 Reset / Buat Baru
        </button>
      </div>
      
      <div class="config-bar">
        
        <div class="config-group load-group">
          <label>📂 Load Template</label>
          <select v-model="selectedLoadId" @change="loadTemplate">
            <option :value="null">-- Pilih Template --</option>
            <option v-for="t in savedTemplates" :key="t.id" :value="t.id">
              {{ t.name }}
            </option>
          </select>
        </div>

        <div class="divider"></div>

        <div class="config-group">
          <label>Nama Template</label>
          <input v-model="templateConfig.name" placeholder="Nama Layout..." />
        </div>

        <div class="config-group">
          <label>Modul Parent</label>
          <select v-model="templateConfig.module_scope" :disabled="isLoading">
            <option v-if="isLoading" value="" disabled>Loading...</option>
            <option v-for="mod in modulesList" :key="mod.id" :value="mod.code">
              {{ mod.name }}
            </option>
          </select>
        </div>

        <div class="config-group">
          <label>Ukuran Label</label>
          <select v-model="selectedSizePreset" @change="applySizePreset">
            <option value="50x30">50mm x 30mm</option>
            <option value="40x30">40mm x 30mm</option>
            <option value="60x40">60mm x 40mm</option>
            <option value="70x50">70mm x 50mm</option>
            <option value="100x50">100mm x 50mm</option>
            <option value="custom">Custom (mm)</option>
          </select>
        </div>

        <div class="config-group" v-if="selectedSizePreset === 'custom'">
          <label>W x H (mm)</label>
          <div style="display:flex; gap:5px;">
            <input type="number" v-model="templateConfig.width_mm" style="width:60px">
            <input type="number" v-model="templateConfig.height_mm" style="width:60px">
          </div>
        </div>

        <div class="actions">
          <button 
            v-if="currentTemplateId" 
            @click="deleteTemplate" 
            class="btn-danger-outline" 
            :disabled="saving"
            style="margin-right: 10px;"
          >
            🗑️ Hapus
          </button>

          <button @click="saveTemplate" class="btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : (currentTemplateId ? '💾 UPDATE' : '💾 SIMPAN BARU') }}
          </button>
        </div>
      </div>
    </div>

    <div class="workspace">
      
      <div class="sidebar">
        
        <div class="tool-section">
          <h3>📂 Data Field ({{ getModuleName(templateConfig.module_scope) }})</h3>
          
          <div v-if="isLoading" class="loading-text">Memuat field...</div>
          
          <div v-else class="grid-tools">
            <button 
              v-for="field in currentModuleFields" 
              :key="field.id"
              @click="addElement('variable', field.field_key, field.field_label)" 
              class="tool-btn var"
              :title="'Preview: ' + field.dummy_data"
            >
              {{ field.field_label }}
            </button>
          </div>
          
          <small v-if="!isLoading && currentModuleFields.length === 0" style="color:#ef4444; font-size:0.8rem;">
            Pilih Modul yang benar.
          </small>
        </div>

        <div class="tool-section">
          <h3>🔣 Elemen Statis</h3>
          <button @click="addElement('text', 'Teks Label', 'Teks')" class="tool-btn">
            🔤 Teks Bebas
          </button>
          <button @click="addElement('qrcode', 'QR_DATA', 'QR Code')" class="tool-btn qr">
            🔳 QR Code
          </button>
        </div>
        
        <div v-if="selectedId !== null" class="properties-panel">
          <h3>⚙️ Properties</h3>
          
          <div v-if="activeElement.type === 'text'" class="form-group">
            <label>Isi Teks</label>
            <input v-model="activeElement.content">
          </div>

          <div v-if="activeElement.type === 'variable'" class="form-group">
            <label>Variable Source</label>
            <input :value="activeElement.content" disabled style="background:#f1f5f9; color:#64748b;">
          </div>

          <div v-if="activeElement.type === 'qrcode'" class="form-group">
            <label>🔍 Sumber Data QR</label>
            <select v-model="activeElement.qr_source_key">
              <option value="custom_text">-- Teks Statis --</option>
              <option 
                v-for="field in currentModuleFields" 
                :key="field.id" 
                :value="field.field_key"
              >
                {{ field.field_label }}
              </option>
            </select>
            <input 
              v-if="activeElement.qr_source_key === 'custom_text'"
              v-model="activeElement.content" 
              placeholder="Isi teks QR..." 
              style="margin-top:5px;"
            >
          </div>

          <div class="form-group">
            <label>{{ activeElement.type === 'qrcode' ? 'Lebar (px)' : 'Font Size (px)' }}</label>
            <input type="number" v-model="activeElement.fontSize">
          </div>

          <div class="form-group">
            <label>Posisi (X, Y)</label>
            <div style="display:flex; gap:5px;">
              <input type="number" v-model="activeElement.x">
              <input type="number" v-model="activeElement.y">
            </div>
          </div>

          <button @click="deleteElement" class="btn-danger">🗑️ Hapus Elemen</button>
        </div>

        <div v-else class="info-box">
          Klik elemen di canvas untuk mengedit.
        </div>
      </div>

      <div class="canvas-container">
        <div class="canvas-wrapper">
          <div 
            class="canvas" 
            ref="canvasRef"
            @mousedown.self="deselect"
            :style="canvasStyle"
          >
            <div
              v-for="el in elements"
              :key="el.id"
              class="draggable-item"
              :class="{ selected: selectedId === el.id }"
              :style="{ 
                left: el.x + 'px', 
                top: el.y + 'px', 
                fontSize: el.fontSize + 'px',
                width: el.type === 'qrcode' ? el.fontSize + 'px' : 'auto',
                fontWeight: el.type === 'variable' ? 'bold' : 'normal'
              }"
              @mousedown.stop="startDrag($event, el.id)"
            >
              <span v-if="el.type === 'text'">{{ el.content }}</span>
              <span v-if="el.type === 'variable'" class="var-tag">
                [{{ el.placeholder_label || 'VAR' }}]
              </span>
              <div v-if="el.type === 'qrcode'" style="position:relative;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=PREVIEW" style="width:100%; pointer-events:none; opacity:0.8;" />
                <span class="qr-label-overlay">{{ getQrLabel(el.qr_source_key) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="canvas-info">
          {{ templateConfig.width_mm }}mm x {{ templateConfig.height_mm }}mm 
          <span style="opacity:0.7">({{ Math.round(templateConfig.width_mm * MM_TO_PX) }}px x {{ Math.round(templateConfig.height_mm * MM_TO_PX) }}px)</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';
const MM_TO_PX = 3.78; 

// --- INTERFACES ---
interface LabelField { id: number; field_key: string; field_label: string; dummy_data: string; }
interface LabelModule { id: number; name: string; code: string; fields: LabelField[]; }
interface DesignElement { id: number; type: 'text'|'variable'|'qrcode'; x: number; y: number; content: string; placeholder_label?: string; fontSize: number; qr_source_key?: string; }
interface SavedTemplate { id: number; name: string; module_scope: string; width_mm: number; height_mm: number; design_schema: DesignElement[]; }

// --- STATE ---
const modulesList = ref<LabelModule[]>([]);
const savedTemplates = ref<SavedTemplate[]>([]); // List template untuk dropdown

const isLoading = ref(true);
const saving = ref(false);

// State Edit Mode
const currentTemplateId = ref<number | null>(null);
const selectedLoadId = ref<number | null>(null);

const templateConfig = reactive({
  name: '',
  module_scope: '', 
  width_mm: 100,
  height_mm: 50
});

const selectedSizePreset = ref('100x50');
const selectedId = ref<number | null>(null);
const elements = ref<DesignElement[]>([]); 

// --- COMPUTED ---
const activeElement = computed(() => elements.value.find(e => e.id === selectedId.value) || {} as any);

const currentModuleFields = computed(() => {
  const mod = modulesList.value.find(m => m.code === templateConfig.module_scope);
  return mod ? mod.fields : [];
});

const canvasStyle = computed(() => ({
  width: `${templateConfig.width_mm * MM_TO_PX}px`,
  height: `${templateConfig.height_mm * MM_TO_PX}px`
}));

// --- LOAD DATA ---
onMounted(async () => {
  await fetchInitialData();
  resetWorkspace(); // Set default state
});

const fetchInitialData = async () => {
  isLoading.value = true;
  try {
    const [resMod, resTpl] = await Promise.all([
      axios.get(`${API_URL}/label-modules/`),
      axios.get(`${API_URL}/templates/`)
    ]);
    modulesList.value = resMod.data;
    savedTemplates.value = resTpl.data;
  } catch (e) {
    console.error(e);
    alert("Gagal memuat data server.");
  } finally {
    isLoading.value = false;
  }
};

// --- LOGIC LOAD / RESET ---

const resetWorkspace = () => {
  currentTemplateId.value = null;
  selectedLoadId.value = null;
  selectedId.value = null;
  
  templateConfig.name = 'Template Baru';
  templateConfig.width_mm = 100;
  templateConfig.height_mm = 50;
  selectedSizePreset.value = '100x50';
  
  elements.value = [{ id: Date.now(), type: 'text', x: 10, y: 10, content: 'LABEL BARU', fontSize: 12 }];

  // PERBAIKAN 1: Cek existence sebelum akses index 0
  const firstMod = modulesList.value[0];
  if (firstMod) {
    templateConfig.module_scope = firstMod.code;
  }
};

const loadTemplate = () => {
  if (!selectedLoadId.value) return;

  const tpl = savedTemplates.value.find(t => t.id === selectedLoadId.value);
  if (!tpl) return;

  // Isi State dengan data Database
  currentTemplateId.value = tpl.id;
  templateConfig.name = tpl.name;
  templateConfig.module_scope = tpl.module_scope;
  templateConfig.width_mm = tpl.width_mm;
  templateConfig.height_mm = tpl.height_mm;
  
  if (Array.isArray(tpl.design_schema)) {
     elements.value = JSON.parse(JSON.stringify(tpl.design_schema)); 
  } else {
     elements.value = [];
  }

  const sizeStr = `${tpl.width_mm}x${tpl.height_mm}`;
  if (['50x30','40x30','60x40','70x50','100x50'].includes(sizeStr)) {
    selectedSizePreset.value = sizeStr;
  } else {
    selectedSizePreset.value = 'custom';
  }

  selectedId.value = null;
};

// --- CRUD LOGIC ---

const getModuleName = (code: string) => {
  const mod = modulesList.value.find(m => m.code === code);
  return mod ? mod.name : code;
};

const getQrLabel = (key?: string) => {
  if (!key || key === 'custom_text') return 'TXT';
  const field = currentModuleFields.value.find(f => f.field_key === key);
  return field ? field.field_label.substring(0, 8) : 'VAR';
};

const applySizePreset = () => {
  if (selectedSizePreset.value === 'custom') return;
  
  // PERBAIKAN 2: Destructuring dan Validasi tipe data Number
  const parts = selectedSizePreset.value.split('x').map(Number);
  const w = parts[0];
  const h = parts[1];

  // Pastikan w dan h adalah number (bukan undefined) sebelum assign
  if (typeof w === 'number' && typeof h === 'number' && !isNaN(w) && !isNaN(h)) {
    templateConfig.width_mm = w;
    templateConfig.height_mm = h;
  }
};

let isDragging = false;
let dragOffset = { x: 0, y: 0 }; 

const startDrag = (e: MouseEvent, id: number) => {
  selectedId.value = id;
  isDragging = true; // Set status dragging

  const el = elements.value.find(item => item.id === id);
  
  if (el) {
    // 2. Hitung jarak antara posisi mouse dan pojok kiri-atas elemen
    // Agar saat digeser, elemen tidak 'lompat' ke posisi mouse
    dragOffset.x = e.clientX - el.x;
    dragOffset.y = e.clientY - el.y;

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  }
};

const onMouseMove = (e: MouseEvent) => {
  // Cek apakah sedang dragging dan ada elemen terpilih
  if (!isDragging || selectedId.value === null) return;
  
  const el = elements.value.find(item => item.id === selectedId.value);
  
  if (el) {
    // 3. Update posisi elemen berdasarkan posisi mouse dikurangi offset awal
    // Ini memperbaiki error karena kita memakai 'e' dan 'dragOffset'
    el.x = e.clientX - dragOffset.x;
    el.y = e.clientY - dragOffset.y;
  }
};

const onMouseUp = () => {
  isDragging = false;
  window.removeEventListener('mousemove', onMouseMove);
  window.removeEventListener('mouseup', onMouseUp);
};

const deselect = () => selectedId.value = null;

const addElement = (type: any, content: string, label?: string) => {
  const newEl: DesignElement = {
    id: Date.now(),
    type, x: 10, y: 10, content, placeholder_label: label,
    fontSize: type === 'qrcode' ? 60 : 12,
  };
  if (type === 'qrcode') { newEl.qr_source_key = 'custom_text'; newEl.content = 'QR DATA'; }
  elements.value.push(newEl);
};

const deleteElement = () => {
  if (selectedId.value !== null) {
    elements.value = elements.value.filter(e => e.id !== selectedId.value);
    selectedId.value = null;
  }
};

// --- SAVE & UPDATE ---
const saveTemplate = async () => {
  if (!templateConfig.name) { alert("Nama Template wajib diisi!"); return; }
  saving.value = true;

  const wPx = templateConfig.width_mm * MM_TO_PX;
  const hPx = templateConfig.height_mm * MM_TO_PX;

  let html = `<div style="position:relative; width:${wPx}px; height:${hPx}px; border:1px solid #000; overflow:hidden; font-family:Arial, sans-serif; background:white;">`;
  elements.value.forEach(el => {
    let contentHtml = el.content;
    if(el.type === 'qrcode') {
      const source = el.qr_source_key === 'custom_text' ? el.content : el.qr_source_key;
      contentHtml = `<img src="{{ qr_code }}" data-qr-source="${source}" style="width:100%; height:100%; display:block;" />`;
    }
    html += `<div style="position:absolute; left:${el.x}px; top:${el.y}px; font-size:${el.fontSize}px; width:${el.type==='qrcode'?el.fontSize+'px':'auto'}; white-space:nowrap;">${contentHtml}</div>`;
  });
  html += `</div>`;

  const payload = {
    name: templateConfig.name,
    module_scope: templateConfig.module_scope,
    width_mm: templateConfig.width_mm,
    height_mm: templateConfig.height_mm,
    design_schema: elements.value,
    html_content: html
  };

  try {
    if (currentTemplateId.value) {
      await axios.put(`${API_URL}/templates/${currentTemplateId.value}/`, payload);
      alert("Template berhasil di-UPDATE!");
    } else {
      await axios.post(`${API_URL}/templates/`, payload);
      alert("Template berhasil di-SIMPAN!");
    }
    await fetchInitialData(); 
  } catch (e) {
    console.error(e);
    alert("Gagal menyimpan.");
  } finally {
    saving.value = false;
  }
};

const deleteTemplate = async () => {
  if (!currentTemplateId.value) return;
  if (!confirm("Yakin ingin menghapus template ini?")) return;
  
  saving.value = true;
  try {
    await axios.delete(`${API_URL}/templates/${currentTemplateId.value}/`);
    alert("Template dihapus.");
    await fetchInitialData();
    resetWorkspace();
  } catch(e) {
    alert("Gagal menghapus.");
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
.designer-page { padding: 20px; max-width: 1400px; margin: 0 auto; color: #1e293b; }

.header-section { margin-bottom: 20px; }
.header-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.header-top h2 { margin: 0; color: #334155; }

/* CONFIG BAR */
.config-bar { 
  background: white; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; 
  display: flex; gap: 15px; align-items: flex-end; flex-wrap: wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.load-group { min-width: 200px; flex-grow: 1; max-width: 300px; }
.load-group select { border-color: #2563eb; background: #eff6ff; font-weight: 600; }
.divider { width: 1px; background: #e2e8f0; height: 40px; margin: 0 10px; }

.config-group { display: flex; flex-direction: column; gap: 5px; }
.config-group label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; }
.config-group input, .config-group select { padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; min-width: 120px; }
.actions { margin-left: auto; display: flex; }

/* WORKSPACE LAYOUT */
.workspace { display: flex; gap: 20px; height: 700px; }
.sidebar { width: 300px; background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; overflow-y: auto; }

/* TOOL BUTTONS */
.tool-section { margin-bottom: 20px; }
.tool-section h3 { font-size: 0.8rem; color: #94a3b8; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; border-bottom: 1px solid #f1f5f9; padding-bottom: 5px; }
.loading-text { font-size: 0.8rem; color: #94a3b8; font-style: italic; }

.grid-tools { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.tool-btn { 
  padding: 8px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; 
  cursor: pointer; text-align: left; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; transition: all 0.2s;
}
.tool-btn:hover { background: #e2e8f0; transform: translateY(-1px); }
.tool-btn.var { border-left: 3px solid #2563eb; color: #1e293b; }
.tool-btn.qr { border-left: 3px solid #0f172a; width: 100%; margin-bottom: 5px; }

/* CANVAS AREA */
.canvas-container { flex: 1; background: #94a3b8; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 8px; position: relative; overflow: hidden; }
.canvas-wrapper { padding: 50px; overflow: auto; max-width: 100%; max-height: 100%; }
.canvas { background: white; position: relative; box-shadow: 0 20px 50px rgba(0,0,0,0.5); transition: width 0.3s, height 0.3s; }

/* DRAGGABLE ITEMS */
.draggable-item { position: absolute; cursor: grab; padding: 0; line-height: 1; user-select: none; border: 1px dashed transparent; }
.draggable-item:hover { border-color: #cbd5e1; }
.draggable-item.selected { border: 1px solid #2563eb; background: rgba(37, 99, 235, 0.05); z-index: 10; }
.var-tag { color: #2563eb; font-family: monospace; background: rgba(37, 99, 235, 0.1); padding: 2px 4px; border-radius: 2px; font-size: 0.9em; }

.qr-label-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0,0,0,0.7); color: white; padding: 2px 5px; font-size: 10px; border-radius: 3px; white-space: nowrap; }

/* PROPERTIES PANEL */
.properties-panel { margin-top: auto; padding-top: 15px; border-top: 2px solid #f1f5f9; }
.form-group { margin-bottom: 10px; }
.form-group label { display: block; font-size: 0.75rem; font-weight: 600; color: #64748b; margin-bottom: 3px; }
.form-group input, .form-group select { width: 100%; padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.9rem; }
.info-box { margin-top: auto; text-align: center; color: #94a3b8; font-style: italic; font-size: 0.9rem; padding: 20px 0; }

.btn-primary { background: #2563eb; color: white; padding: 10px 24px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 0.9rem; transition: background 0.2s; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }

.btn-secondary { background: #64748b; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.9rem; }
.btn-secondary:hover { background: #475569; }

.btn-danger { background: #fee2e2; color: #ef4444; padding: 8px; width: 100%; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-top: 10px; }
.btn-danger:hover { background: #fecaca; }

.btn-danger-outline { background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-danger-outline:hover { background: #fef2f2; }

.canvas-info { margin-top: 10px; color: white; font-size: 0.85rem; font-family: monospace; background: rgba(0,0,0,0.6); padding: 5px 12px; border-radius: 20px; }
</style>