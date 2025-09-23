# backend/services.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError
from db.session import get_session
from db.models import Client, Location, Device, BatteryData, ManualUpload, User


# ---------------------------
# Users
# ---------------------------
def get_user_by_username(username: str) -> Optional[User]:
    with get_session() as s:
        return s.query(User).filter(User.username == username).first()


# ---------------------------
# Clients
# ---------------------------
def create_client(name: str) -> Client:
    with get_session() as s:
        client = Client(name=name)
        s.add(client)
        s.flush()
        return client


def get_clients() -> List[Client]:
    with get_session() as s:
        return s.query(Client).all()


def get_client(client_id: int) -> Optional[Client]:
    with get_session() as s:
        return s.query(Client).filter(Client.id == client_id).first()


# ---------------------------
# Locations
# ---------------------------
def create_location(client_id: int, address: str) -> Location:
    with get_session() as s:
        location = Location(client_id=client_id, address=address)
        s.add(location)
        s.flush()
        return location


def get_locations_by_client(client_id: int) -> List[Location]:
    with get_session() as s:
        return s.query(Location).filter(Location.client_id == client_id).all()


# ---------------------------
# Devices
# ---------------------------
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


def get_devices_by_location(location_id: int) -> List[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.location_id == location_id).all()


def get_devices_by_client(client_id: int) -> List[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.client_id == client_id).all()


def get_device_by_serial(serial: str) -> Optional[Device]:
    with get_session() as s:
        return s.query(Device).filter(Device.serial_number == serial).first()


# ---------------------------
# Battery Data
# ---------------------------
def get_files_by_device(device_id: int) -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.device_id == device_id).all()


def get_files_by_client(client_id: int) -> List[BatteryData]:
    with get_session() as s:
        return s.query(BatteryData).filter(BatteryData.client_id == client_id).all()


# ---------------------------
# Manual Uploads
# ---------------------------
def get_manual_uploads() -> List[ManualUpload]:
    with get_session() as s:
        return s.query(ManualUpload).all()


def get_manual_uploads_by_author(author: str) -> List[ManualUpload]:
    with get_session() as s:
        return s.query(ManualUpload).filter(ManualUpload.author == author).all()
