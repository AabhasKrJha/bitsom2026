"""Log retrieval API endpoints."""

import json
from typing import Optional
from fastapi import APIRouter

from backend.app.core.database import get_db_connection
from backend.app.models.log_models import LogQueryResponse

router = APIRouter(prefix="/api/logs", tags=["Logs"])


@router.get("", response_model=LogQueryResponse)
def get_logs(limit: int = 50, user_id: Optional[str] = None):
    """Returns recent logs from SQLite, optionally filtered by user persona."""
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
    return LogQueryResponse(count=len(rows), logs=rows)
