<template>
  <div class="list-page">
    
    <div class="header">
      <div>
        <h2>Data VIN Record</h2>
        <p>History produksi dan pencatatan nomor rangka.</p>
      </div>
      <button @click="fetchData" class="btn-icon refresh-btn" title="Refresh">🔄</button>
    </div>

    <div class="card filter-card">
      <div class="search-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="filters.search" 
          @input="handleSearch" 
          placeholder="Cari VIN / Serial Number..." 
          class="search-input"
        />
      </div>
      <div class="filter-group">
        <select v-model="filters.product_type" @change="fetchData" class="filter-select">
            <option value="">Semua Produk</option>
            <template v-for="t in masterData.types" :key="t?.id || Math.random()">
                <option v-if="t" :value="t.id">{{ t.name }}</option>
            </template>
        </select>
        <select v-model="filters.year" @change="fetchData" class="filter-select small">
            <option value="">Semua Tahun</option>
            <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
        </select>
      </div>
    </div>

    <div v-if="selectedIds.length > 0" class="bulk-toolbar">
      <span class="selected-count">{{ selectedIds.length }} Data Terpilih</span>
      <div class="bulk-actions">
        <button @click="openPrintModal(null)" class="btn-bulk print">🖨️ Print Selected</button>
        <button v-if="canDelete" @click="handleBulkDelete" class="btn-bulk delete">🗑️ Delete Selected</button>
      </div>
    </div>

    <div class="card table-card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th class="col-check">
                <input type="checkbox" @change="toggleSelectAll" :checked="isAllSelected">
              </th>
              <th>VIN NUMBER</th>
              <th>PRODUCT</th>
              <th>VARIAN</th>
              <th>WARNA</th>
              <th class="text-center">STATUS</th>
              <th>CREATED BY</th>
              <th class="col-action">ACTION</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="isLoading">
                <td colspan="8" class="text-center loading-cell">
                    <div class="spinner"></div> Memuat data...
                </td>
            </tr>
            <tr v-else-if="records.length === 0">
                <td colspan="8" class="text-center empty-cell">Tidak ada data ditemukan.</td>
            </tr>
            <tr v-else v-for="item in records" :key="item.id" :class="{ selected: selectedIds.includes(item.id) }">
              <td class="col-check">
                <input type="checkbox" :value="item.id" v-model="selectedIds">
              </td>
              <td class="font-mono vin-cell">{{ item.full_vin }}</td>
              <td><strong>{{ item.product_type_name || '-' }}</strong></td>
              <td>{{ item.variant_name || '-' }}</td>
              <td>
                <span v-if="item.color_name" class="color-tag">{{ item.color_name }}</span>
                <span v-else>-</span>
              </td>
              <td class="text-center">
                 <span v-if="item.status === 'AVAILABLE'" class="badge badge-green">Available</span>
                 <span v-else-if="item.status === 'RESERVED'" class="badge badge-orange">Reserved</span>
                 <span v-else-if="item.status === 'USED'" class="badge badge-blue">Used</span>
                 <span v-else class="badge badge-red">Scrap</span>
              </td>
              <td>
                <div class="user-info">
                  <div class="avatar">{{ getInitials(item.created_by_name) }}</div>
                  <span>{{ item.created_by_name || 'System' }}</span>
                </div>
              </td>
              <td class="col-action">
                <button @click="openPrintModal(item)" class="btn-icon" title="Cetak">🖨️</button>
                <button v-if="canEdit" @click="handleEdit(item)" class="btn-icon" title="Edit">✏️</button>
                <button v-if="canDelete" @click="handleDelete(item.id)" class="btn-icon danger" title="Hapus">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <div class="page-size">
            <span>Show:</span>
            <select v-model="pagination.pageSize" @change="handlePageSizeChange">
                <option :value="10">10</option>
                <option :value="50">50</option>
                <option :value="-1">All</option>
            </select>
            <span class="page-count">{{ pagination.from }}-{{ pagination.to }} of {{ pagination.total }}</span>
        </div>
        <div class="page-nav">
            <button :disabled="!pagination.prev" @click="changePage(pagination.current - 1)" class="btn-nav">Prev</button>
            <button :disabled="!pagination.next" @click="changePage(pagination.current + 1)" class="btn-nav">Next</button>
        </div>
      </div>
    </div>

    <div v-if="isPrintModalOpen" class="modal-backdrop" @click.self="isPrintModalOpen = false">
        <div class="modal-dialog">
            <div class="modal-header">
                <h3>🖨️ Cetak Label</h3>
                <button @click="isPrintModalOpen = false" class="btn-close">✕</button>
            </div>
            <div class="modal-body">
                <div class="info-box">
                    <span v-if="printTargetItem">VIN: <strong>{{ printTargetItem.full_vin }}</strong></span>
                    <span v-else>Mencetak <strong>{{ selectedIds.length }}</strong> data terpilih.</span>
                </div>
                <div class="form-group">
                    <label>Template Label</label>
                    <select v-model="printConfig.templateId" class="input-field">
                        <option :value="null">Default Template</option>
                        <option v-for="t in printTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Jumlah Copy</label>
                    <input type="number" v-model="printConfig.copies" min="1" class="input-field text-center">
                </div>
            </div>
            <div class="modal-footer">
                <button @click="isPrintModalOpen = false" class="btn-secondary">Batal</button>
                <button @click="confirmPrint" class="btn-primary" :disabled="isPrinting">
                    {{ isPrinting ? 'Mencetak...' : 'Cetak Sekarang' }}
                </button>
            </div>
        </div>
    </div>

    <div v-if="isEditModalOpen" class="modal-backdrop" @click.self="closeEditModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>Edit Data VIN</h3>
          <button @click="closeEditModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
            <div class="form-group">
                <label>Full VIN (Read Only)</label>
                <input v-model="editForm.full_vin" disabled class="input-field disabled" />
            </div>
            <div class="grid-2-col">
                <div class="form-group">
                    <label>Tahun</label>
                    <select v-model="editForm.production_year" class="input-field">
                        <option v-for="y in masterData.years" :key="y.id" :value="y.id">{{ y.year }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Tipe Produk</label>
                    <select v-model="editForm.product_type" class="input-field">
                        <option v-for="t in masterData.types" :key="t.id" :value="t.id">{{ t.name }}</option>
                    </select>
                </div>
            </div>
            <div class="grid-2-col">
                <div class="form-group">
                    <label>Varian</label>
                    <select v-model="editForm.variant" class="input-field">
                        <option :value="null">-</option>
                        <option v-for="v in editTypeOptions.variants" :key="v.id" :value="v.id">{{ v.name }}</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Warna</label>
                    <select v-model="editForm.color" class="input-field">
                        <option :value="null">-</option>
                        <option v-for="c in editTypeOptions.colors" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                </div>
            </div>
            <div class="warning-box">
               ⚠️ Perubahan ini hanya update data administrasi. VIN fisik (Serial/Digit) tidak berubah.
            </div>
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
import { debounce } from 'lodash'; 
import { usePrintStore } from '@/stores/print';
import { useAuthStore } from '@/stores/auth';
import { toPng } from 'html-to-image';
import QRCode from 'qrcode';
import api from './api';

const printStore = usePrintStore();
const authStore = useAuthStore();

// Permissions
const canEdit = computed(() => authStore.can('vin_record', 'create'));
const canDelete = computed(() => authStore.can('vin_record', 'delete'));

// Template String Default
const defaultTemplate = `<div style="width:300px; height:150px; border:2px solid #000; padding:10px;"><h2>VIN LABEL</h2>{{ full_vin }}</div>`;

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
const filters = reactive({ search: '', product_type: '', year: '' });
const pagination = reactive({ current: 1, total: 0, from: 0, to: 0, prev: null, next: null, pageSize: 10, isCustom: false });

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
    try {
        const [t, y, tmpl] = await Promise.all([
            api.getTraceableTypes(),
            api.getYears(),
            api.getTemplates()
        ]);
        masterData.types = Array.isArray(t.data) ? t.data : (t.data.results || []);
        masterData.years = Array.isArray(y.data) ? y.data : (y.data.results || []);
        printTemplates.value = Array.isArray(tmpl.data) ? tmpl.data : (tmpl.data.results || []);
        if(printTemplates.value.length > 0) printConfig.templateId = printTemplates.value[0].id;
    } catch(e) { console.error("Gagal load Master Data", e); }
};

