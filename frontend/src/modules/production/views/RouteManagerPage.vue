<template>
  <div class="master-page">
    
    <div class="header">
      <div>
        <h2>🗺️ Route & Process Map</h2>
        <p>Atur alur produksi, instruksi kerja, dan interlocking part (Traceability).</p>
      </div>
      <div class="header-actions">
          <button v-if="!isDetailMode" @click="openCreateModal" class="btn-primary">
            <span>+</span> Buat Route
          </button>
          <button v-else @click="backToList" class="btn-secondary">
            &larr; Kembali
          </button>
      </div>
    </div>

    <div v-if="!isDetailMode" class="card fade-in">
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
              <td class="text-center">
                <span class="badge-pill">{{ r.steps?.length || 0 }} St.</span>
              </td>
              <td class="text-center">
                <span v-if="r.is_active" class="badge-success">Active</span>
                <span v-else class="badge-gray">Draft</span>
              </td>
              <td class="text-right">
                <button @click="openDetail(r)" class="btn-icon mr-2" title="Konfigurasi Step">⚙️</button>
                <button @click="deleteRoute(r.id)" class="btn-icon danger">🗑️</button>
              </td>
            </tr>
            <tr v-if="routes.length === 0"><td colspan="5" class="text-center py-12 text-muted">Belum ada route produksi.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-else class="detail-view fade-in">
        
        <div class="info-bar">
            <div class="info-content">
                <h3>Editing: {{ activeRoute.name }}</h3>
                <span class="text-sm text-muted">Produk: <strong>{{ activeRoute.product_type_name }}</strong></span>
            </div>
            
            <div class="weight-meter">
                <div class="flex justify-between text-xs mb-1 font-bold">
                    <span>Total Bobot Kerja</span>
                    <span :class="totalWeight === 100 ? 'text-green-600' : 'text-orange-500'">{{ totalWeight }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2.5">
                    <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: Math.min(totalWeight, 100) + '%' }"></div>
                </div>
                <small v-if="totalWeight !== 100" class="text-xs text-orange-500 mt-1 block">*Idealnya total 100%</small>
            </div>

            <button class="btn-primary btn-sm" @click="openStepModal(null)">+ Tambah Step</button>
        </div>

        <div class="steps-container">
            <div v-for="(step, idx) in activeRoute.steps" :key="step.id" class="step-wrapper">
                
                <div v-if="Number(idx) < activeRoute.steps.length - 1" class="flow-line"></div>

                <div class="step-card">
                    <div class="step-number">{{ Number(idx) + 1 }}</div>
                    
                    <div class="step-content">
                        <div class="step-header">
                            <div class="flex items-center gap-2">
                                <h4>{{ step.station_name }}</h4> 
                                <span class="text-xs text-muted font-mono">({{ step.station_code }})</span>
                                <span class="badge-blue">{{ step.job_weight }}%</span>
                            </div>
                            <span class="badge-seq">Seq: {{ step.sequence }}</span>
                        </div>
                        
                        <div v-if="step.job_description" class="job-desc">
                            <span class="icon">📝</span> {{ step.job_description }}
                        </div>

                        <div class="trace-list mt-3">
                            <div class="flex items-center gap-2 mb-2">
                                <span class="text-[10px] text-muted font-bold uppercase tracking-wider">Interlocking Parts:</span>
                                <span v-if="!step.required_parts_details?.length" class="text-[10px] text-gray-400 italic">None</span>
                            </div>
                            
                            <div v-if="step.required_parts_details?.length" class="tags">
                                <span v-for="part in step.required_parts_details" :key="part.id" class="tag">
                                    <span class="tag-icon">🔧</span> 
                                    <strong>{{ part.part_number }}</strong>
                                    <span class="tag-sep">|</span>
                                    {{ part.part_name }}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="step-actions">
                        <button @click="openStepModal(step)" class="btn-icon sm" title="Edit Step">✏️</button>
                        <button @click="deleteStep(step.id)" class="btn-icon sm danger" title="Hapus Step">&times;</button>
                    </div>
                </div>
            </div>

            <div v-if="!activeRoute.steps || activeRoute.steps.length === 0" class="empty-steps">
                <div class="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg">
                    <p class="text-gray-500">Belum ada langkah produksi.</p>
                    <button class="text-blue-600 font-bold mt-2 hover:underline" @click="openStepModal(null)">
                        Klik disini untuk mulai
                    </button>
                </div>
            </div>
        </div>

    </div>

    <div v-if="modals.create" class="modal-backdrop" @click.self="modals.create = false">
        <div class="modal-dialog">
            <div class="modal-header"><h3>Buat Route Baru</h3></div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Nama Route</label>
                    <input v-model="form.name" class="form-input" placeholder="Contoh: Assembly Line Fortuner" />
                </div>
                <div class="form-group">
                    <label>Tipe Produk</label>
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
            <div class="modal-header">
                <h3>{{ isEditingStep ? 'Edit Step' : 'Tambah Step Baru' }}</h3>
                <button class="close-btn" @click="modals.step = false">&times;</button>
            </div>
            <div class="modal-body">
                
                <div class="grid-2-col">
                    <div class="form-group">
                        <label>Station <span class="text-red">*</span></label>
                        <select v-model="stepForm.station" class="form-select" :disabled="isEditingStep">
                            <option :value="null">-- Pilih Station --</option>
                            <option v-for="s in stations" :key="s.id" :value="s.id">
                                {{ s.code }} - {{ s.name }}
                            </option>
                        </select>
                        <small v-if="isEditingStep" class="text-xs text-muted">Station tidak bisa diubah saat edit.</small>
                    </div>
                    <div class="form-group">
                        <label>Urutan (Seq) <span class="text-red">*</span></label>
                        <input type="number" v-model="stepForm.sequence" class="form-input text-center" />
                    </div>
                </div>

                <div class="form-group">
                    <label>Deskripsi Pekerjaan / SOP</label>
                    <textarea v-model="stepForm.job_description" class="form-input" rows="2" placeholder="Instruksi kerja untuk operator..."></textarea>
                </div>
                <div class="form-group">
                    <label>Bobot Pekerjaan (%)</label>
                    <div class="flex items-center gap-2">
                        <input type="number" v-model="stepForm.job_weight" class="form-input w-24" placeholder="0" min="0" max="100" />
                        <span class="text-sm text-muted">Kontribusi terhadap progress total.</span>
                    </div>
                </div>

                <div class="form-group mt-4">
                    <label>Traceability Interlocking (Parts)</label>
                    
                    <div class="part-selector-box">
                        <div v-if="parts.length === 0" class="p-6 text-center text-muted flex flex-col items-center">
                            <span class="text-2xl mb-2">🚫</span>
                            <span class="text-sm font-bold">Tidak ada Part yang Kompatibel.</span>
                            <span class="text-xs mt-1">
                                Pastikan Anda sudah mendaftarkan Part Master dan <br>
                                menghubungkannya dengan Tipe Produk: 
                                <strong>{{ activeRoute?.product_type_name }}</strong>.
                            </span>
                        </div>
                        
                        <label v-else v-for="part in parts" :key="part.id" class="part-item">
                            <input type="checkbox" :value="part.id" v-model="stepForm.required_parts">
                            <div class="part-details">
                                <span class="part-code">{{ part.part_number }}</span>
                                <span class="part-name">{{ part.part_name }}</span>
                            </div>
                        </label>
                    </div>

                    <div class="bg-blue-50 text-blue-800 p-2 text-xs rounded mt-2 border border-blue-100">
                        ℹ️ <strong>Interlocking:</strong> Operator wajib scan barcode part yang dicentang agar bisa menyelesaikan step ini.
                    </div>
                </div>

            </div>
            <div class="modal-footer">
                <button @click="saveStep" class="btn-primary w-full">
                    {{ isEditingStep ? 'Update Konfigurasi' : 'Simpan Step' }}
                </button>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '../api';

