export interface Brand {
    id?: number;
    name: string;
    code: string;
}

export interface ProductType {
    id?: number;
    brand: number; // ID Brand
    brand_name?: string; // Read only
    name: string;
    code: string;
    
    // Field Baru (Penting)
    has_check_digit: boolean;
    tracking_mode: 'VIN' | 'INTERNAL_ID' | 'BATCH';
    scheduling_policy: 'DAILY_RESET' | 'CONTINUOUS';
    
    // Display only
    tracking_mode_display?: string; 
}

export interface ProductVariant {
    id?: number;
    product_type: number;
    name: string;
}

export interface ProductColor {
    id?: number;
    product_type: number;
    name: string;
    code: string;
}