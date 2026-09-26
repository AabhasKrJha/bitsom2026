"""Database schema, connection manager, and topology initialization for Sentix.

Maintains topology entities (users, infrastructure, client devices, subnets),
an empty raw logs table, and an audit ledger table for recorded decisions.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Auto-inject project root and backend dir into sys.path
_CORE_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _CORE_DIR.parent.parent
_ROOT_DIR = _BACKEND_DIR.parent

for _p in (str(_ROOT_DIR), str(_BACKEND_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.app.core.config import DB_PATH
except ImportError:
    from app.core.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False, seed_static_entities: bool = True):
    """Initializes the database schema and seeds static topology entities.
    
    If reset is True, drops existing tables to guarantee a clean slate.
    The logs and audit_ledger tables are always initialized in an empty state.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS audit_ledger;")
        cursor.execute("DROP TABLE IF EXISTS logs;")
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("DROP TABLE IF EXISTS infrastructure_nodes;")
        cursor.execute("DROP TABLE IF EXISTS client_devices;")
        cursor.execute("DROP TABLE IF EXISTS network_subnets;")
        cursor.execute("DROP TABLE IF EXISTS decisions;")

    # 1. Cybersecurity Personas (Stakeholders)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        role_category TEXT NOT NULL,      -- 'EXECUTIVE', 'INFRASTRUCTURE', 'OPERATIONS', 'ENGINEERING'
        department TEXT NOT NULL,
        asset_scope TEXT NOT NULL,
        avatar_initials TEXT NOT NULL
    );
    """)

    # 2. Infrastructure Inventory (Servers & Cloud Assets)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS infrastructure_nodes (
        id TEXT PRIMARY KEY,
        hostname TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        service_name TEXT NOT NULL,
        environment TEXT NOT NULL,        -- 'PRODUCTION', 'STAGING', 'INTERNAL'
        criticality TEXT NOT NULL         -- 'TIER_0_CRITICAL', 'TIER_1_HIGH', 'TIER_2_MEDIUM'
    );
    """)

    # 3. Known Client Devices (Hardware Fingerprints)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS client_devices (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        device_name TEXT NOT NULL,
        os_type TEXT NOT NULL,
        hardware_fingerprint TEXT NOT NULL,
        is_trusted BOOLEAN NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # 4. Network Subnet Classifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS network_subnets (
        cidr TEXT PRIMARY KEY,
        subnet_name TEXT NOT NULL,
        subnet_type TEXT NOT NULL,        -- 'PARTNER_GATEWAY', 'CORP_VPN', 'HOME_ISP', 'INTERNAL_VPC', 'DATACENTER_PROXY'
        is_shared BOOLEAN NOT NULL DEFAULT 0,
        description TEXT NOT NULL
    );
    """)

    # 5. Raw Enterprise Logs Table (KEPT EMPTY FOR LIVE INGESTION)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        timestamp DATETIME NOT NULL,
        user_id TEXT NOT NULL,
        source_system TEXT NOT NULL,
        event_type TEXT NOT NULL,
        client_ip TEXT NOT NULL,
        subnet_type TEXT NOT NULL,
        status TEXT NOT NULL,             -- 'SUCCESS', 'FAILURE', 'WARN'
        failure_reason TEXT,
        raw_payload JSON NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # High-Performance Indexes for logs
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_time ON logs(user_id, timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_status ON logs(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_source ON logs(source_system);")

    # 6. Audit Ledger Table (DECISION RECEIPTS & EXPLAINABILITY)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_ledger (
        id TEXT PRIMARY KEY,                       -- e.g. 'aud_20260926_0001'
        timestamp DATETIME NOT NULL,               -- UTC timestamp of decision
        log_id TEXT NOT NULL,                      -- Foreign key to logs(id)
        target_user_id TEXT NOT NULL,              -- Target persona (e.g. 'u_ciso')
        target_service TEXT NOT NULL,              -- Target asset (e.g. 'SAP S/4HANA')
        attack_class TEXT NOT NULL,                -- e.g. 'EXECUTIVE_CREDENTIAL_STUFFING'
        selected_tier TEXT NOT NULL,               -- 'TIER_1_AUTOMATED', 'TIER_2_DRAFTED_HITL', 'TIER_3_PLAYBOOK'
        execution_status TEXT NOT NULL,            -- 'EXECUTED', 'AWAITING_APPROVAL', 'ADVISORY_PENDING'
        authorized_persona_id TEXT,                -- Who holds the button for Tier 2 (e.g. 'u_ciso')
        threat_confidence REAL NOT NULL,           -- Float from Jev (0.0 to 1.0)
        blast_radius REAL NOT NULL,                -- Float from Jev (0.0 to 1.0)
        reason TEXT NOT NULL,                      -- Plain English explainability rationale
        action_payload JSON NOT NULL,              -- Full action receipt / button spec / playbook steps
        jev_raw_evaluation JSON NOT NULL,          -- Complete typed Jev response for compliance
        FOREIGN KEY (log_id) REFERENCES logs(id),
        FOREIGN KEY (target_user_id) REFERENCES users(id)
    );
    """)

    # High-Performance Indexes for audit_ledger
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_tier ON audit_ledger(selected_tier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_status ON audit_ledger(execution_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_ledger(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_persona ON audit_ledger(authorized_persona_id);")

    # Seed static topology entities
    if seed_static_entities:
        _seed_topology(cursor)

    # Ensure dynamic tables are completely clean
    cursor.execute("DELETE FROM logs;")
    cursor.execute("DELETE FROM audit_ledger;")

    conn.commit()
    conn.close()


def _seed_topology(cursor: sqlite3.Cursor):
    """Seeds static topology data (users, servers, client devices, subnets)."""
    # 1. Personas
    cursor.execute("DELETE FROM users;")
    personas = [
        ("u_ciso", "Elena Rostova", "elena.rostova@enterprise.com", "Chief Information Security Officer (CISO)", "EXECUTIVE", "Security & Risk Governance", "Enterprise SSO, Identity Governance, Executive Portals, B2B Subnet Blast Radius", "ER"),
        ("u_cto", "David Kim", "david.kim@enterprise.com", "Chief Technology Officer (CTO)", "INFRASTRUCTURE", "Engineering Leadership", "Production Cloud Architecture, AWS Root Accounts, Aurora DB Clusters", "DK"),
        ("u_devops", "Marcus Vance", "marcus.vance@enterprise.com", "Staff Platform / DevOps Tech Lead", "INFRASTRUCTURE", "Cloud & Platform Engineering", "Kubernetes Clusters, CI/CD Secrets, IAM Service Accounts", "MV"),
        ("u_soc", "Sarah Jenkins", "sarah.jenkins@enterprise.com", "Tier-2 Incident Response / SOC Lead", "OPERATIONS", "Security Operations Center", "Edge WAF, Cloudflare Policies, Perimeter Ingress, Threat Hunting", "SJ"),
        ("u_eng", "Alex Rivera", "alex.rivera@enterprise.com", "Senior Backend / Platform Engineer", "ENGINEERING", "Core Commerce Platform", "Developer Workstation, Git Repositories, Staging API Keys", "AR"),
    ]
    cursor.executemany("""
    INSERT INTO users (id, name, email, title, role_category, department, asset_scope, avatar_initials)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, personas)

    # 2. Infrastructure Nodes
    cursor.execute("DELETE FROM infrastructure_nodes;")
    infra = [
        ("srv_okta_sso", "auth-sso.corp.internal", "10.0.1.10", "Okta Identity Provider", "PRODUCTION", "TIER_0_CRITICAL"),
        ("srv_k8s_prod", "k8s-prod-ingress-01.internal", "10.0.2.15", "Kong Kubernetes Ingress", "PRODUCTION", "TIER_0_CRITICAL"),
        ("srv_sap_core", "sap-s4hana.corp.internal", "10.0.4.88", "SAP S/4HANA Finance Core", "PRODUCTION", "TIER_0_CRITICAL"),
        ("srv_db_replica", "db-aurora-replica-02.internal", "10.0.8.22", "Aurora PostgreSQL Read Pool", "PRODUCTION", "TIER_1_HIGH"),
        ("srv_aws_sts", "aws-iam-sts-endpoint.internal", "10.0.0.1", "AWS Security Token Service", "PRODUCTION", "TIER_0_CRITICAL"),
        ("srv_github_ent", "github.enterprise.corp", "10.0.3.50", "Enterprise GitHub Server", "INTERNAL", "TIER_1_HIGH"),
        ("srv_vpn_gw", "vpn-gw-eu.internal", "10.0.99.1", "WireGuard Enterprise Gateway", "PRODUCTION", "TIER_1_HIGH"),
    ]
    cursor.executemany("""
    INSERT INTO infrastructure_nodes (id, hostname, ip_address, service_name, environment, criticality)
    VALUES (?, ?, ?, ?, ?, ?);
    """, infra)

    # 3. Client Devices
    cursor.execute("DELETE FROM client_devices;")
    devices = [
        ("dev_mac_ciso", "u_ciso", "MacBook Pro 16 (Elena - Corp Issued)", "macOS Sequoia 15.3", "HW-FP-9941-CISO", 1),
        ("dev_pad_cto", "u_cto", "ThinkPad X1 Carbon (David - Linux)", "Ubuntu 24.04 LTS", "HW-FP-1102-CTO", 1),
        ("dev_arch_devops", "u_devops", "Precision Workstation (Marcus)", "Fedora 41", "HW-FP-8834-DEVOPS", 1),
        ("dev_soc_box", "u_soc", "SOC Analyst Terminal (Sarah)", "Debian Hardened", "HW-FP-4411-SOC", 1),
        ("dev_mac_eng", "u_eng", "MacBook Pro 14 (Alex - Platform)", "macOS Sequoia 15.3", "HW-FP-5529-ENG", 1),
    ]
    cursor.executemany("""
    INSERT INTO client_devices (id, user_id, device_name, os_type, hardware_fingerprint, is_trusted)
    VALUES (?, ?, ?, ?, ?, ?);
    """, devices)

    # 4. Network Subnets
    cursor.execute("DELETE FROM network_subnets;")
    subnets = [
        ("198.51.100.0/24", "EMEA B2B Partner EDI Gateway", "PARTNER_GATEWAY", 1, "Hosts 18 active European B2B partner EDI channels. HIGH BLAST RADIUS."),
        ("172.16.50.0/24", "Corporate WireGuard VPN Pool", "CORP_VPN", 0, "Internal employee VPN lease pool."),
        ("10.0.0.0/16", "AWS Production VPC Core", "INTERNAL_VPC", 0, "Private microservice and database subnet."),
        ("73.189.44.0/24", "Comcast Residential Remote ISP", "HOME_ISP", 0, "Domestic residential remote worker connection."),
        ("45.33.32.0/24", "Offshore Hosting Datacenter Pool", "DATACENTER_PROXY", 0, "Known external cloud hosting / scanner pool."),
    ]
    cursor.executemany("""
    INSERT INTO network_subnets (cidr, subnet_name, subnet_type, is_shared, description)
    VALUES (?, ?, ?, ?, ?);
    """, subnets)


def save_audit_record(audit_data: Dict[str, Any]) -> str:
    """Inserts a decision audit record into the audit_ledger table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    action_payload_json = json.dumps(audit_data.get("action_payload", {}))
    jev_raw_json = json.dumps(audit_data.get("jev_raw_evaluation", {}))

    cursor.execute("""
    INSERT INTO audit_ledger (
        id, timestamp, log_id, target_user_id, target_service,
        attack_class, selected_tier, execution_status, authorized_persona_id,
        threat_confidence, blast_radius, reason, action_payload, jev_raw_evaluation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        audit_data["id"],
        audit_data["timestamp"],
        audit_data["log_id"],
        audit_data["target_user_id"],
        audit_data.get("target_service", "Unknown Asset"),
        audit_data["attack_class"],
        audit_data["selected_tier"],
        audit_data["execution_status"],
        audit_data.get("authorized_persona_id"),
        audit_data["threat_confidence"],
        audit_data["blast_radius"],
        audit_data["reason"],
        action_payload_json,
        jev_raw_json,
    ))
    conn.commit()
    conn.close()
    return audit_data["id"]


def get_audit_records(
    limit: int = 50,
    persona_id: Optional[str] = None,
    tier: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetches audit ledger records from SQLite, with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM audit_ledger WHERE 1=1"
    params = []

    if tier:
        query += " AND selected_tier = ?"
        params.append(tier)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = []
    for r in cursor.fetchall():
        item = dict(r)
        if isinstance(item.get("action_payload"), str):
            try:
                item["action_payload"] = json.loads(item["action_payload"])
            except Exception:
                pass
        if isinstance(item.get("jev_raw_evaluation"), str):
            try:
                item["jev_raw_evaluation"] = json.loads(item["jev_raw_evaluation"])
            except Exception:
                pass
        
        # Calculate persona actionability flag
        if persona_id:
            item["can_act"] = (
                item["selected_tier"] == "TIER_2_DRAFTED_HITL"
                and item["execution_status"] == "AWAITING_APPROVAL"
                and item.get("authorized_persona_id") == persona_id
            )
        else:
            item["can_act"] = False

        rows.append(item)

    conn.close()
    return rows


def update_audit_status(audit_id: str, new_status: str, actor_id: str) -> bool:
    """Updates the execution status of an audit record (e.g. when 1-click button is approved)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE audit_ledger
    SET execution_status = ?
    WHERE id = ? AND authorized_persona_id = ?;
    """, (new_status, audit_id, actor_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def get_db_summary() -> Dict[str, int]:
    """Returns row counts for all tables currently in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cursor.fetchall()]
    counts = {}
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        counts[t] = cursor.fetchone()[0]
    conn.close()
    return counts


if __name__ == "__main__":
    init_db(reset=True)
    summary = get_db_summary()
    print("[✓] Database initialized to pristine initial state:")
    for tbl, count in summary.items():
        print(f"    • {tbl}: {count} rows")
