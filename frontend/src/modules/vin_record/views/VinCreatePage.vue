<template>
  <div class="master-page">
    
    <div class="header">
      <h2>Input VIN Baru</h2>
      <p>Buat nomor rangka satuan atau generate masal.</p>
    </div>

    <div class="card main-form">
      
      <div class="tabs-header">
        <button :class="['tab-btn', { active: activeTab === 'single' }]" @click="activeTab = 'single'">
          📝 Single Record
        </button>
        <button :class="['tab-btn', { active: activeTab === 'batch' }]" @click="activeTab = 'batch'">
          📦 Batch Generate
        </button>
      </div>

      <div class="card-body">
        
        <form v-if="activeTab === 'single'" @submit.prevent="handleSingleSubmit">
          <div class="form-grid">
            <div class="form-group">
              <label>Tahun Produksi</label>
              <select v-model="form.production_year" required class="input-field">
                <option :value="null" disabled>-- Pilih Tahun --</option>
                <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }} ({{ y.code }})</option>
              </select>
            </div>

            <div class="form-group">
              <label>Tipe Produk</label>
              <select v-model="selectedType" @change="resetChildDropdowns" required class="input-field">
                <option :value="null" disabled>-- Pilih Produk --</option>
                <option v-for="t in traceableTypes" :key="t.id" :value="t">{{ t.name }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Varian</label>
              <select v-model="form.variant" :disabled="!selectedType" required class="input-field">
                <option :value="null">-- Pilih Varian --</option>
                <option v-for="v in filteredVariants" :key="v.id" :value="v.id">{{ v.name }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Warna</label>
              <select v-model="form.color" :disabled="!selectedType" required class="input-field">
                <option :value="null">-- Pilih Warna --</option>
                <option v-for="c in filteredColors" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>

            <div class="form-group full-width">
              <label>Serial Number (6 Digit)</label>
              <input type="text" v-model="form.serial_number" maxlength="6" placeholder="000123" class="input-field font-mono text-center text-lg" required />
            </div>
          </div>

          <div class="preview-box">
            <div class="preview-label">PREVIEW VIN</div>
            <div class="lcd-text">{{ singleVinPreview }}</div>
          </div>

          <div class="print-box">
            <div class="print-header">
               <span>🖨️ Opsi Cetak Label</span>
               <label class="toggle-switch">
                  <input type="checkbox" v-model="printConfig.is_print">
                  <span class="slider round"></span>
               </label>
            </div>
            <div v-if="printConfig.is_print" class="print-body">
               <div class="form-group flex-1">
                 <select v-model="printConfig.templateId" class="input-field">
                    <option :value="null">Default Template</option>
                    <option v-for="t in printTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
                 </select>
               </div>
               <div class="form-group w-24">
                 <input type="number" v-model="printConfig.copies" min="1" class="input-field text-center" placeholder="Qty">
               </div>
            </div>
          </div>

          <div class="action-bar">
             <div v-if="status.msg" :class="['status-msg', status.type]">{{ status.msg }}</div>
             <button v-if="canCreate" type="submit" class="btn-submit" :disabled="status.loading">
               {{ status.loading ? 'Menyimpan...' : 'SIMPAN DATA' }}
             </button>
          </div>
        </form>

        <form v-else @submit.prevent="handleBatchSubmit">
           <div class="form-grid">
              <div class="form-group">
                  <label>Tahun</label>
                  <select v-model="batchForm.production_year" required class="input-field">
                      <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Tipe Produk</label>
                  <select v-model="batchSelectedType" required class="input-field">
                      <option v-for="t in traceableTypes" :key="t.id" :value="t">{{ t.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Varian</label>
                  <select v-model="batchForm.variant" class="input-field">
                      <option :value="null">-- Default --</option>
                      <option v-for="v in batchFilteredVariants" :key="v.id" :value="v.id">{{ v.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Warna</label>
                  <select v-model="batchForm.color" class="input-field">
                      <option :value="null">-- Default --</option>
                      <option v-for="c in batchFilteredColors" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
              </div>
              <div class="form-group">
                  <label>Start Serial</label>
                  <input v-model="batchForm.start_serial" class="input-field font-mono text-center" placeholder="000100" maxlength="6" required/>
              </div>
              <div class="form-group">
                  <label>Quantity</label>
                  <input type="number" v-model="batchForm.quantity" min="1" max="1000" class="input-field text-center" required/>
              </div>
           </div>

           <div class="preview-box">
              <div class="preview-label">ESTIMASI RANGE VIN</div>
              <div class="lcd-text sm">
                 {{ batchPreview.start }} <span class="arrow">➜</span> {{ batchPreview.end }}
              </div>
           </div>

           <div class="print-box">
              <div class="print-header">
                 <span>🖨️ Auto Print Batch</span>
                 <label class="toggle-switch">
                    <input type="checkbox" v-model="printConfig.is_print">
                    <span class="slider round"></span>
                 </label>
              </div>
              <div v-if="printConfig.is_print" class="print-body">
                 <div class="form-group flex-1">
                   <select v-model="printConfig.templateId" class="input-field">
                      <option :value="null">Default Template</option>
                      <option v-for="t in printTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
                   </select>
                 </div>
                 <div class="form-group w-24">
                   <input type="number" v-model="printConfig.copies" min="1" class="input-field text-center" placeholder="Copy">
                 </div>
              </div>
           </div>

           <div class="action-bar">
              <div v-if="status.msg" :class="['status-msg', status.type]">{{ status.msg }}</div>
              <button v-if="canCreate" type="submit" class="btn-submit dark" :disabled="status.loading">
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
/* LOGIC SAMA PERSIS DENGAN SEBELUMNYA, TIDAK BERUBAH */
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { usePrintStore } from '@/stores/print';
import api from './api';
import { toPng } from 'html-to-image';
import QRCode from 'qrcode';

const authStore = useAuthStore();
const printStore = usePrintStore();

const calculateCheckDigit = (vin17chars: string): string => {
    const transliteration: Record<string, number> = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0
    };
    const weights: number[] = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2];
    let total = 0;
    const chars = vin17chars.toUpperCase().split('');
    for (let i = 0; i < 17; i++) {
        if (i === 8) continue;
        const char = chars[i];
        const weight = weights[i];
        if (char === undefined || weight === undefined) return '?';
        const val = transliteration[char];
        if (val === undefined) return '?';
        total += val * weight;
    }
    const remainder = total % 11;
    return remainder === 10 ? 'X' : remainder.toString();
};

const generateFullVIN = (typeObj: any, yearId: number|null, serial: string): string => {
    if (!typeObj || !yearId) return '_________________';
    let prefixData = { wmi_vds: '', plant: '', staticDigit: '0' };
    if (masterData.prefixes.length > 0) {
        const found = masterData.prefixes.find((p:any) => p.product_type === typeObj.id && (p.year_code === yearId || p.year_id === yearId));
        if (found) prefixData = { wmi_vds: found.wmi_vds, plant: found.plant_code, staticDigit: found.static_ninth_digit };
    }
    const yearCode = masterData.years.find((y:any) => y.id === yearId)?.code || '?';
    const serialStr = (serial || '').padEnd(6, '0');
    const useAlgorithm = typeObj.has_check_digit === true; 
    let ninthDigit = prefixData.staticDigit || '0';
    const tempVin = `${prefixData.wmi_vds}0${yearCode}${prefixData.plant}${serialStr}`;
    if (useAlgorithm && tempVin.length === 17) ninthDigit = calculateCheckDigit(tempVin);
    return `${prefixData.wmi_vds}${ninthDigit}${yearCode}${prefixData.plant}${serialStr}`;
};

const defaultTemplate = `<div style="width:300px; height:150px; border:2px solid #000; padding:10px;"><h2>VIN LABEL</h2>{{ full_vin }}</div>`;
const activeTab = ref('single');
const status = reactive({ loading: false, msg: '', type: '' });
const masterData = reactive({ types: [] as any[], years: [] as any[], prefixes: [] as any[] });
const printTemplates = ref<any[]>([]);
const selectedType = ref<any>(null);
const form = reactive({ production_year: null as number|null, variant: null, color: null, serial_number: '' });
const batchSelectedType = ref<any>(null);
const batchForm = reactive({ production_year: null as number|null, variant: null, color: null, start_serial: '', quantity: null as number|null });
const printConfig = reactive({ is_print: true, copies: 1, templateId: null as number | null });
const printRef = ref<HTMLElement|null>(null);
const printData = reactive({ full_vin: '', qr: '', type_name: '', variant_name: '', color_name: '' });
const canRead = computed(() => authStore.can('vin_record', 'read'));
const canCreate = computed(() => authStore.can('vin_record', 'create'));
const traceableTypes = computed(() => masterData.types.filter(t => t.tracking_mode === 'VIN'));
const filteredVariants = computed(() => selectedType.value?.variants || []);
const filteredColors = computed(() => selectedType.value?.colors || []);
const batchFilteredVariants = computed(() => batchSelectedType.value?.variants || []);
const batchFilteredColors = computed(() => batchSelectedType.value?.colors || []);

onMounted(async () => {
  if(!canRead.value) return;
  try {
    const [t, y, p, tmpl] = await Promise.all([api.getTraceableTypes(), api.getYears(), api.getPrefixes(), api.getTemplates()]);
    masterData.types = Array.isArray(t.data) ? t.data : t.data.results || [];
    masterData.years = Array.isArray(y.data) ? y.data : y.data.results || [];
    masterData.prefixes = Array.isArray(p.data) ? p.data : p.data.results || [];
    printTemplates.value = Array.isArray(tmpl.data) ? tmpl.data : tmpl.data.results || [];
    if(printTemplates.value.length > 0) printConfig.templateId = printTemplates.value[0].id;
  } catch(e) { console.error(e); }
});

const singleVinPreview = computed(() => generateFullVIN(selectedType.value, form.production_year, form.serial_number));
const batchPreview = computed(() => {
    if (!batchForm.start_serial || !batchForm.quantity || !batchSelectedType.value) return { start: '.............', end: '.............' };
    const startNum = parseInt(batchForm.start_serial);
    const endNum = startNum + (batchForm.quantity - 1);
    const vStart = generateFullVIN(batchSelectedType.value, batchForm.production_year, startNum.toString());
    const vEnd = generateFullVIN(batchSelectedType.value, batchForm.production_year, endNum.toString());
    return { start: vStart, end: vEnd };
});

const resetChildDropdowns = () => { form.variant = null; form.color = null; };
watch(batchSelectedType, () => { batchForm.variant = null; batchForm.color = null; });

const handleSingleSubmit = async () => {
  if (!canCreate.value) return;
  if (form.serial_number.length !== 6) { status.msg = "Serial harus 6 digit angka!"; status.type = "error"; return; }
  status.loading = true; status.msg = ""; 
  try {
    const finalVin = generateFullVIN(selectedType.value, form.production_year, form.serial_number);
    const payload = {
      product_type: selectedType.value?.id, production_year: form.production_year,
      variant: form.variant, color: form.color, serial_number: form.serial_number, full_vin: finalVin
    };
    await api.createRecord(payload);
    status.msg = "VIN Berhasil Dibuat!"; status.type = "success";
    if (printConfig.is_print) await executePrint(finalVin);
    form.serial_number = ""; 
  } catch (error: any) { status.msg = "Gagal: " + (error.response?.data?.detail || "Cek inputan"); status.type = "error";
  } finally { status.loading = false; }
};

const handleBatchSubmit = async () => {
  if (!canCreate.value) return;
  status.loading = true; status.msg = "Menyimpan ke Database...";
  try {
    const res = await api.batchGenerate({
       product_type: batchSelectedType.value?.id, production_year: batchForm.production_year,
       variant: batchForm.variant, color: batchForm.color, start_serial: batchForm.start_serial, quantity: batchForm.quantity
    });
    status.msg = `Database OK: ${res.data.message}`; status.type = "success";
    if (printConfig.is_print && batchForm.quantity) {
         status.msg = "Mencetak label...";
         const typeName = batchSelectedType.value?.name || '-';
         const variantName = batchSelectedType.value?.variants?.find((v:any) => v.id === batchForm.variant)?.name || '-';
         const colorName = batchSelectedType.value?.colors?.find((c:any) => c.id === batchForm.color)?.name || '-';
         const start = parseInt(batchForm.start_serial);
         const qty = batchForm.quantity;
         for (let i = 0; i < qty; i++) {
            const currentSerial = (start + i).toString();
            const fullVin = generateFullVIN(batchSelectedType.value, batchForm.production_year, currentSerial);
            await executePrint(fullVin, { type: typeName, variant: variantName, color: colorName });
            await new Promise(r => setTimeout(r, 50)); 
         }
         status.msg = "Selesai!";
    }
    batchForm.quantity = null; batchForm.start_serial = '';
  } catch(e: any) { status.msg = e.response?.data?.detail || "Batch Gagal"; status.type = "error";
  } finally { status.loading = false; }
};

const renderedPrintHtml = computed(() => {
   let tmpl = null;
   if(printConfig.templateId) tmpl = printTemplates.value.find(t => t.id === printConfig.templateId);
   let html = tmpl ? (tmpl.design_data || tmpl.html_content) : defaultTemplate;
   html = html.replace(/{{ full_vin }}/g, printData.full_vin).replace(/{{ qr_code }}/g, printData.qr).replace(/{{ type_name }}/g, printData.type_name).replace(/{{ variant_name }}/g, printData.variant_name).replace(/{{ color_name }}/g, printData.color_name);
   const style = tmpl ? `width:${tmpl.width}mm; height:${tmpl.height}mm; overflow:hidden;` : '';
   return `<div style="background:white; position:relative; ${style}">${html}</div>`;
});

const executePrint = async (vinStr: string, metadata: any = null) => {
   try {
     printData.full_vin = vinStr; printData.qr = await QRCode.toDataURL(vinStr);
     if (metadata) { printData.type_name = metadata.type; printData.variant_name = metadata.variant; printData.color_name = metadata.color; } 
     else {
         printData.type_name = selectedType.value?.name || '-';
         const v = filteredVariants.value.find((i:any) => i.id === form.variant); printData.variant_name = v ? v.name : '-';
         const c = filteredColors.value.find((i:any) => i.id === form.color); printData.color_name = c ? c.name : '-';
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
.master-page { padding: 24px; max-width: 900px; margin: 0 auto; color: var(--text-primary); }
.header { text-align: center; margin-bottom: 24px; }
.header h2 { margin: 0; font-size: 1.8rem; color: #1e293b; }
.header p { color: #64748b; margin-top: 6px; }

.main-form { max-width: 800px; margin: 0 auto; }
.tabs-header { display: flex; border-bottom: 1px solid var(--border-color); background: #f8fafc; border-radius: 12px 12px 0 0; }
.tab-btn { flex: 1; padding: 16px; border: none; background: transparent; font-weight: 600; color: #64748b; cursor: pointer; border-bottom: 3px solid transparent; transition: 0.2s; }
.tab-btn.active { background: white; color: #2563eb; border-bottom-color: #2563eb; }

.card-body { padding: 32px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.full-width { grid-column: span 2; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-weight: 600; font-size: 0.9rem; color: #334155; }
.input-field { padding: 12px 16px; border: 1px solid var(--border-color); border-radius: 8px; font-size: 1rem; width: 100%; box-sizing: border-box; }
.input-field:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }

/* PREVIEW LCD */
.preview-box { background: #0f172a; border-radius: 12px; padding: 24px; margin: 30px 0; text-align: center; border: 4px solid #334155; box-shadow: inset 0 0 15px #000; }
.preview-label { color: #64748b; font-size: 0.75rem; letter-spacing: 2px; font-weight: 700; margin-bottom: 8px; }
.lcd-text { font-family: 'Courier New', monospace; font-size: 2.2rem; font-weight: 700; color: #fbbf24; letter-spacing: 4px; text-shadow: 0 0 10px rgba(251, 191, 36, 0.5); word-break: break-all; }
.lcd-text.sm { font-size: 1.6rem; }
.arrow { color: #475569; margin: 0 10px; }

/* PRINT BOX */
.print-box { background: #f8fafc; border: 1px solid var(--border-color); border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; }
.print-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-weight: 600; color: #334155; }
.print-body { display: flex; gap: 12px; }
.flex-1 { flex: 1; }
.w-24 { width: 100px; }

/* TOGGLE */
.toggle-switch { position: relative; width: 40px; height: 22px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(18px); }

/* BUTTONS */
.action-bar { margin-top: 24px; }
.btn-submit { width: 100%; padding: 14px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 1.1rem; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2); }
.btn-submit:hover { background: #1d4ed8; transform: translateY(-2px); }
.btn-submit.dark { background: #0f172a; }
.btn-submit.dark:hover { background: #1e293b; }
.btn-submit:disabled { background: #94a3b8; cursor: not-allowed; transform: none; }

.status-msg { padding: 12px; border-radius: 8px; text-align: center; font-weight: 600; margin-bottom: 16px; }
.status-msg.success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.status-msg.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

.font-mono { font-family: monospace; }
.text-center { text-align: center; }
.text-lg { font-size: 1.25rem; }

@media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } .full-width { grid-column: span 1; } }
</style>