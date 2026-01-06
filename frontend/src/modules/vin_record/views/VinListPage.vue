<template>
  <div class="list-page">
    
    <div class="page-header">
      <div>
        <h2 class="title">Data VIN Record</h2>
        <p class="subtitle">History produksi dan pencatatan nomor rangka.</p>
      </div>
      <button @click="fetchData" class="btn-icon-refresh" title="Refresh Data">🔄</button>
    </div>

    <div class="filter-bar card">
      <div class="search-group">
        <span class="icon">🔍</span>
        <input 
          v-model="filters.search" 
          @input="handleSearch" 
          placeholder="Cari VIN / Serial Number..." 
          class="search-input"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.product_type" @change="fetchData">
          <option value="">Semua Produk</option>
          <template v-for="t in masterData.types" :key="t?.id || Math.random()">
              <option v-if="t" :value="t.id">{{ t.name }}</option>
          </template>
        </select>
        <select v-model="filters.year" @change="fetchData">
          <option value="">Semua Tahun</option>
          <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
        </select>
      </div>
    </div>

    <div v-if="selectedIds.length > 0" class="bulk-toolbar">
      <span class="selected-count">{{ selectedIds.length }} Data Terpilih:</span>
      <div class="bulk-actions">
        <button @click="openPrintModal(null)" class="btn-bulk print">
          🖨️ Print Selected
        </button>
        <button v-if="canDelete" @click="handleBulkDelete" class="btn-bulk delete">
          🗑️ Delete Selected
        </button>
      </div>
    </div>

    <div class="table-container card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th class="col-check">
                <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected">
              </th>
              <th>VIN NUMBER</th>
              <th>PRODUCT</th> <th>VARIAN</th>
              <th>COLOR</th>
              <th>CREATED BY</th>
              <th class="col-action sticky-right">ACTION</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
              <td colspan="7" class="text-center">Memuat data...</td>
            </tr>
            <tr v-else-if="records.length === 0">
              <td colspan="7" class="text-center">Tidak ada data ditemukan.</td>
            </tr>
            <tr v-else v-for="item in records" :key="item.id" :class="{ selected: selectedIds.includes(item.id) }">
              <td class="col-check">
                <input type="checkbox" :value="item.id" v-model="selectedIds">
              </td>
              <td data-label="VIN" class="font-mono bold text-primary">{{ item.full_vin }}</td>
              
              <td data-label="Product">{{ item.product_type_name || '-' }}</td>
              <td data-label="Varian">{{ item.variant_name || '-' }}</td>
              
              <td data-label="Warna">
                <span v-if="item.color_name" class="badge-color">{{ item.color_name }}</span>
                <span v-else>-</span>
              </td>
              <td data-label="User">
                <div class="user-info">
                  <span class="avatar-xs">{{ getInitials(item.created_by_name) }}</span>
                  {{ item.created_by_name || 'System' }}
                </div>
              </td>
              <td data-label="Action" class="col-action sticky-right">
                <div class="action-buttons">
                  <button @click="openPrintModal(item)" class="btn-icon" title="Cetak Label">🖨️</button>
                  <button v-if="canEdit" @click="handleEdit(item)" class="btn-icon" title="Edit Data">✏️</button>
                  <button v-if="canDelete" @click="handleDelete(item.id)" class="btn-icon danger" title="Hapus">🗑️</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <div class="rows-per-page">
            <span>Show:</span>
            <select v-model="pagination.pageSize" @change="handlePageSizeChange" class="size-select">
            <option :value="10">10</option>
            <option :value="50">50</option>
            <option :value="-1">Custom</option>
            </select>
            <input v-if="pagination.isCustom" type="number" v-model="customSizeInput" @change="applyCustomSize" class="custom-size-input">
        </div>
        <span class="page-info">{{ pagination.from }}-{{ pagination.to }} / {{ pagination.total }}</span>
        <div class="page-controls">
            <button :disabled="!pagination.prev" @click="changePage(pagination.current - 1)" class="btn-nav">Prev</button>
            <button :disabled="!pagination.next" @click="changePage(pagination.current + 1)" class="btn-nav">Next</button>
        </div>
      </div>
    </div>

    <div v-if="isPrintModalOpen" class="modal-backdrop" @click.self="isPrintModalOpen = false">
        <div class="modal-content small-modal">
            <div class="modal-header">
                <h3>🖨️ Cetak Label</h3>
                <button @click="isPrintModalOpen = false" class="btn-close">✕</button>
            </div>
            <div class="modal-body">
                <div class="print-target-info">
                    <span v-if="printTargetItem">Mencetak VIN: <strong>{{ printTargetItem.full_vin }}</strong></span>
                    <span v-else>Mencetak <strong>{{ selectedIds.length }}</strong> data terpilih.</span>
                </div>

                <div class="form-group">
                    <label>Pilih Template Label</label>
                    <select v-model="printConfig.templateId" class="select-lg">
                        <option :value="null">Default Template</option>
                        <option v-for="t in printTemplates" :key="t.id" :value="t.id">
                            {{ t.name }} ({{ t.width }}x{{ t.height }}mm)
                        </option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Jumlah Copy (Qty)</label>
                    <input type="number" v-model="printConfig.copies" min="1" class="input-lg-center">
                </div>
            </div>
            <div class="modal-footer">
                <button @click="isPrintModalOpen = false" class="btn-secondary">Batal</button>
                <button @click="confirmPrint" class="btn-primary" :disabled="isPrinting">
                    {{ isPrinting ? 'Sedang Mencetak...' : 'Cetak Sekarang' }}
                </button>
            </div>
        </div>
    </div>

    <div v-if="isEditModalOpen" class="modal-backdrop" @click.self="closeEditModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Data VIN</h3>
          <button @click="closeEditModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
            <div class="form-row">
                <div class="form-group">
                    <label>Full VIN</label>
                    <input v-model="editForm.full_vin" disabled class="input-disabled" />
                </div>
            </div>
            <div class="form-group">
                <label>Tahun</label>
                <select v-model="editForm.production_year">
                    <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tipe Produk</label>
                <select v-model="editForm.product_type">
                    <option v-for="t in masterData.types" :key="t.id" :value="t.id">{{ t.name }}</option>
                </select>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Varian</label>
                    <select v-model="editForm.variant">
                        <option :value="null">-</option>
                        <option v-for="v in editTypeOptions.variants" :key="v.id" :value="v.id">{{ v.name }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Warna</label>
                    <select v-model="editForm.color">
                        <option :value="null">-</option>
                        <option v-for="c in editTypeOptions.colors" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                </div>
            </div>
            <div class="warning-box">⚠️ Hanya update data administrasi. VIN Fisik tidak berubah.</div>
        </div>
        <div class="modal-footer">
          <button @click="closeEditModal" class="btn-secondary">Batal</button>
          <button v-if="canEdit" @click="saveEdit" class="btn-primary" :disabled="isSavingEdit">Simpan</button>
        </div>
      </div>
    </div>

    <div style="position:absolute; left:-9999px; top:-9999px;">
       <div ref="printRef" v-html="renderedPrintHtml" class="print-canvas"></div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue';
import axios from 'axios';
import { debounce } from 'lodash'; 
import { usePrintStore } from '../../../stores/print';
import { useAuthStore } from '../../../stores/auth';
import { toPng } from 'html-to-image';
import QRCode from 'qrcode';

const API_URL = 'http://127.0.0.1:8000/api';
const printStore = usePrintStore();
const authStore = useAuthStore();

// Permissions
const canEdit = computed(() => authStore.can('vin_record', 'create'));
const canDelete = computed(() => authStore.can('vin_record', 'delete'));

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

// State
const isLoading = ref(false);
const records = ref<any[]>([]);
const selectedIds = ref<number[]>([]);
const masterData = reactive({ types: [] as any[], years: [] as any[] });

// Printing State
const isPrintModalOpen = ref(false);
const isPrinting = ref(false);
const printTargetItem = ref<any>(null); 
const printTemplates = ref<any[]>([]);
const printConfig = reactive({ templateId: null as number|null, copies: 1 });
const printData = reactive({ full_vin: '', qr: '', type_name: '', variant_name: '', color_name: '' });
const printRef = ref<HTMLElement | null>(null);

// Filters & Pagination
// FIX: Gunakan 'product_type' agar konsisten dengan backend
const filters = reactive({ search: '', product_type: '', year: '' });
const pagination = reactive({ current: 1, total: 0, from: 0, to: 0, prev: null, next: null, pageSize: 10, isCustom: false });
const customSizeInput = ref(10);

// Edit State
const isEditModalOpen = ref(false);
const isSavingEdit = ref(false);
const editForm = reactive<any>({});

const editTypeOptions = computed(() => {
  const typeObj = masterData.types.find((t: any) => t.id === editForm.product_type);
  return typeObj ? typeObj : { variants: [], colors: [] };
});

// --- LOAD DATA ---
onMounted(() => {
    loadMasterData();
    fetchData();
});

const loadMasterData = async () => {
    // 1. Types (Handle Pagination / Array)
    try {
        const t = await axios.get(`${API_URL}/vin-record/product-options/`);
        // Logic: Jika backend kirim { results: [...] } ambil results, jika [...] ambil langsung
        masterData.types = Array.isArray(t.data) ? t.data : (t.data.results || []);
    } catch(e) { console.error("Gagal load Types", e); }

    // 2. Years (Handle Pagination / Array)
    try {
        const y = await axios.get(`${API_URL}/vin-record/years/`);
        masterData.years = Array.isArray(y.data) ? y.data : (y.data.results || []);
    } catch(e) { console.error("Gagal load Years", e); }

    // 3. Templates
    try {
        const tmpl = await axios.get(`${API_URL}/templates/`);
        printTemplates.value = Array.isArray(tmpl.data) ? tmpl.data : (tmpl.data.results || []);
        if(printTemplates.value.length > 0) printConfig.templateId = printTemplates.value[0].id;
    } catch(e) {}
};

const fetchData = async () => {
  isLoading.value = true; 
  selectedIds.value = []; 
  
  try {
    const actualSize = pagination.isCustom ? customSizeInput.value : pagination.pageSize;
    
    // --- FIX 1: BERSIHKAN PARAMETER KOSONG ---
    // Backend akan error jika dikirim ?product_type="" (string kosong bukan integer)
    const params: any = { 
        page: pagination.current, 
        page_size: actualSize, 
        search: filters.search 
    };
    
    // Hanya kirim jika ada nilai
    if (filters.product_type) params.product_type = filters.product_type;
    if (filters.year) params.production_year = filters.year;

    // --- FIX 2: GUNAKAN ENDPOINT YANG BENAR ---
    const res = await axios.get(`${API_URL}/vin-record/records/`, { params });
    
    // Mapping Data untuk Tampilan Tabel
    // Kita handle kasus dimana response backend mungkin "results" (Paginated) atau array langsung
    const rawData = res.data.results || res.data || [];
    
    records.value = rawData.map((r: any) => {
        // Coba cari nama produk di master data jika backend hanya kirim ID
        let pName = r.product_type_name; 
        if(!pName && masterData.types.length > 0) {
            const t = masterData.types.find((mt:any) => mt.id === r.product_type);
            pName = t ? t.name : '-';
        }
        
        return {
            ...r,
            product_type_name: pName,
            variant_name: r.variant_name || '-',
            color_name: r.color_name || '-',
            created_by_name: r.created_by_name || 'System'
        };
    });

    // Setup Pagination
    pagination.total = res.data.count || rawData.length; 
    pagination.next = res.data.next; 
    pagination.prev = res.data.previous;
    pagination.from = (pagination.current - 1) * actualSize + 1; 
    pagination.to = Math.min(pagination.current * actualSize, pagination.total);

  } catch (e) { 
      console.error("Load Error Records", e); 
      records.value = [];
  } finally { 
      isLoading.value = false; 
  }
};

const handleSearch = debounce(() => { pagination.current = 1; fetchData(); }, 500);
const changePage = (p: number) => { if(p>0) { pagination.current = p; fetchData(); } };
const handlePageSizeChange = () => { if (pagination.pageSize === -1) { pagination.isCustom = true; customSizeInput.value = 10; } else { pagination.isCustom = false; pagination.current = 1; fetchData(); } };
const applyCustomSize = () => { if (customSizeInput.value < 1) customSizeInput.value = 1; pagination.current = 1; fetchData(); };
const toggleSelectAll = (e: Event) => { selectedIds.value = (e.target as HTMLInputElement).checked ? records.value.map(r => r.id) : []; };
const isAllSelected = computed(() => records.value.length > 0 && selectedIds.value.length === records.value.length);

const handleDelete = async (id: number) => { if (confirm('Hapus?')) { await axios.delete(`${API_URL}/vin-record/records/${id}/`); fetchData(); } };
const handleBulkDelete = async () => { if (confirm(`Hapus ${selectedIds.value.length} item?`)) { for (const id of selectedIds.value) await axios.delete(`${API_URL}/vin-record/records/${id}/`); fetchData(); } };

// Printing
const openPrintModal = (item: any = null) => { printTargetItem.value = item; isPrintModalOpen.value = true; };
const confirmPrint = async () => {
    isPrinting.value = true;
    try {
        const items = printTargetItem.value ? [printTargetItem.value] : records.value.filter(r => selectedIds.value.includes(r.id));
        if (items.length === 0) { alert("Tidak ada data terpilih"); return; }
        for (const item of items) {
            await renderAndSend(item); await new Promise(r => setTimeout(r, 100));
        }
        isPrintModalOpen.value = false; alert("Perintah cetak terkirim!");
    } catch(e) { alert("Gagal mencetak"); } finally { isPrinting.value = false; }
};
const renderAndSend = async (item: any) => {
     printData.full_vin = item.full_vin;
     printData.type_name = item.product_type_name || '-';
     printData.variant_name = item.variant_name || '-';
     printData.color_name = item.color_name || '-';
     printData.qr = await QRCode.toDataURL(item.full_vin);
     await nextTick(); await new Promise(r => setTimeout(r, 50));
     if(printRef.value) {
        const element = printRef.value.firstElementChild as HTMLElement;
        const url = await toPng(element, { quality: 1, pixelRatio: 3 });
        await printStore.silentPrint(url, printConfig.copies);
     }
};
const renderedPrintHtml = computed(() => {
   let tmpl = null;
   if(printConfig.templateId) tmpl = printTemplates.value.find(t => t.id === printConfig.templateId);
   let html = tmpl ? (tmpl.design_data || tmpl.html_content) : defaultTemplate;
   html = html.replace(/{{ full_vin }}/g, printData.full_vin); html = html.replace(/{{ qr_code }}/g, printData.qr);
   html = html.replace(/{{ type_name }}/g, printData.type_name); html = html.replace(/{{ variant_name }}/g, printData.variant_name); html = html.replace(/{{ color_name }}/g, printData.color_name);
   const style = tmpl ? `width:${tmpl.width}mm; height:${tmpl.height}mm; overflow:hidden;` : '';
   return `<div style="background:white; position:relative; ${style}">${html}</div>`;
});

// Edit
const handleEdit = (item: any) => { 
    editForm.id = item.id; editForm.full_vin = item.full_vin; editForm.serial_number = item.serial_number; 
    editForm.production_year = item.production_year; 
    editForm.product_type = item.product_type; // Match backend field
    editForm.variant = item.variant; editForm.color = item.color; 
    isEditModalOpen.value = true; 
};
const closeEditModal = () => isEditModalOpen.value = false;
const saveEdit = async () => { 
    if (!editForm.id) return; isSavingEdit.value = true; 
    try { 
        await axios.patch(`${API_URL}/vin-record/records/${editForm.id}/`, { 
            product_type: editForm.product_type, variant: editForm.variant, color: editForm.color, production_year: editForm.production_year 
        }); 
        alert("Updated!"); closeEditModal(); fetchData(); 
    } catch (e) { alert("Error update"); } finally { isSavingEdit.value = false; } 
};
const getInitials = (name: any) => { if (!name) return 'NA'; return String(name).substring(0, 2).toUpperCase(); };
</script>

<style scoped>
/* GENERAL */
.list-page { max-width: 100%; padding: 0 20px 50px; }
.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); box-shadow: var(--shadow-sm); overflow: hidden; }

