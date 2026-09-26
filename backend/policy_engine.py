"""Policy Engine: Code-owned control flow that combines Jev System-One answers,
applies blast-radius guardrails, and drafts actionable mitigations.
"""

from backend.schemas import (
    ExtractedTelemetry,
    JevAnswers,
    PolicyEvaluation,
    DraftedMitigation,
)


def evaluate_policy_and_guardrails(telemetry: ExtractedTelemetry, jev: JevAnswers) -> PolicyEvaluation:
    """Combines Jev primitives with deterministic enterprise business logic and blast-radius rules."""
    
    # 1. Normalize Base Score (0-2 scale to 0-10 scale)
    base_normalized = (jev.base_threat_score.score / 2.0) * 10.0

    # 2. Factor in Dynamic Speculative Scores (Composite Scoring Pattern)
    dynamic_risk_weight = 0.0
    if "executive_compromise_risk" in jev.dynamic_answers:
        exec_score = jev.dynamic_answers["executive_compromise_risk"].get("score", 0.0)
        # executive risk adds up to +3.0 to composite score
        dynamic_risk_weight += (exec_score / 2.0) * 3.0

    composite_score = min(10.0, round(base_normalized * 0.7 + dynamic_risk_weight * 0.3, 1))

    # 3. Blast-Radius Assessment
    blast_rating = "ZERO"
    blast_details = "Single consumer IP. Zero impact on collateral business systems."

    if telemetry.is_shared_subnet or "shared_partner_gateway_subnet" in telemetry.dynamic_context_tags:
        blast_rating = "HIGH"
        blast_details = (
            "Source subnet 198.51.100.0/24 hosts 18 active European B2B partner EDI channels. "
            "Null-routing the full /24 subnet carries severe operational disruption risk."
        )
    elif telemetry.is_privileged:
        blast_rating = "MEDIUM"
        blast_details = (
            f"Account {telemetry.target_user} is an Executive Officer ({telemetry.user_role}). "
            "Hard lockout would disrupt active financial governance approvals."
        )

    # 4. Routing Decision & Guardrails
    policy_choice = jev.triage_policy.choice
    policy_confidence = jev.triage_policy.confidence
    sig_noul = jev.is_signature_match.noul

    # Rule A: If Jev flagged ambiguous or confidence is low, escalate to human lead
    if policy_choice == "escalate_to_lead" or policy_confidence < 0.60:
        recommended_action = "ESCALATE_LEAD"
        requires_human = True
        drafted = DraftedMitigation(
            action_type="DISPATCH_SOC_DIAGNOSTIC_PACKET",
            target=telemetry.target_user,
            scope_description="Escalate multi-token telemetry to Tier-2 Threat Hunter queue",
            estimated_blast_radius="Zero operational impact",
            recommended_duration="Indefinite until reviewed",
            reversible=True,
        )
        rationale = (
            f"Jev confidence is low ({policy_confidence}) and brute-force signature is ambiguous (Noul: {sig_noul}). "
            "Distributed token probes across internal service accounts require manual threat hunting, not automated blocking."
        )

    # Rule B: High Blast Radius or High Threat Score -> Draft & Require Human Click
    elif blast_rating in ["HIGH", "CRITICAL"] or composite_score >= 7.5 or policy_choice == "draft_and_approve":
        recommended_action = "DRAFT_AND_APPROVE"
        requires_human = True

        if telemetry.is_shared_subnet:
            action_type = "BLOCK_IP_AND_STEPUP_MFA"
            scope_desc = (
                f"Null-route offending IP {telemetry.source_ip} (preserves remaining /24 subnet) "
                f"and force biometric Step-up MFA challenge on {telemetry.target_user}"
            )
            duration = "24 hours"
        else:
            action_type = "LOCKOUT_ACCOUNT_AND_RESET_SSO"
            scope_desc = f"Invalidate active sessions and enforce password reset on {telemetry.target_user}"
            duration = "Immediate until reset"

        drafted = DraftedMitigation(
            action_type=action_type,
            target=f"{telemetry.source_ip} | {telemetry.target_user}",
            scope_description=scope_desc,
            estimated_blast_radius=blast_details,
            recommended_duration=duration,
            reversible=True,
        )
        rationale = (
            f"Critical threat detected (Composite Score {composite_score}/10, Brute-force Noul {sig_noul}). "
            f"Target is {telemetry.user_role} ({telemetry.target_user}). "
            f"Automated execution blocked by Blast-Radius Guardrail: {blast_details} "
            "Action has been pre-drafted for 1-click human verification."
        )

    # Rule C: Low Blast Radius & Low/Medium Threat -> Straight-through Auto-Mitigate
    else:
        recommended_action = "AUTO_MITIGATE"
        requires_human = False
        drafted = DraftedMitigation(
            action_type="RATE_LIMIT_IP",
            target=telemetry.source_ip,
            scope_description=f"Apply temporary rate-limit of 5 req/min on IP {telemetry.source_ip} via Edge WAF",
            estimated_blast_radius="Zero collateral impact (isolated client)",
            recommended_duration="15 minutes",
            reversible=True,
        )
        rationale = (
            f"Routine failure volume ({telemetry.attempt_count} attempts) on non-privileged account. "
            f"Threat score is low ({composite_score}/10) with zero blast radius. "
            "Reversible rate-limit applied autonomously to eliminate analyst alert fatigue."
        )

    return PolicyEvaluation(
        recommended_action=recommended_action,
        composite_risk_score=composite_score,
        blast_radius_rating=blast_rating,
        blast_radius_details=blast_details,
        requires_human_approval=requires_human,
        drafted_mitigation=drafted,
        ai_rationale=rationale,
        confidence_score=policy_confidence,
    )