const fetchData = async () => {
  isLoading.value = true; 
  selectedIds.value = []; 
  try {
    const params: any = { 
        page: pagination.current, 
        page_size: pagination.isCustom ? 1000 : pagination.pageSize, 
        search: filters.search 
    };
    if (filters.product_type) params.product_type = filters.product_type;
    if (filters.year) params.production_year = filters.year;

    const res = await api.getRecords(params);
    const rawData = res.data.results || res.data || [];
    
    records.value = rawData.map((r: any) => ({
        ...r,
        product_type_name: r.product_type_name || (masterData.types.find((mt:any) => mt.id === r.product_type)?.name || '-'),
        variant_name: r.variant_name || '-',
        color_name: r.color_name || '-',
        created_by_name: r.created_by_name || 'System'
    }));

    pagination.total = res.data.count || rawData.length; 
    pagination.next = res.data.next; 
    pagination.prev = res.data.previous;
    const size = pagination.isCustom ? 1000 : pagination.pageSize;
    pagination.from = (pagination.current - 1) * size + 1; 
    pagination.to = Math.min(pagination.current * size, pagination.total);

  } catch (e) { records.value = []; } finally { isLoading.value = false; }
};

const handleSearch = debounce(() => { pagination.current = 1; fetchData(); }, 500);
const changePage = (p: number) => { if(p>0) { pagination.current = p; fetchData(); } };
const handlePageSizeChange = () => { pagination.isCustom = pagination.pageSize === -1; pagination.current = 1; fetchData(); };
const toggleSelectAll = (e: Event) => { selectedIds.value = (e.target as HTMLInputElement).checked ? records.value.map(r => r.id) : []; };
const isAllSelected = computed(() => records.value.length > 0 && selectedIds.value.length === records.value.length);

