import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import type { Rule, Part, Version } from '@/types/traceability';

// 1. URL ABSOLUT (Sama seperti module Product)
const BASE_URL = '/traceability';

// 2. Helper Header Token
const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: {
            'Authorization': `Token ${authStore.token}`
        }
    };
};

export default {
  // --- RULES ---
  getRules() { 
      return axios.get<Rule[]>(`${BASE_URL}/rules/`, getConfig()); 
  },
  getRule(id: number) { 
      return axios.get<Rule>(`${BASE_URL}/rules/${id}/`, getConfig()); 
  },
  createRule(data: Rule) { 
      return axios.post(`${BASE_URL}/rules/`, data, getConfig()); 
  },
  updateRule(id: number, data: Rule) { 
      return axios.put(`${BASE_URL}/rules/${id}/`, data, getConfig()); 
  },
  deleteRule(id: number) { 
      return axios.delete(`${BASE_URL}/rules/${id}/`, getConfig()); 
  },
  testValidate(id: number, scanInput: string) { 
    return axios.post(`${BASE_URL}/rules/${id}/test-validate/`, { scan_input: scanInput }, getConfig()); 
  },

  // --- PARTS ---
  getParts() { 
      return axios.get<Part[]>(`${BASE_URL}/parts/`, getConfig()); 
  },
  getPart(id: number) { 
      return axios.get<Part>(`${BASE_URL}/parts/${id}/`, getConfig()); 
  },
  createPart(data: Part) { 
      return axios.post(`${BASE_URL}/parts/`, data, getConfig()); 
  },
  updatePart(id: number, data: Part) { 
      return axios.put(`${BASE_URL}/parts/${id}/`, data, getConfig()); 
  },
  deletePart(id: number) { 
      return axios.delete(`${BASE_URL}/parts/${id}/`, getConfig()); 
  },

  // --- VERSIONS (BOM) ---
  getVersions() { 
      return axios.get<Version[]>(`${BASE_URL}/versions/`, getConfig()); 
  },
  getVersion(id: number) { 
      return axios.get<Version>(`${BASE_URL}/versions/${id}/`, getConfig()); 
  },
  createVersion(data: Version) { 
      return axios.post(`${BASE_URL}/versions/`, data, getConfig()); 
  },
  updateVersion(id: number, data: Version) { 
      return axios.put(`${BASE_URL}/versions/${id}/`, data, getConfig()); 
  },
  deleteVersion(id: number) { 
      return axios.delete(`${BASE_URL}/versions/${id}/`, getConfig()); 
  },

  // --- HELPER UNTUK PRODUCT TYPES ---
  // Kita tembak langsung API Product untuk dropdown (Cross-Module)
  getProductTypes() { 
      return axios.get('http://127.0.0.1:8000/api/product/types/', getConfig()); 
  } 
};