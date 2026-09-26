"""Ground Truth State Synthesizer for Sentix.

Enriches incoming raw security telemetry with SQLite topology entities
(user profiles, server criticality, network subnet sharing, device trust)
and rolling temporal metrics into a unified State dictionary.
"""

import sqlite3
from typing import Dict, Any
from datetime import datetime, timezone, timedelta

from backend.app.core.database import get_db_connection


def synthesize_state(raw_log: Dict[str, Any], conn: sqlite3.Connection = None) -> Dict[str, Any]:
    """Synthesizes the complete ground-truth State dictionary from SQLite for Jev evaluation."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cursor = conn.cursor()

    # 1. Actor Profile
    user_id = raw_log.get("user_id", "")
    cursor.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
    user_row = cursor.fetchone()
    if user_row:
        user_dict = dict(user_row)
    else:
        user_dict = {
            "id": user_id,
            "name": "Unknown User",
            "title": "Employee",
            "role_category": "OPERATIONS",
            "department": "General",
            "asset_scope": "Standard User Access",
        }

    # 2. Network Subnet Classification
    client_ip = raw_log.get("client_ip", "0.0.0.0")
    subnet_type = raw_log.get("subnet_type", "")
    cursor.execute("SELECT * FROM network_subnets WHERE subnet_type = ?;", (subnet_type,))
    subnet_row = cursor.fetchone()
    if subnet_row:
        subnet_dict = dict(subnet_row)
    else:
        subnet_dict = {
            "cidr": f"{client_ip}/32",
            "subnet_name": "Unclassified External Host",
            "subnet_type": subnet_type or "EXTERNAL",
            "is_shared": 0,
            "description": "External client endpoint",
        }

    # 3. Known Client Device
    cursor.execute("SELECT * FROM client_devices WHERE user_id = ?;", (user_id,))
    device_row = cursor.fetchone()
    if device_row:
        device_dict = dict(device_row)
    else:
        device_dict = {
            "device_name": "Unregistered Device",
            "is_trusted": 0,
            "hardware_fingerprint": "UNREGISTERED",
        }

    # 4. Target Infrastructure Service
    source_sys = raw_log.get("source_system", "")
    cursor.execute("""
    SELECT * FROM infrastructure_nodes 
    WHERE service_name LIKE ? OR hostname LIKE ?
    LIMIT 1;
    """, (f"%{source_sys.split('/')[0].strip()}%", f"%{source_sys.split('/')[0].strip()}%"))
    infra_row = cursor.fetchone()
    if infra_row:
        infra_dict = dict(infra_row)
    else:
        infra_dict = {
            "service_name": source_sys,
            "environment": "PRODUCTION",
            "criticality": "TIER_1_HIGH",
            "hostname": "core-cluster.internal",
        }

    # 5. Rolling Temporal Velocity Window (Last 60 Seconds)
    log_ts_str = raw_log.get("timestamp", "")
    try:
        current_dt = datetime.strptime(log_ts_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        current_dt = datetime.now(timezone.utc)

    window_start = (current_dt - timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    SELECT COUNT(*), SUM(CASE WHEN status != 'SUCCESS' THEN 1 ELSE 0 END)
    FROM logs
    WHERE user_id = ? AND timestamp >= ? AND timestamp <= ?;
    """, (user_id, window_start, log_ts_str))
    cnt_row = cursor.fetchone()
    total_in_window = (cnt_row[0] or 0) + 1
    failures_in_window = (cnt_row[1] or 0) + (1 if raw_log.get("status") != "SUCCESS" else 0)

    if close_conn:
        conn.close()

    # Determine Domain Type for RBAC Mapping
    domain_type = "EXECUTIVE_IDENTITY"
    if subnet_dict.get("is_shared"):
        domain_type = "PARTNER_GATEWAY"
    elif "AWS" in source_sys or "Aurora" in infra_dict.get("service_name", ""):
        domain_type = "PRODUCTION_DATABASE"
    elif "Kong" in source_sys or "k8s" in infra_dict.get("service_name", ""):
        domain_type = "KUBERNETES_VPC"
    elif "GitHub" in source_sys:
        domain_type = "DEVELOPER_CODEBASE"
    elif "Okta" in source_sys:
        domain_type = "EXECUTIVE_IDENTITY"

    # Assemble Structured State
    return {
        "telemetry": raw_log,
        "actor": {
            "id": user_dict["id"],
            "name": user_dict["name"],
            "title": user_dict["title"],
            "role": user_dict["role_category"],
            "department": user_dict["department"],
            "asset_scope": user_dict["asset_scope"],
        },
        "network": {
            "ip": client_ip,
            "cidr": subnet_dict["cidr"],
            "subnet_name": subnet_dict["subnet_name"],
            "subnet_type": subnet_dict["subnet_type"],
            "is_shared": bool(subnet_dict["is_shared"]),
            "description": subnet_dict["description"],
        },
        "target_service": {
            "name": infra_dict["service_name"],
            "hostname": infra_dict.get("hostname", "srv.internal"),
            "environment": infra_dict["environment"],
            "criticality": infra_dict["criticality"],
        },
        "device": {
            "name": device_dict["device_name"],
            "is_trusted": bool(device_dict["is_trusted"]),
        },
        "asset": {
            "domain_type": domain_type,
        },
        "velocity_stats": {
            "attempts_last_60s": total_in_window,
            "failures_last_60s": failures_in_window,
            "failure_rate": round(failures_in_window / max(1, total_in_window), 2),
        }
    }
