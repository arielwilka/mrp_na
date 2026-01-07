export interface Segment {
  id?: number;
  order: number;
  segment_type: string;
  start_index?: number | null;
  length: number;
  static_value?: string;
}

export interface Rule {
  id?: number;
  code: string;
  name: string;
  description: string;
  segments: Segment[];
}

export interface Part {
  id?: number;
  part_number: string;
  part_name: string;
  validation_rule: number | null;
  rule_code?: string;
  rule_name?: string;
  supplier?: string;
  is_qc_required?: boolean;
  is_unique_serial?: boolean;
}

export interface Requirement {
  part_master: number | null;
  qty: number;
  is_mandatory: boolean;
  part_name?: string;
  part_number?: string;
}

export interface Version {
  id?: number;
  product_type: number | null;
  version_code: string;
  valid_from: string;
  is_active: boolean;
  requirements: Requirement[];
  product_name?: string;
}