const isLoading = ref(false);
const isDetailMode = ref(false);
const isEditingStep = ref(false); 

const routes = ref<any[]>([]);
const activeRoute = ref<any>(null);

const productTypes = ref<any[]>([]);
const stations = ref<any[]>([]);
const parts = ref<any[]>([]); // Dynamic based on product

const modals = reactive({ create: false, step: false });

const form = reactive({ name: '', product_type: null, is_active: true });

// Form Step
const stepForm = reactive({ 
    id: null as number | null,
    station: null, 
    sequence: 10, 
    required_parts: [] as number[],
    job_description: '',
    job_weight: 0
});

// Computed: Hitung total bobot
const totalWeight = computed(() => {
    if (!activeRoute.value || !activeRoute.value.steps) return 0;
    return activeRoute.value.steps.reduce((sum: number, s: any) => sum + (s.job_weight || 0), 0);
});

onMounted(async () => {
    loadRoutes();
    // [UPDATE] Hapus load all parts. Load parts dilakukan per route.
    const [prodRes, stRes] = await Promise.all([
        api.getProductTypes(),
        api.getStations()
    ]);
    productTypes.value = prodRes.data.results || prodRes.data || [];
    stations.value = stRes.data.results || stRes.data || [];
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
    try {
        const res = await api.getRoute(route.id);
        activeRoute.value = res.data;
        
        // [UPDATE] Load parts yang relevan dengan produk route ini
        if (activeRoute.value.product_type) {
            loadPartsForProduct(activeRoute.value.product_type);
        } else {
            parts.value = [];
        }

        isDetailMode.value = true;
    } catch(e) { alert("Error loading detail"); }
};

// [BARU] Helper load part terfilter
const loadPartsForProduct = async (typeId: number) => {
    try {
        const res = await api.getParts(typeId);
        parts.value = res.data.results || res.data || [];
    } catch (e) {
        console.error("Gagal load BOM parts", e);
    }
};

const openCreateModal = () => { form.name = ''; form.product_type = null; modals.create = true; };

const saveRoute = async () => {
    try { await api.createRoute(form); modals.create = false; loadRoutes(); } catch(e) { alert("Gagal"); }
};

const deleteRoute = async (id: number) => {
    if(confirm("Hapus?")) { await api.deleteRoute(id); loadRoutes(); }
};

// --- STEP MANAGEMENT ---

const openStepModal = (stepData: any | null) => {
    if (stepData) {
        // Mode Edit
        isEditingStep.value = true;
        stepForm.id = stepData.id;
        stepForm.station = stepData.station;
        stepForm.sequence = stepData.sequence;
        stepForm.job_description = stepData.job_description;
        stepForm.job_weight = stepData.job_weight;
        // Map required_parts dari details ke array ID
        stepForm.required_parts = stepData.required_parts_details 
            ? stepData.required_parts_details.map((p: any) => p.id) 
            : [];
    } else {
        // Mode Create
        isEditingStep.value = false;
        stepForm.id = null;
        stepForm.station = null;
        
        // Auto Sequence (Max + 10)
        const currentSteps = activeRoute.value.steps || [];
        const maxSeq = currentSteps.length > 0 ? Math.max(...currentSteps.map((s:any) => s.sequence)) : 0;
        stepForm.sequence = maxSeq + 10;
        
        stepForm.required_parts = [];
        stepForm.job_description = '';
        stepForm.job_weight = 0;
    }
    
    modals.step = true;
};

const saveStep = async () => {
    if(!stepForm.station) return alert("Pilih Station!");

    const payload = {
        route: activeRoute.value.id,
        station: stepForm.station,
        sequence: stepForm.sequence,
        required_parts: stepForm.required_parts,
        job_description: stepForm.job_description,
        job_weight: stepForm.job_weight
    };

    try {
        if (isEditingStep.value && stepForm.id) {
            await api.updateRouteStep(stepForm.id, payload);
        } else {
            await api.addRouteStep(payload);
        }
        
        modals.step = false;
        openDetail(activeRoute.value); // Refresh detail
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
/* --- BASE & LAYOUT --- */
.master-page { padding: 24px; max-width: 1200px; margin: 0 auto; font-family: 'Inter', sans-serif; color: #334155; }
.header { margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; color: #0f172a; font-size: 1.5rem; font-weight: 700; }
.header p { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }

/* --- CARD & TABLE --- */
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.table-responsive { width: 100%; overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th { background: #f8fafc; padding: 14px 20px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.75rem; color: #475569; text-transform: uppercase; font-weight: 700; }
.table td { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; vertical-align: middle; }
.table tr:hover td { background-color: #f8fafc; }

/* --- DETAIL VIEW (PROCESS MAP) --- */
.detail-view { animation: slideUp 0.3s ease-out; }
.info-bar { background: #fff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; gap: 20px; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.info-content { flex: 1; }
.info-content h3 { margin: 0; font-size: 1.2rem; font-weight: 700; color: #1e293b; }

.weight-meter { width: 200px; margin-right: 20px; }

/* FLOW STYLES */
.steps-container { display: flex; flex-direction: column; padding-bottom: 40px; position: relative; }
.step-wrapper { position: relative; padding-left: 10px; }

/* Vertical Flow Line */
.flow-line { position: absolute; left: 38px; top: 50px; bottom: -20px; width: 2px; background: #cbd5e1; z-index: 0; }

.step-card { display: flex; align-items: flex-start; background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; position: relative; margin-bottom: 16px; transition: all 0.2s; z-index: 1; }
.step-card:hover { border-color: #94a3b8; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); transform: translateY(-1px); }

.step-number { width: 40px; height: 40px; background: #3b82f6; color: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; margin-right: 16px; flex-shrink: 0; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3); border: 2px solid white; z-index: 2; }

.step-content { flex: 1; }
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px dashed #e2e8f0; padding-bottom: 8px; }
.step-header h4 { margin: 0; font-size: 1.1rem; color: #0f172a; font-weight: 700; }

.job-desc { background: #fffbeb; color: #b45309; padding: 10px 14px; border-radius: 8px; font-size: 0.9rem; border: 1px solid #fcd34d; margin-bottom: 12px; line-height: 1.5; }

/* Traceability Tags */
.trace-list { background: #f8fafc; padding: 12px 16px; border-radius: 8px; border: 1px solid #e2e8f0; }
.tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { font-size: 0.8rem; background: white; color: #0f172a; padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e1; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
.tag-icon { color: #3b82f6; }
.tag-sep { color: #cbd5e1; }

.step-actions { display: flex; flex-direction: column; gap: 6px; margin-left: 12px; }

/* --- FORM & MODAL --- */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; font-size: 0.9rem; color: #334155; }
.form-input, .form-select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; box-sizing: border-box; }
.form-select:disabled { background-color: #f1f5f9; cursor: not-allowed; }

.part-selector-box { border: 1px solid #cbd5e1; border-radius: 8px; max-height: 240px; overflow-y: auto; background: #fff; }
.part-item { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: background 0.1s; }
.part-item:hover { background: #f0f9ff; }
.part-item input { width: 18px; height: 18px; margin-right: 12px; }
.part-details { display: flex; flex-direction: column; }
.part-code { font-size: 0.75rem; font-weight: 700; color: #64748b; font-family: monospace; }
.part-name { font-size: 0.9rem; font-weight: 600; color: #1e293b; }

.modal-backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(4px); display: flex; justify-content: center; align-items: center; z-index: 50; }
.modal-dialog { background: white; width: 90%; max-width: 420px; border-radius: 16px; padding: 0; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-direction: column; max-height: 90vh; overflow: hidden; }
.modal-dialog.wide { max-width: 600px; }
.modal-header { padding: 20px 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.modal-header h3 { margin: 0; font-size: 1.2rem; font-weight: 700; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }
.modal-body { padding: 24px; overflow-y: auto; }
.modal-footer { padding: 16px 24px; background: #f8fafc; border-top: 1px solid #f1f5f9; }

/* --- UTILS --- */
.btn-primary { background: #2563eb; color: white; padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background: #1d4ed8; }
.btn-secondary { background: white; color: #475569; padding: 10px 20px; border-radius: 8px; border: 1px solid #cbd5e1; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-secondary:hover { background: #f1f5f9; }

.btn-icon { width: 34px; height: 34px; border-radius: 8px; border: 1px solid #e2e8f0; background: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; color: #64748b; transition: 0.2s; }
.btn-icon:hover { border-color: #3b82f6; color: #3b82f6; }
.btn-icon.danger:hover { background: #fef2f2; border-color: #ef4444; color: #ef4444; }

.badge-success { background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-gray { background: #f1f5f9; color: #64748b; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-blue { background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; border: 1px solid #bfdbfe; }
.badge-pill { background: #f1f5f9; color: #475569; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
.badge-seq { background: #f8fafc; border: 1px solid #e2e8f0; color: #64748b; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; }

.grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.text-red { color: #ef4444; }
.w-24 { width: 6rem; }

@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>