# agent.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import win32print
import win32ui
from PIL import Image, ImageWin
import base64
import io

app = FastAPI()

# Izinkan Frontend mengakses Agent ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PrintJob(BaseModel):
    printer_name: str
    image_base64: str  # Kita akan mengirim gambar label (hasil render frontend)
    copies: int = 1

@app.get("/printers")
def get_printers():
    """Mengambil list printer yang terinstall di Windows"""
    try:
        # EnumPrinters 2 = PRINTER_ENUM_LOCAL, 4 = PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(2 | 4)
        printer_list = [p[2] for p in printers]
        return {"printers": printer_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/print")
def print_label(job: PrintJob):
    """Mencetak Gambar Silent ke Printer"""
    try:
        # 1. Decode Base64 Image
        image_data = base64.b64decode(job.image_base64.split(',')[1])
        img = Image.open(io.BytesIO(image_data))

        # 2. Buka Printer
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(job.printer_name)
        
        # 3. Mulai Job
        hDC.StartDoc("VIN Record Label")
        hDC.StartPage()

        # 4. Scaling Gambar agar pas di kertas (Opsional, sesuaikan kebutuhan)
        # Di sini kita asumsi print 1:1 sesuai ukuran pixel gambar
        dib = ImageWin.Dib(img)
        dib.draw(hDC.GetHandleOutput(), (0, 0, img.size[0], img.size[1]))

        # 5. Selesai
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()

        # Ulangi sesuai copies (looping manual atau set di driver)
        # Untuk simple loop di python:
        for _ in range(job.copies - 1):
             # (Ulangi proses open DC di atas jika perlu, atau kirim command copies)
             # Sederhananya loop request ini di frontend atau loop logic drawing
             pass 

        return {"status": "success", "message": "Sent to printer"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Jalan di port beda, misal 8081
    print("🖨️  Print Agent Running on localhost:8081...")
    uvicorn.run(app, host="127.0.0.1", port=8081)