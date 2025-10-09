# backend/telemetry_service.py
"""
Lightweight 24/7 Telemetry Receiver Service
Runs in a separate thread, minimal resource usage
Receives CSV files from BMS devices and saves to proper directory
"""
from __future__ import annotations

import os
import sys
import threading
import time
from datetime import datetime
from typing import Optional, Dict
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import cgi

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from db.session import get_session
from db.models import Device, BatteryData
from backend.file_utils import validateFile, writeLog

# Configuration
TELEMETRY_PORT = 8080
TELEMETRY_BASE_DIR = os.path.join(PROJECT_ROOT, "data", "uploads", "telemetry")
REQUIRED_HEADERS = ["timestamp", "voltage", "current", "temperature"]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Service statistics
service_stats = {
    "start_time": None,
    "total_uploads": 0,
    "failed_uploads": 0,
    "validation_failures": 0,
    "files_with_warnings": 0,
    "active": False
}


class TelemetryHandler(BaseHTTPRequestHandler):
    """HTTP request handler for telemetry uploads"""
    
    def log_message(self, format, *args):
        """Override to use custom logging"""
        writeLog(f"{self.address_string()} - {format % args}", "INFO")
    
    def do_GET(self):
        """Handle GET requests - health check"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            uptime = 0
            if service_stats["start_time"]:
                uptime = (datetime.now() - service_stats["start_time"]).total_seconds()
            
            response = {
                "status": "running",
                "uptime_seconds": uptime,
                "total_uploads": service_stats["total_uploads"],
                "failed_uploads": service_stats["failed_uploads"],
                "validation_failures": service_stats["validation_failures"],
                "files_with_warnings": service_stats["files_with_warnings"]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests - file upload"""
        if self.path == "/telemetry/upload":
            self.handle_telemetry_upload()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_telemetry_upload(self):
        """Process telemetry file upload"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error(400, "Content-Type must be multipart/form-data")
                return
            
            # Get device credentials from headers
            device_serial = self.headers.get('X-Device-Serial')
            client_id = self.headers.get('X-Client-ID')
            location_id = self.headers.get('X-Location-ID')
            device_id = self.headers.get('X-Device-ID')
            
            if not all([device_serial, client_id, location_id, device_id]):
                self.send_error(400, "Missing required headers")
                writeLog("Upload failed: Missing required headers", "ERROR")
                return
            
            # Parse form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            # Get uploaded file
            if 'file' not in form:
                self.send_error(400, "No file uploaded")
                return
            
            file_item = form['file']
            if not file_item.filename:
                self.send_error(400, "No file selected")
                return
            
            # Verify device exists
            device = self.verify_device(device_serial, int(device_id))
            if not device:
                self.send_error(401, "Device not found or unauthorized")
                writeLog(f"Upload failed: Device {device_serial} not found", "WARNING")
                return
            
            # Save file
            result = self.save_telemetry_file(
                file_data=file_item.file.read(),
                filename=file_item.filename,
                client_id=int(client_id),
                location_id=int(location_id),
                device_id=int(device_id)
            )
            
            if result["success"]:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                service_stats["total_uploads"] += 1
            else:
                self.send_error(500, result["message"])
                service_stats["failed_uploads"] += 1
        
        except Exception as e:
            writeLog(f"Error handling upload: {str(e)}", "ERROR")
            self.send_error(500, f"Server error: {str(e)}")
            service_stats["failed_uploads"] += 1
    
    def verify_device(self, serial_number: str, device_id: int) -> Optional[Device]:
        """Verify device exists in database"""
        try:
            with get_session() as s:
                device = s.query(Device).filter(
                    Device.serial_number == serial_number,
                    Device.id == device_id
                ).first()
                return device
        except Exception as e:
            writeLog(f"Database error verifying device: {str(e)}", "ERROR")
            return None
    
    def save_telemetry_file(
        self,
        file_data: bytes,
        filename: str,
        client_id: int,
        location_id: int,
        device_id: int
    ) -> Dict:
        """Save telemetry file to proper directory"""
        try:
            # Verify file is CSV
            if not filename.endswith('.csv'):
                return {"success": False, "message": "Only CSV files are accepted"}
            
            # Check file size
            if len(file_data) > MAX_FILE_SIZE:
                return {
                    "success": False,
                    "message": f"File too large. Max size: {MAX_FILE_SIZE} bytes"
                }
            
            # Generate filename and path
            now = datetime.now()
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")
            date_str = now.strftime("%Y%m%d")
            new_filename = f"{client_id}_{device_id}_{timestamp_str}.csv"
            
            # Create directory structure
            target_dir = os.path.join(
                TELEMETRY_BASE_DIR,
                str(client_id),
                str(location_id),
                str(device_id),
                date_str
            )
            os.makedirs(target_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(target_dir, new_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Validate file using comprehensive validation
            validation_result = validateFile(file_path, requiredHeaders=REQUIRED_HEADERS)
            
            if not validation_result["success"]:
                # Delete invalid file
                os.remove(file_path)
                writeLog(
                    f"Validation failed for {new_filename}: {validation_result['message']}",
                    "ERROR"
                )
                service_stats["validation_failures"] += 1
                return {
                    "success": False,
                    "message": f"Validation failed: {validation_result['message']}",
                    "validation_details": validation_result
                }
            
            # Log warnings if any
            if validation_result.get("warnings"):
                service_stats["files_with_warnings"] += 1
                for warning in validation_result["warnings"]:
                    writeLog(
                        f"Validation warning for {new_filename}: {warning}",
                        "WARNING"
                    )
            
            # Insert database record
            with get_session() as s:
                entry = BatteryData(
                    client_id=client_id,
                    location_id=location_id,
                    device_id=device_id,
                    file_name=new_filename,
                    directory=file_path
                )
                s.add(entry)
                s.flush()
                file_id = entry.id
            
            writeLog(
                f"Telemetry uploaded: Device {device_id}, File: {new_filename}",
                "INFO"
            )
            
            return {
                "success": True,
                "message": "File uploaded successfully",
                "file_id": file_id,
                "file_path": file_path,
                "filename": new_filename,
                "validation_info": {
                    "row_count": validation_result.get("rowCount", 0),
                    "file_size": validation_result.get("fileSize", 0),
                    "warnings": validation_result.get("warnings", []),
                    "encoding": validation_result.get("encoding", "utf-8")
                }
            }
        
        except Exception as e:
            writeLog(f"Error saving telemetry file: {str(e)}", "ERROR")
            return {"success": False, "message": f"Upload failed: {str(e)}"}


class TelemetryService:
    """Telemetry service manager"""
    
    def __init__(self, port: int = TELEMETRY_PORT):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self):
        """Start the telemetry service in a separate thread"""
        if self.running:
            writeLog("Telemetry service already running", "WARNING")
            return
        
        try:
            # Create base directory
            os.makedirs(TELEMETRY_BASE_DIR, exist_ok=True)
            
            # Start server in thread
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            
            self.running = True
            service_stats["active"] = True
            service_stats["start_time"] = datetime.now()
            
            writeLog(f"Telemetry service started on port {self.port}", "INFO")
        
        except Exception as e:
            writeLog(f"Failed to start telemetry service: {str(e)}", "ERROR")
            raise
    
    def _run_server(self):
        """Run the HTTP server"""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), TelemetryHandler)
            writeLog(f"Telemetry receiver listening on port {self.port}", "INFO")
            self.server.serve_forever()
        except Exception as e:
            writeLog(f"Telemetry server error: {str(e)}", "ERROR")
            self.running = False
            service_stats["active"] = False
    
    def stop(self):
        """Stop the telemetry service"""
        if not self.running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            self.running = False
            service_stats["active"] = False
            
            writeLog("Telemetry service stopped", "INFO")
        except Exception as e:
            writeLog(f"Error stopping telemetry service: {str(e)}", "ERROR")
    
    def is_running(self) -> bool:
        """Check if service is running"""
        return self.running and self.thread and self.thread.is_alive()
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        uptime = 0
        if service_stats["start_time"]:
            uptime = (datetime.now() - service_stats["start_time"]).total_seconds()
        
        return {
            "running": self.is_running(),
            "uptime_seconds": uptime,
            "uptime_hours": uptime / 3600,
            "total_uploads": service_stats["total_uploads"],
            "failed_uploads": service_stats["failed_uploads"],
            "validation_failures": service_stats["validation_failures"],
            "files_with_warnings": service_stats["files_with_warnings"],
            "success_rate": (
                (service_stats["total_uploads"] / 
                 (service_stats["total_uploads"] + service_stats["failed_uploads"]) * 100)
                if (service_stats["total_uploads"] + service_stats["failed_uploads"]) > 0
                else 0
            )
        }


# Global service instance
_telemetry_service = None


def start_telemetry_service(port: int = TELEMETRY_PORT):
    """Start the global telemetry service"""
    global _telemetry_service
    
    if _telemetry_service is None:
        _telemetry_service = TelemetryService(port)
    
    _telemetry_service.start()
    return _telemetry_service


def stop_telemetry_service():
    """Stop the global telemetry service"""
    global _telemetry_service
    
    if _telemetry_service:
        _telemetry_service.stop()


def get_telemetry_service() -> Optional[TelemetryService]:
    """Get the global telemetry service instance"""
    return _telemetry_service


if __name__ == "__main__":
    # Run as standalone service
    print("Starting BatteryIQ Telemetry Receiver Service...")
    print(f"Listening on port {TELEMETRY_PORT}")
    print("Press Ctrl+C to stop")
    
    service = start_telemetry_service()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping service...")
        stop_telemetry_service()
        print("Service stopped")