const handleDelete = async (id: number) => { if (confirm('Hapus?')) { await api.deleteRecord(id); fetchData(); } };
const handleBulkDelete = async () => { if (confirm(`Hapus ${selectedIds.value.length} item?`)) { for (const id of selectedIds.value) await api.deleteRecord(id); fetchData(); } };

// Print Logic
const openPrintModal = (item: any = null) => { printTargetItem.value = item; isPrintModalOpen.value = true; };
const confirmPrint = async () => {
    isPrinting.value = true;
    try {
        const items = printTargetItem.value ? [printTargetItem.value] : records.value.filter(r => selectedIds.value.includes(r.id));
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
    Object.assign(editForm, item); isEditModalOpen.value = true; 
};
const closeEditModal = () => isEditModalOpen.value = false;
const saveEdit = async () => { 
    if (!editForm.id) return; isSavingEdit.value = true; 
    try { 
        await api.updateRecord(editForm.id, { 
            product_type: editForm.product_type, variant: editForm.variant, color: editForm.color, production_year: editForm.production_year 
        }); 
        closeEditModal(); fetchData(); 
    } catch (e) { alert("Error update"); } finally { isSavingEdit.value = false; } 
};
const getInitials = (name: any) => { if (!name) return 'NA'; return String(name).substring(0, 2).toUpperCase(); };
</script>

<style scoped>
/* PAGE LAYOUT */
.list-page { padding: 24px; max-width: 1200px; margin: 0 auto; color: var(--text-primary); }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
.header h2 { margin: 0; font-size: 1.5rem; color: #1e293b; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

.refresh-btn { width: 40px; height: 40px; border-radius: 8px; border: 1px solid var(--border-color); background: white; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.refresh-btn:hover { background: #f8fafc; transform: rotate(180deg); }

/* FILTER BAR */
.filter-card { padding: 16px; margin-bottom: 24px; display: flex; gap: 16px; flex-wrap: wrap; align-items: center; }
.search-wrapper { flex: 1; display: flex; align-items: center; border: 1px solid var(--border-color); border-radius: 8px; padding: 0 12px; background: #fff; min-width: 250px; }
.search-icon { margin-right: 8px; color: #94a3b8; }
.search-input { border: none; outline: none; padding: 10px 0; width: 100%; font-size: 0.95rem; color: #334155; }
.filter-group { display: flex; gap: 12px; }
.filter-select { padding: 10px 12px; border: 1px solid var(--border-color); border-radius: 8px; background: white; font-size: 0.95rem; color: #334155; }
.filter-select.small { width: 120px; }

/* BULK ACTIONS */
.bulk-toolbar { margin-bottom: 16px; background: #eff6ff; border: 1px solid #bfdbfe; padding: 12px 16px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
.selected-count { font-weight: 600; color: #1e40af; }
.bulk-actions { display: flex; gap: 12px; }
.btn-bulk { padding: 8px 16px; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.85rem; }
.btn-bulk.print { background: #3b82f6; color: white; }
.btn-bulk.delete { background: #ef4444; color: white; }

/* TABLE */
.table-card { overflow: hidden; }
.table-responsive { width: 100%; overflow-x: auto; }
.table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 900px; }
.table th { background: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border-color); white-space: nowrap; }
.table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; vertical-align: middle; }
.table tr:last-child td { border-bottom: none; }
.table tr:hover { background-color: #f8fafc; }
.table tr.selected { background-color: #eff6ff; }

/* Column Specific */
.col-check { width: 40px; text-align: center; }
.col-action { text-align: right; width: 140px; }
.text-center { text-align: center; }
.vin-cell { color: #2563eb; font-weight: 700; letter-spacing: 0.5px; }
.color-tag { background: #f1f5f9; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; border: 1px solid #e2e8f0; }

/* Status Badges */
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; border: 1px solid transparent; }
.badge-green { background: #dcfce7; color: #166534; border-color: #bbf7d0; }
.badge-orange { background: #ffedd5; color: #9a3412; border-color: #fed7aa; }
.badge-blue { background: #dbeafe; color: #1e40af; border-color: #bfdbfe; }
.badge-red { background: #fee2e2; color: #991b1b; border-color: #fecaca; }

/* User Info */
.user-info { display: flex; align-items: center; gap: 8px; }
.avatar { width: 24px; height: 24px; background: #cbd5e1; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; color: white; }

/* Action Buttons */
.btn-icon { width: 32px; height: 32px; border: 1px solid var(--border-color); background: white; border-radius: 6px; cursor: pointer; margin-left: 6px; color: #64748b; display: inline-flex; align-items: center; justify-content: center; }
.btn-icon:hover { border-color: #2563eb; color: #2563eb; }
.btn-icon.danger:hover { border-color: #ef4444; color: #ef4444; background: #fee2e2; }

/* PAGINATION */
.pagination { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: white; border-top: 1px solid var(--border-color); }
.page-size { display: flex; align-items: center; gap: 8px; color: #64748b; font-size: 0.9rem; }
.page-size select { padding: 4px 8px; border: 1px solid var(--border-color); border-radius: 4px; }
.btn-nav { padding: 6px 12px; border: 1px solid var(--border-color); background: white; border-radius: 6px; cursor: pointer; font-size: 0.85rem; color: #334155; }
.btn-nav:hover:not(:disabled) { background: #f8fafc; }
.btn-nav:disabled { opacity: 0.5; cursor: not-allowed; }

/* MODAL STYLES */
.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 100; }
.modal-dialog { background: white; width: 100%; max-width: 480px; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); overflow: hidden; animation: slideUp 0.3s ease; }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.modal-header { padding: 16px 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.1rem; color: #1e293b; }
.modal-body { padding: 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 12px; background: #f8fafc; }

.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; color: #334155; }
.input-field { width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; box-sizing: border-box; }
.input-field:disabled { background: #f1f5f9; color: #94a3b8; }
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.btn-primary { background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-secondary { background: white; border: 1px solid var(--border-color); color: #334155; padding: 10px 20px; border-radius: 6px; cursor: pointer; }
.btn-close { background: transparent; border: none; font-size: 1.2rem; color: #94a3b8; cursor: pointer; }

.info-box { background: #eff6ff; color: #1e40af; padding: 12px; border-radius: 6px; text-align: center; margin-bottom: 20px; font-size: 0.9rem; border: 1px solid #dbeafe; }
.warning-box { background: #fffbeb; color: #92400e; padding: 12px; border-radius: 6px; font-size: 0.85rem; margin-top: 16px; border: 1px solid #fde68a; }
.spinner { width: 20px; height: 20px; border: 2px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>