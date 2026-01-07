# backend/traceability/utils.py
from django.core.exceptions import ValidationError

def validate_serial_number(serial_number, rule):
    """
    Core Logic Validasi. 
    Bisa dipanggil oleh SerialRuleViewSet (Test) ataupun Modul QC (Live Scan).
    """
    if not rule:
        return True # Lolos jika tidak ada rule

    segments = rule.segments.all().order_by('order')
    
    # Cursor default (0-based index)
    current_cursor = 0 
    
    for seg in segments:
        # 1. Tentukan Posisi Awal (Start)
        if seg.start_index is not None and seg.start_index > 0:
            start_pos = seg.start_index - 1
        else:
            start_pos = current_cursor

        # 2. Tentukan Posisi Akhir (End)
        end_pos = start_pos + seg.length

        # 3. Cek Batas String (Safety Check)
        if len(serial_number) < end_pos:
            raise ValidationError(
                f"Segmen #{seg.order}: String terlalu pendek. Butuh sampai index {end_pos}, input cuma {len(serial_number)}."
            )

        # 4. Ambil Potongan String
        chunk = serial_number[start_pos : end_pos]

        # 5. Validasi Berdasarkan Tipe
        err_prefix = f"Posisi {start_pos+1}-{end_pos} (Segmen #{seg.order})"
        
        if seg.segment_type == 'STATIC':
            if chunk != seg.static_value:
                raise ValidationError(f"{err_prefix}: Harusnya '{seg.static_value}', terbaca '{chunk}'.")
        
        elif seg.segment_type == 'DIGIT':
            if not chunk.isdigit():
                raise ValidationError(f"{err_prefix}: Harusnya Angka, terbaca '{chunk}'.")
        
        elif seg.segment_type == 'CHAR':
            if not chunk.isalpha():
                raise ValidationError(f"{err_prefix}: Harusnya Huruf, terbaca '{chunk}'.")
                
        elif seg.segment_type == 'ALPHANUM':
            if not chunk.isalnum():
                raise ValidationError(f"{err_prefix}: Harusnya Alfanumerik, terbaca '{chunk}'.")

        elif seg.segment_type == 'YEAR':
            if not chunk.isdigit() or len(chunk) != 2:
                 raise ValidationError(f"{err_prefix}: Harusnya 2 digit Tahun.")

        elif seg.segment_type == 'MONTH':
            if not chunk.isdigit() or not (1 <= int(chunk) <= 12):
                 raise ValidationError(f"{err_prefix}: Harusnya Bulan (01-12).")

        # Update cursor
        current_cursor = end_pos
        
    return True