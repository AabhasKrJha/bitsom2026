"""Pydantic models for raw log ingestion and telemetry queries."""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class LogIngestPayload(BaseModel):
    id: str
    timestamp: str
    user_id: str
    source_system: str
    event_type: str
    client_ip: str
    subnet_type: str
    status: str  # 'SUCCESS', 'FAILURE', 'WARN'
    failure_reason: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class LogIngestResponse(BaseModel):
    status: str = "recorded"
    log_id: str
    ingested_count: int
    audit_id: Optional[str] = None
    selected_tier: Optional[str] = None
    execution_status: Optional[str] = None
    attack_class: Optional[str] = None
    authorized_persona_id: Optional[str] = None


class LogQueryResponse(BaseModel):
    count: int
    logs: List[Dict[str, Any]]


class TopologyResponse(BaseModel):
    users: List[Dict[str, Any]]
    infrastructure_nodes: List[Dict[str, Any]]
    client_devices: List[Dict[str, Any]]
    network_subnets: List[Dict[str, Any]]
    total_logs_stored: int
