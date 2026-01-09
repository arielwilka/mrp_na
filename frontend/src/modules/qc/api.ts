import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import type { QCTemplate, QCResultPayload } from '@/types/qc'; 

const BASE_URL = '/qc';

const getConfig = () => {
    const authStore = useAuthStore();
    return {
        headers: { 'Authorization': `Token ${authStore.token}` }
    };
};

export default {
  // Read
  getTemplatesByPart(partId: number) { 
      return axios.get<QCTemplate[]>(`${BASE_URL}/templates/`, {
          ...getConfig(),
          params: { part_master: partId }
      }); 
  },

  // --- [BARU] Create & Delete Template ---
  createTemplate(data: Partial<QCTemplate>) {
      return axios.post(`${BASE_URL}/templates/`, data, getConfig());
  },
  
  deleteTemplate(id: number) {
      return axios.delete(`${BASE_URL}/templates/${id}/`, getConfig());
  },
  // --------------------------------------

  submitResult(data: QCResultPayload) { 
      return axios.post(`${BASE_URL}/submit-result/`, data, getConfig()); 
  },
  
  getParts() { 
      return axios.get('http://127.0.0.1:8000/api/traceability/parts/', getConfig()); 
  }, 
  getHistory() {
      return axios.get(`${BASE_URL}/inspections/`, getConfig());
  },
  getSecureImage(filename: string) {
      return axios.get(`${BASE_URL}/evidence/${filename}`, {
          ...getConfig(),
          responseType: 'blob' // PENTING: Minta respons sebagai file biner
      });
  }
};