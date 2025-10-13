# backend/services.py
from __future__ import annotations

from typing import Optional, List, Dict
import logging
import os
from sqlalchemy.exc import SQLAlchemyError
from db.session import get_session
from db.models import Client, Location, Device, BatteryData, ManualUpload, User, Metrics

from backend.user_profiles import (
    create_user_profile, 
    get_user_profile, 
    update_user_profile,
    delete_user_profile
)

# Setup logging
logger = logging.getLogger(__name__)

# ---------------------------
# Error Handling Decorator
# ---------------------------
def handle_db_errors(func):
    """Decorator to handle database errors consistently"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    return wrapper

# ---------------------------
# Users
# ---------------------------
@handle_db_errors
def get_user_by_username(username: str) -> Optional[User]:
    with get_session() as s:
        return s.query(User).filter(User.username == username).first()

@handle_db_errors
def get_user_by_id(user_id: int) -> Optional[User]:
    with get_session() as s:
        return s.query(User).filter(User.id == user_id).first()

@handle_db_errors
def get_all_users() -> List[User]:
    with get_session() as s:
        return s.query(User).all()

@handle_db_errors
def create_user(username: str, email: str, hashed_password: str, role: str) -> User:
    with get_session() as s:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        s.add(user)
        s.flush()
        return user

@handle_db_errors
def update_user(user_id: int, **kwargs) -> Optional[User]:
    with get_session() as s:
        user = s.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            s.flush()
        return user

@handle_db_errors
def delete_user(user_id: int) -> bool:
    with get_session() as s:
        user = s.query(User).filter(User.id == user_id).first()
        if user:
            s.delete(user)
            s.flush()
            return True
        return False

# ---------------------------
# Clients
# ---------------------------
@handle_db_errors
def create_client(name: str) -> Client:
    with get_session() as s:
        client = Client(name=name)
        s.add(client)
        s.flush()
        return client

@handle_db_errors
def get_clients() -> List[Client]:
    with get_session() as s:
        return s.query(Client).all()

@handle_db_errors
def get_client(client_id: int) -> Optional[Client]:
    with get_session() as s:
        return s.query(Client).filter(Client.id == client_id).first()

@handle_db_errors
def update_client(client_id: int, **kwargs) -> Optional[Client]:
    with get_session() as s:
        client = s.query(Client).filter(Client.id == client_id).first()
        if client:
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            s.flush()
        return client

@handle_db_errors
def delete_client(client_id: int) -> bool:
    with get_session() as s:
        client = s.query(Client).filter(Client.id == client_id).first()
        if client:
            s.delete(client)
            s.flush()
            return True
        return False

# ---------------------------
# Locations
# ---------------------------
@handle_db_errors
def create_location(client_id: int, address: str, nickname: str = None) -> Location:
    with get_session() as s:
        location = Location(
            client_id=client_id, 
            address=address,
            nickname=nickname
        )
        s.add(location)
        s.flush()
        return location

@handle_db_errors
def get_locations_by_client(client_id: int) -> List[Location]:
    with get_session() as s:
        return s.query(Location).filter(Location.client_id == client_id).all()

@handle_db_errors
def get_location(location_id: int) -> Optional[Location]:
    with get_session() as s:
        return s.query(Location).filter(Location.id == location_id).first()

@handle_db_errors
def get_all_locations() -> List[Location]:
    with get_session() as s:
        return s.query(Location).all()

@handle_db_errors
def update_location(location_id: int, **kwargs) -> Optional[Location]:
    with get_session() as s:
        location = s.query(Location).filter(Location.id == location_id).first()
        if location:
            for key, value in kwargs.items():
                if hasattr(location, key):
                    setattr(location, key, value)
            s.flush()
        return location

@handle_db_errors
def delete_location(location_id: int) -> bool:
    with get_session() as s:
        location = s.query(Location).filter(Location.id == location_id).first()
        if location:
            s.delete(location)
            s.flush()
            return True
        return False

# ---------------------------
# Devices
# ---------------------------
@handle_db_errors
def create_device(client_id: int, location_id: int, name: str, serial: str,
                  firmware_version: str = None, status: str = "active") -> Device:
    with get_session() as s:
        device = Device(
            client_id=client_id,
            location_id=location_id,
            name=name,
            serial_number=serial,
            firmware_version=firmware_version,
            status=status,
        )
        s.add(device)
        s.flush()
        return device

@handle_db_errors
def get_devices_by_location(location_id: int) -> List[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.location_id == location_id).all()

@handle_db_errors
def get_devices_by_client(client_id: int) -> List[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.client_id == client_id).all()

@handle_db_errors
def get_device_by_serial(serial: str) -> Optional[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.serial_number == serial).first()

@handle_db_errors
def get_device(device_id: int) -> Optional[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.id == device_id).first()

@handle_db_errors
def get_all_devices() -> List[Device]:
    with get_session() as s:
        return s.query(Device).all()

@handle_db_errors
def update_device(device_id: int, **kwargs) -> Optional[Device]:
    with get_session() as s:
        device = s.query(Device).filter(Device.id == device_id).first()
        if device:
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            s.flush()
        return device

@handle_db_errors
def delete_device(device_id: int) -> bool:
    with get_session() as s:
        device = s.query(Device).filter(Device.id == device_id).first()
        if device:
            s.delete(device)
            s.flush()
            return True
        return False

# ---------------------------
# Battery Data (Telemetry)
# ---------------------------
@handle_db_errors
def get_files_by_device(device_id: int) -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.device_id == device_id).all()

@handle_db_errors
def get_files_by_client(client_id: int) -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.client_id == client_id).all()

@handle_db_errors
def get_files_by_location(location_id: int) -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.location_id == location_id).all()

@handle_db_errors
def get_all_battery_data() -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).all()

@handle_db_errors
def get_battery_data(data_id: int) -> Optional[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.id == data_id).first()

@handle_db_errors
def delete_battery_data(data_id: int) -> bool:
    with get_session() as s:
        data = s.query(BatteryData).filter(BatteryData.id == data_id).first()
        if data:
            s.delete(data)
            s.flush()
            return True
        return False

# ---------------------------
# Manual Uploads
# ---------------------------
@handle_db_errors
def get_manual_uploads() -> List[ManualUpload]:
    with get_session() as s:
        return s.query(ManualUpload).order_by(ManualUpload.recorded_date.desc()).all()

@handle_db_errors
def get_manual_uploads_by_author(author: str) -> List[ManualUpload]:
    with get_session() as s:
        return s.query(ManualUpload).filter(ManualUpload.author == author).order_by(ManualUpload.recorded_date.desc()).all()

@handle_db_errors
def get_manual_upload(upload_id: int) -> Optional[ManualUpload]:
    with get_session() as s:
        return s.query(ManualUpload).filter(ManualUpload.id == upload_id).first()

@handle_db_errors
def update_manual_upload(upload_id: int, **kwargs) -> Optional[ManualUpload]:
    with get_session() as s:
        upload = s.query(ManualUpload).filter(ManualUpload.id == upload_id).first()
        if upload:
            for key, value in kwargs.items():
                if hasattr(upload, key):
                    setattr(upload, key, value)
            s.flush()
        return upload

@handle_db_errors
def delete_manual_upload(upload_id: int) -> bool:
    with get_session() as s:
        upload = s.query(ManualUpload).filter(ManualUpload.id == upload_id).first()
        if upload:
            s.delete(upload)
            s.flush()
            return True
        return False

# ---------------------------
# Metrics
# ---------------------------
@handle_db_errors
def get_metrics_by_battery_data(battery_data_id: int) -> List[Metrics]:
    with get_session() as s:
        return s.query(Metrics).filter(Metrics.telemetry_id == battery_data_id).all()

@handle_db_errors
def get_metrics_by_device(device_id: int) -> List[Metrics]:
    with get_session() as s:
        return s.query(Metrics).join(BatteryData).filter(BatteryData.device_id == device_id).all()

@handle_db_errors
def get_all_metrics() -> List[Metrics]:
    with get_session() as s:
        return s.query(Metrics).all()

@handle_db_errors
def create_metrics(telemetry_id: int, **kwargs) -> Metrics:
    with get_session() as s:
        metrics = Metrics(telemetry_id=telemetry_id, **kwargs)
        s.add(metrics)
        s.flush()
        return metrics

@handle_db_errors
def delete_metrics(metrics_id: int) -> bool:
    with get_session() as s:
        metrics = s.query(Metrics).filter(Metrics.id == metrics_id).first()
        if metrics:
            s.delete(metrics)
            s.flush()
            return True
        return False

# ---------------------------
# Statistics & Summary Functions
# ---------------------------
@handle_db_errors
def get_client_statistics(client_id: int) -> dict:
    """Get comprehensive statistics for a client"""
    with get_session() as s:
        client = s.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {}
        
        locations = s.query(Location).filter(Location.client_id == client_id).count()
        devices = s.query(Device).filter(Device.client_id == client_id).count()
        telemetry_files = s.query(BatteryData).filter(BatteryData.client_id == client_id).count()
        
        return {
            "client_name": client.name,
            "total_locations": locations,
            "total_devices": devices,
            "total_telemetry_files": telemetry_files,
        }

@handle_db_errors
def get_device_statistics(device_id: int) -> dict:
    """Get comprehensive statistics for a device"""
    with get_session() as s:
        device = s.query(Device).filter(Device.id == device_id).first()
        if not device:
            return {}
        
        telemetry_files = s.query(BatteryData).filter(BatteryData.device_id == device_id).count()
        metrics_count = s.query(Metrics).join(BatteryData).filter(BatteryData.device_id == device_id).count()
        
        return {
            "device_name": device.name,
            "serial_number": device.serial_number,
            "status": device.status,
            "firmware_version": device.firmware_version,
            "total_files": telemetry_files,
            "total_metrics": metrics_count,
        }

@handle_db_errors
def get_system_overview() -> dict:
    """Get system-wide statistics"""
    with get_session() as s:
        total_clients = s.query(Client).count()
        total_locations = s.query(Location).count()
        total_devices = s.query(Device).count()
        total_telemetry = s.query(BatteryData).count()
        total_manual = s.query(ManualUpload).count()
        total_users = s.query(User).count()
        
        return {
            "total_clients": total_clients,
            "total_locations": total_locations,
            "total_devices": total_devices,
            "total_telemetry_files": total_telemetry,
            "total_manual_uploads": total_manual,
            "total_users": total_users,
        }

# ---------------------------
# Search and Filter Functions
# ---------------------------
@handle_db_errors
def search_devices(query: str, client_id: int = None) -> List[Device]:
    """Search devices by name or serial number"""
    with get_session() as s:
        base_query = s.query(Device)
        
        if client_id:
            base_query = base_query.filter(Device.client_id == client_id)
        
        # Search in name and serial number
        search_filter = (Device.name.ilike(f"%{query}%")) | (Device.serial_number.ilike(f"%{query}%"))
        
        return base_query.filter(search_filter).all()

@handle_db_errors
def get_recent_uploads(limit: int = 10) -> List[dict]:
    """Get recent uploads from both telemetry and manual sources"""
    with get_session() as s:
        # Get recent telemetry uploads
        recent_telemetry = s.query(BatteryData).order_by(BatteryData.id.desc()).limit(limit//2).all()
        
        # Get recent manual uploads
        recent_manual = s.query(ManualUpload).order_by(ManualUpload.recorded_date.desc()).limit(limit//2).all()
        
        results = []
        
        # Add telemetry uploads
        for item in recent_telemetry:
            results.append({
                "type": "telemetry",
                "file_name": item.file_name,
                "client": item.client.name if item.client else "Unknown",
                "device": f"Device {item.device_id}" if item.device_id else "Unknown",
                "date": "Recent",  # You might want to add timestamp to BatteryData model
                "path": item.directory
            })
        
        # Add manual uploads
        for item in recent_manual:
            results.append({
                "type": "manual",
                "file_name": os.path.basename(item.file_directory),
                "author": item.author,
                "date": item.recorded_date.strftime("%Y-%m-%d %H:%M"),
                "notes": item.notes,
                "path": item.file_directory
            })
        
        return results[:limit]
    
# ---------------------------
# Guest Flag Management
# ---------------------------
@handle_db_errors
def toggle_telemetry_guest_flag(telemetry_id: int) -> Optional[BatteryData]:
    """Toggle guest flag for telemetry data"""
    with get_session() as s:
        data = s.query(BatteryData).filter(BatteryData.id == telemetry_id).first()
        if data:
            data.guest_flag = 1 if data.guest_flag == 0 else 0
            s.flush()
            return data
        return None

@handle_db_errors
def toggle_manual_upload_guest_flag(upload_id: int) -> Optional[ManualUpload]:
    """Toggle guest flag for manual upload"""
    with get_session() as s:
        upload = s.query(ManualUpload).filter(ManualUpload.id == upload_id).first()
        if upload:
            upload.guest_flag = 1 if upload.guest_flag == 0 else 0
            s.flush()
            return upload
        return None

@handle_db_errors
def get_guest_flagged_telemetry() -> List[BatteryData]:
    """Get all telemetry data flagged for guest access"""
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.guest_flag == 1).all()

@handle_db_errors
def get_guest_flagged_manual_uploads() -> List[ManualUpload]:
    """Get all manual uploads flagged for guest access"""
    with get_session() as s:
        return s.query(ManualUpload).filter(ManualUpload.guest_flag == 1).all()
    

@handle_db_errors
def create_user_with_profile(username: str, email: str, hashed_password: str, 
                             role: str, profile_data: Dict, created_by: int = None) -> Dict:
    """
    Create user in database and corresponding profile in JSON
    
    Args:
        username: Username
        email: Email address
        hashed_password: Hashed password
        role: User role
        profile_data: Extended profile information
        created_by: ID of admin creating the user
        
    Returns:
        Dictionary with user and profile objects
    """
    with get_session() as s:
        # Create database user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        s.add(user)
        s.flush()
        
        # Create JSON profile
        profile_data["created_by"] = created_by
        profile = create_user_profile(user.id, profile_data)
        
        return {
            "user": user,
            "profile": profile,
            "success": True
        }


@handle_db_errors
def get_user_with_profile(user_id: int) -> Optional[Dict]:
    """
    Get user from database with profile information
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with user and profile data
    """
    with get_session() as s:
        user = s.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        profile = get_user_profile(user_id)
        
        return {
            "user": user,
            "profile": profile
        }


@handle_db_errors
def update_user_with_profile(user_id: int, user_data: Dict = None, 
                             profile_data: Dict = None) -> Optional[Dict]:
    """
    Update user in database and/or profile
    
    Args:
        user_id: User ID
        user_data: Database user fields to update (email, role, etc)
        profile_data: Profile fields to update
        
    Returns:
        Updated user and profile data
    """
    with get_session() as s:
        user = s.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Update database user if data provided
        if user_data:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            s.flush()
        
        # Update profile if data provided
        profile = None
        if profile_data:
            profile = update_user_profile(user_id, profile_data)
        else:
            profile = get_user_profile(user_id)
        
        return {
            "user": user,
            "profile": profile,
            "success": True
        }


@handle_db_errors
def delete_user_with_profile(user_id: int) -> bool:
    """
    Delete user from database and their profile
    
    Args:
        user_id: User ID
        
    Returns:
        True if successful
    """
    with get_session() as s:
        user = s.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        # Delete profile first
        delete_user_profile(user_id)
        
        # Delete database user
        s.delete(user)
        s.flush()
        
        return True


@handle_db_errors
def get_all_users_with_profiles() -> List[Dict]:
    """
    Get all users with their profile information
    
    Returns:
        List of dictionaries with user and profile data
    """
    with get_session() as s:
        users = s.query(User).all()
        
        users_with_profiles = []
        
        for user in users:
            profile = get_user_profile(user.id)
            users_with_profiles.append({
                "user": user,
                "profile": profile
            })
        
        return users_with_profiles


@handle_db_errors
def get_client_info(location_id: int = None, device_id: int = None) -> Optional[Dict]:
    if location_id:
        with get_session() as s:
            location = s.query(Location).filter(Location.id == location_id).first()
        
            if location and location.client:
                client = location.client
                return {
                    "success" : True,
                    "id": client.id,
                    "name": client.name,
                    "num_sites": client.num_sites,
                    "num_devices": client.num_devices,
                    "location": location.address
                }
        
        return {"success": False, "message": "Location not found"}
    
    elif device_id:
        with get_session() as s:
            device = s.query(Device).filter(Device.id == device_id).first()
            
            if device:
                client = device.client
                location = device.location
                
                return {
                    "success" : True,
                    "id": client.id if client else None,
                    "name": client.name if client else None,
                    "num_sites": client.num_sites if client else None,
                    "num_devices": client.num_devices if client else None,
                    "location": location.address if location else None,
                    "device_name": device.name,
                    "device_serial": device.serial_number
                }
            
            return {"success": False, "message": "Device not found"}
        