<template>
  <div class="vin-page">
    
    <div class="page-header">
      <div>
        <h2 class="title">Input VIN Baru</h2>
        <p class="subtitle">Buat nomor rangka satuan atau generate masal.</p>
      </div>
    </div>

    <div v-if="!canRead" class="alert-box error">
      ⛔ <strong>Akses Ditolak</strong><br>Anda tidak memiliki izin untuk melihat halaman ini.
    </div>

    <div v-else class="main-card">
      
      <div class="tabs-header">
        <button :class="['tab-btn', { active: activeTab === 'single' }]" @click="activeTab = 'single'">
          <span class="icon">📝</span> Single Record
        </button>
        <button :class="['tab-btn', { active: activeTab === 'batch' }]" @click="activeTab = 'batch'">
          <span class="icon">📦</span> Batch Generate
        </button>
      </div>

      <div class="card-body">
        
        <form v-if="activeTab === 'single'" @submit.prevent="handleSingleSubmit">
          <div class="form-grid">
            <div class="form-group">
              <label>Tahun Produksi</label>
              <select v-model="form.production_year" required>
                <option :value="null" disabled>-- Pilih Tahun --</option>
                <option v-for="y in masterData.years" :key="y.id" :value="y.id">
                  {{ y.year }} (Kode: {{ y.code }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Tipe Produk</label>
              <select v-model="selectedType" @change="resetChildDropdowns" required>
                <option :value="null" disabled>-- Pilih Produk --</option>
                <option v-for="t in traceableTypes" :key="t.id" :value="t">{{ t.name }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Varian</label>
              <select v-model="form.variant" :disabled="!selectedType" required>
                <option :value="null">-- Pilih Varian --</option>
                <option v-for="v in filteredVariants" :key="v.id" :value="v.id">{{ v.name }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Warna</label>
              <select v-model="form.color" :disabled="!selectedType" required>
                <option :value="null">-- Pilih Warna --</option>
                <option v-for="c in filteredColors" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>

            <div class="form-group full-width">
              <label>Serial Number (6 Digit)</label>
              <input type="text" v-model="form.serial_number" maxlength="6" placeholder="000123" class="input-lg font-mono" required />
            </div>
          </div>

          <div class="preview-container">
            <div class="preview-header">PREVIEW VIN</div>
            <div class="lcd-display">
               {{ singleVinPreview }}
            </div>
          </div>

          <div class="print-settings">
            <div class="settings-header">
               <span>🖨️ Opsi Cetak Label</span>
               <label class="switch-sm">
                  <input type="checkbox" v-model="printConfig.is_print">
                  <span class="slider round"></span>
               </label>
            </div>
            <div v-if="printConfig.is_print" class="settings-body">
               <div class="form-group grow">
                 <label>Template Desain</label>
                 <select v-model="printConfig.templateId">
                    <option :value="null">Default Template</option>
                    <option v-for="t in printTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
                 </select>
               </div>
               <div class="form-group short">
                 <label>Copy</label>
                 <input type="number" v-model="printConfig.copies" min="1">
               </div>
            </div>
          </div>

          <div class="form-actions">
             <div v-if="status.msg" :class="['status-msg', status.type]">{{ status.msg }}</div>
             <button v-if="canCreate" type="submit" class="btn-save" :disabled="status.loading">
               {{ status.loading ? 'Menyimpan...' : 'SIMPAN DATA' }}
             </button>
          </div>
        </form>

        <form v-else @submit.prevent="handleBatchSubmit">
           <div class="form-grid">
              <div class="form-group">
                  <label>Tahun</label>
                  <select v-model="batchForm.production_year" required>
                      <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Tipe Produk</label>
                  <select v-model="batchSelectedType" required>
                      <option v-for="t in traceableTypes" :key="t.id" :value="t">{{ t.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Varian</label>
                  <select v-model="batchForm.variant">
                      <option v-for="v in batchFilteredVariants" :key="v.id" :value="v.id">{{ v.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Warna</label>
                  <select v-model="batchForm.color">
                      <option v-for="c in batchFilteredColors" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Start Serial</label>
                  <input v-model="batchForm.start_serial" class="font-mono input-lg" placeholder="000100" maxlength="6" required/>
              </div>
              <div class="form-group">
                  <label>Quantity</label>
                  <input type="number" v-model="batchForm.quantity" min="1" max="1000" class="input-lg" required/>
              </div>
           </div>

           <div class="preview-container batch">
              <div class="preview-header">ESTIMASI RANGE VIN</div>
              <div class="lcd-display sm">
                 {{ batchPreview.start }} <span class="arrow">➜</span> {{ batchPreview.end }}
              </div>
           </div>

           <div class="print-settings">
              <div class="settings-header">
                <span>🖨️ Auto Print Batch</span>
                <label class="switch-sm">
                    <input type="checkbox" v-model="printConfig.is_print">
                    <span class="slider round"></span>
                </label>
              </div>

              <div v-if="printConfig.is_print" class="settings-body">
                <div class="form-group grow">
                  <label>Template Desain</label>
                  <select v-model="printConfig.templateId">
                      <option :value="null">Default Template</option>
                      <option v-for="t in printTemplates" :key="t.id" :value="t.id">
                        {{ t.name }} ({{ t.width }}x{{ t.height }}mm)
                      </option>
                  </select>
                </div>
                <div class="form-group short">
                  <label>Copy</label>
                  <input type="number" v-model="printConfig.copies" min="1">
                </div>
              </div>
            </div>

           <div class="form-actions">
              <span v-if="status.msg" :class="['status-msg', status.type]">{{ status.msg }}</span>
              <button v-if="canCreate" type="submit" class="btn-save batch" :disabled="status.loading">
                 {{ status.loading ? 'Memproses...' : 'GENERATE BATCH' }}
              </button>
           </div>
        </form>

      </div>
    </div>

    <div style="position:absolute; left:-9999px; top:-9999px;">
       <div ref="printRef" v-html="renderedPrintHtml" class="print-canvas"></div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../../../stores/auth';
import { usePrintStore } from '../../../stores/print';
import { toPng } from 'html-to-image';
import QRCode from 'qrcode';

// --- CONFIG API ---
const BASE_API = 'http://127.0.0.1:8000/api';
const PRODUCT_API = `${BASE_API}/product`;
const VIN_API = `${BASE_API}/vin-record`;
const CORE_API = `${BASE_API}`; 

const authStore = useAuthStore();
const printStore = usePrintStore();

// --- 1. CORE LOGIC: ISO 3779 CHECK DIGIT CALCULATOR (FRONTEND VERSION) ---
const calculateCheckDigit = (vin17chars: string): string => {
    // Kamus Transliterasi
    const transliteration: Record<string, number> = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0
    };
    // Bobot Posisi
    const weights: number[] = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2];
    
    let total = 0;
    const chars = vin17chars.toUpperCase().split('');
    
    // Loop strict 17 kali
    for (let i = 0; i < 17; i++) {
        if (i === 8) continue; // Skip posisi Check Digit (Index 8)

        const char = chars[i];
        const weight = weights[i];

        // Validasi ketat untuk TypeScript Strict Mode
        if (char === undefined || weight === undefined) return '?';

        const val = transliteration[char];
        if (val === undefined) return '?'; // Karakter tidak valid

        total += val * weight;
    }
    
    const remainder = total % 11;
    return remainder === 10 ? 'X' : remainder.toString();
};

// --- 2. CORE LOGIC: VIN ASSEMBLER ---
const generateFullVIN = (typeObj: any, yearId: number|null, serial: string): string => {
    // Jika data belum lengkap, return placeholder
    if (!typeObj || !yearId) return '_________________';

    // A. Ambil Data Prefix
    // Kita cari prefix yang cocok di array masterData.prefixes
    let prefixData = { wmi_vds: '', plant: '', staticDigit: '0' };
    
    if (masterData.prefixes.length > 0) {
        const found = masterData.prefixes.find((p:any) => 
            p.product_type === typeObj.id && 
            (p.year_code === yearId || p.year_id === yearId)
        );
        if (found) {
            prefixData = { 
                wmi_vds: found.wmi_vds, 
                plant: found.plant_code, 
                staticDigit: found.static_ninth_digit 
            };
        }
    }

    // B. Ambil Kode Tahun
    const yearCode = masterData.years.find((y:any) => y.id === yearId)?.code || '?';
    
    // C. Format Serial Number (Pastikan 6 Digit)
    const serialStr = (serial || '').padEnd(6, '0');

    // D. Tentukan Logic Check Digit
    // PENTING: Sesuaikan nama field dengan API/Model Backend Anda ('has_check_digit')
    const useAlgorithm = typeObj.has_check_digit === true; 
    
    // Default pakai Static
    let ninthDigit = prefixData.staticDigit || '0';
    
    // E. Susun VIN Sementara
    // Format: WMI_VDS (8) + DUMMY (1) + YEAR (1) + PLANT (1) + SERIAL (6)
    const tempVin = `${prefixData.wmi_vds}0${yearCode}${prefixData.plant}${serialStr}`;

    // F. Hitung Check Digit (Jika Config Aktif & Panjang VIN Valid)
    if (useAlgorithm && tempVin.length === 17) {
        ninthDigit = calculateCheckDigit(tempVin);
    }

    // G. Return Hasil Akhir
    return `${prefixData.wmi_vds}${ninthDigit}${yearCode}${prefixData.plant}${serialStr}`;
};

// --- DEFAULT TEMPLATE ---
const defaultTemplate = `
<div style="width:300px; height:150px; border:2px solid #000; padding:10px; font-family:Arial; box-sizing:border-box; background:white; position:relative;">
    <h2 style="margin:0; font-size:18px; text-align:center; border-bottom:1px solid #000; padding-bottom:5px;">VIN LABEL</h2>
    <div style="display:flex; align-items:center; margin-top:10px;">
        <img src="{{ qr_code }}" width="80" height="80" />
        <div style="margin-left:10px; flex:1;">
            <div style="font-weight:bold; font-size:16px; margin-bottom:5px;">{{ full_vin }}</div>
            <div style="font-size:12px;">{{ type_name }} - {{ variant_name }}</div>
            <div style="font-size:11px;">Color: {{ color_name }}</div>
        </div>
    </div>
</div>
`;

// --- STATE ---
const activeTab = ref('single');
const status = reactive({ loading: false, msg: '', type: '' });
const masterData = reactive({ types: [] as any[], years: [] as any[], prefixes: [] as any[] });
const printTemplates = ref<any[]>([]);

// Form State
const selectedType = ref<any>(null);
const form = reactive({ production_year: null as number|null, variant: null, color: null, serial_number: '' });
const batchSelectedType = ref<any>(null);
const batchForm = reactive({ production_year: null as number|null, variant: null, color: null, start_serial: '', quantity: null as number|null });

// Printing State
const printConfig = reactive({ is_print: true, copies: 1, templateId: null as number | null });
const printRef = ref<HTMLElement|null>(null);
const printData = reactive({ full_vin: '', qr: '', type_name: '', variant_name: '', color_name: '' });

// RBAC
const canRead = computed(() => authStore.can('vin_record', 'read'));
const canCreate = computed(() => authStore.can('vin_record', 'create'));

// Filtering
// Filter Traceable: Pastikan field backend 'is_vin_trace'
const traceableTypes = computed(() => masterData.types.filter(t => t.is_vin_trace === true));

const filteredVariants = computed(() => selectedType.value?.variants || []);
const filteredColors = computed(() => selectedType.value?.colors || []);
const batchFilteredVariants = computed(() => batchSelectedType.value?.variants || []);
const batchFilteredColors = computed(() => batchSelectedType.value?.colors || []);

// --- LOAD DATA ---
onMounted(async () => {
  if(!canRead.value) return;
  try {
    const [t, y, p, tmpl] = await Promise.all([ 
        axios.get(`${PRODUCT_API}/types/`), 
        axios.get(`${VIN_API}/years/`),
        axios.get(`${VIN_API}/prefixes/`), 
        axios.get(`${CORE_API}/templates/`)
    ]);
    masterData.types = Array.isArray(t.data) ? t.data : t.data.results || [];
    masterData.years = Array.isArray(y.data) ? y.data : y.data.results || [];
    masterData.prefixes = Array.isArray(p.data) ? p.data : p.data.results || [];
    printTemplates.value = Array.isArray(tmpl.data) ? tmpl.data : tmpl.data.results || [];
    if(printTemplates.value.length > 0) printConfig.templateId = printTemplates.value[0].id;
  } catch(e) { console.error(e); }
});

// --- PREVIEW COMPUTED (LCD) ---
const singleVinPreview = computed(() => {
    // Fungsi ini dipanggil realtime saat user mengetik
    return generateFullVIN(selectedType.value, form.production_year, form.serial_number);
});

const batchPreview = computed(() => {
    // Preview Start & End untuk Batch
    if (!batchForm.start_serial || !batchForm.quantity || !batchSelectedType.value) {
        return { start: '.............', end: '.............' };
    }
    const startNum = parseInt(batchForm.start_serial);
    const endNum = startNum + (batchForm.quantity - 1);
    
    // Generate VIN Lengkap (termasuk Check Digit) untuk Start dan End
    const vStart = generateFullVIN(batchSelectedType.value, batchForm.production_year, startNum.toString());
    const vEnd = generateFullVIN(batchSelectedType.value, batchForm.production_year, endNum.toString());

    return { start: vStart, end: vEnd };
});

const resetChildDropdowns = () => { form.variant = null; form.color = null; };
watch(batchSelectedType, () => { batchForm.variant = null; batchForm.color = null; });

// --- SUBMIT SINGLE ---
const handleSingleSubmit = async () => {
  if (!canCreate.value) return;
  if (form.serial_number.length !== 6) { status.msg = "Serial harus 6 digit angka!"; status.type = "error"; return; }
  
  status.loading = true; status.msg = ""; 
  try {
    // Kita kirim VIN yang sudah dihitung Frontend (agar sama dengan preview), 
    // tapi ingat Backend tetap akan menghitung ulang untuk keamanan.
    const finalVin = generateFullVIN(selectedType.value, form.production_year, form.serial_number);
    
    const payload = {
      product_type: selectedType.value?.id,
      production_year: form.production_year,
      variant: form.variant, 
      color: form.color, 
      serial_number: form.serial_number,
      full_vin: finalVin
    };
    await axios.post(`${VIN_API}/records/`, payload);
    status.msg = "VIN Berhasil Dibuat!"; status.type = "success";
    
    // Print pakai VIN hasil frontend yang sudah ada check digitnya
    if (printConfig.is_print) await executePrint(finalVin);
    
    form.serial_number = ""; 
  } catch (error: any) {
    status.msg = "Gagal: " + (error.response?.data?.detail || "Cek inputan"); status.type = "error";
  } finally { status.loading = false; }
};

// --- SUBMIT BATCH ---
const handleBatchSubmit = async () => {
  if (!canCreate.value) return;
  status.loading = true; status.msg = "Menyimpan ke Database...";
  
  try {
    // 1. Simpan ke Backend (Backend akan hitung ulang & simpan)
    const res = await axios.post(`${VIN_API}/records/batch-generate/`, {
       product_type: batchSelectedType.value?.id,
       production_year: batchForm.production_year,
       variant: batchForm.variant,
       color: batchForm.color,
       start_serial: batchForm.start_serial,
       quantity: batchForm.quantity
    });
    status.msg = `Database OK: ${res.data.message}`; status.type = "success";
    
    // 2. Proses Printing (Frontend Side)
    // Disini Frontend harus menghitung ulang Check Digit agar label yang diprint benar
    if (printConfig.is_print && batchForm.quantity) {
         status.msg = "Mencetak label...";
         
         const typeName = batchSelectedType.value?.name || '-';
         const variantName = batchSelectedType.value?.variants?.find((v:any) => v.id === batchForm.variant)?.name || '-';
         const colorName = batchSelectedType.value?.colors?.find((c:any) => c.id === batchForm.color)?.name || '-';

         const start = parseInt(batchForm.start_serial);
         const qty = batchForm.quantity;

         for (let i = 0; i < qty; i++) {
            const currentSerial = (start + i).toString();
            
            // Generate Full VIN (Auto Check Digit)
            const fullVin = generateFullVIN(batchSelectedType.value, batchForm.production_year, currentSerial);
            
            await executePrint(fullVin, {
                type: typeName, variant: variantName, color: colorName
            });
            
            // Delay minimal agar DOM update
            await new Promise(r => setTimeout(r, 50)); 
         }
         status.msg = "Selesai!";
    }
    batchForm.quantity = null; batchForm.start_serial = '';
  } catch(e: any) {
    status.msg = e.response?.data?.detail || "Batch Gagal"; status.type = "error";
  } finally { status.loading = false; }
};

// --- PRINT ENGINE ---
const renderedPrintHtml = computed(() => {
   let tmpl = null;
   if (printConfig.templateId) tmpl = printTemplates.value.find(t => t.id === printConfig.templateId);
   let html = tmpl ? (tmpl.design_data || tmpl.html_content) : defaultTemplate;
   html = html.replace(/{{ full_vin }}/g, printData.full_vin); 
   html = html.replace(/{{ qr_code }}/g, printData.qr);
   html = html.replace(/{{ type_name }}/g, printData.type_name);
   html = html.replace(/{{ variant_name }}/g, printData.variant_name);
   html = html.replace(/{{ color_name }}/g, printData.color_name);
   const style = tmpl ? `width:${tmpl.width}mm; height:${tmpl.height}mm; overflow:hidden;` : '';
   return `<div style="background:white; position:relative; ${style}">${html}</div>`;
});

const executePrint = async (vinStr: string, metadata: any = null) => {
   try {
     printData.full_vin = vinStr; 
     printData.qr = await QRCode.toDataURL(vinStr);
     if (metadata) {
         printData.type_name = metadata.type; printData.variant_name = metadata.variant; printData.color_name = metadata.color;
     } else {
         printData.type_name = selectedType.value?.name || '-';
         const v = filteredVariants.value.find((i:any) => i.id === form.variant);
         printData.variant_name = v ? v.name : '-';
         const c = filteredColors.value.find((i:any) => i.id === form.color);
         printData.color_name = c ? c.name : '-';
     }
     await nextTick(); 
     if(printRef.value) {
        const element = printRef.value.firstElementChild as HTMLElement;
        const url = await toPng(element, { quality: 1, pixelRatio: 2 });
        await printStore.silentPrint(url, printConfig.copies);
     }
   } catch(e) { console.error(e); }
};
</script>

<style scoped>
/* CSS Sama seperti sebelumnya */
.vin-page { max-width: 800px; margin: 0 auto; padding: 20px 20px 60px; }
.page-header { text-align: center; margin-bottom: 30px; }
.title { font-size: 1.8rem; color: #1e293b; margin: 0; font-weight: 800; }
.subtitle { color: #64748b; font-size: 0.95rem; margin-top: 5px; }
.main-card { background: white; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); overflow: hidden; border: 1px solid #e2e8f0; }
.tabs-header { display: grid; grid-template-columns: 1fr 1fr; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; }
.tab-btn { padding: 16px; border: none; background: transparent; font-weight: 600; color: #64748b; font-size: 1rem; cursor: pointer; transition: all 0.2s; border-bottom: 3px solid transparent; display: flex; align-items: center; justify-content: center; gap: 8px; }
.tab-btn:hover { background: #e2e8f0; color: #334155; }
.tab-btn.active { background: white; color: #2563eb; border-bottom-color: #2563eb; }
.card-body { padding: 30px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.full-width { grid-column: span 2; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
label { font-weight: 600; font-size: 0.9rem; color: #475569; }
input, select { padding: 12px 16px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; color: #1e293b; transition: all 0.2s; background: #fff; }
input:focus, select:focus { border-color: #2563eb; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1); outline: none; }
.input-lg { font-size: 1.2rem; padding: 14px; text-align: center; letter-spacing: 2px; }
.input-mono { font-family: 'Courier New', monospace; font-weight: bold; }
.preview-container { background: #0f172a; border-radius: 12px; padding: 20px; margin: 30px 0; border: 4px solid #334155; text-align: center; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }
.preview-header { color: #64748b; font-size: 0.75rem; letter-spacing: 1px; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; }
.lcd-display { font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: 700; color: #fbbf24; letter-spacing: 4px; text-shadow: 0 0 10px rgba(251, 191, 36, 0.5); background: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; word-break: break-all; }
.lcd-display.sm { font-size: 1.5rem; }
.arrow { color: #64748b; margin: 0 10px; }
.print-settings { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; margin-bottom: 25px; }
.settings-header { padding: 12px 20px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #334155; }
.settings-body { padding: 15px 20px; display: flex; gap: 15px; align-items: flex-end; }
.grow { flex: 1; }
.short { width: 80px; }
.switch-sm { position: relative; display: inline-block; width: 36px; height: 20px; }
.switch-sm input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(16px); }
.form-actions { display: flex; flex-direction: column; gap: 15px; }
.btn-save { width: 100%; padding: 16px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); transition: all 0.2s; }
.btn-save:hover { background: #1d4ed8; transform: translateY(-1px); }
.btn-save:disabled { background: #94a3b8; cursor: not-allowed; }
.btn-save.batch { background: #0f172a; }
.status-msg { padding: 12px; border-radius: 8px; text-align: center; font-weight: 600; font-size: 0.95rem; }
.status-msg.success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.status-msg.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.read-only-badge { text-align: center; background: #f1f5f9; padding: 15px; color: #64748b; font-weight: bold; border-radius: 8px; }
.alert-box.error { padding: 20px; background: #fee2e2; color: #991b1b; text-align: center; border-radius: 8px; }
@media (max-width: 640px) {
    .vin-page { padding: 10px; }
    .card-body { padding: 20px; }
    .form-grid { grid-template-columns: 1fr; }
    .full-width { grid-column: span 1; }
    .settings-body { flex-direction: column; align-items: stretch; }
    .form-group.short { width: 100%; }
    .lcd-display { font-size: 1.5rem; }
}
</style>