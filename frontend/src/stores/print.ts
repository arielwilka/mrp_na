import { defineStore } from 'pinia';
import axios from 'axios';

export const usePrintStore = defineStore('print', {
  state: () => ({
    agentUrl: 'http://127.0.0.1:8081',
    availablePrinters: [] as string[],
    selectedPrinter: localStorage.getItem('mrp_printer') || '',
    isAgentConnected: false,
  }),
  
  actions: {
    async checkAgent() {
      try {
        const res = await axios.get(`${this.agentUrl}/printers`);
        this.availablePrinters = res.data.printers;
        this.isAgentConnected = true;
      } catch (e) {
        this.isAgentConnected = false;
        console.warn("Print Agent not running");
      }
    },

    setPrinter(printerName: string) {
      this.selectedPrinter = printerName;
      localStorage.setItem('mrp_printer', printerName);
    },

    async silentPrint(base64Image: string, copies: number) {
      if (!this.selectedPrinter) throw new Error("Pilih printer terlebih dahulu!");
      if (!this.isAgentConnected) throw new Error("Print Agent tidak terdeteksi!");

      // --- PERBAIKAN LOGIC ---
      // Server Python crash karena dia mencoba split(',') tapi tidak menemukan koma.
      // Jadi kita harus PASTIKAN ada koma, bukan membuangnya.
      
      let payloadImage = base64Image;

      // Jika string BELUM punya header (tidak ada koma), tambahkan dummy header
      // agar server bisa melakukan .split(',')[1] dengan aman.
      if (!base64Image.includes(',')) {
          payloadImage = 'data:image/png;base64,' + base64Image;
      } 
      // Jika SUDAH punya koma, biarkan saja (JANGAN di-split di sini)

      try {
        for(let i = 0; i < copies; i++) {
            await axios.post(`${this.agentUrl}/print`, {
              printer_name: this.selectedPrinter,
              image_base64: payloadImage, // Kirim data yang punya header (koma)
            });
            
            if (copies > 1) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
      } catch (error) {
        console.error("Print Agent Error:", error);
        throw new Error("Gagal mencetak. Pastikan Local Agent berjalan.");
      }
    }
  }
});