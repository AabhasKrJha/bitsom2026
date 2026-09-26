"""Database schema, connection manager, and topology initialization for Sentix.

Maintains topology entities (users, infrastructure, client devices, subnets)
and an empty raw logs table. If sentix.db is ever deleted, running this file
directly restores the database to its pristine initial state in milliseconds.
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "sentix.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(reset: bool = False):
    """Initializes the database schema and seeds static topology entities only.
    
    If reset is True, drops existing tables to guarantee a clean slate.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if reset:
        cursor.execute("DROP TABLE IF EXISTS logs;")
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("DROP TABLE IF EXISTS infrastructure_nodes;")
        cursor.execute("DROP TABLE IF EXISTS client_devices;")
        cursor.execute("DROP TABLE IF EXISTS network_subnets;")
        cursor.execute("DROP TABLE IF EXISTS decisions;")
        cursor.execute("DROP TABLE IF EXISTS audit_ledger;")

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

    # Seed static topology entities
    _seed_topology(cursor)

    # Ensure logs table is completely clean
    cursor.execute("DELETE FROM logs;")

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


def get_db_summary() -> Dict[str, int]:
    """Returns row counts for all tables currently in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
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
