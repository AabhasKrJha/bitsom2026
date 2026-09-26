"""FastAPI Log Ingestion Service.

Receives enterprise logs, stores them directly into SQLite, and prints
clean formatted output to the terminal.
"""

import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.database import get_db_connection

app = FastAPI(
    title="Sentix Log Ingestion API",
    description="High-speed ingestion receiver for enterprise security telemetry",
    version="1.0.0",
)

# Enable CORS for Next.js (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ingestion Counter for Terminal Display
ingestion_counter = 0


class LogIngestPayload(BaseModel):
    id: str
    timestamp: str
    user_id: str
    source_system: str
    event_type: str
    client_ip: str
    subnet_type: str
    status: str  # 'SUCCESS', 'FAILURE', 'WARN'
    failure_reason: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Sentix Ingestion API",
        "mode": "Raw Ingestion & Storage",
    }


@app.get("/api/topology")
def get_topology():
    """Returns static enterprise topology (users, servers, client devices, subnets)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users ORDER BY id;")
    users = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM infrastructure_nodes ORDER BY id;")
    nodes = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM client_devices ORDER BY id;")
    devices = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT * FROM network_subnets ORDER BY cidr;")
    subnets = [dict(r) for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM logs;")
    total_logs = cursor.fetchone()[0]

    conn.close()

    return {
        "users": users,
        "infrastructure_nodes": nodes,
        "client_devices": devices,
        "network_subnets": subnets,
        "total_logs_stored": total_logs,
    }


@app.get("/api/logs")
def get_logs(limit: int = 50, user_id: Optional[str] = None):
    """Returns recent logs from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM logs WHERE 1=1"
    params = []
    if user_id:
        query += " AND user_id = ?"
        params.append(user_id)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = []
    for r in cursor.fetchall():
        item = dict(r)
        if isinstance(item.get("raw_payload"), str):
            try:
                item["raw_payload"] = json.loads(item["raw_payload"])
            except Exception:
                pass
        rows.append(item)

    conn.close()
    return {"count": len(rows), "logs": rows}


@app.post("/api/logs/ingest")
def ingest_log(payload: LogIngestPayload):
    """Receives a log event, persists it directly into SQLite, and logs to terminal."""
    global ingestion_counter
    ingestion_counter += 1

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO logs (id, timestamp, user_id, source_system, event_type, client_ip, subnet_type, status, failure_reason, raw_payload)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            payload.id,
            payload.timestamp,
            payload.user_id,
            payload.source_system,
            payload.event_type,
            payload.client_ip,
            payload.subnet_type,
            payload.status,
            payload.failure_reason,
            json.dumps(payload.raw_payload),
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database write error: {e}")

    conn.close()

    # Formatted terminal print
    status_tag = f"[{payload.status}]"
    if payload.failure_reason:
        status_tag += f" ({payload.failure_reason})"

    print(
        f"[INGESTED #{ingestion_counter:04d}] "
        f"{payload.timestamp} | "
        f"{payload.source_system:<22} | "
        f"{payload.event_type:<24} | "
        f"{payload.user_id:<10} | "
        f"IP: {payload.client_ip:<15} ({payload.subnet_type}) | "
        f"{status_tag}"
    )

    return {
        "status": "recorded",
        "log_id": payload.id,
        "ingested_count": ingestion_counter,
    }
