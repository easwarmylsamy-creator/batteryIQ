# scripts/test_ingestion.py
import io
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from backend.ingestion import process_file

# --- Telemetry Upload Test ---
print("=== Telemetry Upload Test ===")
with open("sample.csv", "rb") as f:
    result = process_file(
        uploaded_file=io.BytesIO(f.read()),
        client_id=1,       # must exist in your DB
        location_id=1,     # must exist in your DB
        device_id=1,       # must exist in your DB
        test_mode=True
    )
    print(result)

# --- Manual Upload Test ---
print("\n=== Manual Upload Test ===")
with open("sample.csv", "rb") as f:
    result = process_file(
        uploaded_file=io.BytesIO(f.read()),
        author="Tester",
        notes="Quick manual test",
        test_mode=True
    )
    print(result)
