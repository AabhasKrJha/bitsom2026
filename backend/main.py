"""Sentix Ingestion Service Entrypoint.

Exposes the FastAPI app so that all execution styles work seamlessly:
- `python -m uvicorn backend.main:app --port 8000` (from project root)
- `python -m uvicorn main:app --port 8000` (from inside backend/)
- `python -m uvicorn backend.app.main:app --port 8000`
- `python backend/main.py` or `python main.py`
"""

import sys
from pathlib import Path

# Automatically ensure project root and backend dir are in sys.path
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parent
PROJECT_ROOT = BACKEND_DIR.parent

for p in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.main import app, create_app
except ImportError:
    from app.main import app, create_app

__all__ = ["app", "create_app"]

if __name__ == "__main__":
    import uvicorn
    from backend.app.core.config import API_HOST, API_PORT
    uvicorn.run("backend.main:app", host=API_HOST, port=API_PORT, reload=True)
