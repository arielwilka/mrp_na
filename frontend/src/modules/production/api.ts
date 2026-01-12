import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

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
    };
};

export default {
    // ==========================================
    // 2. MASTER DATA
    // ==========================================
    
    // Work Centers
    getWorkCenters() { return axios.get(`${BASE_URL}/work-centers/`, getConfig()); },
    createWorkCenter(data: any) { return axios.post(`${BASE_URL}/work-centers/`, data, getConfig()); },
    updateWorkCenter(id: number, data: any) { return axios.put(`${BASE_URL}/work-centers/${id}/`, data, getConfig()); },
    deleteWorkCenter(id: number) { return axios.delete(`${BASE_URL}/work-centers/${id}/`, getConfig()); },

    // Stations
    getStations(params?: any) {
        // Fix: Use BASE_URL variable for consistency
        return axios.get(`${BASE_URL}/stations/`, { ...getConfig(), params });
    },
    createStation(data: any) { return axios.post(`${BASE_URL}/stations/`, data, getConfig()); },
    updateStation(id: number, data: any) { return axios.put(`${BASE_URL}/stations/${id}/`, data, getConfig()); },
    deleteStation(id: number) { return axios.delete(`${BASE_URL}/stations/${id}/`, getConfig()); },

    // Routes & Config
    getRoutes() { return axios.get(`${BASE_URL}/routes/`, getConfig()); },
    getRoute(id: number) { return axios.get(`${BASE_URL}/routes/${id}/`, getConfig()); },
    createRoute(data: any) { return axios.post(`${BASE_URL}/routes/`, data, getConfig()); },
    deleteRoute(id: number) { return axios.delete(`${BASE_URL}/routes/${id}/`, getConfig()); },
    
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
    getPlans() { return axios.get(`${BASE_URL}/plans/`, getConfig()); },
    createPlan(data: any) { return axios.post(`${BASE_URL}/plans/`, data, getConfig()); },
    deletePlan(id: number) { return axios.delete(`${BASE_URL}/plans/${id}/`, getConfig()); },

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
            scan_value: scanValue, 
            station_id: stationId 
        }, getConfig()); 
    },
    
    // Scan Part (Traceability)
    shopFloorScanPart(payload: { unit_id: number, station_id: number, part_barcode: string }) {
        return axios.post(`${BASE_URL}/shop-floor/scan-part/`, payload, getConfig());
    },
    
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
};