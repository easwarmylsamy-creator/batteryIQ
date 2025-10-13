# db/models.py
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .session import Base


# ---------------------------
# User table
# ---------------------------
class UserRole(str, enum.Enum):
    admin = "admin"
    scientist = "scientist"
    client = "client"
    guest = "guest"
    super_admin = "super_admin"
    


# ---------------------------
# User table
# ---------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.client)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"


# ---------------------------
# Clients table
# ---------------------------
class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    num_sites: Mapped[int] = mapped_column(Integer, default=0)
    num_devices: Mapped[int] = mapped_column(Integer, default=0)

    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="client", cascade="all, delete-orphan"
    )
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="client", cascade="all, delete-orphan"
    )
    telemetry: Mapped[list["BatteryData"]] = relationship(
        "BatteryData", back_populates="client", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name!r}>"


# ---------------------------
# Locations table
# ---------------------------
class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    nickname: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    client: Mapped["Client"] = relationship("Client", back_populates="locations")
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="location", cascade="all, delete-orphan"
    )
    telemetry: Mapped[list["BatteryData"]] = relationship(
        "BatteryData", back_populates="location", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("client_id", "address", name="uq_client_address"),
    )

    def __repr__(self) -> str:
        return f"<Location id={self.id} nickname={self.nickname!r} address={self.address!r}>"
# ---------------------------
# Devices table
# ---------------------------
class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    firmware_version: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    location: Mapped["Location"] = relationship("Location", back_populates="devices")
    client: Mapped["Client"] = relationship("Client", back_populates="devices")
    telemetry: Mapped[list["BatteryData"]] = relationship(
        "BatteryData", back_populates="device", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} status={self.status} sn={self.serial_number!r} client_id={self.client_id} location_id={self.location_id}>"


# ---------------------------
# Battery Data table
# ---------------------------
class BatteryData(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    directory: Mapped[str] = mapped_column(String(255), nullable=False)
    guest_flag: Mapped[bool] = mapped_column(Integer, default=0, nullable=False)  # 0=not flagged, 1=flagged for guest

    client: Mapped["Client"] = relationship("Client", back_populates="telemetry")
    location: Mapped["Location"] = relationship("Location", back_populates="telemetry")
    device: Mapped["Device"] = relationship("Device", back_populates="telemetry")

    def __repr__(self) -> str:
        return f"<BatteryData id={self.id} client_id={self.client_id} device_id={self.device_id} file={self.file_name!r}>"


# ---------------------------
# Manual Uploads table
# ---------------------------
class ManualUpload(Base):
    __tablename__ = "manual_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    recorded_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    file_directory: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    guest_flag: Mapped[bool] = mapped_column(Integer, default=0, nullable=False)  # 0=not flagged, 1=flagged for guest

    def __repr__(self) -> str:
        return f"<ManualUpload id={self.id} author={self.author!r} file={self.file_directory!r}>"
    
# ---------------------------   
# Metrics table
# ---------------------------
class Metrics(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telemetry_id: Mapped[int] = mapped_column(
        ForeignKey("telemetry.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    avg_voltage: Mapped[float] = mapped_column(nullable=True)
    min_voltage: Mapped[float] = mapped_column(nullable=True)
    max_voltage: Mapped[float] = mapped_column(nullable=True)
    avg_current: Mapped[float] = mapped_column(nullable=True)
    avg_temperature: Mapped[float] = mapped_column(nullable=True)

    telemetry: Mapped["BatteryData"] = relationship("BatteryData")

    def __repr__(self) -> str:
        return f"<Metrics id={self.id} file={self.telemetry_id} avgV={self.avg_voltage}>"