/* HEADER */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.title { font-size: 1.5rem; margin: 0; color: #1e293b; }
.subtitle { color: #64748b; margin: 5px 0 0; font-size: 0.9rem; }
.btn-icon-refresh { background: #fff; border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
.btn-icon-refresh:hover { background: #f8fafc; transform: rotate(180deg); }

/* FILTER */
.filter-bar { display: flex; gap: 15px; padding: 15px; align-items: center; flex-wrap: wrap; margin-bottom: 20px; }
.search-group { flex: 1; display: flex; border: 1px solid #ddd; border-radius: 4px; padding: 0 10px; align-items: center; background: #f8fafc; }
.search-input { border: none; background: transparent; padding: 10px; width: 100%; outline: none; }
.filter-group { display: flex; gap: 10px; }
.filter-group select { padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; }

/* BULK TOOLBAR */
.bulk-toolbar { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; padding: 10px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.btn-bulk { padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.btn-bulk.print { background: #3b82f6; color: white; }
.btn-bulk.delete { background: #ef4444; color: white; }

/* TABLE */
.table-container { padding: 0; overflow: hidden; }
.table-wrapper { overflow-x: auto; width: 100%; }
table { width: 100%; border-collapse: collapse; min-width: 900px; }
th, td { padding: 14px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; white-space: nowrap; font-size: 0.95rem; vertical-align: middle; }
th { background: #f8fafc; font-weight: 600; color: #64748b; font-size: 0.8rem; text-transform: uppercase; }
tr:hover { background-color: #f8fafc; }
tr.selected { background-color: #eff6ff; }

.font-mono { font-family: monospace; letter-spacing: 0.5px; }
.text-primary { color: #2563eb; font-weight: 700; }
.badge-color { padding: 3px 8px; background: #e2e8f0; border-radius: 4px; font-size: 0.8rem; }
.user-info { display: flex; align-items: center; gap: 8px; }
.avatar-xs { width: 24px; height: 24px; background: #cbd5e1; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; font-weight: bold; }
.action-buttons { display: flex; gap: 5px; justify-content: center; }
.btn-icon { width: 32px; height: 32px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; color: #64748b; }
.btn-icon:hover { background: #f1f5f9; color: #0f172a; }
.btn-icon.danger:hover { background: #fee2e2; border-color: #fca5a5; color: #ef4444; }
.sticky-right { position: sticky; right: 0; background: white; z-index: 5; box-shadow: -2px 0 5px rgba(0,0,0,0.05); text-align: center; }
tr:hover .sticky-right { background: #f8fafc; }

/* PAGINATION */
.pagination { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; border-top: 1px solid #e2e8f0; background: #fff; }
.btn-nav { padding: 6px 12px; border: 1px solid #e2e8f0; background: white; border-radius: 4px; cursor: pointer; }
.size-select, .custom-size-input { padding: 5px; border-radius: 4px; border: 1px solid #ccc; }

/* MODAL STYLING */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 100; backdrop-filter: blur(2px); }
.modal-content { background: white; width: 500px; max-width: 90%; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); display: flex; flex-direction: column; overflow: hidden; animation: popIn 0.3s ease; }
.modal-content.small-modal { width: 400px; }
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

.modal-header { padding: 15px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-body { padding: 25px; }
.modal-footer { padding: 15px 20px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 10px; background: #f8fafc; }

.form-group { margin-bottom: 15px; display: flex; flex-direction: column; gap: 8px; }
label { font-weight: 600; color: #475569; font-size: 0.9rem; }
.select-lg, .input-lg-center { padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 1rem; width: 100%; box-sizing: border-box; }
.input-lg-center { text-align: center; font-weight: bold; }

.print-target-info { background: #eff6ff; color: #1e40af; padding: 10px; border-radius: 6px; margin-bottom: 20px; text-align: center; font-size: 0.9rem; border: 1px solid #dbeafe; }
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-secondary { background: #e2e8f0; color: #334155; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: #94a3b8; }
.input-disabled { background: #f1f5f9; color: #94a3b8; }
.warning-box { background: #fffbeb; color: #b45309; font-size: 0.8rem; padding: 10px; border-radius: 6px; margin-top: 10px; }

/* MOBILE */
@media (max-width: 768px) {
    .page-header { flex-direction: column; align-items: flex-start; }
    .filter-bar { flex-direction: column; align-items: stretch; }
    .filter-group { flex-direction: column; }
    .bulk-toolbar { flex-direction: column; gap: 10px; }
    
    thead { display: none; }
    tr { display: block; margin-bottom: 15px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; padding: 15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    td { display: block; text-align: right; padding: 8px 0; border: none; position: relative; padding-left: 40%; }
    td::before { content: attr(data-label); position: absolute; left: 0; top: 8px; width: 35%; text-align: left; font-weight: 700; color: #64748b; font-size: 0.85rem; }
    
    .col-check { text-align: left; padding-left: 0; }
    .col-check::before { content: none; }
    .sticky-right { position: static; box-shadow: none; border-top: 1px dashed #e2e8f0; margin-top: 10px; padding-top: 15px; text-align: right; }
    .action-buttons { justify-content: flex-end; }
}
</style>