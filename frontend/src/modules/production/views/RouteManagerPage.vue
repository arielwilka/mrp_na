<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>🗺️ Route & Process Map</h2>
        <p>Atur alur produksi dan interlocking part (Traceability).</p>
      </div>
      <button v-if="!isDetailMode" @click="openCreateModal" class="btn-primary">+ Buat Route</button>
      <button v-else @click="backToList" class="btn-secondary">&larr; Kembali</button>
    </div>

    <div v-if="!isDetailMode" class="card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Nama Route</th>
              <th>Tipe Produk</th>
              <th class="text-center">Jml Step</th>
              <th class="text-center">Status</th>
              <th class="text-right">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in routes" :key="r.id">
              <td class="font-bold text-primary">{{ r.name }}</td>
              <td>{{ r.product_type_name }}</td>
              <td class="text-center">{{ r.steps?.length || 0 }} Station</td>
              <td class="text-center">
                <span v-if="r.is_active" class="badge-success">Active</span>
                <span v-else class="badge-gray">Draft</span>
              </td>
              <td class="text-right">
                <button @click="openDetail(r)" class="btn-icon mr-2" title="Konfigurasi Step">⚙️</button>
                <button @click="deleteRoute(r.id)" class="btn-icon danger">🗑️</button>
              </td>
            </tr>
            <tr v-if="routes.length === 0"><td colspan="5" class="text-center py-8 text-muted">Belum ada route.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="detail-view fade-in">
        
        <div class="info-bar">
            <div>
                <h3>Editing: {{ activeRoute.name }}</h3>
                <span class="text-sm text-muted">Produk: {{ activeRoute.product_type_name }}</span>
            </div>
            <button class="btn-primary btn-sm" @click="openStepModal">+ Tambah Step</button>
        </div>

        <div class="steps-container">
            <div v-for="(step, idx) in activeRoute.steps" :key="step.id" class="step-card">
                <div class="step-number">{{ Number(idx) + 1 }}</div>
                <div class="step-content">
                    <div class="step-header">
                        <h4>{{ step.station_name }} <span class="text-xs text-muted">({{ step.station_code }})</span></h4>
                        <span class="badge-seq">Urutan: {{ step.sequence }}</span>
                    </div>
                    
                    <div class="trace-list">
                        <span class="text-xs text-muted font-bold uppercase mb-1 block">Wajib Scan:</span>
                        
                        <div v-if="step.required_parts_names && step.required_parts_names.length > 0" class="tags">
                            <span v-for="pName in step.required_parts_names" :key="pName" class="tag">
                                🔧 {{ pName }}
                            </span>
                        </div>
                        <div v-else class="text-xs text-muted italic">
                            Tidak ada part interlocking. (Station Progress Only)
                        </div>
                    </div>
                </div>
                <div class="step-actions">
                    <button @click="deleteStep(step.id)" class="btn-icon sm danger" title="Hapus Step">&times;</button>
                </div>
            </div>

            <div v-if="!activeRoute.steps || activeRoute.steps.length === 0" class="empty-steps">
                <p>Belum ada langkah produksi.</p>
                <p>Klik tombol <strong>+ Tambah Step</strong>.</p>
            </div>
        </div>

    </div>

    <div v-if="modals.create" class="modal-backdrop" @click.self="modals.create = false">
        <div class="modal-dialog">
            <div class="modal-header"><h3>Buat Route Baru</h3></div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Nama Route</label>
                    <input v-model="form.name" class="form-input" placeholder="Standard Assembly Flow" />
                </div>
                <div class="form-group">
                    <label>Produk</label>
                    <select v-model="form.product_type" class="form-select">
                        <option :value="null">-- Pilih Produk --</option>
                        <option v-for="p in productTypes" :key="p.id" :value="p.id">{{ p.name }}</option>
                    </select>
                </div>
                <div class="form-group checkbox-wrapper">
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" v-model="form.is_active"> 
                        <span>Set Aktif?</span>
                    </label>
                </div>
            </div>
            <div class="modal-footer">
                <button @click="saveRoute" class="btn-primary w-full">Buat Route</button>
            </div>
        </div>
    </div>

    <div v-if="modals.step" class="modal-backdrop" @click.self="modals.step = false">
        <div class="modal-dialog wide">
            <div class="modal-header"><h3>Tambah Step Produksi</h3></div>
            <div class="modal-body">
                
                <div class="grid-2-col">
                    <div class="form-group">
                        <label>Station <span class="text-red">*</span></label>
                        <select v-model="stepForm.station" class="form-select">
                            <option :value="null">-- Pilih Station --</option>
                            <option v-for="s in stations" :key="s.id" :value="s.id">
                                {{ s.code }} - {{ s.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Urutan (Seq) <span class="text-red">*</span></label>
                        <input type="number" v-model="stepForm.sequence" class="form-input text-center" />
                    </div>
                </div>

                <div class="form-group mt-4">
                    <label>Traceability Interlocking (Wajib Scan)</label>
                    <div class="part-selector-box">
                        <div v-if="parts.length === 0" class="p-4 text-center text-muted text-sm">
                            Tidak ada Part Master. <br>Silakan input di modul Traceability dulu.
                        </div>
                        
                        <label v-for="part in parts" :key="part.id" class="part-item">
                            <input type="checkbox" :value="part.id" v-model="stepForm.required_parts">
                            <div class="part-details">
                                <span class="part-code">{{ part.part_number }}</span>
                                <span class="part-name">{{ part.part_name }}</span>
                            </div>
                        </label>
                    </div>
                    <small class="text-muted block mt-2">
                        * Operator wajib scan barcode part yang dicentang sebelum bisa PASS.
                    </small>
                </div>

            </div>
            <div class="modal-footer">
                <button @click="saveStep" class="btn-primary w-full">Simpan Step</button>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '../api';

const isLoading = ref(false);
const isDetailMode = ref(false);
const routes = ref<any[]>([]);
const activeRoute = ref<any>(null);

const productTypes = ref<any[]>([]);
const stations = ref<any[]>([]);
const parts = ref<any[]>([]); // Part Master Data

const modals = reactive({ create: false, step: false });
const form = reactive({ name: '', product_type: null, is_active: true });
const stepForm = reactive({ station: null, sequence: 10, required_parts: [] as number[] });

onMounted(async () => {
    loadRoutes();
    const [prodRes, stRes, partRes] = await Promise.all([
        api.getProductTypes(),
        api.getStations(),
        api.getParts() // Ambil list Part Master
    ]);
    productTypes.value = prodRes.data.results || prodRes.data || [];
    stations.value = stRes.data.results || stRes.data || [];
    parts.value = partRes.data.results || partRes.data || [];
});

const loadRoutes = async () => {
    isLoading.value = true;
    try {
        const res = await api.getRoutes();
        routes.value = res.data.results || res.data || [];
    } catch(e) { console.error(e); } 
    finally { isLoading.value = false; }
};

const backToList = () => { isDetailMode.value = false; activeRoute.value = null; };

const openDetail = async (route: any) => {
    // Reload detail untuk dapat steps terbaru
    try {
        const res = await api.getRoute(route.id);
        activeRoute.value = res.data;
        isDetailMode.value = true;
    } catch(e) { alert("Error loading detail"); }
};

// --- ACTION CREATE ROUTE ---
const openCreateModal = () => { form.name = ''; form.product_type = null; modals.create = true; };
const saveRoute = async () => {
    try { await api.createRoute(form); modals.create = false; loadRoutes(); } catch(e) { alert("Gagal"); }
};
const deleteRoute = async (id: number) => {
    if(confirm("Hapus?")) { await api.deleteRoute(id); loadRoutes(); }
};

// --- ACTION STEP ---
const openStepModal = () => {
    stepForm.station = null;
    // Auto increment sequence
    const currentSteps = activeRoute.value.steps || [];
    const maxSeq = currentSteps.length > 0 ? Math.max(...currentSteps.map((s:any) => s.sequence)) : 0;
    stepForm.sequence = maxSeq + 10;
    stepForm.required_parts = [];
    modals.step = true;
};

const saveStep = async () => {
    if(!stepForm.station) return alert("Pilih Station!");
    try {
        // Backend (Serializer) mengharapkan 'required_parts' sebagai Array ID
        await api.addRouteStep({
            route: activeRoute.value.id,
            station: stepForm.station,
            sequence: stepForm.sequence,
            required_parts: stepForm.required_parts 
        });
        modals.step = false;
        openDetail(activeRoute.value); // Refresh list steps
    } catch(e: any) {
        alert("Gagal: " + (e.response?.data?.detail || "Cek Koneksi"));
    }
};

const deleteStep = async (id: number) => {
    if(confirm("Hapus step ini?")) {
        await api.deleteRouteStep(id);
        openDetail(activeRoute.value);
    }
};
</script>

<style scoped>
/* --- LAYOUT UTAMA --- */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; font-family: 'Inter', sans-serif; color: #334155; }

.header { 
    margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0; 
    display: flex; justify-content: space-between; align-items: center; 
}
.header h2 { margin: 0; color: #0f172a; font-size: 1.5rem; font-weight: 700; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* --- CARD & TABLE --- */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { width: 100%; overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 14px 20px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.75rem; color: #475569; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
.table td { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; }
.table tr:last-child td { border-bottom: none; }
.table tr:hover td { background-color: #f8fafc; }

/* --- DETAIL VIEW (STEPS) --- */
.detail-view { animation: slideUp 0.3s ease-out; }
.info-bar { 
    background: #fff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; 
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.info-bar h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b; }

.steps-container { display: flex; flex-direction: column; gap: 16px; padding-bottom: 40px; }

.step-card { 
    display: flex; align-items: flex-start; background: white; 
    border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; 
    position: relative; transition: 0.2s; 
}
.step-card:hover { border-color: #94a3b8; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

.step-number { 
    width: 36px; height: 36px; background: #3b82f6; color: white; 
    border-radius: 8px; display: flex; align-items: center; justify-content: center; 
    font-weight: 800; font-size: 1rem; margin-right: 16px; flex-shrink: 0; 
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.step-content { flex: 1; }
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.step-header h4 { margin: 0; font-size: 1.1rem; color: #0f172a; font-weight: 600; }

.trace-list { background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px dashed #cbd5e1; }
.tags { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
.tag { 
    font-size: 0.75rem; background: #fff; color: #0369a1; 
    padding: 4px 10px; border-radius: 20px; border: 1px solid #bae6fd; font-weight: 600; 
    display: inline-flex; align-items: center; gap: 4px;
}

/* --- FORM COMPONENTS --- */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; color: #334155; }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; transition: 0.2s; background: white; }
.form-input:focus, .form-select:focus { 
    outline: none; 
    border-color: #3b82f6; 
    /* Gunakan box-shadow untuk efek ring */
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); 
}

/* --- PART SELECTOR (MODAL) --- */
.part-selector-box { 
    border: 1px solid #cbd5e1; border-radius: 8px; max-height: 240px; overflow-y: auto; 
    background: #fff; box-shadow: inset 0 2px 4px rgba(0,0,0,0.03); 
}
.part-item { 
    display: flex; align-items: center; padding: 12px 16px; 
    border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: 0.15s; 
}
.part-item:hover { background: #f0f9ff; }
.part-item input { width: 18px; height: 18px; margin-right: 12px; accent-color: #2563eb; }
.part-details { display: flex; flex-direction: column; }
.part-code { font-size: 0.75rem; font-weight: 700; color: #64748b; font-family: monospace; letter-spacing: 0.5px; }
.part-name { font-size: 0.95rem; font-weight: 600; color: #1e293b; }

/* --- MODAL DIALOG --- */
.modal-backdrop { 
    position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
    background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(4px); 
    display: flex; justify-content: center; align-items: center; z-index: 50; 
}
.modal-dialog { 
    background: white; width: 90%; max-width: 420px; border-radius: 16px; 
    padding: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); 
    display: flex; flex-direction: column; max-height: 85vh;
}
.modal-dialog.wide { max-width: 550px; }
.modal-header h3 { margin: 0 0 20px; font-size: 1.25rem; color: #0f172a; }
.modal-body { overflow-y: auto; padding-right: 4px; }
.modal-footer { margin-top: 24px; display: flex; gap: 12px; justify-content: flex-end; }

/* --- BUTTONS --- */
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary { background: white; color: #475569; padding: 10px 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-weight: 600; cursor: pointer; }
.btn-secondary:hover { background: #f8fafc; border-color: #94a3b8; }
.btn-icon { width: 32px; height: 32px; border-radius: 6px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: #64748b; }
.btn-icon:hover { border-color: #3b82f6; color: #3b82f6; }
.btn-icon.danger:hover { background: #fef2f2; border-color: #ef4444; color: #ef4444; }

/* --- UTILS --- */
.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.badge-success { background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.text-red { color: #ef4444; }

@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>