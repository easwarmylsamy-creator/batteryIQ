# backend/file_utils.py
import os
import csv
from datetime import datetime
from typing import Dict, List


def validateFile(file_path: str, requiredHeaders: List[str] | None = None) -> Dict[str, any]:
    """
    Validate a CSV file.
    Checks: existence, readability, headers, row consistency.

    Returns:
        dict with keys: success, message, path, rowCount, warnings, headers
    """
    print("inside validateFile")
    result = {
        "success": True,
        "message": "CSV file is valid",
        "path": file_path,
        "rowCount": 0,
        "warnings": [],
    }

    if not os.path.exists(file_path):
        return {"success": False, "message": "File does not exist."}

    if not os.path.isfile(file_path):
        return {"success": False, "message": "Path is not a file."}

    if not os.access(file_path, os.R_OK):
        return {"success": False, "message": "File is not readable (permission denied)."}

    try:
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            if headers is None:
                return {"success": False, "message": "CSV file is empty or missing headers."}

            result["headers"] = headers

            # Check duplicate headers
            if len(headers) != len(set(headers)):
                result["warnings"].append("Duplicate headers found.")

            # Check required headers
            if requiredHeaders:
                missing = [h for h in requiredHeaders if h not in headers]
                if missing:
                    return {"success": False, "message": f"Missing required headers: {missing}"}

            # Row count + consistency
            for i, row in enumerate(reader, start=1):
                result["rowCount"] += 1
                if len(row) != len(headers):
                    result["warnings"].append(f"Inconsistent column count in row {i}.")

        return result

    except UnicodeDecodeError:
        return {"success": False, "message": "Encoding error: Unable to decode file. Try UTF-8."}

    except csv.Error as csv_error:
        return {"success": False, "message": f"CSV parsing error: {csv_error}"}

    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {e}"}


def writeLog(message: str, level: str = "INFO", log_dir: str = "./logs") -> Dict[str, any]:
    """
    Write a log message to a daily log file.

    Args:
        message (str): The log message
        level (str): Log level ("INFO", "WARNING", "ERROR")
        log_dir (str): Directory to store log files (default: ./logs)

    Returns:
        dict: { "success": bool, "file": str | None, "error": str | None }
    """
    try:
        os.makedirs(log_dir, exist_ok=True)

        # Prepare log file path
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{date_str}.log")

        # Prepare log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

        # Append to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        return {"success": True, "file": log_file, "error": None}

    except Exception as e:
        return {"success": False, "file": None, "error": str(e)}
