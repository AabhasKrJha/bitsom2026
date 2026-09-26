"""Database Reset Utility.

Resets sentix.db to its initial scratch state:
- Seeds all 4 static enterprise topology tables (users, servers, client devices, subnets).
- Keeps the raw `logs` table 100% empty and ready for fresh demo ingestion.
"""

import sys
from pathlib import Path

# Automatically inject project root and backend dir into sys.path
CURRENT_FILE = Path(__file__).resolve()
SCRIPTS_DIR = CURRENT_FILE.parent
BACKEND_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

for p in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.core.config import DB_PATH
    from backend.app.core.database import init_db, get_db_summary
except ImportError:
    from app.core.config import DB_PATH
    from app.core.database import init_db, get_db_summary


def run_reset():
    print(f"[*] Target SQLite Database: {DB_PATH}")
    print("[*] Rebuilding schema and reseeding static topology entities...")

    init_db(reset=True, seed_static_entities=True)

    summary = get_db_summary()
    print("\n[✓] Database reset successfully to pristine scratch state:")
    for tbl, count in sorted(summary.items()):
        status = "EMPTY (ready for live ingestion)" if count == 0 else f"{count} seeded records"
        print(f"    • {tbl:<22} : {status}")


if __name__ == "__main__":
    run_reset()
