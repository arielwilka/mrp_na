export interface QCTemplate {
  id: number;
  field_key: string;
  field_label: string;
  field_type: 'NUMBER' | 'TEXT' | 'BOOLEAN' | 'IMAGE';
  min_val?: number;
  max_val?: number;
  is_mandatory: boolean;
}

export interface QCResultPayload {
  part_id: number;
  serial_number: string;
  decision: 'PASS' | 'FAIL';
  qc_data: Record<string, any>; // JSON Object dinamis
}