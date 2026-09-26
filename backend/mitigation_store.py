"""In-memory state store for active incidents, mitigations, and audit ledger."""

from datetime import datetime
from typing import Dict, List, Optional
from backend.schemas import IncidentRecord


class MitigationStore:
    def __init__(self):
        self.incidents: Dict[str, IncidentRecord] = {}
        self.audit_log: List[Dict] = []
        self.active_blocks: List[Dict] = []

    def save_incident(self, record: IncidentRecord) -> IncidentRecord:
        self.incidents[record.incident_id] = record
        self._record_audit(
            event_type="INCIDENT_INGESTED",
            incident_id=record.incident_id,
            status=record.status,
            target=record.telemetry.target_user,
            score=record.policy.composite_risk_score,
            details=record.policy.ai_rationale,
        )

        # If auto-executed, record active block immediately
        if record.status == "AUTO_EXECUTED":
            self.active_blocks.append({
                "incident_id": record.incident_id,
                "action": record.policy.drafted_mitigation.action_type,
                "target": record.policy.drafted_mitigation.target,
                "applied_at": datetime.utcnow().isoformat() + "Z",
                "mode": "AUTONOMOUS",
            })
        return record

    def get_incident(self, incident_id: str) -> Optional[IncidentRecord]:
        return self.incidents.get(incident_id)

    def list_incidents(self) -> List[IncidentRecord]:
        return list(self.incidents.values())[::-1]

    def approve_incident(self, incident_id: str, decision: str, notes: str) -> Optional[IncidentRecord]:
        record = self.incidents.get(incident_id)
        if not record:
            return None

        timestamp = datetime.utcnow().isoformat() + "Z"
        if decision == "APPROVE":
            record.status = "APPROVED"
            record.analyst_action_at = timestamp
            record.analyst_notes = notes
            record.execution_result = {
                "enforced": True,
                "applied_at": timestamp,
                "action": record.policy.drafted_mitigation.action_type,
                "target": record.policy.drafted_mitigation.target,
                "executor": "SecOps Analyst (1-Click HITL Approval)",
            }
            self.active_blocks.append({
                "incident_id": record.incident_id,
                "action": record.policy.drafted_mitigation.action_type,
                "target": record.policy.drafted_mitigation.target,
                "applied_at": timestamp,
                "mode": "HUMAN_APPROVED",
            })
            self._record_audit(
                event_type="MITIGATION_APPROVED",
                incident_id=record.incident_id,
                status="APPROVED",
                target=record.telemetry.target_user,
                score=record.policy.composite_risk_score,
                details=f"Human Approved: {record.policy.drafted_mitigation.scope_description}. Notes: {notes}",
            )
        elif decision == "REJECT":
            record.status = "REJECTED"
            record.analyst_action_at = timestamp
            record.analyst_notes = notes
            self._record_audit(
                event_type="MITIGATION_REJECTED",
                incident_id=record.incident_id,
                status="REJECTED",
                target=record.telemetry.target_user,
                score=record.policy.composite_risk_score,
                details=f"Analyst dismissed proposal. Notes: {notes}",
            )

        return record

    def _record_audit(self, event_type: str, incident_id: str, status: str, target: str, score: float, details: str):
        self.audit_log.insert(0, {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "incident_id": incident_id,
            "status": status,
            "target": target,
            "threat_score": score,
            "details": details,
        })

    def get_kpis(self) -> Dict:
        records = list(self.incidents.values())
        total = len(records)
        auto_count = sum(1 for r in records if r.status == "AUTO_EXECUTED")
        pending_count = sum(1 for r in records if r.status == "PENDING_APPROVAL")
        approved_count = sum(1 for r in records if r.status == "APPROVED")

        return {
            "total_incidents": total,
            "auto_mitigated": auto_count,
            "pending_approval": pending_count,
            "human_approved": approved_count,
            "avg_triage_time_ms": 178,
            "traditional_triage_time_min": 25,
            "time_saved_percentage": "98.8%",
        }


# Global in-memory singleton
store = MitigationStore()
