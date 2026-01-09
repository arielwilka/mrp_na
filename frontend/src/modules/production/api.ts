import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const BASE_URL = '/production';
const TRACE_URL = '/traceability';
const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: { 'Authorization': `Token ${authStore.token}` }
    };
};

export default {
    // --- MASTER DATA (Existing) ---
    getWorkCenters() { return axios.get(`${BASE_URL}/work-centers/`, getConfig()); },
    createWorkCenter(data: any) { return axios.post(`${BASE_URL}/work-centers/`, data, getConfig()); },
    updateWorkCenter(id: number, data: any) { return axios.put(`${BASE_URL}/work-centers/${id}/`, data, getConfig()); },
    deleteWorkCenter(id: number) { return axios.delete(`${BASE_URL}/work-centers/${id}/`, getConfig()); },

    getStations() { return axios.get(`${BASE_URL}/stations/`, getConfig()); },
    createStation(data: any) { return axios.post(`${BASE_URL}/stations/`, data, getConfig()); },
    updateStation(id: number, data: any) { return axios.put(`${BASE_URL}/stations/${id}/`, data, getConfig()); },
    deleteStation(id: number) { return axios.delete(`${BASE_URL}/stations/${id}/`, getConfig()); },

    getRoutes() { return axios.get(`${BASE_URL}/routes/`, getConfig()); },
    getRoute(id: number) { return axios.get(`${BASE_URL}/routes/${id}/`, getConfig()); },
    createRoute(data: any) { return axios.post(`${BASE_URL}/routes/`, data, getConfig()); },
    deleteRoute(id: number) { return axios.delete(`${BASE_URL}/routes/${id}/`, getConfig()); },
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
    getPlans() { return axios.get(`${BASE_URL}/plans/`, getConfig()); },
    createPlan(data: any) { return axios.post(`${BASE_URL}/plans/`, data, getConfig()); },
    deletePlan(id: number) { return axios.delete(`${BASE_URL}/plans/${id}/`, getConfig()); },

    // --- [BARU] PPIC: ORDERS (SPK) ---
    getOrders() { return axios.get(`${BASE_URL}/orders/`, getConfig()); },
    createOrder(data: any) { return axios.post(`${BASE_URL}/orders/`, data, getConfig()); }, // Auto VIN Booking Backend
    
    
    // Ambil varian spesifik (untuk dropdown plan)
    getVariants(typeId: number) { return axios.get(`/product/variants/?product_type=${typeId}`, getConfig()); },
    shopFloorScan(scanValue: string, stationId: number) { 
        return axios.post(`${BASE_URL}/shop-floor/scan-unit/`, { 
            scan_value: scanValue, 
            station_id: stationId 
        }, getConfig()); 
    },
    getColors() { 
        // Asumsi endpoint master product color ada di sini
        return axios.get('/product/colors/', getConfig()); 
    },
    shopFloorScanPart(payload: { unit_id: number, station_id: number, part_barcode: string }) {
        return axios.post(`${BASE_URL}/shop-floor/scan-part/`, payload, getConfig());
    },
    
    // Eksekusi (PASS/FAIL/PAUSE)
    shopFloorProcess(payload: { unit_id: number, station_id: number, action: 'PASS' | 'REJECT' | 'PAUSE' | string, reason?: string }) {
        return axios.post(`${BASE_URL}/shop-floor/process-station/`, payload, getConfig());
    }
    
};