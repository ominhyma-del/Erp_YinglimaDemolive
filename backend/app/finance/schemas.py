"""
Pydantic Schemas for the Financial Report & Payment Planner Module.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


SourceTypeLiteral = Literal["local_purchase", "sale_order"]
StageLiteral = Literal["pending", "cleared", "all"]


class FinancePaymentCreate(BaseModel):
    payment_date: date
    amount: float = Field(..., gt=0, description="Payment installment amount")
    currency: str | None = Field(default=None, max_length=16)
    payment_mode: str | None = Field(default=None, max_length=100)
    bank_charges: float = Field(default=0.0, ge=0)
    reference_no: str | None = Field(default=None, max_length=150)
    attachment_url: str | None = Field(default=None, max_length=500)
    remarks: str | None = Field(default=None)
    # Optional convenience: update due_date or payment_terms on the parent record at the same time
    next_due_date: date | None = Field(default=None)
    payment_terms: str | None = Field(default=None, max_length=120)


class FinancePaymentResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    payment_date: date
    amount: float
    currency: str
    payment_mode: str | None = None
    bank_charges: float = 0.0
    reference_no: str | None = None
    attachment_url: str | None = None
    remarks: str | None = None
    created_by_id: uuid.UUID | None = None
    created_by_name: str | None = None
    created_at: datetime | None = None


class FinanceMetaUpdate(BaseModel):
    payment_terms: str | None = None
    expected_dispatch_date: date | None = None
    due_date: date | None = None
    delivery_status: str | None = None
    attachment_url: str | None = None
    remarks: str | None = None

    # Sales Process / Export & Agent Freight Bill fields
    tt_received_date: date | None = None
    expected_stuffing_date: str | None = None
    bl_details: str | None = None
    bl_status: str | None = None
    bill_status: str | None = None
    agent_name: str | None = None
    agent_local_charge: float | None = None
    agent_freight_charge: float | None = None
    agent_inv_amount: float | None = None
    agent_payment_date: date | None = None


class LocalPurchaseFinanceRow(BaseModel):
    source_id: uuid.UUID
    source_type: str = "local_purchase"
    invoice_no: str
    invoice_date: date | None = None
    consignment_code: str | None = None
    supplier_id: uuid.UUID | None = None
    supplier_name: str
    organization_name: str | None = None
    branch_name: str | None = None
    source_status: str
    currency: str = "RMB"

    # Product summary (from LocalPurchaseItem rows)
    items_summary: str = ""
    items_count: int = 0
    total_quantity: float = 0.0

    # Financials (RMB + USD equivalent)
    invoice_total_value: float = 0.0
    total_expenses: float = 0.0
    total_amount: float = 0.0
    paid_amount: float = 0.0
    balance_amount: float = 0.0
    total_bank_charges: float = 0.0
    usd_exchange_rate: float = 7.20
    total_amount_usd: float = 0.0
    paid_amount_usd: float = 0.0
    balance_amount_usd: float = 0.0

    # Stage & Payment Planner Metadata
    stage: Literal["pending", "cleared"] = "pending"
    payment_terms: str | None = None
    expected_dispatch_date: date | None = None
    due_date: date | None = None
    last_payment_date: date | None = None
    delivery_status: str | None = None
    attachment_url: str | None = None
    remarks: str | None = None
    payments_count: int = 0
    payments: list[FinancePaymentResponse] = Field(default_factory=list)


class SaleOrderFinanceRow(BaseModel):
    source_id: uuid.UUID
    source_type: str = "sale_order"
    order_no: str
    order_date: date | None = None
    consignment_code: str | None = None
    buyer_id: uuid.UUID | None = None
    buyer_name: str
    buyer_branch_name: str | None = None
    organization_name: str | None = None
    source_status: str
    currency: str = "USD"

    # Shipment & Product Info
    items_summary: str = ""
    items_count: int = 0
    total_quantity: float = 0.0
    expected_stuffing_date: str | None = None
    etd_origin_date: date | None = None
    eta_port_date: date | None = None
    container_no: str | None = None

    # Customer Export Financials (USD / Order Currency)
    ocean_freight_usd: float = 0.0
    local_charges_coc_usd: float = 0.0
    total_amount: float = 0.0
    paid_amount: float = 0.0
    balance_amount: float = 0.0
    total_bank_charges: float = 0.0
    usd_exchange_rate: float = 7.20

    # Stage & Customer Schedule Metadata
    stage: Literal["pending", "cleared"] = "pending"
    payment_terms: str | None = None
    tt_received_date: date | None = None
    due_date: date | None = None
    last_payment_date: date | None = None
    attachment_url: str | None = None
    remarks: str | None = None

    # Forwarder / Agent Freight Bill Info (Manager's Excel Tabs 3 & 4)
    bl_details: str | None = None
    bl_status: str | None = None
    bill_status: str | None = None
    agent_name: str | None = None
    agent_local_charge: float = 0.0
    agent_freight_charge: float = 0.0
    agent_inv_amount: float = 0.0
    agent_payment_date: date | None = None

    payments_count: int = 0
    payments: list[FinancePaymentResponse] = Field(default_factory=list)


class SectionKpiSummary(BaseModel):
    total_records: int = 0
    pending_records: int = 0
    cleared_records: int = 0
    currency: str = "RMB"
    total_amount: float = 0.0
    paid_amount: float = 0.0
    balance_amount: float = 0.0
    secondary_currency: str = "USD"
    total_amount_secondary: float = 0.0
    paid_amount_secondary: float = 0.0
    balance_amount_secondary: float = 0.0


class FinanceReportResponse(BaseModel):
    usd_to_rmb_rate: float = 7.20
    local_purchase_kpi: SectionKpiSummary
    sale_order_kpi: SectionKpiSummary
    agent_freight_kpi: SectionKpiSummary
    local_purchases: list[LocalPurchaseFinanceRow] = Field(default_factory=list)
    sale_orders: list[SaleOrderFinanceRow] = Field(default_factory=list)


# ==============================================================================
# Consignment Overview Schemas (Unified Finance Planning + Gallery + Cargo Status)
# ==============================================================================

class ConsignmentFinanceLine(BaseModel):
    id: str
    role: Literal["Supplier", "Customer", "Cargo Forwarder"]
    party_name: str
    doc_no: str
    payment_terms: str | None = None
    attachment_url: str | None = None
    currency: str = "RMB"
    total_amount: float = 0.0
    paid_amount: float = 0.0
    balance_amount: float = 0.0
    due_date: date | None = None
    stage: Literal["pending", "cleared"] = "pending"
    source_type: str | None = None
    source_id: str | None = None


class ConsignmentDocumentSlot(BaseModel):
    slot_key: str
    label: str
    file_url: str | None = None
    filename: str | None = None
    uploaded_at: str | None = None
    uploaded_by: str | None = None
    is_auto_linked: bool = False


class ConsignmentChecklistItem(BaseModel):
    key: str
    label: str
    value: bool = False


class ConsignmentProductLine(BaseModel):
    sr_no: int
    product_name: str
    product_code: str | None = None
    hsn_code: str | None = None
    quantity: float = 0.0
    uom: str = "PCS"
    consignment_code: str | None = None
    supplier_name: str | None = None
    source_doc_no: str | None = None


class ConsignmentOverviewRow(BaseModel):
    consignment_key: str
    display_title: str
    consignment_code: str | None = None
    invoice_or_order_summary: str
    order_date: date | None = None
    supplier_summary: str = "—"
    buyer_name: str | None = None
    branch_name: str | None = None
    organization_name: str | None = None
    etd_origin_date: date | None = None
    eta_port_date: date | None = None
    stuffing_date: str | None = None
    container_no: str | None = None
    bl_no: str | None = None
    forwarder_name: str | None = None
    cargo_remarks: str | None = None

    # Counts & status summary for list view
    overall_stage: Literal["pending", "cleared"] = "pending"
    docs_uploaded_count: int = 0
    docs_total_count: int = 16
    checklist_yes_count: int = 0
    checklist_total_count: int = 12
    total_supplier_rmb: float = 0.0
    paid_supplier_rmb: float = 0.0
    balance_supplier_rmb: float = 0.0
    total_customer_usd: float = 0.0
    received_customer_usd: float = 0.0
    balance_customer_usd: float = 0.0
    total_forwarder_rmb: float = 0.0

    # Full detail sections
    finance_rows: list[ConsignmentFinanceLine] = Field(default_factory=list)
    documents: list[ConsignmentDocumentSlot] = Field(default_factory=list)
    checklist: list[ConsignmentChecklistItem] = Field(default_factory=list)
    products: list[ConsignmentProductLine] = Field(default_factory=list)


class ConsignmentOverviewListResponse(BaseModel):
    total_consignments: int = 0
    pending_consignments: int = 0
    cleared_consignments: int = 0
    items: list[ConsignmentOverviewRow] = Field(default_factory=list)


class ConsignmentChecklistUpdatePayload(BaseModel):
    checklist: dict[str, bool] | None = None
    cargo_remarks: str | None = None
    etd_origin_date: date | None = None
    eta_port_date: date | None = None
    forwarder_name: str | None = None


