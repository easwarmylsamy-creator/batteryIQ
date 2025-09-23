# scripts/seed_db.py
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError

# ------------------------------------------------------------------
# Ensure Python finds the project root
# ------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ------------------------------------------------------------------
# Imports from db package
# ------------------------------------------------------------------
from db.session import Base, engine, get_session
from db.models import User, UserRole, Client, Location, Device, BatteryData, ManualUpload


def create_schema() -> None:
    """Create all tables if they don't exist."""
    print("Creating tables (if not exist)…")
    Base.metadata.create_all(bind=engine)
    print("Done.")

def seed_users() -> None:
    print("Seeding users…")
    default_password = "password123"

    demo_users = [
        ("admin", "admin@local", UserRole.admin),
        ("scientist", "scientist@local", UserRole.scientist),  # role will be handled separately if you add more enums
        ("client", "client@local", UserRole.client),
        ("guest", "guest@local", UserRole.guest),
        ("god", "god@local", UserRole.god),  # treat god as elevated admin
    ]

    with get_session() as s:
        for username, email, role in demo_users:
            if not s.query(User).filter(User.username == username).first():
                u = User(
                    username=username,
                    email=email,
                    hashed_password=bcrypt.hash(default_password),
                    role=role,
                )
                s.add(u)
        s.flush()
    print("Users seeded.")


def seed_minimal() -> None:
    """Insert demo data for testing (idempotent)."""
    print("Seeding minimal data…")
    with get_session() as s:
        # # 1. Admin User
        # if not s.query(User).filter(User.username == "admin").first():
        #     admin = User(
        #         username="admin",
        #         email="admin@local",
        #         hashed_password=bcrypt.hash("admin123"),  # ⚠️ demo only
        #         role=UserRole.admin,
        #     )
        #     s.add(admin)

        # 2. Client
        client = s.query(Client).filter(Client.name == "Demo Client").first()
        if not client:
            client = Client(name="Demo Client", num_sites=1, num_devices=1)
            s.add(client)
            s.flush()

        # 3. Location
        loc = s.query(Location).filter(
            Location.client_id == client.id,
            Location.address == "123 Local Street",
        ).first()
        if not loc:
            loc = Location(client_id=client.id, address="123 Local Street")
            s.add(loc)
            s.flush()

        # 4. Device
        dev = s.query(Device).filter(Device.serial_number == "SN-0001").first()
        if not dev:
            dev = Device(
                location_id=loc.id,
                client_id=client.id,
                name="BMS-001",
                serial_number="SN-0001",
                firmware_version="1.0.0",
                status="active",
            )
            s.add(dev)
            s.flush()

        # 5. Battery Data
        data_entry = (
            s.query(BatteryData)
            .filter(
                BatteryData.client_id == client.id,
                BatteryData.location_id == loc.id,
                BatteryData.device_id == dev.id,
                BatteryData.file_name == "demo.csv",
            )
            .first()
        )
        if not data_entry:
            data_entry = BatteryData(
                client_id=client.id,
                location_id=loc.id,
                device_id=dev.id,
                file_name="demo.csv",
                directory="./data/raw/demo.csv",
            )
            s.add(data_entry)

        # 6. Manual Uploads
        manual = (
            s.query(ManualUpload)
            .filter(ManualUpload.file_directory == "./data/manual/manual1.csv")
            .first()
        )
        if not manual:
            manual = ManualUpload(
                author="Test User",
                recorded_date=datetime.now(timezone.utc),
                file_directory="./data/manual/manual1.csv",
                notes="Seeded manual upload file",
            )
            s.add(manual)

        try:
            s.flush()
            print("Seed successful.")
        except IntegrityError as e:
            s.rollback()
            print(f"Seed skipped: {e.orig}")


def main() -> None:
    create_schema()
    seed_minimal()
    seed_users()
    print("All done ✅")


if __name__ == "__main__":
    main()
