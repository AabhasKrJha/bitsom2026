from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class RawLogInput(BaseModel):
    log_text: str
    source_system: str = "Okta SSO"
    scenario_id: Optional[str] = None


class ExtractedTelemetry(BaseModel):
    source_ip: str
    target_user: str
    user_role: str
    is_privileged: bool = False
    attempt_count: int
    time_window_seconds: int
    timestamp: str
    target_service: str
    geo_origin: str
    asn_org: str
    is_shared_subnet: bool = False
    is_off_hours: bool = False
    dynamic_context_tags: List[str] = Field(default_factory=list)


class JevChoiceAnswer(BaseModel):
    choice: str
    confidence: float
    probabilities: Dict[str, float]


class JevScoreAnswer(BaseModel):
    score: float
    confidence: float
    probabilities: Dict[str, float]
    legend: Dict[str, Union[str, Dict[str, Any]]]


class JevNoulAnswer(BaseModel):
    noul: float


class JevAnswers(BaseModel):
    is_signature_match: JevNoulAnswer
    base_threat_score: JevScoreAnswer
    triage_policy: JevChoiceAnswer
    dynamic_answers: Dict[str, Any] = Field(default_factory=dict)


class DraftedMitigation(BaseModel):
    action_type: str  # e.g., "RATE_LIMIT_IP", "BLOCK_SUBNET", "FORCE_PASSWORD_RESET", "STEP_UP_MFA"
    target: str       # e.g., "198.51.100.42" or "sarah.chen@enterprise.com" or "198.51.100.0/24"
    scope_description: str
    estimated_blast_radius: str
    recommended_duration: str
    reversible: bool = True


class PolicyEvaluation(BaseModel):
    recommended_action: str  # "AUTO_MITIGATE" | "DRAFT_AND_APPROVE" | "ESCALATE_LEAD"
    composite_risk_score: float  # Normalized 0.0 - 10.0
    blast_radius_rating: str     # "ZERO" | "LOW" | "HIGH" | "CRITICAL"
    blast_radius_details: str
    requires_human_approval: bool
    drafted_mitigation: DraftedMitigation
    ai_rationale: str
    confidence_score: float


class IncidentRecord(BaseModel):
    incident_id: str
    created_at: str
    source_system: str
    status: str  # "AUTO_EXECUTED" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED" | "ESCALATED"
    raw_log: str
    telemetry: ExtractedTelemetry
    jev_answers: JevAnswers
    policy: PolicyEvaluation
    execution_result: Optional[Dict[str, Any]] = None
    analyst_action_at: Optional[str] = None
    analyst_notes: Optional[str] = None


class ApprovalRequest(BaseModel):
    decision: str  # "APPROVE" | "REJECT" | "APPLY_SAFE_ALTERNATIVE"
    analyst_notes: Optional[str] = "Approved via Sentix SOC Cockpit"
