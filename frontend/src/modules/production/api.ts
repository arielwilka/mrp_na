import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

<<<<<<< HEAD
// Sesuaikan URL prefix dengan backend
const BASE_URL = '/production';
const TRACE_URL = '/traceability';
const PROD_URL = '/product';

// ==========================================
// 1. TYPE DEFINITIONS
// ==========================================

export interface ProductionOrder {
  id: number;
  order_number: string;
  plan_code: string;
  target_total_qty: number;
  carried_over_wip_qty: number;
  new_material_qty: number;
  current_wip_qty: number;
  actual_finish_qty: number;
  actual_reject_qty: number;
  status: 'DRAFT' | 'RELEASED' | 'CLOSED';
  created_at: string;
  closed_at?: string | null;
}

// Support Hybrid Mode (Unit & Batch)
export interface ShopFloorResponse {
  mode: 'UNIT' | 'BATCH'; 

  // --- Fields Mode UNIT ---
  id?: number;
  internal_id?: string;
  status?: string;
  vin?: string;
  warning?: string; 
  job_info?: {
    description: string;
    weight: number;
    bom_requirements: Array<{
      part_name: string;
      part_number: string;
      is_scanned: boolean;
      status: 'INSTALLED' | 'PENDING';
    }>;
  };

  // --- Fields Mode BATCH ---
  order_id?: number;
  order_number?: string;
  product_name?: string;
  target_qty?: number;
  current_output?: number;
  current_reject?: number;
}

// Fix: Next/Previous allow null or string
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// --- CONFIG HEADER ---
const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: { 
            'Authorization': `Token ${authStore.token}`,
            'Content-Type': 'application/json'
        }
=======
const BASE_URL = '/production';
const TRACE_URL = '/traceability';
const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: { 'Authorization': `Token ${authStore.token}` }
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    };
};

