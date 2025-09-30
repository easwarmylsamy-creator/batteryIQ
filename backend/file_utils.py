# backend/file_utils.py
import os
import csv
import shutil
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

def validateFile(file_path: str, requiredHeaders: List[str] = None) -> Dict[str, any]:
    """
    Comprehensive CSV file validation.
    Checks: existence, readability, headers, row consistency, data quality.

    Args:
        file_path: Path to the file to validate
        requiredHeaders: List of required column headers

    Returns:
        dict with keys: success, message, path, rowCount, warnings, headers, fileSize
    """
    logger.info(f"Validating file: {file_path}")
    
    result = {
        "success": True,
        "message": "CSV file is valid",
        "path": file_path,
        "rowCount": 0,
        "warnings": [],
        "headers": [],
        "fileSize": 0,
        "encoding": "utf-8"
    }

    # Check file existence
    if not os.path.exists(file_path):
        result.update({"success": False, "message": "File does not exist."})
        return result

    if not os.path.isfile(file_path):
        result.update({"success": False, "message": "Path is not a file."})
        return result

    # Check file permissions
    if not os.access(file_path, os.R_OK):
        result.update({"success": False, "message": "File is not readable (permission denied)."})
        return result

    # Get file size
    try:
        result["fileSize"] = os.path.getsize(file_path)
        
        # Check if file is too large (100MB limit)
        if result["fileSize"] > 100 * 1024 * 1024:
            result["warnings"].append("File is very large (>100MB). Processing may be slow.")
        
        # Check if file is empty
        if result["fileSize"] == 0:
            result.update({"success": False, "message": "File is empty."})
            return result
            
    except OSError as e:
        result.update({"success": False, "message": f"Cannot access file: {str(e)}"})
        return result

    # Try different encodings
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    successful_encoding = None
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, mode="r", newline="", encoding=encoding) as file:
                # Try to read the first line to test encoding
                first_line = file.readline()
                if first_line:
                    successful_encoding = encoding
                    result["encoding"] = encoding
                    break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.warning(f"Error testing encoding {encoding}: {str(e)}")
            continue
    
    if not successful_encoding:
        result.update({
            "success": False, 
            "message": "Cannot decode file. Unsupported encoding or corrupted file."
        })
        return result

    # Parse CSV file
    try:
        with open(file_path, mode="r", newline="", encoding=successful_encoding) as file:
            # Detect CSV dialect
            sample = file.read(1024)
            file.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            except csv.Error:
                # Use default dialect if detection fails
                dialect = csv.excel
                result["warnings"].append("Could not detect CSV format. Using default settings.")
            
            reader = csv.DictReader(file, dialect=dialect)
            headers = reader.fieldnames

            if headers is None:
                result.update({"success": False, "message": "CSV file is empty or missing headers."})
                return result

            result["headers"] = headers

            # Check for empty headers
            empty_headers = [i for i, h in enumerate(headers) if not h or h.strip() == '']
            if empty_headers:
                result["warnings"].append(f"Empty headers found at positions: {empty_headers}")

            # Check duplicate headers
            if len(headers) != len(set(headers)):
                duplicates = [h for h in headers if headers.count(h) > 1]
                result["warnings"].append(f"Duplicate headers found: {set(duplicates)}")

            # Check required headers
            if requiredHeaders:
                missing = [h for h in requiredHeaders if h not in headers]
                if missing:
                    result.update({
                        "success": False, 
                        "message": f"Missing required headers: {missing}"
                    })
                    return result

            # Validate rows
            row_lengths = []
            empty_rows = 0
            rows_with_issues = []
            
            for i, row in enumerate(reader, start=1):
                result["rowCount"] += 1
                
                # Check row length consistency
                actual_length = len([v for v in row.values() if v is not None])
                row_lengths.append(actual_length)
                
                # Check for completely empty rows
                if all(not str(v).strip() for v in row.values()):
                    empty_rows += 1
                
                # Check for rows with too many missing values
                missing_values = sum(1 for v in row.values() if not str(v).strip())
                if missing_values > len(headers) * 0.7:  # More than 70% missing
                    rows_with_issues.append(i)
                
                # Limit validation to first 1000 rows for performance
                if i > 1000:
                    result["warnings"].append("Only validated first 1000 rows due to file size.")
                    break

            # Add warnings based on validation
            if empty_rows > 0:
                result["warnings"].append(f"Found {empty_rows} empty rows.")
            
            if rows_with_issues:
                if len(rows_with_issues) <= 5:
                    result["warnings"].append(f"Rows with many missing values: {rows_with_issues}")
                else:
                    result["warnings"].append(f"Found {len(rows_with_issues)} rows with many missing values.")
            
            # Check row length consistency
            if row_lengths and len(set(row_lengths)) > 1:
                result["warnings"].append("Inconsistent number of values across rows.")

        return result

    except UnicodeDecodeError as e:
        result.update({
            "success": False, 
            "message": f"Encoding error with {successful_encoding}: {str(e)}"
        })
        return result

    except csv.Error as csv_error:
        result.update({
            "success": False, 
            "message": f"CSV parsing error: {str(csv_error)}"
        })
        return result

    except Exception as e:
        result.update({
            "success": False, 
            "message": f"Unexpected error during validation: {str(e)}"
        })
        return result


