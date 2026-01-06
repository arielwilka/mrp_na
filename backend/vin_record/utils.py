def calculate_vin_check_digit(vin_without_check_digit):
    """
    Menghitung Check Digit VIN (ISO 3779).
    Input: String VIN 17 karakter (posisi ke-9 bebas/dummy).
    Output: Karakter Check Digit ('0'-'9' atau 'X').
    """
    # Validasi panjang harus 17
    if len(vin_without_check_digit) != 17:
        return '?'

    transliteration = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
        'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '0': 0
    }
    
    weights = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]
    
    vin_list = list(vin_without_check_digit.upper())
    total_sum = 0
    
    try:
        for i, char in enumerate(vin_list):
            if i == 8: continue # Skip posisi digit ke-9
            
            value = transliteration.get(char)
            if value is None:
                return '?' # Karakter invalid
            
            total_sum += value * weights[i]
            
        remainder = total_sum % 11
        if remainder == 10:
            return 'X'
        return str(remainder)
        
    except Exception:
        return '?'