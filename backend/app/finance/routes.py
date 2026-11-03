"""
API Routes for the Financial Report & Payment Planner Module.
"""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends, File, Query, Request, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.service import CurrentUser
from app.core.logging import get_logger
from app.core.responses import build_success_response
from app.database.session import get_db_session
from app.finance.schemas import (
    ConsignmentChecklistUpdatePayload,
    FinanceMetaUpdate,
    FinancePaymentCreate,
    SourceTypeLiteral,
    StageLiteral,
)
from app.finance.service import FinanceService

logger = get_logger(__name__)

router = APIRouter(prefix="/finance", tags=["Finance - Financial Report & Payment Planner"])


def get_service(session: AsyncSession = Depends(get_db_session)) -> FinanceService:
    return FinanceService(session)


@router.get("/report", summary="Get full Financial Report for confirmed Local Purchases and Sale Orders")
async def get_financial_report(
    request: Request,
    stage: StageLiteral = Query(default="all", description="Filter by stage: pending | cleared | all"),
    search: str | None = Query(default=None),
    party_name: str | None = Query(default=None),
    consignment_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    report = await service.get_report(
        stage=stage,
        search=search,
        party_name=party_name,
        consignment_code=consignment_code,
        date_from=date_from,
        date_to=date_to,
    )
    return build_success_response(
        data=report.model_dump(mode="json"),
        message="Financial report fetched successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.post(
    "/{source_type}/{source_id}/payments",
    status_code=status.HTTP_201_CREATED,
    summary="Record a payment installment (advance, partial, or full) against a Local Purchase or Sale Order",
)
async def add_payment(
    request: Request,
    source_type: SourceTypeLiteral,
    source_id: uuid.UUID,
    payload: FinancePaymentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    payment = await service.add_payment(
        source_type=source_type,
        source_id=source_id,
        payload=payload,
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", None) or getattr(current_user, "email", None),
    )
    return build_success_response(
        data=payment.model_dump(mode="json"),
        message="Payment recorded successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get(
    "/{source_type}/{source_id}/payments",
    summary="List all recorded payment installments for a Local Purchase or Sale Order",
)
async def list_payments(
    request: Request,
    source_type: SourceTypeLiteral,
    source_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    payments = await service.list_payments(source_type=source_type, source_id=source_id)
    return build_success_response(
        data=[p.model_dump(mode="json") for p in payments],
        message="Payment history fetched successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.delete(
    "/payments/{payment_id}",
    summary="Delete a recorded payment installment and recalculate balance",
)
async def delete_payment(
    request: Request,
    payment_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    await service.delete_payment(payment_id=payment_id)
    return build_success_response(
        data={"deleted": True, "id": str(payment_id)},
        message="Payment installment deleted and balance recalculated.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.patch(
    "/{source_type}/{source_id}/meta",
    summary="Update financial schedule, payment terms, due date, or agent freight bill info",
)
async def update_finance_meta(
    request: Request,
    source_type: SourceTypeLiteral,
    source_id: uuid.UUID,
    payload: FinanceMetaUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    updated = await service.update_meta(
        source_type=source_type,
        source_id=source_id,
        payload=payload,
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", None) or getattr(current_user, "email", None),
    )
    return build_success_response(
        data=updated,
        message="Financial metadata updated successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get("/export", summary="Export multi-sheet Financial Planner Excel workbook")
async def export_financial_report(
    format: str = Query(default="xlsx"),
    stage: StageLiteral = Query(default="all"),
    search: str | None = Query(default=None),
    party_name: str | None = Query(default=None),
    consignment_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    excel_bytes = await service.export_excel(
        stage=stage,
        search=search,
        party_name=party_name,
        consignment_code=consignment_code,
        date_from=date_from,
        date_to=date_to,
    )
    filename = f"Financial_Planner_Report_{date.today().isoformat()}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ==============================================================================
# Consignment Overview Endpoints (Finance Planning + Gallery + Cargo Status)
# ==============================================================================

@router.get(
    "/consignment-overview",
    summary="List all Consignment Overview records (combining Finance Planning, Document Gallery, and Cargo Status)",
)
async def list_consignment_overviews(
    request: Request,
    stage: StageLiteral = Query(default="all", description="Filter by stage: pending | cleared | all"),
    search: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    result = await service.list_consignment_overviews(
        stage=stage,
        search=search,
        branch_name=branch_name,
    )
    return build_success_response(
        data=result.model_dump(mode="json"),
        message="Consignment overviews fetched successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.get(
    "/consignment-overview/detail",
    summary="Get single Consignment Overview detail by consignment_key",
)
async def get_consignment_overview_detail(
    request: Request,
    key: str = Query(..., description="Consignment key (e.g. 'MUM 51' or 'LP:INV-384')"),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    row = await service.get_consignment_overview(consignment_key=key)
    return build_success_response(
        data=row.model_dump(mode="json"),
        message="Consignment overview detail fetched successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.patch(
    "/consignment-overview/checklist",
    summary="Update Cargo Status shipment checklist toggles (Yes/No), remarks, or ETD/ETA dates",
)
async def update_consignment_checklist(
    request: Request,
    payload: ConsignmentChecklistUpdatePayload,
    key: str = Query(..., description="Consignment key"),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    updated = await service.update_consignment_checklist(
        consignment_key=key,
        payload=payload,
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", None) or getattr(current_user, "email", None),
    )
    return build_success_response(
        data=updated,
        message="Cargo status checklist updated successfully.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.post(
    "/consignment-overview/documents",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document file to a Consignment Gallery slot in Supabase Storage",
)
async def upload_consignment_document(
    request: Request,
    key: str = Query(..., description="Consignment key"),
    slot_key: str = Query(..., description="Document slot key (e.g. 'proforma_invoice', 'final_bl')"),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    file_bytes = await file.read()
    slot = await service.upload_consignment_document(
        consignment_key=key,
        slot_key=slot_key,
        file_bytes=file_bytes,
        filename=file.filename or f"{slot_key}.pdf",
        content_type=file.content_type,
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", None) or getattr(current_user, "email", None),
    )
    return build_success_response(
        data=slot.model_dump(mode="json"),
        message="Consignment document uploaded to Supabase Storage.",
        request_id=getattr(request.state, "request_id", "-"),
    )


@router.delete(
    "/consignment-overview/documents",
    summary="Delete a manually uploaded document from a Consignment Gallery slot",
)
async def delete_consignment_document(
    request: Request,
    key: str = Query(..., description="Consignment key"),
    slot_key: str = Query(..., description="Document slot key"),
    current_user: CurrentUser = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    res = await service.delete_consignment_document(
        consignment_key=key,
        slot_key=slot_key,
        user_id=current_user.id,
        user_name=getattr(current_user, "full_name", None) or getattr(current_user, "email", None),
    )
    return build_success_response(
        data=res,
        message="Consignment document removed.",
        request_id=getattr(request.state, "request_id", "-"),
    )

