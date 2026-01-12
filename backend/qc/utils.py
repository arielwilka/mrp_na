import base64
import os
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.text import slugify

def save_base64_image(data, identifier_name="capture"):
    """
    Simpan gambar dengan format nama: WAKTU_IDENTIFIER.ext
    identifier_name bisa berupa: SerialNumber_FieldKey
    """
    if isinstance(data, str) and data.startswith('data:image'):
        # 1. Pisahkan header dan data
        format, imgstr = data.split(';base64,') 
        ext = format.split('/')[-1] 
        
        # 2. Buat Nama File (Format: YYYYMMDD_HHMMSS_SerialNumber_FieldKey.jpg)
        # Gunakan slugify agar karakter aneh (misal spasi atau /) di SN aman untuk nama file
        safe_identifier = slugify(identifier_name) 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tambahkan short UUID (4 karakter) di belakang untuk cegah bentrok milidetik
        short_uuid = str(uuid.uuid4())[:4]
        
        filename = f"{timestamp}_{safe_identifier}_{short_uuid}.{ext}"
        
        # 3. Decode & Simpan
        file_data = ContentFile(base64.b64decode(imgstr), name=filename)
        
        folder = os.path.join(settings.MEDIA_ROOT, 'private_evidence')
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        file_path = os.path.join(folder, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data.read())
            
        return f"private_evidence/{filename}"
    
    return data