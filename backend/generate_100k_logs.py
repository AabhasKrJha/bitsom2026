"""Generates 100,000 streamable enterprise logs into JSONL format with 6 distinct attack classes.

Initializes sentix.db with topology entities (users, infrastructure, client devices, subnets)
while keeping the live logs and decisions tables 100% empty for live demo ingestion.
"""

import os
import json
import random
import time
from datetime import datetime, timezone, timedelta
from backend.database import init_db, get_db_summary

# Fixed Seed for Reproducible Consistency
random.seed(42)

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "data_exports")
JSONL_PATH = os.path.join(EXPORTS_DIR, "enterprise_logs_100k.jsonl")
SAMPLE_SCENARIOS_PATH = os.path.join(EXPORTS_DIR, "attack_scenarios_sample.json")

PERSONA_IDS = ["u_ciso", "u_cto", "u_devops", "u_soc", "u_eng"]

SUBNETS = {
    "CORP_VPN": ["172.16.50.14", "172.16.50.45", "172.16.50.88", "172.16.50.112"],
    "HOME_ISP": ["73.189.44.12", "73.189.44.89", "98.244.11.5", "104.28.19.4"],
    "PARTNER_GATEWAY": ["198.51.100.42", "198.51.100.18", "198.51.100.99"],
    "INTERNAL_VPC": ["10.0.12.88", "10.0.12.89", "10.0.14.2", "10.0.15.77"],
    "DATACENTER_PROXY": ["45.33.32.18", "45.33.32.90", "185.220.101.5"],
}


