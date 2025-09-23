# backend/ingestion.py
from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.exc import SQLAlchemyError

from backend.file_utils import validateFile, writeLog
from db.session import get_session
from db.models import BatteryData, Client, Location, Device, ManualUpload


# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------
def get_base_dir(test_mode: bool = False) -> str:
    """Return base directory depending on environment."""
    if test_mode:
        return os.path.join(os.getcwd(), "data", "test", "uploads")
    return os.path.join(os.getcwd(), "data", "uploads")


REQUIRED_COLUMNS = ["timestamp", "voltage", "current", "temperature"]


def save_file(uploaded_file, target_path: str) -> str:
    """Save uploaded file to target path and return path."""
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "wb") as out_file:
        shutil.copyfileobj(uploaded_file, out_file)
    return target_path


def get_next_manual_serial(date_dir: str) -> int:
    """Generate next serial number for manual uploads in a date folder."""
    os.makedirs(date_dir, exist_ok=True)
    existing_files = [f for f in os.listdir(date_dir) if os.path.isfile(os.path.join(date_dir, f))]

    existing_serials = []
    for f in existing_files:
        try:
            serial = int(f.split("_")[0])
            existing_serials.append(serial)
        except (ValueError, IndexError):
            continue

    return max(existing_serials, default=0) + 1


def process_file(
    uploaded_file,
    client_id: Optional[int] = None,
    location_id: Optional[int] = None,
    device_id: Optional[int] = None,
    author: Optional[str] = None,
    notes: Optional[str] = None,
    test_mode: bool = False,
) -> Dict[str, any]:
    """
    Validate and store uploaded CSV.

    If client_id/location_id/device_id provided → Telemetry Upload.
    Else → Manual Upload.

    Args:
        test_mode (bool): if True, saves under data/test/uploads instead of data/uploads
    """
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    date_str = now.strftime("%Y%m%d")

    base_dir = get_base_dir(test_mode)
    telemetry_dir = os.path.join(base_dir, "telemetry")
    manual_dir = os.path.join(base_dir, "manual")

    try:
        if client_id and location_id and device_id:
            # ----------------------------
            # Telemetry Upload
            # ----------------------------
            filename = f"{client_id}_{device_id}_{timestamp_str}.csv"
            target_path = os.path.join(
                telemetry_dir, str(client_id), str(location_id), str(device_id), date_str, filename
            )
            file_path = save_file(uploaded_file, target_path)

            # Validate file
            result = validateFile(file_path, requiredHeaders=REQUIRED_COLUMNS)
            if not result["success"]:
                writeLog(f"Validation failed for {file_path}: {result['message']}", "ERROR")
                return result

            # Insert DB record
            with get_session() as s:
                client = s.query(Client).filter_by(id=client_id).first()
                location = s.query(Location).filter_by(id=location_id).first()
                device = s.query(Device).filter_by(id=device_id).first()

                if not client or not location or not device:
                    msg = "Invalid client/location/device reference"
                    writeLog(f"{msg} for {file_path}", "ERROR")
                    return {"success": False, "message": msg}

                entry = BatteryData(
                    client_id=client.id,
                    location_id=location.id,
                    device_id=device.id,
                    file_name=filename,
                    directory=file_path,
                )
                s.add(entry)
                s.flush()

            writeLog(f"Telemetry file {file_path} ingested for device {device_id}", "INFO")
            return {"success": True, "message": "Telemetry file processed successfully", "path": file_path}

        else:
            # ----------------------------
            # Manual Upload
            # ----------------------------
            date_dir = os.path.join(manual_dir, date_str)
            serial = get_next_manual_serial(date_dir)
            filename = f"{serial}_{now.strftime('%d%m%Y')}.csv"
            target_path = os.path.join(date_dir, filename)
            file_path = save_file(uploaded_file, target_path)

            with get_session() as s:
                entry = ManualUpload(
                    author=author or "Unknown",
                    recorded_date=now,
                    file_directory=file_path,
                    notes=notes or "Manual file upload",
                )
                s.add(entry)
                s.flush()

            writeLog(f"Manual file {file_path} uploaded by {author}", "INFO")
            return {"success": True, "message": "Manual file uploaded successfully", "path": file_path}

    except (OSError, SQLAlchemyError) as e:
        writeLog(f"Processing failed: {e}", "ERROR")
        return {"success": False, "message": f"Processing failed: {e}"}
