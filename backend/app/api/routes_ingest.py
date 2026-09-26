"""Log Ingestion & Cognitive Decision Pipeline for Sentix.

Receives enterprise security telemetry events, persists them into SQLite `logs`,
evaluates risk via TypeSafe Jev AI, strictly assigns ONE tier (Tier 1 auto-executed,
Tier 2 drafted 1-click button, Tier 3 technical playbook), records the decision in
`audit_ledger`, and prints formatted status to the terminal.
"""

import json
from fastapi import APIRouter, HTTPException

from backend.app.core.database import get_db_connection
from backend.app.models.log_models import LogIngestPayload, LogIngestResponse
from backend.app.services.audit_service import process_telemetry_pipeline

router = APIRouter(prefix="/api/logs", tags=["Ingestion"])

# Global counter for sequential terminal output tracking
ingestion_counter = 0


@router.post("/ingest", response_model=LogIngestResponse)
def ingest_log(payload: LogIngestPayload):
    """Receives a log event, persists it into SQLite, runs the Jev cognitive engine,

    and writes the decision to the audit ledger.
    """
    global ingestion_counter
    ingestion_counter += 1

    conn = get_db_connection()
    cursor = conn.cursor()

    raw_dict = {
        "id": payload.id,
        "timestamp": payload.timestamp,
        "user_id": payload.user_id,
        "source_system": payload.source_system,
        "event_type": payload.event_type,
        "client_ip": payload.client_ip,
        "subnet_type": payload.subnet_type,
        "status": payload.status,
        "failure_reason": payload.failure_reason,
        "raw_payload": payload.raw_payload,
    }

    try:
        cursor.execute("""
        INSERT INTO logs (id, timestamp, user_id, source_system, event_type, client_ip, subnet_type, status, failure_reason, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            payload.id,
            payload.timestamp,
            payload.user_id,
            payload.source_system,
            payload.event_type,
            payload.client_ip,
            payload.subnet_type,
            payload.status,
            payload.failure_reason,
            json.dumps(payload.raw_payload),
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database write error: {e}")

    conn.close()

    # Run the Cognitive Jev Decision & Audit Pipeline
    pipeline_result = process_telemetry_pipeline(raw_dict)

    # Format status for terminal display
    status_tag = f"[{payload.status}]"
    if payload.failure_reason:
        status_tag += f" ({payload.failure_reason})"

    tier_label = pipeline_result.get("selected_tier", "TIER_0_BENIGN")
    exec_status = pipeline_result.get("execution_status", "NORMAL")
    auth_persona = pipeline_result.get("authorized_persona_id")

    decision_info = f"DECISION: {tier_label} [{exec_status}]"
    if auth_persona:
        decision_info += f" (Auth: {auth_persona})"

    print(
        f"[INGESTED #{ingestion_counter:04d}] "
        f"{payload.timestamp} | "
        f"{payload.source_system:<20} | "
        f"{payload.user_id:<8} | "
        f"{status_tag:<22} | "
        f"{decision_info}"
    )

    return LogIngestResponse(
        status="recorded",
        log_id=payload.id,
        ingested_count=ingestion_counter,
        audit_id=pipeline_result.get("audit_id"),
        selected_tier=tier_label,
        execution_status=exec_status,
        attack_class=pipeline_result.get("attack_class"),
        authorized_persona_id=auth_persona,
    )
