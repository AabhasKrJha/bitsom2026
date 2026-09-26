"""Log Streaming Simulator for Sentix with Smart Demo Pacing.

Reads enterprise security telemetry from `enterprise_logs_100k.jsonl` and streams
events to the Ingestion API (`POST /api/logs/ingest`).

Features:
- Smart Demo Pacing (Option 1): Mixes 75% baseline enterprise noise with 25%
  curated attack bursts so judges see real live attacks every 15-20 seconds!
- Configurable ATTACK_RATIO (default 0.25, configurable via env var).
- Multi-event bursts (1 to 3 logs arriving within milliseconds).
- Dynamic delays: intra-burst: 30ms–120ms | inter-burst: 1.0s–2.5s.
- Automatic live UTC timestamp updates.
- Collision-free unique IDs for continuous streaming.
- Auto-path discovery: runnable from root or inside `backend/`.
"""

import os
import sys
import json
import time
import random
import requests
from pathlib import Path
from datetime import datetime, timezone

# Automatically inject project root and backend dir into sys.path
CURRENT_FILE = Path(__file__).resolve()
SCRIPTS_DIR = CURRENT_FILE.parent
BACKEND_DIR = SCRIPTS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

for p in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.core.config import JSONL_LOGS_PATH, INGEST_API_URL
except ImportError:
    from app.core.config import JSONL_LOGS_PATH, INGEST_API_URL

# Configurable attack ratio for demo pacing (default: 25% attacks, 75% baseline)
ATTACK_RATIO = float(os.getenv("ATTACK_RATIO", "0.25"))


def stream_logs():
    if not JSONL_LOGS_PATH.exists():
        print(f"[!] Error: {JSONL_LOGS_PATH} not found.")
        print("    Generate it first by running: python backend/scripts/generate_100k_logs.py")
        sys.exit(1)

    print("=" * 72)
    print("   📡  Sentix Smart Enterprise Log Streamer (Option 1)")
    print(f"   Target Endpoint   : {INGEST_API_URL}")
    print(f"   Source Dataset    : {JSONL_LOGS_PATH.name} (100k records)")
    print(f"   Demo Pacing Ratio : {int((1 - ATTACK_RATIO) * 100)}% Baseline Noise | {int(ATTACK_RATIO * 100)}% Attack Bursts")
    print("   Timing Profile    : Intra-burst: 30ms–120ms | Inter-burst: 1.0s–2.5s")
    print("=" * 72 + "\n")

    print("[*] Loading 100,000 telemetry records into memory buffer...")
    t0 = time.time()
    with open(JSONL_LOGS_PATH, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Partition into attack and baseline pools for smart sampling
    attack_lines = [l for l in all_lines if "attack_class" in l]
    baseline_lines = [l for l in all_lines if "attack_class" not in l]

    print(
        f"[✓] Loaded {len(all_lines):,} records in {time.time() - t0:.2f}s "
        f"({len(attack_lines):,} attack scenarios, {len(baseline_lines):,} baseline events)."
    )
    print("    Ready to stream. Press Ctrl+C to stop.\n")

    sent_count = 0
    burst_count = 0

    try:
        while True:
            burst_count += 1

            # Decide whether this burst is an Attack Scenario or Baseline Noise
            is_attack_burst = (random.random() < ATTACK_RATIO) and len(attack_lines) > 0

            if is_attack_burst:
                # Attack burst: 1 to 3 related attack logs
                batch_size = random.choice([1, 2, 2, 3])
                selected_lines = random.sample(attack_lines, batch_size)
                burst_type_tag = "ATTACK"
            else:
                # Normal baseline noise: 1 to 2 routine logs
                batch_size = 1 if random.random() < 0.70 else 2
                selected_lines = random.sample(baseline_lines, batch_size)
                burst_type_tag = "BASELINE"

            for idx, raw_line in enumerate(selected_lines):
                log_entry = json.loads(raw_line.strip())
                sent_count += 1

                # Update timestamp to current live UTC second
                now_utc = datetime.now(timezone.utc)
                log_entry["timestamp"] = now_utc.strftime("%Y-%m-%d %H:%M:%S")

                # Ensure globally unique log ID for SQLite insertion
                base_id = log_entry.get("id", "log")
                log_entry["id"] = f"{base_id}_{sent_count:06d}"

                # Send POST request to Ingestion API
                try:
                    resp = requests.post(str(INGEST_API_URL), json=log_entry, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        decision_tag = f" -> {data.get('selected_tier', 'TIER_0')} [{data.get('execution_status', '')}]"
                        if data.get("authorized_persona_id"):
                            decision_tag += f" (Auth: {data['authorized_persona_id']})"

                        intra_info = f" (burst {idx+1}/{batch_size})" if batch_size > 1 else ""
                        print(
                            f"[STREAMER #{sent_count:05d} ({burst_type_tag}){intra_info}] "
                            f"{log_entry['source_system']:<20} | "
                            f"{log_entry['user_id']:<8} | "
                            f"status={log_entry['status']:<7}"
                            f"{decision_tag}"
                        )
                    else:
                        print(f"[STREAMER WARN] API responded {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    print(f"[STREAMER WAIT] Cannot reach {INGEST_API_URL}. Is FastAPI running on port 8000?")
                    time.sleep(3.0)
                    break

                # Intra-burst delay: rapid millisecond gap between events in the same burst
                if idx < batch_size - 1:
                    intra_delay = round(random.uniform(0.03, 0.12), 3)  # 30ms to 120ms
                    time.sleep(intra_delay)

            # Inter-burst delay: randomized between 1.0s and 2.5s
            inter_delay = round(random.uniform(1.0, 2.5), 2)
            time.sleep(inter_delay)

    except KeyboardInterrupt:
        print(f"\n[!] Streamer stopped by operator.")
        print(f"    Total bursts: {burst_count} | Total events dispatched: {sent_count}")


if __name__ == "__main__":
    stream_logs()
