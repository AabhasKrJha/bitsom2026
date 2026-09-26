"""Question and Candidate Action Catalog for Sentix.

Provides the dynamic inquiry battery across the 3 TypeSafe Jev primitives
(Noul, Score, Choice) and contextual mitigation candidates tailored to
specific enterprise assets.
"""

from typing import Dict, Any, List
from typesafe_sdk import Noul, Score, Choice


def get_candidate_actions(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns candidate mitigations tailored to the specific target asset and network context."""
    source_sys = state.get("telemetry", {}).get("source_system", "")
    client_ip = state.get("network", {}).get("ip", "0.0.0.0")
    subnet_cidr = state.get("network", {}).get("cidr", "0.0.0.0/0")
    user_name = state.get("actor", {}).get("name", "User")

    if "SAP" in source_sys or state.get("network", {}).get("is_shared"):
        return [
            {
                "id": "act_drop_ip",
                "title": f"Drop Attacker IP ({client_ip}) at Edge WAF",
                "target": client_ip,
                "enforcement_point": "Perimeter Cloudflare / Kong WAF",
                "blast_radius_rating": 0.05,
                "blast_radius_warning": "Affects only attacker source IP. Zero partner disruption.",
            },
            {
                "id": "act_ban_subnet",
                "title": f"Quarantine Entire B2B Partner Subnet ({subnet_cidr})",
                "target": subnet_cidr,
                "enforcement_point": "Core Border Gateway Protocol (BGP)",
                "blast_radius_rating": 0.94,
                "blast_radius_warning": "Warning: Subnet hosts 18 active European B2B partner EDI channels. Supply chain billing will suspend.",
            },
            {
                "id": "act_stepup_mfa",
                "title": f"Enforce Out-of-Band FIDO2 Re-Authentication for {user_name}",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "Okta SSO Identity Provider",
                "blast_radius_rating": 0.15,
                "blast_radius_warning": "Elena is prompted for hardware YubiKey on trusted device.",
            },
        ]
    elif "AWS" in source_sys or "Aurora" in source_sys:
        return [
            {
                "id": "act_sever_sts_token",
                "title": "Invalidate Active STS AssumeRole Token",
                "target": "arn:aws:iam::112233445566:role/DatabaseClusterSuperAdmin",
                "enforcement_point": "AWS Security Token Service (STS)",
                "blast_radius_rating": 0.10,
                "blast_radius_warning": "Terminates active sessions initiated from untrusted datacenter proxy.",
            },
            {
                "id": "act_lock_iam_user",
                "title": f"Lock DB Admin IAM Credentials for {user_name}",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "AWS IAM Access Management",
                "blast_radius_rating": 0.35,
                "blast_radius_warning": "Prevents new STS assume-role calls until David re-authenticates via root console.",
            },
            {
                "id": "act_quarantine_db_cluster",
                "title": "Sever All External Aurora DB Read-Replica Connections",
                "target": "db-aurora-replica-02.internal",
                "enforcement_point": "AWS RDS Security Group",
                "blast_radius_rating": 0.90,
                "blast_radius_warning": "Extreme: Drops customer query pools across live commerce checkout.",
            },
        ]
    elif "Kong" in source_sys or "k8s" in source_sys or "VPC" in str(state.get("network", {}).get("subnet_type", "")):
        return [
            {
                "id": "act_clamp_scope",
                "title": "Clamp Microservice Token Scope to Read-Only",
                "target": "svc-billing-sync",
                "enforcement_point": "Kong API Gateway OAuth Plugin",
                "blast_radius_rating": 0.08,
                "blast_radius_warning": "Restricts lateral token traversal without breaking background sync.",
            },
            {
                "id": "act_isolate_pod",
                "title": "Restart & Quarantine Deploy Runner Pod",
                "target": "pod-deploy-runner-7b49f",
                "enforcement_point": "Kubernetes Ingress Controller",
                "blast_radius_rating": 0.40,
                "blast_radius_warning": "Active deployment jobs will be delayed by ~5 minutes while pod reboots in sandbox.",
            },
            {
                "id": "act_sever_vpc_gateway",
                "title": "Isolate Entire Internal VPC Subnet (10.0.0.0/16)",
                "target": "10.0.0.0/16",
                "enforcement_point": "AWS Transit Gateway",
                "blast_radius_rating": 0.95,
                "blast_radius_warning": "Catastrophic: Halts all internal inter-service communication.",
            },
        ]
    elif "GitHub" in source_sys:
        return [
            {
                "id": "act_revoke_pat",
                "title": "Revoke Leaked Personal Access Token (ghp_staging_api_99x)",
                "target": "ghp_staging_api_99x",
                "enforcement_point": "GitHub Enterprise Token Authority",
                "blast_radius_rating": 0.05,
                "blast_radius_warning": "Leaked staging token revoked immediately. Zero production impact.",
            },
            {
                "id": "act_git_scrub",
                "title": "Execute Git Filter-Repo History Scrub on commerce-core",
                "target": "enterprise/commerce-core",
                "enforcement_point": "GitHub Enterprise Git Hooks",
                "blast_radius_rating": 0.30,
                "blast_radius_warning": "Requires developer branch rebase on next push.",
            },
            {
                "id": "act_lock_dev_account",
                "title": f"Suspend GitHub Account for {user_name}",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "GitHub Enterprise SSO",
                "blast_radius_rating": 0.50,
                "blast_radius_warning": "Prevents developer from pushing code until security review.",
            },
        ]
    elif "Posture" in source_sys or "audit_key_age" in str(state.get("telemetry", {}).get("event_type", "")):
        return [
            {
                "id": "act_stage_rotation_window",
                "title": "Initiate 72-Hour Key Rotation Grace Window",
                "target": "AWS Admin Access Keys (x3)",
                "enforcement_point": "AWS Secrets Manager & Posture Scheduler",
                "blast_radius_rating": 0.20,
                "blast_radius_warning": "Gives DevOps 72 hours to swap keys before automated deprecation.",
            },
            {
                "id": "act_slack_alert_owner",
                "title": f"Publish Posture Drift Warning to {user_name}",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "Enterprise Slack Webhook",
                "blast_radius_rating": 0.01,
                "blast_radius_warning": "Informational alert only.",
            },
            {
                "id": "act_hard_delete_keys",
                "title": "Immediately Delete All 3 Unrotated Admin Keys",
                "target": "AWS Admin Access Keys (x3)",
                "enforcement_point": "AWS IAM Key Management",
                "blast_radius_rating": 0.92,
                "blast_radius_warning": "Extreme: Legacy batch cron jobs relying on static credentials will crash immediately.",
            },
        ]
    else:  # Default / Okta
        return [
            {
                "id": "act_kill_remote_session",
                "title": f"Terminate Rogue Session from {client_ip}",
                "target": client_ip,
                "enforcement_point": "Okta SSO Session Manager",
                "blast_radius_rating": 0.08,
                "blast_radius_warning": "Kills anomalous connection while preserving legitimate local terminal.",
            },
            {
                "id": "act_prompt_local_device",
                "title": f"Trigger Out-of-Band Verification on {user_name}'s Trusted Device",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "FIDO2 Mobile Authenticator",
                "blast_radius_rating": 0.05,
                "blast_radius_warning": "Prompts user to confirm physical location.",
            },
            {
                "id": "act_global_user_lockout",
                "title": f"Global Account Lockout for {user_name}",
                "target": state.get("actor", {}).get("id", "user"),
                "enforcement_point": "Active Directory / Okta Universal Directory",
                "blast_radius_rating": 0.70,
                "blast_radius_warning": "Locks employee out of all corporate apps globally.",
            },
        ]


def build_question_battery(state: Dict[str, Any], candidate_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds a dynamic inquiry battery of typed Noul, Score, and Choice questions."""
    action_ids = [a["id"] for a in candidate_actions]
    subnet = state.get("network", {})
    infra = state.get("target_service", {})

    return {
        # 1. Threat Probability (Noul: 0.0 to 1.0)
        "q_threat_prob": Noul(
            instructions="Evaluate the probability (0.0 to 1.0) that this sequence represents malicious adversary activity rather than benign user error."
        ),
        # 2. Account Takeover Risk (Noul: 0.0 to 1.0)
        "q_account_takeover_risk": Noul(
            instructions="Estimate the probability (0.0 to 1.0) that the attacker currently holds valid active credentials or session tokens."
        ),
        # 3. Collateral Blast Radius Risk (Noul: 0.0 to 1.0)
        "q_blast_radius": Noul(
            instructions=f"Evaluate the collateral damage risk (0.0 to 1.0) to legitimate enterprise operations if aggressive subnet/asset isolation is executed on {subnet.get('cidr', 'target')}."
        ),
        # 4. Service Downtime Risk (Noul: 0.0 to 1.0)
        "q_service_downtime_risk": Noul(
            instructions=f"Estimate the downtime impact (0.0 to 1.0) if {infra.get('name', 'target service')} is restarted or isolated."
        ),
        # 5. Action Proportionality Scoring (Score: utility ranking)
        "q_action_scores": Score(
            instructions="Score each candidate action on proportionality balancing containment efficacy against business operational disruption.",
            criteria=action_ids
        ),
        # 6. Action Reversibility Scoring (Score: ease of rollback)
        "q_reversibility_scores": Score(
            instructions="Score candidate actions on ease and speed of operational rollback if a false positive occurs.",
            criteria=action_ids
        ),
        # 7. Threat Classification (Choice)
        "q_attack_class": Choice(
            instructions="Classify the primary threat vector.",
            criteria={
                "EXECUTIVE_CREDENTIAL_STUFFING": "Rapid automated brute-force password spraying targeting high-privilege executive",
                "PRIVILEGE_ESCALATION_ASSUME_ROLE": "Unauthorized high-privilege STS assume-role traversal from untrusted proxy",
                "LATERAL_TOKEN_INTROSPECTION": "Cross-service token scope probing across internal microservices",
                "DEVELOPER_SECRET_EXPOSURE": "Plaintext secret, API key, or PAT detected in repository source commit",
                "IMPOSSIBLE_TRAVEL_ANOMALY": "Geographically unachievable authentication speed indicating session token replay",
                "HYGIENE_POSTURE_DRIFT": "Passive compliance or configuration drift such as unrotated administrative keys",
                "BENIGN_NOISE": "Normal authorized employee activity with occasional expected typo or token expiry"
            }
        ),
        # 8. Target Asset Criticality (Choice)
        "q_target_criticality": Choice(
            instructions="Rate the organizational criticality of the compromised target asset.",
            criteria={
                "TIER_0_CRITICAL": "Core identity provider, financial ledger, or root cloud infrastructure",
                "TIER_1_HIGH": "Internal database read replicas, deployment runners, or code repositories",
                "TIER_2_MEDIUM": "Development, staging, or transient worker environments"
            }
        )
    }
