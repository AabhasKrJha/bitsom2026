"""Deterministic Tier 3 Technical Mitigation Playbook Catalog.

Provides parameterized, battle-tested technical remediation playbooks with exact
CLI commands, IaC steps, and verification checklists. Operates with 0ms latency
and zero external LLM dependencies.
"""

from typing import Dict, Any


def generate_tier_3_playbook(attack_class: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a structured, parameterized technical mitigation playbook for Tier 3 advisories."""
    target_service = state.get("target_service", {}).get("name", "Enterprise Asset")
    actor_name = state.get("actor", {}).get("name", "Target Persona")
    client_ip = state.get("network", {}).get("ip", "0.0.0.0")
    subnet_cidr = state.get("network", {}).get("cidr", "0.0.0.0/0")
    raw_payload = state.get("telemetry", {}).get("raw_payload", {})

    playbooks = {
        "EXECUTIVE_CREDENTIAL_STUFFING": {
            "title": f"B2B Partner Ingress Re-Routing & SOX Ledger Defense ({target_service})",
            "blast_radius_explanation": f"Subnet {subnet_cidr} hosts 18 active European B2B partner EDI channels. Direct automated shutdown will cause tier-1 supply chain billing failure.",
            "technical_steps": [
                f"1. Deploy edge rate-limit filter: `iptables -A INPUT -s {client_ip} -m limit --limit 2/min -j ACCEPT`",
                f"2. Stage partner notification to EMEA clearinghouse regarding scheduled gateway maintenance window.",
                f"3. Re-key mutual TLS (mTLS) client certificates for all European EDI endpoints on {subnet_cidr}.",
                f"4. Audit SAP transaction queue logs for uncommitted journal entries in the last 4 hours."
            ],
            "verification_command": f"curl -Iv --interface {subnet_cidr.split('/')[0]} https://sap-s4hana.corp.internal/health",
            "estimated_recovery_time": "30 minutes"
        },
        "PRIVILEGE_ESCALATION_ASSUME_ROLE": {
            "title": f"AWS IAM Root & Aurora DB Privilege Quarantine ({target_service})",
            "blast_radius_explanation": f"Directly revoking IAM role affects production database connection pools and background microservices.",
            "technical_steps": [
                f"1. Review active STS sessions: `aws sts get-caller-identity` across role 'DatabaseClusterSuperAdmin'.",
                f"2. Apply temporary IAM inline policy restricting STS sessions to VPC-only CIDRs: `aws iam put-role-policy --policy-name VPCOnly`.",
                f"3. Rotate AWS root DB credentials in AWS Secrets Manager with automatic replica synchronization.",
                f"4. Inspect CloudTrail logs for S3 export calls or RDS snapshot share events initiated by IP {client_ip}."
            ],
            "verification_command": "aws rds describe-db-clusters --db-cluster-identifier aurora-prod-replica --query 'DBClusters[*].Status'",
            "estimated_recovery_time": "45 minutes"
        },
        "LATERAL_TOKEN_INTROSPECTION": {
            "title": f"Internal VPC Mesh mTLS Rotation & Service Account Scrub ({target_service})",
            "blast_radius_explanation": f"Abruptly terminating deployment runner pods interrupts live release pipelines across platform engineering.",
            "technical_steps": [
                f"1. Inspect pod security context: `kubectl get pods -n platform -o wide` on target node.",
                f"2. Revoke and rotate Kubernetes service account token for 'svc-deploy-runner'.",
                f"3. Enforce Istio mTLS STRICT mode on internal subnet {subnet_cidr}.",
                f"4. Verify git commit signatures on all staged artifact packages."
            ],
            "verification_command": "kubectl auth can-i get secrets --as=system:serviceaccount:platform:svc-deploy-runner",
            "estimated_recovery_time": "20 minutes"
        },
        "DEVELOPER_SECRET_EXPOSURE": {
            "title": f"Git Repository History Scrubbing & Vault Secret Rotation ({target_service})",
            "blast_radius_explanation": f"Force-pushing branch rewrite may break open pull requests across core commerce platform.",
            "technical_steps": [
                f"1. Run history scrub: `git filter-repo --invert-paths --path tests/integration/test_payment_gateway.py`",
                f"2. Invalidate git commit cache on self-hosted GitHub Enterprise runners.",
                f"3. Add pre-commit secret detection hook to enterprise repo template.",
                f"4. Issue new staging credentials via HashiCorp Vault API and notify developer ({actor_name})."
            ],
            "verification_command": "git log -p -S 'ghp_staging_api' --all",
            "estimated_recovery_time": "15 minutes"
        },
        "IMPOSSIBLE_TRAVEL_ANOMALY": {
            "title": f"Zero-Trust Identity Re-Verification & Token Replay Hunt ({actor_name})",
            "blast_radius_explanation": f"Global user lockout prevents SOC lead from managing ongoing security response operations.",
            "technical_steps": [
                f"1. Revoke active Okta OAuth refresh tokens: `POST /api/v1/users/{state.get('actor', {}).get('id')}/lifecycle/revoke_sessions`",
                f"2. Trigger out-of-band phone verification to confirm {actor_name}'s physical location.",
                f"3. Check endpoint EDR logs for infostealer malware or session cookie dumping.",
                f"4. Inspect WireGuard Europe gateway logs for unauthorized split-tunnel routing."
            ],
            "verification_command": "okta-cli user get --id " + str(state.get("actor", {}).get("id")),
            "estimated_recovery_time": "10 minutes"
        },
        "HYGIENE_POSTURE_DRIFT": {
            "title": f"CIS Benchmark 1.14 Compliance: 72-Hour Key Rotation Grace Window ({actor_name})",
            "blast_radius_explanation": f"Instantly deleting 184-day-old admin keys will crash legacy automated batch cron jobs.",
            "technical_steps": [
                f"1. Query last-used timestamp: `aws iam get-access-key-last-used --access-key-id <KEY_ID>`",
                f"2. Generate replacement credentials in AWS Secrets Manager.",
                f"3. Publish automated Slack alert to {actor_name} with a 72-hour deprecation grace period.",
                f"4. Schedule automatic deactivation at expiry of the 72-hour window."
            ],
            "verification_command": "aws iam list-access-keys --user-name " + str(state.get("actor", {}).get("name", "admin")),
            "estimated_recovery_time": "72-hour window"
        }
    }

    return playbooks.get(attack_class, {
        "title": f"Standard Incident Containment: {attack_class}",
        "blast_radius_explanation": "Direct autonomous containment exceeds safety threshold.",
        "technical_steps": [
            "1. Isolate target node from internal routing table.",
            "2. Preserve volatile memory and network connection state for forensic analysis.",
            "3. Notify incident response lead and schedule operational review."
        ],
        "verification_command": "systemctl status sentix-agent",
        "estimated_recovery_time": "60 minutes"
    })
