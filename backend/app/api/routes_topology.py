"""Topology retrieval API endpoint."""

from fastapi import APIRouter

from backend.app.core.database import get_db_connection
from backend.app.models.log_models import TopologyResponse

router = APIRouter(prefix="/api/topology", tags=["Topology"])


@router.get("", response_model=TopologyResponse)
def get_topology():
    """Returns static enterprise topology (users, servers, client devices, subnets)

    and current count of logs stored.
    """
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

    return TopologyResponse(
        users=users,
        infrastructure_nodes=nodes,
        client_devices=devices,
        network_subnets=subnets,
        total_logs_stored=total_logs,
    )


@router.post("/reset")
def reset_database():
    """Resets logs and audit ledger, restoring pristine demo state."""
    from backend.app.core.database import init_db
    init_db(reset=True, seed_static_entities=True)
    return {"status": "success", "message": "Database reset to pristine state."}