def generate_100k_logs_file():
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # 1. Reset DB topology & ensure live logs table is EMPTY
    print("[*] Initializing sentix.db with clean topology entities (logs/decisions empty)...")
    init_db(seed_static_entities=True)

    print(f"[*] Generating 100,000 streamable enterprise logs to {JSONL_PATH}...")
    start_time = time.time()

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(hours=24)
    total_seconds = int((end_dt - start_dt).total_seconds())

    # 2. Curated Attack Scenarios across 6 Classes
    curated_scenarios = {}

    # Class 1: Executive Credential Stuffing (Target: Elena Rostova / CISO)
    # 52 rapid brute force attempts within 45s from Partner Gateway
    cluster_a = []
    cluster_a_base = start_dt + timedelta(hours=3, minutes=18)
    for seq in range(1, 53):
        ts = cluster_a_base + timedelta(milliseconds=seq * 800)
        item = {
            "id": f"log_cfo_attack_{seq:03d}",
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": "u_ciso",
            "source_system": "SAP S/4HANA / Okta",
            "event_type": "user.authentication",
            "client_ip": "198.51.100.42",
            "subnet_type": "PARTNER_GATEWAY",
            "status": "FAILURE",
            "failure_reason": "INVALID_PASSWORD",
            "raw_payload": {
                "user_agent": "Python-urllib/3.11 AutomatedPenTest/2.4",
                "attempt_seq": seq,
                "velocity": "52_attempts_per_45_seconds",
                "target_app": "SAP S/4HANA Finance Core",
                "subnet_warning": "Subnet 198.51.100.0/24 hosts 18 active European B2B partner EDI channels",
                "attack_class": "EXECUTIVE_CREDENTIAL_STUFFING",
            },
        }
        cluster_a.append(item)
    curated_scenarios["class_1_executive_credential_stuffing"] = cluster_a

    # Class 2: High-Privilege DB AssumeRole Probe (Target: David Kim / CTO)
    # 18 failed assume-role attempts from offshore datacenter
    cluster_b = []
    cluster_b_base = start_dt + timedelta(hours=23, minutes=45)
    for seq in range(1, 19):
        ts = cluster_b_base + timedelta(seconds=seq * 4)
        item = {
            "id": f"log_cto_assume_role_{seq:03d}",
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": "u_cto",
            "source_system": "AWS CloudTrail / IAM",
            "event_type": "sts:AssumeRole",
            "client_ip": "45.33.32.18",
            "subnet_type": "DATACENTER_PROXY",
            "status": "FAILURE",
            "failure_reason": "MFA_CHALLENGE_FAILED",
            "raw_payload": {
                "target_role": "arn:aws:iam::112233445566:role/DatabaseClusterSuperAdmin",
                "session_name": "emergency_breakglass_probe",
                "mfa_serial": "arn:aws:iam::112233445566:mfa/david.kim",
                "attack_class": "PRIVILEGE_ESCALATION_ASSUME_ROLE",
            },
        }
        cluster_b.append(item)
    curated_scenarios["class_2_privileged_db_assume_role"] = cluster_b

    # Class 3: Internal Lateral Token Introspection (Target: Marcus Vance / DevOps Lead)
    # 25 lateral introspection probes across internal microservices
    cluster_c = []
    cluster_c_base = start_dt + timedelta(hours=8, minutes=14)
    for seq in range(1, 26):
        ts = cluster_c_base + timedelta(seconds=seq * 15)
        ip = "10.0.12.88" if seq % 2 == 0 else "10.0.12.89"
        svc = "svc-billing-sync" if seq < 12 else "svc-deploy-runner"
        item = {
            "id": f"log_devops_spray_{seq:03d}",
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": "u_devops",
            "source_system": "Kong API Gateway / AWS IAM",
            "event_type": "token.introspection",
            "client_ip": ip,
            "subnet_type": "INTERNAL_VPC",
            "status": "WARN" if seq % 4 == 0 else "FAILURE",
            "failure_reason": "INVALID_SCOPE",
            "raw_payload": {
                "target_service": svc,
                "pattern": "ROTATING_INTERNAL_PROBE",
                "anomaly_note": "Multi-token probe across internal microservices",
                "attack_class": "LATERAL_TOKEN_INTROSPECTION",
            },
        }
        cluster_c.append(item)
    curated_scenarios["class_3_lateral_token_spray"] = cluster_c

    # Class 4: Developer Staging Secret Leak (Target: Alex Rivera / Staff Engineer)
    cluster_d = [{
        "id": "log_eng_secret_leak_001",
        "timestamp": (start_dt + timedelta(hours=2, minutes=14, seconds=22)).strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": "u_eng",
        "source_system": "GitHub Enterprise Server",
        "event_type": "secret.git_leak_detected",
        "client_ip": "73.189.44.12",
        "subnet_type": "HOME_ISP",
        "status": "WARN",
        "failure_reason": "PUBLIC_COMMIT_SECRET",
        "raw_payload": {
            "repository": "enterprise/commerce-core",
            "commit_hash": "f8a91c90b34e12",
            "secret_type": "Personal Access Token (ghp_staging_api_99x)",
            "file_path": "tests/integration/test_payment_gateway.py",
            "attack_class": "DEVELOPER_SECRET_EXPOSURE",
        },
    }]
    curated_scenarios["class_4_developer_secret_leak"] = cluster_d

    # Class 5: Impossible Travel Anomaly (Target: Sarah Jenkins / SOC Lead)
    # Login NY at 10:00, Login SG at 10:14
    cluster_e = [
        {
            "id": "log_soc_travel_001",
            "timestamp": (start_dt + timedelta(hours=10, minutes=0)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": "u_soc",
            "source_system": "Okta SSO",
            "event_type": "user.login",
            "client_ip": "73.189.44.89",
            "subnet_type": "HOME_ISP",
            "status": "SUCCESS",
            "failure_reason": None,
            "raw_payload": {"geo_city": "New York", "geo_country": "US", "auth_method": "FIDO2_PASSKEY"},
        },
        {
            "id": "log_soc_travel_002",
            "timestamp": (start_dt + timedelta(hours=10, minutes=14)).strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": "u_soc",
            "source_system": "Okta SSO",
            "event_type": "user.login",
            "client_ip": "203.0.113.88",
            "subnet_type": "DATACENTER_PROXY",
            "status": "FAILURE",
            "failure_reason": "IMPOSSIBLE_TRAVEL_SPEED",
            "raw_payload": {
                "geo_city": "Singapore",
                "geo_country": "SG",
                "delta_km": 15300,
                "delta_minutes": 14,
                "attack_class": "IMPOSSIBLE_TRAVEL_ANOMALY",
            },
        },
    ]
    curated_scenarios["class_5_impossible_travel"] = cluster_e

    # Class 6: Stale Key Hygiene Drift (Target: Marcus Vance & David Kim)
    cluster_f = [{
        "id": "log_hygiene_stale_keys_001",
        "timestamp": (start_dt + timedelta(hours=12, minutes=0)).strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": "u_devops",
        "source_system": "AWS IAM / Posture Scanner",
        "event_type": "iam.audit_key_age",
        "client_ip": "10.0.0.1",
        "subnet_type": "INTERNAL_VPC",
        "status": "WARN",
        "failure_reason": "UNROTATED_ADMIN_CREDENTIAL",
        "raw_payload": {
            "key_count": 3,
            "age_days": 184,
            "permission_tier": "AdministratorAccess",
            "attack_class": "HYGIENE_POSTURE_DRIFT",
        },
    }]
    curated_scenarios["class_6_stale_key_hygiene"] = cluster_f

    # Combine All Curated Attack Events
    all_attack_events = []
    for cls_name, ev_list in curated_scenarios.items():
        all_attack_events.extend(ev_list)

    # Save Curated Attack Scenarios Sample File for reference
    with open(SAMPLE_SCENARIOS_PATH, "w") as f:
        json.dump(curated_scenarios, f, indent=2)
    print(f"[✓] Saved curated attack scenarios sample to {SAMPLE_SCENARIOS_PATH}")

    # 3. Stream 100,000 Logs to JSONL File (Attack Events + Realistic Baseline)
    baseline_target = 100000 - len(all_attack_events)
    systems = [
        ("Okta SSO", "user.login", "CORP_VPN"),
        ("Okta SSO", "session.refresh", "CORP_VPN"),
        ("Kong API Gateway", "api.request", "INTERNAL_VPC"),
        ("AWS CloudTrail", "iam.get_caller_identity", "INTERNAL_VPC"),
        ("WireGuard Gateway", "vpn.session_keepalive", "CORP_VPN"),
        ("GitHub Enterprise", "git.push", "HOME_ISP"),
    ]

    with open(JSONL_PATH, "w") as f:
        # Write curated attack logs first
        for item in all_attack_events:
            f.write(json.dumps(item) + "\n")

        # Write remaining baseline logs
        for i in range(baseline_target):
            offset_sec = random.randint(0, total_seconds)
            ts = start_dt + timedelta(seconds=offset_sec)
            hour = ts.hour

            user_id = random.choice(PERSONA_IDS)
            src_sys, ev_type, def_subnet = random.choice(systems)
            ip = random.choice(SUBNETS[def_subnet])

            rand_stat = random.random()
            if rand_stat < 0.985:
                status = "SUCCESS"
                reason = None
                payload = {
                    "auth_method": "SAML2.0_MFA_VERIFIED",
                    "response_code": 200,
                    "latency_ms": random.randint(12, 85),
                }
            elif rand_stat < 0.998:
                status = "FAILURE"
                reason = "TYPO_RETRY_PASSWD" if "Okta" in src_sys else "TOKEN_TRANSIENT_EXPIRED"
                payload = {
                    "retry_allowed": True,
                    "response_code": 401,
                    "latency_ms": random.randint(20, 110),
                }
            else:
                status = "WARN"
                reason = "RATE_LIMIT_ELEVATED"
                payload = {
                    "response_code": 429,
                    "threshold_hit": "50_req_per_sec",
                }

            row = {
                "id": f"log_stream_{i:08d}",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": user_id,
                "source_system": src_sys,
                "event_type": ev_type,
                "client_ip": ip,
                "subnet_type": def_subnet,
                "status": status,
                "failure_reason": reason,
                "raw_payload": payload,
            }
            f.write(json.dumps(row) + "\n")

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(JSONL_PATH) / (1024 * 1024)
    print(f"[✓] Generated 100,000 logs in {elapsed:.2f}s ({file_size_mb:.1f} MB JSONL at {JSONL_PATH})")

    # 4. Final DB Status Verification
    summary = get_db_summary()
    print("\n[+] Database State (Topology Seeded, Execution Tables EMPTY):")
    for tbl, cnt in summary.items():
        print(f"    • {tbl}: {cnt} rows")


if __name__ == "__main__":
    generate_100k_logs_file()
