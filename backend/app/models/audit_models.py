"""Pydantic models for the Sentix Audit Ledger and Jev Evaluation Responses."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AuditActionPayload(BaseModel):
    title: Optional[str] = None
    target: Optional[str] = None
    action_id: Optional[str] = None
    button_label: Optional[str] = None
    authorized_persona_id: Optional[str] = None
    blast_radius_guardrail: Optional[str] = None
    execution_receipt: Optional[Dict[str, Any]] = None
    technical_steps: Optional[List[str]] = None
    blast_radius_explanation: Optional[str] = None


class AuditRecord(BaseModel):
    id: str
    timestamp: str
    log_id: str
    target_user_id: str
    target_service: str
    attack_class: str
    selected_tier: str  # 'TIER_1_AUTOMATED', 'TIER_2_DRAFTED_HITL', 'TIER_3_PLAYBOOK'
    execution_status: str  # 'EXECUTED', 'AWAITING_APPROVAL', 'ADVISORY_PENDING'
    authorized_persona_id: Optional[str] = None
    threat_confidence: float
    blast_radius: float
    reason: str
    action_payload: Dict[str, Any] = Field(default_factory=dict)
    jev_raw_evaluation: Dict[str, Any] = Field(default_factory=dict)
    can_act: bool = False  # Set dynamically based on querying persona


class AuditListResponse(BaseModel):
    count: int
    persona_id: Optional[str] = None
    records: List[AuditRecord]


class AuditActionApprovalRequest(BaseModel):
    actor_id: str  # Persona approving the action (e.g. 'u_ciso')
    notes: Optional[str] = None


class AuditActionApprovalResponse(BaseModel):
    status: str
    audit_id: str
    execution_status: str
    message: str
