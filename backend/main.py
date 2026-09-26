"""FastAPI Server for Sentix AutoOps Incident Triage & Mitigation Engine."""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.schemas import (
    RawLogInput,
    IncidentRecord,
    ApprovalRequest,
)
from backend.scenarios import SCENARIOS
from backend.extractor import extract_telemetry
from backend.jev_client import evaluate_system_one
from backend.policy_engine import evaluate_policy_and_guardrails
from backend.mitigation_store import store

app = FastAPI(
    title="Sentix AutoOps Engine",
    description="Autonomous SecOps Triage & Blast-Radius Guardrails powered by TypeSafe Jev System-One",
    version="1.0.0",
)

# Enable CORS for Streamlit / external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Sentix AutoOps Engine",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "jev_mode": "Live TypeSafe API" if os.getenv("TYPESAFE_API_KEY") else "Calibrated System-One Simulator",
        "llm_mode": "Live OpenAI/Azure" if os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY") else "Deterministic Heuristic Extractor",
    }


@app.get("/api/scenarios")
def get_scenarios():
    return SCENARIOS


@app.post("/api/incidents/analyze", response_model=IncidentRecord)
def analyze_incident(payload: RawLogInput):
    # If scenario_id is provided, populate log text from prebuilt scenarios
    log_text = payload.log_text
    source_system = payload.source_system

    if payload.scenario_id and payload.scenario_id in SCENARIOS:
        scenario = SCENARIOS[payload.scenario_id]
        log_text = scenario["log_text"]
        source_system = scenario["source_system"]

    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Log content cannot be empty.")

    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    # 1. Telemetry Extraction & Dynamic Tag Synthesis
    telemetry = extract_telemetry(log_text, source_system)

    # 2. TypeSafe Jev System-One Parallel Evaluation (Static + Dynamic Speculative)
    jev_answers = evaluate_system_one(telemetry)

    # 3. Policy Engine Evaluation with Blast-Radius Guardrails
    policy = evaluate_policy_and_guardrails(telemetry, jev_answers)

    # 4. Determine initial execution state
    if policy.recommended_action == "AUTO_MITIGATE":
        initial_status = "AUTO_EXECUTED"
        exec_result = {
            "enforced": True,
            "applied_at": datetime.utcnow().isoformat() + "Z",
            "action": policy.drafted_mitigation.action_type,
            "target": policy.drafted_mitigation.target,
            "executor": "Sentix Autonomous Daemon (Zero-Touch)",
            "message": "Temporary rate-limit applied successfully to WAF edge.",
        }
    elif policy.recommended_action == "DRAFT_AND_APPROVE":
        initial_status = "PENDING_APPROVAL"
        exec_result = None
    else:
        initial_status = "ESCALATED"
        exec_result = {
            "enforced": False,
            "action": "DISPATCH_SOC_DIAGNOSTIC_PACKET",
            "target": telemetry.target_user,
            "executor": "Escalated to Tier-2 SecOps Threat Hunter",
            "message": "Diagnostic bundle transmitted to SOC lead Slack/PagerDuty queue.",
        }

    record = IncidentRecord(
        incident_id=incident_id,
        created_at=datetime.utcnow().isoformat() + "Z",
        source_system=source_system,
        status=initial_status,
        raw_log=log_text,
        telemetry=telemetry,
        jev_answers=jev_answers,
        policy=policy,
        execution_result=exec_result,
    )

    return store.save_incident(record)


@app.post("/api/mitigations/{incident_id}/approve", response_model=IncidentRecord)
def approve_mitigation(incident_id: str, request: ApprovalRequest):
    record = store.approve_incident(
        incident_id=incident_id,
        decision=request.decision,
        notes=request.analyst_notes or "Approved via Cockpit",
    )
    if not record:
        raise HTTPException(status_code=404, detail="Incident ID not found.")
    return record


@app.get("/api/incidents")
def list_incidents():
    return store.list_incidents()


@app.get("/api/audit-log")
def get_audit_log():
    return store.audit_log


@app.get("/api/kpis")
def get_kpis():
    return store.get_kpis()
