"""Audit Orchestration Service for Sentix.

Glues together State Synthesis, Question Formulation, Jev AI Evaluation,
Single-Tier Governance Decision, and Audit Ledger Persistence.
"""

import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db_connection, save_audit_record
from backend.app.services.state_synthesizer import synthesize_state
from backend.app.services.question_catalog import get_candidate_actions, build_question_battery
from backend.app.services.jev_client import jev_evaluator
from backend.app.services.decision_engine import decide_incident_tier


def process_telemetry_pipeline(raw_log: Dict[str, Any]) -> Dict[str, Any]:
    """Executes the end-to-end cognitive decision pipeline for an incoming log."""
    conn = get_db_connection()

    try:
        # Step 1: Synthesize Ground-Truth State
        state = synthesize_state(raw_log, conn=conn)

        # Step 2: Formulate Contextual Candidate Actions
        candidate_actions = get_candidate_actions(state)

        # Step 3: Build Dynamic Question Battery
        questions = build_question_battery(state, candidate_actions)

        # Step 4: Single Persona-Agnostic Jev AI Evaluation
        jev_output = jev_evaluator.evaluate(state=state, questions=questions)

        # Step 5: Strictly Assign Exactly ONE Tier
        decision = decide_incident_tier(raw_log, state, candidate_actions, jev_output)

        audit_id = None
        # Step 6: Record in audit_ledger Table if Actionable (Tier 1, 2, or 3)
        if decision.get("should_audit", False):
            now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            audit_id = f"aud_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

            audit_record = {
                "id": audit_id,
                "timestamp": now_ts,
                "log_id": raw_log["id"],
                "target_user_id": raw_log.get("user_id", "u_unknown"),
                "target_service": state.get("target_service", {}).get("name", "Unknown Asset"),
                "attack_class": decision["attack_class"],
                "selected_tier": decision["selected_tier"],
                "execution_status": decision["execution_status"],
                "authorized_persona_id": decision.get("authorized_persona_id"),
                "threat_confidence": decision["threat_confidence"],
                "blast_radius": decision["blast_radius"],
                "reason": decision["reason"],
                "action_payload": decision["action_payload"],
                "jev_raw_evaluation": jev_output,
            }
            save_audit_record(audit_record)

    finally:
        conn.close()

    return {
        "log_id": raw_log["id"],
        "audit_id": audit_id,
        "selected_tier": decision["selected_tier"],
        "tier_label": decision["tier_label"],
        "execution_status": decision["execution_status"],
        "attack_class": decision["attack_class"],
        "threat_confidence": decision["threat_confidence"],
        "blast_radius": decision["blast_radius"],
        "authorized_persona_id": decision.get("authorized_persona_id"),
        "reason": decision["reason"],
        "action_payload": decision["action_payload"],
        "jev_output": jev_output,
    }
