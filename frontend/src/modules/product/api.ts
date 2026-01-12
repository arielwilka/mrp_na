import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import type { Brand, ProductType, ProductVariant, ProductColor } from '@/types/product';

// Gunakan URL ABSOLUT yang sama persis dengan kode normal Anda
const BASE_URL = '/product';

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
    // --- BRANDS ---
    getBrands() { 
        return axios.get<Brand[]>(`${BASE_URL}/brands/`, getConfig()); 
    },
    createBrand(data: Brand) { 
        return axios.post(`${BASE_URL}/brands/`, data, getConfig()); 
    },
    updateBrand(id: number, data: Brand) {
        return axios.put(`${BASE_URL}/brands/${id}/`, data, getConfig());
    },
    deleteBrand(id: number) { 
        return axios.delete(`${BASE_URL}/brands/${id}/`, getConfig()); 
    },

    // --- TYPES (KENDARAAN) ---
    getTypes() { 
        return axios.get<ProductType[]>(`${BASE_URL}/types/`, getConfig()); 
    },
    createType(data: ProductType) { 
        return axios.post(`${BASE_URL}/types/`, data, getConfig()); 
    },
    updateType(id: number, data: ProductType) {
        return axios.put(`${BASE_URL}/types/${id}/`, data, getConfig());
    },
    deleteType(id: number) { 
        return axios.delete(`${BASE_URL}/types/${id}/`, getConfig()); 
    },

    // --- VARIANTS ---
    getVariants(typeId: number) { 
        return axios.get<ProductVariant[]>(`${BASE_URL}/variants/?product_type=${typeId}`, getConfig()); 
    },
    createVariant(data: ProductVariant) { 
        return axios.post(`${BASE_URL}/variants/`, data, getConfig()); 
    },
    deleteVariant(id: number) { 
        return axios.delete(`${BASE_URL}/variants/${id}/`, getConfig()); 
    },

    // --- COLORS ---
    getColors(typeId: number) { 
        return axios.get<ProductColor[]>(`${BASE_URL}/colors/?product_type=${typeId}`, getConfig()); 
    },
    createColor(data: ProductColor) { 
        return axios.post(`${BASE_URL}/colors/`, data, getConfig()); 
    },
    deleteColor(id: number) { 
        return axios.delete(`${BASE_URL}/colors/${id}/`, getConfig()); 
    },
};