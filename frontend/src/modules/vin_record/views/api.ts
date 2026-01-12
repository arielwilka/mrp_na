import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

// --- KOREKSI URL ---
// Hapus prefix '/api' karena sudah di-set global di main.ts
const BASE_URL = '/vin-record'; 

// Helper Header Token
// Kita tetap gunakan ini untuk memastikan token yang diambil adalah yang 
// paling update dari Pinia Store (jika user baru login tanpa refresh page)
const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: { 'Authorization': `Token ${authStore.token}` }
    };
};

export default {
    // --- MASTER DATA (Years & Prefixes) ---
    // URL Akhir: /api/vin-record/years/
    getYears() { 
        return axios.get(`${BASE_URL}/years/`, getConfig()); 
    },
    createYear(data: any) { 
        return axios.post(`${BASE_URL}/years/`, data, getConfig()); 
    },
    deleteYear(id: number) { 
        return axios.delete(`${BASE_URL}/years/${id}/`, getConfig()); 
    },

    // URL Akhir: /api/vin-record/prefixes/
    getPrefixes() { 
        return axios.get(`${BASE_URL}/prefixes/`, getConfig()); 
    },
    createPrefix(data: any) { 
        return axios.post(`${BASE_URL}/prefixes/`, data, getConfig()); 
    },
    deletePrefix(id: number) { 
        return axios.delete(`${BASE_URL}/prefixes/${id}/`, getConfig()); 
    },

    // --- OPERATIONAL (Records) ---
    // URL Akhir: /api/vin-record/records/
    getRecords(params: any) { 
        return axios.get(`${BASE_URL}/records/`, { ...getConfig(), params }); 
    },
    createRecord(data: any) { 
        return axios.post(`${BASE_URL}/records/`, data, getConfig()); 
    },
    updateRecord(id: number, data: any) { 
        return axios.patch(`${BASE_URL}/records/${id}/`, data, getConfig()); 
    },
    deleteRecord(id: number) { 
        return axios.delete(`${BASE_URL}/records/${id}/`, getConfig()); 
    },
    
    // Batch Generation
    batchGenerate(data: any) { 
        return axios.post(`${BASE_URL}/records/batch-generate/`, data, getConfig()); 
    },

    // --- HELPER / OPTIONS ---
    // URL Akhir: /api/vin-record/product-options/
    // Endpoint khusus untuk dropdown produk yang tracking_mode='VIN'
    getTraceableTypes() { 
        return axios.get(`${BASE_URL}/product-options/`, getConfig()); 
    },
    
    // Get Print Templates (Core Module)
    // URL Akhir: /api/templates/
    // Karena ini ada di root API (core), kita langsung slash '/'
    getTemplates() { 
        return axios.get('/templates/', getConfig()); 
    }
};