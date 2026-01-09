export interface Brand {
    id?: number;
    name: string;
    code: string;
}

export interface ProductType {
    id?: number;
    brand: number;
    brand_name?: string;
    name: string;
    code: string;
    // UPDATED FIELD DARI BACKEND
    tracking_mode: 'VIN' | 'INTERNAL_ID' | 'BATCH'; 
    tracking_mode_display?: string; // Field helper dari serializer
    has_check_digit: boolean;
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
    code?: string;
}