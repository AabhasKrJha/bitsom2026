#!/bin/bash
# Sentix AutoOps Startup Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "   🛡️  Starting Sentix AutoOps SOC Command System        "
echo "=========================================================="

source ./venv/bin/activate

# 1. Start FastAPI Backend in background
echo "[1/2] Launching FastAPI Backend on http://localhost:8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 1

# 2. Launch Streamlit Frontend
echo "[2/2] Launching Streamlit SOC Dashboard on http://localhost:8501..."
streamlit run frontend/app.py --server.port 8501 --server.headless false

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
