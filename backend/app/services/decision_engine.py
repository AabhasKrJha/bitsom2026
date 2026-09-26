"""Deterministic Decision Engine for Sentix.

Evaluates TypeSafe Jev's objective numbers (Threat Likelihood, Blast Radius,
Action Scores) and strictly assigns EXACTLY ONE tier to the incident:
- TIER 1: Automated Action (Low risk) -> Status: EXECUTED
- TIER 2: 1-Click Action Button (Moderate risk) -> Status: AWAITING_APPROVAL
- TIER 3: Technical Mitigation Playbook (High risk / Hygiene) -> Status: ADVISORY_PENDING
- TIER 0: Benign Noise -> No action required

Assigns Tier 2 button authorization deterministically via static RBAC asset scope.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.app.services.playbook_catalog import generate_tier_3_playbook

# Static RBAC mapping: Asset domain -> Responsible persona ID
DOMAIN_TO_PERSONA = {
    "PARTNER_GATEWAY": "u_ciso",        # Elena Rostova (B2B Partner Subnet Blast Radius)
    "EXECUTIVE_IDENTITY": "u_ciso",     # Elena Rostova (SSO & Executive Portals)
    "PRODUCTION_DATABASE": "u_cto",     # David Kim (Aurora DB & Production Cloud)
    "CLOUD_IAM_ROOT": "u_cto",          # David Kim (AWS Root Accounts)
    "KUBERNETES_VPC": "u_devops",       # Marcus Vance (Kubernetes, CI/CD, VPC Secrets)
    "DEVELOPER_CODEBASE": "u_eng",      # Alex Rivera (Git Repositories, Staging Keys)
    "PERIMETER_WAF": "u_soc",           # Sarah Jenkins (Edge WAF, Threat Hunting)
}


def decide_incident_tier(
    raw_log: Dict[str, Any],
    state: Dict[str, Any],
    candidate_actions: List[Dict[str, Any]],
    jev_output: Dict[str, Any]
) -> Dict[str, Any]:
    """Inspects Jev's objective outputs and assigns strictly ONE tier."""
    threat_prob = float(jev_output.get("q_threat_prob", 0.0))
    blast_radius = float(jev_output.get("q_blast_radius", 0.0))
    attack_class = jev_output.get("q_attack_class", "BENIGN_NOISE")
    action_scores = jev_output.get("q_action_scores", {})

    # -----------------------------------------------------------------
    # BRANCH 0: BENIGN NOISE (Normal operations)
    # -----------------------------------------------------------------
    if threat_prob < 0.20 and attack_class == "BENIGN_NOISE":
        return {
            "selected_tier": "TIER_0_BENIGN",
            "tier_label": "Tier 0: Benign Telemetry",
            "execution_status": "NORMAL",
            "threat_confidence": threat_prob,
            "blast_radius": blast_radius,
            "attack_class": attack_class,
            "reason": "Normal enterprise baseline telemetry. No security action required.",
            "authorized_persona_id": None,
            "action_payload": {},
            "should_audit": False,
        }

    # Best-scored candidate action
    if action_scores and candidate_actions:
        best_action_id = max(action_scores, key=action_scores.get)
        best_action = next((a for a in candidate_actions if a["id"] == best_action_id), candidate_actions[0])
    elif candidate_actions:
        best_action = candidate_actions[0]
    else:
        best_action = {"id": "act_none", "title": "No Action", "target": "none"}

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # -----------------------------------------------------------------
    # BRANCH 1: TIER 1 (LOW RISK) -> AUTOMATED ACTION EXECUTED
    # Threat is verified (>=0.75) and blast radius is negligible (<0.20).
    # -----------------------------------------------------------------
    if threat_prob >= 0.75 and blast_radius < 0.20:
        return {
            "selected_tier": "TIER_1_AUTOMATED",
            "tier_label": "Tier 1: Autonomous Machine Action",
            "execution_status": "EXECUTED",
            "threat_confidence": threat_prob,
            "blast_radius": blast_radius,
            "attack_class": attack_class,
            "authorized_persona_id": None,
            "reason": (
                f"Autonomous containment executed. Threat confidence is high ({threat_prob:.2f}) "
                f"and collateral blast radius is negligible ({blast_radius:.2f}). Zero business disruption."
            ),
            "action_payload": {
                "action_id": best_action["id"],
                "title": best_action["title"],
                "target": best_action["target"],
                "execution_receipt": {
                    "rule_id": f"AUTO-{best_action['id'].upper()}-{raw_log['id'][-4:]}",
                    "executed_at": now_str,
                    "enforcement_point": best_action.get("enforcement_point", "Perimeter Edge"),
                }
            },
            "should_audit": True,
        }

    # -----------------------------------------------------------------
    # BRANCH 2: TIER 2 (MODERATE RISK) -> 1-CLICK ACTION BUTTON DRAFTED
    # Threat is verified (>=0.70) and blast radius is moderate (0.20 to 0.70).
    # Too risky for auto-execution, but contained enough for 1-click human sign-off.
    # -----------------------------------------------------------------
    elif threat_prob >= 0.70 and blast_radius <= 0.70:
        asset_domain = state.get("asset", {}).get("domain_type", "EXECUTIVE_IDENTITY")
        authorized_persona = DOMAIN_TO_PERSONA.get(asset_domain, "u_ciso")

        return {
            "selected_tier": "TIER_2_DRAFTED_HITL",
            "tier_label": "Tier 2: 1-Click Action Button",
            "execution_status": "AWAITING_APPROVAL",
            "threat_confidence": threat_prob,
            "blast_radius": blast_radius,
            "attack_class": attack_class,
            "authorized_persona_id": authorized_persona,
            "reason": (
                f"Action drafted with 1-click authorization button. Threat confidence is elevated ({threat_prob:.2f}), "
                f"but collateral blast radius ({blast_radius:.2f}) requires designated human sign-off from {authorized_persona}."
            ),
            "action_payload": {
                "action_id": best_action["id"],
                "button_label": f"Authorize {best_action['title']}",
                "target": best_action["target"],
                "authorized_persona_id": authorized_persona,
                "blast_radius_guardrail": best_action.get("blast_radius_warning", "Moderate operational impact."),
            },
            "should_audit": True,
        }

    # -----------------------------------------------------------------
    # BRANCH 3: TIER 3 (HIGH RISK / HYGIENE) -> TECHNICAL PLAYBOOK
    # Blast radius is high (>0.70) or passive posture drift.
    # Direct autonomous button is rejected; generates technical mitigation playbook.
    # -----------------------------------------------------------------
    else:
        playbook = generate_tier_3_playbook(attack_class, state)
        return {
            "selected_tier": "TIER_3_PLAYBOOK",
            "tier_label": "Tier 3: Course of Technical Mitigation",
            "execution_status": "ADVISORY_PENDING",
            "threat_confidence": threat_prob,
            "blast_radius": blast_radius,
            "attack_class": attack_class,
            "authorized_persona_id": None,
            "reason": (
                f"Technical course of action synthesized. Direct autonomous execution was rejected because "
                f"collateral blast radius ({blast_radius:.2f}) exceeds safety limits. Requires verified engineering remediation."
            ),
            "action_payload": playbook,
            "should_audit": True,
        }