export default {
<<<<<<< HEAD
    // ==========================================
    // 2. MASTER DATA
    // ==========================================
    
    // Work Centers
=======
    // --- MASTER DATA (Existing) ---
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    getWorkCenters() { return axios.get(`${BASE_URL}/work-centers/`, getConfig()); },
    createWorkCenter(data: any) { return axios.post(`${BASE_URL}/work-centers/`, data, getConfig()); },
    updateWorkCenter(id: number, data: any) { return axios.put(`${BASE_URL}/work-centers/${id}/`, data, getConfig()); },
    deleteWorkCenter(id: number) { return axios.delete(`${BASE_URL}/work-centers/${id}/`, getConfig()); },

<<<<<<< HEAD
    // Stations
    getStations(params?: any) {
        // Fix: Use BASE_URL variable for consistency
        return axios.get(`${BASE_URL}/stations/`, { ...getConfig(), params });
    },
=======
    getStations() { return axios.get(`${BASE_URL}/stations/`, getConfig()); },
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    createStation(data: any) { return axios.post(`${BASE_URL}/stations/`, data, getConfig()); },
    updateStation(id: number, data: any) { return axios.put(`${BASE_URL}/stations/${id}/`, data, getConfig()); },
    deleteStation(id: number) { return axios.delete(`${BASE_URL}/stations/${id}/`, getConfig()); },

<<<<<<< HEAD
    // Routes & Config
=======
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    getRoutes() { return axios.get(`${BASE_URL}/routes/`, getConfig()); },
    getRoute(id: number) { return axios.get(`${BASE_URL}/routes/${id}/`, getConfig()); },
    createRoute(data: any) { return axios.post(`${BASE_URL}/routes/`, data, getConfig()); },
    deleteRoute(id: number) { return axios.delete(`${BASE_URL}/routes/${id}/`, getConfig()); },
<<<<<<< HEAD
    
    // Route Steps (Detail)
    addRouteStep(data: any) { return axios.post(`${BASE_URL}/route-steps/`, data, getConfig()); },
    updateRouteStep(id: number, data: any) { return axios.put(`${BASE_URL}/route-steps/${id}/`, data, getConfig()); },
    deleteRouteStep(id: number) { return axios.delete(`${BASE_URL}/route-steps/${id}/`, getConfig()); },

    // ==========================================
    // 3. HELPERS (CROSS-APP)
    // ==========================================
    getProductTypes() { return axios.get(`${PROD_URL}/types/`, getConfig()); },
    getParts(productTypeId?: number) { 
        let url = `${TRACE_URL}/parts/`;
        if (productTypeId) {
            url += `?compatible_product_types=${productTypeId}`;
        }
        return axios.get(url, getConfig()); 
    },
    getVariants(typeId: number) { return axios.get(`${PROD_URL}/variants/?product_type=${typeId}`, getConfig()); },
    getColors(typeId: number) { 
        return axios.get(`${PROD_URL}/colors/?product_type=${typeId}`, getConfig()); 
    },

    // ==========================================
    // 4. PPIC: PLANNING & ORDERS
    // ==========================================
    
    // Plans
=======
    // --- [BARU] ROUTE STEPS (DETAIL) ---
    addRouteStep(data: any) { 
        return axios.post(`${BASE_URL}/route-steps/`, data, getConfig()); 
    },
    deleteRouteStep(id: number) { 
        return axios.delete(`${BASE_URL}/route-steps/${id}/`, getConfig()); 
    },
    // --- HELPERS ---
    getProductTypes() { return axios.get('/product/types/', getConfig()); },
    // Ambil daftar Part Master untuk dipilih sebagai "Wajib Scan"
    getParts() { return axios.get(`${TRACE_URL}/parts/`, getConfig()); },

    // --- [BARU] PPIC: PLANNING ---
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    getPlans() { return axios.get(`${BASE_URL}/plans/`, getConfig()); },
    createPlan(data: any) { return axios.post(`${BASE_URL}/plans/`, data, getConfig()); },
    deletePlan(id: number) { return axios.delete(`${BASE_URL}/plans/${id}/`, getConfig()); },

<<<<<<< HEAD
    // Orders (SPK)
    getOrders(params = {}) { 
        return axios.get<PaginatedResponse<ProductionOrder> | ProductionOrder[]>(`${BASE_URL}/orders/`, { ...getConfig(), params }); 
    },
    getOrderDetail(id: number) {
        return axios.get<ProductionOrder>(`${BASE_URL}/orders/${id}/`, getConfig());
    },
    createOrder(data: any) { 
        return axios.post(`${BASE_URL}/orders/`, data, getConfig()); 
    }, 
    
    // Handover / Close Order
    handoverOrder(id: number) { 
        return axios.post(`${BASE_URL}/orders/${id}/handover/`, {}, getConfig()); 
    },

    // ==========================================
    // 5. SHOP FLOOR (OPERATOR TABLET)
    // ==========================================
    
    // Scan Unit / SPK 
    shopFloorScan(scanValue: string, stationId: number) { 
        return axios.post<ShopFloorResponse>(`${BASE_URL}/shop-floor/scan-unit/`, { 
=======
    // --- [BARU] PPIC: ORDERS (SPK) ---
    getOrders() { return axios.get(`${BASE_URL}/orders/`, getConfig()); },
    createOrder(data: any) { return axios.post(`${BASE_URL}/orders/`, data, getConfig()); }, // Auto VIN Booking Backend
    
    
    // Ambil varian spesifik (untuk dropdown plan)
    getVariants(typeId: number) { return axios.get(`/product/variants/?product_type=${typeId}`, getConfig()); },
    shopFloorScan(scanValue: string, stationId: number) { 
        return axios.post(`${BASE_URL}/shop-floor/scan-unit/`, { 
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
            scan_value: scanValue, 
            station_id: stationId 
        }, getConfig()); 
    },
<<<<<<< HEAD
    
    // Scan Part (Traceability)
=======
    getColors() { 
        // Asumsi endpoint master product color ada di sini
        return axios.get('/product/colors/', getConfig()); 
    },
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
    shopFloorScanPart(payload: { unit_id: number, station_id: number, part_barcode: string }) {
        return axios.post(`${BASE_URL}/shop-floor/scan-part/`, payload, getConfig());
    },
    
<<<<<<< HEAD
    // Process Unit (Pass/Reject)
    shopFloorProcess(payload: { unit_id: number, station_id: number, action: 'PASS' | 'REJECT' }) {
        return axios.post(`${BASE_URL}/shop-floor/process-station/`, payload, getConfig());
    },

    // Process Batch (Counter Good/Reject) - Operator View
    shopFloorProcessBatch(payload: { order_id: number, station_id: number, type: 'GOOD'|'REJECT', qty: number }) {
        return axios.post<{
            status: string;
            current_output: number;
            current_reject: number;
            today_output: number;
        }>(`${BASE_URL}/shop-floor/process-batch/`, payload, getConfig());
    },

    // ==========================================
    // 6. UNIT MANAGEMENT (WORK ORDER LIST)
    // ==========================================
    
    // Ambil list unit dengan filter
    getProductionUnits(params: any = {}) {
        return axios.get<PaginatedResponse<any>>(`${BASE_URL}/units/`, { ...getConfig(), params });
    },

    // [ADD] Update Batch Qty (Dipakai oleh Supervisor/Admin Modal di ProductionWorkOrder.vue)
    updateBatchQty(data: { id: number, station_id: number, add_good: number, add_reject: number }) {
        // Asumsi endpoint backend untuk update qty manual via Supervisor
        return axios.post(`${BASE_URL}/units/${data.id}/update_qty/`, data, getConfig());
    },

    // [BARU] Start Manual untuk unit PLANNED (memaksa masuk Station 1)
    startManualUnit(id: number) {
        return axios.post(`${BASE_URL}/units/${id}/start_manual/`, {}, getConfig());
    },

    // Helper untuk mengambil kebutuhan part (BOM)
    getUnitRequirements(unitId: number, stationId: number) {
        return axios.get(`${BASE_URL}/shop-floor/requirements/`, { 
            ...getConfig(), 
            params: { unit_id: unitId, station_id: stationId } 
        });
    },
    updateBatchOutput(payload: { unit_id: number, added_good: number, added_reject: number }) {
        // Menggunakan endpoint units/{id}/update_qty/
        return axios.post(`${BASE_URL}/units/${payload.unit_id}/update_qty/`, payload, getConfig());
    },
=======
    // Eksekusi (PASS/FAIL/PAUSE)
    shopFloorProcess(payload: { unit_id: number, station_id: number, action: 'PASS' | 'REJECT' | 'PAUSE' | string, reason?: string }) {
        return axios.post(`${BASE_URL}/shop-floor/process-station/`, payload, getConfig());
    }
    
>>>>>>> 3d247cd96e94d8d31c95411d6828dca3da6a78d7
};