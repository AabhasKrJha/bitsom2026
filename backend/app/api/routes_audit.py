"""Audit Ledger API Routes for Sentix.

Provides endpoints to query decision audit records with persona-specific actionability,
and approve drafted 1-click Tier 2 actions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException

from backend.app.core.database import get_audit_records, update_audit_status, get_db_connection
from backend.app.models.audit_models import (
    AuditListResponse,
    AuditActionApprovalRequest,
    AuditActionApprovalResponse,
)

router = APIRouter(prefix="/api/audit", tags=["Audit Ledger"])


@router.get("", response_model=AuditListResponse)
def list_audit_records(
    limit: int = 50,
    persona_id: Optional[str] = None,
    tier: Optional[str] = None,
):
    """Returns decision audit records from SQLite, with persona clickability calculated."""
    records = get_audit_records(limit=limit, persona_id=persona_id, tier=tier)
    return AuditListResponse(
        count=len(records),
        persona_id=persona_id,
        records=records,
    )


@router.post("/{audit_id}/approve", response_model=AuditActionApprovalResponse)
def approve_tier_2_action(audit_id: str, request: AuditActionApprovalRequest):
    """Authorizes and executes a drafted Tier 2 action button."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_ledger WHERE id = ?;", (audit_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Audit record '{audit_id}' not found.")

    record = dict(row)

    if record["selected_tier"] != "TIER_2_DRAFTED_HITL":
        raise HTTPException(status_code=400, detail="Only Tier 2 drafted actions can be approved.")

    if record["execution_status"] != "AWAITING_APPROVAL":
        raise HTTPException(status_code=400, detail=f"Action is already in status: {record['execution_status']}.")

    authorized = record.get("authorized_persona_id")
    if authorized and authorized != request.actor_id:
        raise HTTPException(
            status_code=403,
            detail=f"Unauthorized: Persona '{request.actor_id}' cannot approve this action. Required: '{authorized}'."
        )

    success = update_audit_status(audit_id, "EXECUTED_BY_OPERATOR", request.actor_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update execution status in audit ledger.")

    return AuditActionApprovalResponse(
        status="success",
        audit_id=audit_id,
        execution_status="EXECUTED_BY_OPERATOR",
        message=f"Action authorized and executed by {request.actor_id}.",
    )
