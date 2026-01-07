export interface Brand {
  id?: number;
  name: string;
  code: string;
}

export interface ProductType {
  id?: number;
  brand: number;
  brand_name?: string; // Field tambahan dari backend
  name: string;
  code: string;
  is_vin_trace: boolean;
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
  code: string;
}