/**
 * TypeScript definitions for the Financial Report & Payment Planner Module.
 */

export type FinanceSourceType = "local_purchase" | "sale_order";
export type FinanceStage = "pending" | "cleared" | "all";

export interface FinancePaymentItem {
  id: string;
  source_type: FinanceSourceType;
  source_id: string;
  payment_date: string;
  amount: number;
  currency: string;
  payment_mode?: string | null;
  bank_charges: number;
  reference_no?: string | null;
  attachment_url?: string | null;
  remarks?: string | null;
  created_by_id?: string | null;
  created_by_name?: string | null;
  created_at?: string | null;
}

export interface LocalPurchaseFinanceRow {
  source_id: string;
  source_type: "local_purchase";
  invoice_no: string;
  invoice_date?: string | null;
  consignment_code?: string | null;
  supplier_id?: string | null;
  supplier_name: string;
  organization_name?: string | null;
  branch_name?: string | null;
  source_status: string;
  currency: string;

  items_summary: string;
  items_count: number;
  total_quantity: number;

  invoice_total_value: number;
  total_expenses: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  total_bank_charges: number;
  usd_exchange_rate: number;
  total_amount_usd: number;
  paid_amount_usd: number;
  balance_amount_usd: number;

  stage: "pending" | "cleared";
  payment_terms?: string | null;
  expected_dispatch_date?: string | null;
  due_date?: string | null;
  last_payment_date?: string | null;
  delivery_status?: string | null;
  attachment_url?: string | null;
  remarks?: string | null;
  payments_count: number;
  payments: FinancePaymentItem[];
}

export interface SaleOrderFinanceRow {
  source_id: string;
  source_type: "sale_order";
  order_no: string;
  order_date?: string | null;
  consignment_code?: string | null;
  buyer_id?: string | null;
  buyer_name: string;
  buyer_branch_name?: string | null;
  organization_name?: string | null;
  source_status: string;
  currency: string;

  items_summary: string;
  items_count: number;
  total_quantity: number;
  expected_stuffing_date?: string | null;
  etd_origin_date?: string | null;
  eta_port_date?: string | null;
  container_no?: string | null;

  ocean_freight_usd: number;
  local_charges_coc_usd: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  total_bank_charges: number;
  usd_exchange_rate: number;

  stage: "pending" | "cleared";
  payment_terms?: string | null;
  tt_received_date?: string | null;
  due_date?: string | null;
  last_payment_date?: string | null;
  attachment_url?: string | null;
  remarks?: string | null;

  bl_details?: string | null;
  bl_status?: string | null;
  bill_status?: string | null;
  agent_name?: string | null;
  agent_local_charge: number;
  agent_freight_charge: number;
  agent_inv_amount: number;
  agent_payment_date?: string | null;

  payments_count: number;
  payments: FinancePaymentItem[];
}

export interface SectionKpiSummary {
  total_records: number;
  pending_records: number;
  cleared_records: number;
  currency: string;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  secondary_currency: string;
  total_amount_secondary: number;
  paid_amount_secondary: number;
  balance_amount_secondary: number;
}

export interface FinanceReportResponse {
  usd_to_rmb_rate: number;
  local_purchase_kpi: SectionKpiSummary;
  sale_order_kpi: SectionKpiSummary;
  agent_freight_kpi: SectionKpiSummary;
  local_purchases: LocalPurchaseFinanceRow[];
  sale_orders: SaleOrderFinanceRow[];
}

export interface FinancePaymentCreatePayload {
  payment_date: string;
  amount: number;
  currency?: string | null;
  payment_mode?: string | null;
  bank_charges?: number;
  reference_no?: string | null;
  attachment_url?: string | null;
  remarks?: string | null;
  next_due_date?: string | null;
  payment_terms?: string | null;
}

export interface FinanceMetaUpdatePayload {
  payment_terms?: string | null;
  expected_dispatch_date?: string | null;
  due_date?: string | null;
  delivery_status?: string | null;
  attachment_url?: string | null;
  remarks?: string | null;
  tt_received_date?: string | null;
  expected_stuffing_date?: string | null;
  bl_details?: string | null;
  bl_status?: string | null;
  bill_status?: string | null;
  agent_name?: string | null;
  agent_local_charge?: number | null;
  agent_freight_charge?: number | null;
  agent_inv_amount?: number | null;
  agent_payment_date?: string | null;
}

// =============================================================================
// Consignment Overview Types (Finance Planning + Gallery + Cargo Status)
// =============================================================================

export interface ConsignmentFinanceLine {
  id: string;
  role: "Supplier" | "Customer" | "Cargo Forwarder";
  party_name: string;
  doc_no: string;
  payment_terms?: string | null;
  attachment_url?: string | null;
  currency: string;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  due_date?: string | null;
  stage: "pending" | "cleared";
  source_type?: string | null;
  source_id?: string | null;
}

export interface ConsignmentDocumentSlot {
  slot_key: string;
  label: string;
  file_url?: string | null;
  filename?: string | null;
  uploaded_at?: string | null;
  uploaded_by?: string | null;
  is_auto_linked: boolean;
}

export interface ConsignmentChecklistItem {
  key: string;
  label: string;
  value: boolean;
}

export interface ConsignmentProductLine {
  sr_no: number;
  product_name: string;
  product_code?: string | null;
  hsn_code?: string | null;
  quantity: number;
  uom: string;
  consignment_code?: string | null;
  supplier_name?: string | null;
  source_doc_no?: string | null;
}

export interface ConsignmentOverviewRow {
  consignment_key: string;
  display_title: string;
  consignment_code?: string | null;
  invoice_or_order_summary: string;
  order_date?: string | null;
  supplier_summary: string;
  buyer_name?: string | null;
  branch_name?: string | null;
  organization_name?: string | null;
  etd_origin_date?: string | null;
  eta_port_date?: string | null;
  stuffing_date?: string | null;
  container_no?: string | null;
  bl_no?: string | null;
  forwarder_name?: string | null;
  cargo_remarks?: string | null;

  overall_stage: "pending" | "cleared";
  docs_uploaded_count: number;
  docs_total_count: number;
  checklist_yes_count: number;
  checklist_total_count: number;
  total_supplier_rmb: number;
  paid_supplier_rmb: number;
  balance_supplier_rmb: number;
  total_customer_usd: number;
  received_customer_usd: number;
  balance_customer_usd: number;
  total_forwarder_rmb: number;

  finance_rows: ConsignmentFinanceLine[];
  documents: ConsignmentDocumentSlot[];
  checklist: ConsignmentChecklistItem[];
  products: ConsignmentProductLine[];
}

export interface ConsignmentOverviewListResponse {
  total_consignments: number;
  pending_consignments: number;
  cleared_consignments: number;
  items: ConsignmentOverviewRow[];
}

export interface ConsignmentChecklistUpdatePayload {
  checklist?: Record<string, boolean> | null;
  cargo_remarks?: string | null;
  etd_origin_date?: string | null;
  eta_port_date?: string | null;
  forwarder_name?: string | null;
}


