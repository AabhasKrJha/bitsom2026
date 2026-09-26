"""Log Streaming Simulator.

Reads enterprise logs line-by-line from enterprise_logs_100k.jsonl and dispatches
them to the Ingestion API with a randomized 2.0 to 3.0 second delay between calls.
"""

import os
import sys
import json
import time
import random
import requests
from datetime import datetime, timezone

JSONL_PATH = os.path.join(os.path.dirname(__file__), "data_exports", "enterprise_logs_100k.jsonl")
API_URL = os.getenv("INGEST_API_URL", "http://localhost:8000/api/logs/ingest")


def stream_logs():
    if not os.path.exists(JSONL_PATH):
        print(f"[!] Error: {JSONL_PATH} not found. Run python backend/generate_100k_logs.py first.")
        sys.exit(1)

    print("=================================================================")
    print("   📡  Sentix Live Enterprise Log Streamer                      ")
    print(f"   Target: {API_URL}                                            ")
    print("   Delay: Randomized 2.0s - 3.0s between events                 ")
    print("=================================================================\n")

    sent_count = 0

    try:
        with open(JSONL_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                log_entry = json.loads(line)

                # Set timestamp to current live UTC second
                log_entry["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

                # Dispatch to FastAPI Ingestion API
                try:
                    resp = requests.post(API_URL, json=log_entry, timeout=5)
                    if resp.status_code == 200:
                        sent_count += 1
                        delay = round(random.uniform(2.0, 3.0), 2)
                        print(
                            f"[STREAMER #{sent_count:04d}] "
                            f"Sent {log_entry['id']} | "
                            f"{log_entry['source_system']} -> {log_entry['status']} | "
                            f"Next event in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        print(f"[STREAMER WARN] API responded with {resp.status_code}: {resp.text}")
                        time.sleep(2.0)
                except requests.exceptions.ConnectionError:
                    print(f"[STREAMER ERROR] Cannot connect to {API_URL}. Is FastAPI running on port 8000?")
                    time.sleep(3.0)

    except KeyboardInterrupt:
        print(f"\n[!] Streamer stopped by user. Total events sent: {sent_count}")


if __name__ == "__main__":
    stream_logs()
