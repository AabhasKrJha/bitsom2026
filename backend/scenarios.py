"""Pre-built realistic synthetic enterprise log sets for the demo."""

SCENARIOS = {
    "scenario_1_routine": {
        "id": "scenario_1_routine",
        "title": "Scenario 1: Routine Portal Noise (Low Blast Radius)",
        "subtitle": "4 failed logins on junior coordinator account during business hours",
        "category": "Routine Non-Privileged",
        "expected_action": "AUTO_MITIGATE",
        "expected_score_range": "2.0 - 3.5 / 10",
        "log_text": """
2026-09-26T11:28:14.201Z [AUTH_AUDIT] service="Okta SSO" event="user.authentication.auth_via_mfa" status="FAILURE" 
reason="INVALID_CREDENTIALS" client_ip="73.189.44.12" geo_city="Chicago" geo_country="US" asn="AS7922 COMCAST-7922" 
user="alex.morgan@enterprise.com" role="Junior Marketing Coordinator" department="Marketing" auth_protocol="SAML2.0" 
attempt_seq="1/4" target_app="HubSpot Portal" user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

2026-09-26T11:28:22.819Z [AUTH_AUDIT] service="Okta SSO" event="user.authentication.auth_via_mfa" status="FAILURE" 
reason="INVALID_CREDENTIALS" client_ip="73.189.44.12" geo_city="Chicago" geo_country="US" asn="AS7922 COMCAST-7922" 
user="alex.morgan@morgan-enterprise.com" role="Junior Marketing Coordinator" department="Marketing" 
attempt_seq="2/4" target_app="HubSpot Portal"

2026-09-26T11:28:31.102Z [AUTH_AUDIT] service="Okta SSO" event="user.authentication.auth_via_mfa" status="FAILURE" 
reason="INVALID_CREDENTIALS" client_ip="73.189.44.12" user="alex.morgan@enterprise.com" attempt_seq="3/4" target_app="HubSpot Portal"

2026-09-26T11:28:44.590Z [AUTH_AUDIT] service="Okta SSO" event="user.authentication.auth_via_mfa" status="FAILURE" 
reason="INVALID_CREDENTIALS" client_ip="73.189.44.12" user="alex.morgan@enterprise.com" attempt_seq="4/4" target_app="HubSpot Portal"
threshold_trigger="WARN_CONSECUTIVE_AUTH_FAILURE" blast_radius_category="ISOLATED_SINGLE_CLIENT"
        """.strip(),
        "source_system": "Okta SSO",
    },
    "scenario_2_executive": {
        "id": "scenario_2_executive",
        "title": "Scenario 2: Targeted Attack on CFO (High Blast Radius)",
        "subtitle": "52 rapid brute-force attempts on CFO SAP account at 3:18 AM from shared subnet",
        "category": "Targeted Privileged Attack",
        "expected_action": "DRAFT_AND_APPROVE",
        "expected_score_range": "9.0 - 9.8 / 10",
        "log_text": """
2026-09-26T03:18:02.109Z [SECURITY_EVENT] service="SAP NetWeaver / Okta SSO" event="auth.credential_validation" 
status="DENIED" reason="PASSWORD_FAILED" client_ip="198.51.100.42" client_subnet="198.51.100.0/24" 
geo_city="Frankfurt" geo_country="DE" asn="AS16509 AMAZON-02" subnet_shared_pool="EMEA-B2B-PARTNER-GATEWAY" 
user="sarah.chen@enterprise.com" role="Chief Financial Officer (CFO)" privilege_tier="EXECUTIVE_CRITICAL" 
target_app="SAP S/4HANA Finance Core" off_hours="TRUE" velocity="52_attempts_per_45_seconds" 
user_agent="Python-urllib/3.11 AutomatedPenTest/2.4" threat_feed_flag="BULK_CREDENTIAL_STUFFING" 
warning="Subnet 198.51.100.0/24 hosts 18 active European enterprise supplier webhooks and EDI billing channels"
        """.strip(),
        "source_system": "SAP S/4HANA / Okta",
    },
    "scenario_3_anomaly": {
        "id": "scenario_3_anomaly",
        "title": "Scenario 3: Multi-Service Account Spray (Ambiguous Anomaly)",
        "subtitle": "Distributed low-frequency probes across internal service tokens",
        "category": "Ambiguous Lateral Spray",
        "expected_action": "ESCALATE_LEAD",
        "expected_score_range": "5.5 - 7.0 / 10",
        "log_text": """
2026-09-26T08:14:09.330Z [API_GATEWAY] service="Kong Gateway / AWS IAM" event="token.introspection" status="INVALID_SCOPE" 
client_ip="203.0.113.88" geo_city="Singapore" geo_country="SG" target_service="svc-billing-sync" 
token_fingerprint="sha256:8f4a..." attempt_rate="1_per_2_minutes" pattern="LOW_AND_SLOW_PROBE"

2026-09-26T08:16:12.115Z [API_GATEWAY] service="Kong Gateway / AWS IAM" event="token.introspection" status="UNAUTHORIZED" 
client_ip="203.0.113.89" target_service="svc-deploy-runner" pattern="ROTATING_CLIENT_IP"

2026-09-26T08:18:04.992Z [API_GATEWAY] service="Kong Gateway / AWS IAM" event="token.introspection" status="EXPIRED_TOKEN" 
client_ip="203.0.113.90" target_service="svc-audit-collector" pattern="INTERMITTENT_INTERNAL_FINGERPRINT"
anomaly_note="Confidence split: Could be misconfigured Kubernetes daemonset OR stealthy internal reconnaissance"
        """.strip(),
        "source_system": "AWS IAM / Kong API Gateway",
    },
}