def writeLog(message: str, level: str = "INFO", log_dir: str = "./logs") -> Dict[str, any]:
    """
    Write a log message to a daily log file with rotation support.

    Args:
        message (str): The log message
        level (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        log_dir (str): Directory to store log files (default: ./logs)

    Returns:
        dict: { "success": bool, "file": str | None, "error": str | None }
    """
    try:
        os.makedirs(log_dir, exist_ok=True)

        # Prepare log file path with rotation
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"batteryiq_{date_str}.log")

        # Prepare log entry with more details
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"

        # Append to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        # Rotate logs if file gets too large (10MB limit)
        if os.path.getsize(log_file) > 10 * 1024 * 1024:
            rotate_log_file(log_file)

        return {"success": True, "file": log_file, "error": None}

    except Exception as e:
        return {"success": False, "file": None, "error": str(e)}


def rotate_log_file(log_file: str, max_backups: int = 5) -> bool:
    """
    Rotate log file when it gets too large.
    
    Args:
        log_file: Path to the log file to rotate
        max_backups: Maximum number of backup files to keep
        
    Returns:
        bool: True if rotation successful, False otherwise
    """
    try:
        base_name = log_file.replace('.log', '')
        
        # Remove oldest backup if we have too many
        oldest_backup = f"{base_name}_{max_backups}.log"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)
        
        # Shift existing backups
        for i in range(max_backups - 1, 0, -1):
            old_backup = f"{base_name}_{i}.log"
            new_backup = f"{base_name}_{i + 1}.log"
            if os.path.exists(old_backup):
                shutil.move(old_backup, new_backup)
        
        # Move current log to backup
        first_backup = f"{base_name}_1.log"
        shutil.move(log_file, first_backup)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to rotate log file {log_file}: {str(e)}")
        return False


def clean_old_logs(log_dir: str = "./logs", days_to_keep: int = 30) -> Dict[str, any]:
    """
    Clean up old log files to save disk space.
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days worth of logs to keep
        
    Returns:
        dict: Summary of cleanup operation
    """
    result = {
        "files_deleted": 0,
        "space_freed_bytes": 0,
        "errors": []
    }
    
    try:
        if not os.path.exists(log_dir):
            return result
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for filename in os.listdir(log_dir):
            if not filename.endswith('.log'):
                continue
                
            file_path = os.path.join(log_dir, filename)
            
            try:
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    result["files_deleted"] += 1
                    result["space_freed_bytes"] += file_size
                    
            except Exception as e:
                result["errors"].append(f"Error deleting {filename}: {str(e)}")
        
    except Exception as e:
        result["errors"].append(f"Error cleaning logs: {str(e)}")
    
    return result


def create_backup(file_path: str, backup_dir: str = None) -> Dict[str, any]:
    """
    Create a backup copy of a file.
    
    Args:
        file_path: Path to the file to backup
        backup_dir: Directory to store backup (defaults to ./backups)
        
    Returns:
        dict: Backup operation result
    """
    result = {
        "success": False,
        "backup_path": None,
        "error": None
    }
    
    try:
        if not os.path.exists(file_path):
            result["error"] = "Source file does not exist"
            return result
        
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        base_name = os.path.basename(file_path)
        name_part, ext_part = os.path.splitext(base_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{name_part}_backup_{timestamp}{ext_part}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        result.update({
            "success": True,
            "backup_path": backup_path
        })
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def compress_files(file_paths: List[str], zip_path: str) -> Dict[str, any]:
    """
    Compress multiple files into a ZIP archive.
    
    Args:
        file_paths: List of file paths to compress
        zip_path: Path for the output ZIP file
        
    Returns:
        dict: Compression operation result
    """
    result = {
        "success": False,
        "files_compressed": 0,
        "zip_size_bytes": 0,
        "error": None
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    # Use basename to avoid directory structure in ZIP
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                    result["files_compressed"] += 1
        
        if os.path.exists(zip_path):
            result["zip_size_bytes"] = os.path.getsize(zip_path)
            result["success"] = True
        else:
            result["error"] = "ZIP file was not created"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result


def get_file_info(file_path: str) -> Dict[str, any]:
    """
    Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: File information
    """
    info = {
        "exists": False,
        "path": file_path,
        "error": None
    }
    
    try:
        if not os.path.exists(file_path):
            info["error"] = "File does not exist"
            return info
        
        stat = os.stat(file_path)
        
        info.update({
            "exists": True,
            "size_bytes": stat.st_size,
            "size_human": format_file_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_file": os.path.isfile(file_path),
            "is_directory": os.path.isdir(file_path),
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "executable": os.access(file_path, os.X_OK),
        })
        
        # For CSV files, add additional info
        if file_path.lower().endswith('.csv'):
            validation_result = validateFile(file_path)
            info["csv_info"] = {
                "valid": validation_result["success"],
                "row_count": validation_result.get("rowCount", 0),
                "headers": validation_result.get("headers", []),
                "warnings": validation_result.get("warnings", [])
            }
    
    except Exception as e:
        info["error"] = str(e)
    
    return info


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Human-readable file size
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {units[i]}"


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {str(e)}")
        return False


def safe_file_delete(file_path: str, backup: bool = True) -> Dict[str, any]:
    """
    Safely delete a file with optional backup.
    
    Args:
        file_path: Path to the file to delete
        backup: Whether to create a backup before deletion
        
    Returns:
        dict: Deletion operation result
    """
    result = {
        "success": False,
        "backup_created": False,
        "backup_path": None,
        "error": None
    }
    
    try:
        if not os.path.exists(file_path):
            result["error"] = "File does not exist"
            return result
        
        # Create backup if requested
        if backup:
            backup_result = create_backup(file_path)
            if backup_result["success"]:
                result["backup_created"] = True
                result["backup_path"] = backup_result["backup_path"]
            else:
                result["error"] = f"Backup failed: {backup_result['error']}"
                return result
        
        # Delete the file
        os.remove(file_path)
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
    
    return result