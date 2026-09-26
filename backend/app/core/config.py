"""Application configuration and path definitions for Sentix AutoOps."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent

# Load .env file from root or backend directory
env_path = ROOT_DIR / ".env"
if not env_path.exists():
    env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

DB_PATH = BACKEND_DIR / "sentix.db"
DATA_EXPORTS_DIR = BACKEND_DIR / "data_exports"
JSONL_LOGS_PATH = DATA_EXPORTS_DIR / "enterprise_logs_100k.jsonl"
SAMPLE_SCENARIOS_PATH = DATA_EXPORTS_DIR / "attack_scenarios_sample.json"

# API & Streaming
INGEST_API_URL = os.getenv("INGEST_API_URL", "http://localhost:8000/api/logs/ingest")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# TypeSafe Jev Settings
JEV_API_KEY = os.getenv("JEV_API_KEY") or os.getenv("TYPESAFE_API_KEY") or ""
JEV_MODEL = os.getenv("JEV_MODEL", "jev-system-one-v1")
JEV_TIMEOUT = float(os.getenv("JEV_TIMEOUT", "10.0"))
JEV_OFFLINE_FALLBACK = os.getenv("JEV_OFFLINE_FALLBACK", "true").lower() in ("true", "1", "yes")
