# scripts/seed_db.py
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone, timedelta

from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError

# Ensure Python finds the project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Imports from db package
from db.session import Base, engine, get_session
from db.models import User, UserRole, Client, Location, Device, BatteryData, ManualUpload


def create_schema() -> None:
    """Create all tables if they don't exist."""
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")


def seed_users() -> None:
    """Seed demo users with different roles"""
    print("\nSeeding users...")
    default_password = "password123"

    demo_users = [
        ("admin", "admin@batteryiq.com", UserRole.admin),
        ("scientist", "scientist@batteryiq.com", UserRole.scientist),
        ("client", "client@batteryiq.com", UserRole.client),
        ("guest", "guest@batteryiq.com", UserRole.guest),
        ("super_admin", "super_admin@batteryiq.com", UserRole.super_admin),
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
                print(f"  Created user: {username} ({role.value})")
            else:
                print(f"  User already exists: {username}")
        s.flush()
    print("Users seeded.")


def seed_clients_locations_devices() -> None:
    """Seed 5 clients, each with 5 locations and 5 devices per location"""
    print("\nSeeding clients, locations, and devices...")
    
    # Real New Zealand energy/tech companies
    client_names = [
        "Contact Energy",
        "Mercury Energy",
        "Genesis Energy",
        "Meridian Energy",
        "Vector Limited"
    ]
    
    # New Zealand locations with nicknames and addresses
    location_templates = [
        [
            ("Auckland Central Hub", "123 Queen Street, Auckland CBD, Auckland 1010"),
            ("Manukau Solar Farm", "45 Great South Road, Manukau, Auckland 2104"),
            ("North Shore Battery Station", "78 Takapuna Beach Road, North Shore, Auckland 0622"),
            ("Waitakere Wind Farm", "12 Henderson Valley Road, Waitakere, Auckland 0612"),
            ("Papakura Grid Station", "90 Great South Road, Papakura, Auckland 2110")
        ],
        [
            ("Wellington Central Office", "56 Lambton Quay, Wellington Central, Wellington 6011"),
            ("Lower Hutt Storage", "34 High Street, Lower Hutt, Wellington 5010"),
            ("Upper Hutt Facility", "22 Main Street, Upper Hutt, Wellington 5018"),
            ("Porirua Battery Hub", "15 Cobham Court, Porirua, Wellington 5022"),
            ("Kapiti Wind Station", "88 Kapiti Road, Kapiti Coast, Wellington 5032")
        ],
        [
            ("Christchurch Main Hub", "199 High Street, Christchurch Central, Canterbury 8011"),
            ("Riccarton Solar Farm", "67 Riccarton Road, Riccarton, Canterbury 8041"),
            ("Shirley Storage Facility", "45 Shirley Road, Shirley, Canterbury 8013"),
            ("Hornby Battery Station", "23 Main South Road, Hornby, Canterbury 8042"),
            ("Timaru Grid Hub", "101 Stafford Street, Timaru, Canterbury 7910")
        ],
        [
            ("Hamilton Energy Center", "234 Victoria Street, Hamilton, Waikato 3204"),
            ("Tauranga Solar Array", "78 Cameron Road, Tauranga, Bay of Plenty 3110"),
            ("Rotorua Thermal Station", "45 Fenton Street, Rotorua, Bay of Plenty 3010"),
            ("New Plymouth Wind Farm", "12 Devon Street, New Plymouth, Taranaki 4310"),
            ("Palmerston North Hub", "67 The Square, Palmerston North, Manawatu 4410")
        ],
        [
            ("Dunedin Battery Center", "123 George Street, Dunedin, Otago 9016"),
            ("Queenstown Storage", "45 Shotover Street, Queenstown, Otago 9300"),
            ("Invercargill Grid Hub", "78 Dee Street, Invercargill, Southland 9810"),
            ("Nelson Solar Farm", "34 Trafalgar Street, Nelson, Nelson-Tasman 7010"),
            ("Napier Energy Station", "90 Marine Parade, Napier, Hawke's Bay 4110")
        ]
    ]
    
    # Device name templates
    device_types = ["BMS", "ESS", "Grid", "Solar", "Wind"]
    device_statuses = ["active", "active", "active", "inactive", "maintenance"]
    firmware_versions = ["1.0.0", "1.2.0", "2.0.0", "2.1.0", "3.0.0"]
    
    with get_session() as s:
        for client_idx, client_name in enumerate(client_names):
            # Create or get client
            client = s.query(Client).filter(Client.name == client_name).first()
            if not client:
                client = Client(name=client_name, num_sites=5, num_devices=25)
                s.add(client)
                s.flush()
                print(f"\n  Created client: {client_name} (ID: {client.id})")
            else:
                print(f"\n  Client already exists: {client_name} (ID: {client.id})")
            
            # Create 5 locations for this client
            for loc_idx, (nickname, address) in enumerate(location_templates[client_idx], 1):
                location = s.query(Location).filter(
                    Location.client_id == client.id,
                    Location.address == address
                ).first()
                
                if not location:
                    location = Location(
                        client_id=client.id,
                        nickname=nickname,
                        address=address
                    )
                    s.add(location)
                    s.flush()
                    print(f"    Created location: {nickname} - {address} (ID: {location.id})")
                else:
                    print(f"    Location already exists: {nickname} (ID: {location.id})")
                
                # Create 5 devices for this location
                for dev_idx in range(5):
                    device_name = f"{device_types[dev_idx]}-{client.id:02d}{loc_idx:02d}{dev_idx+1:02d}"
                    serial_number = f"SN-{client.id:02d}{loc_idx:02d}{dev_idx+1:03d}"
                    
                    device = s.query(Device).filter(Device.serial_number == serial_number).first()
                    
                    if not device:
                        device = Device(
                            location_id=location.id,
                            client_id=client.id,
                            name=device_name,
                            serial_number=serial_number,
                            firmware_version=firmware_versions[dev_idx],
                            status=device_statuses[dev_idx]
                        )
                        s.add(device)
                        s.flush()
                        print(f"      Created device: {device_name} (SN: {serial_number}, Status: {device_statuses[dev_idx]})")
                    else:
                        print(f"      Device already exists: {device_name} (SN: {serial_number})")
        
        try:
            s.flush()
            print("\nClients, locations, and devices seeded successfully!")
        except IntegrityError as e:
            s.rollback()
            print(f"\nError during seeding: {e.orig}")


def generate_sample_csv_data(num_rows: int = 100) -> str:
    """Generate sample battery CSV data"""
    import random
    from datetime import datetime, timedelta
    
    csv_content = "timestamp,voltage,current,temperature\n"
    
    base_time = datetime.now() - timedelta(hours=num_rows)
    base_voltage = 3.7
    base_current = 0.5
    base_temp = 25.0
    
    for i in range(num_rows):
        timestamp = base_time + timedelta(hours=i)
        
        # Add realistic variations
        voltage = base_voltage + random.uniform(-0.3, 0.3) + (i * 0.001)
        current = base_current + random.uniform(-0.2, 0.2)
        temperature = base_temp + random.uniform(-5, 5) + (i * 0.01)
        
        # Clamp values to realistic ranges
        voltage = max(3.0, min(4.2, voltage))
        current = max(0.0, min(2.0, current))
        temperature = max(15.0, min(45.0, temperature))
        
        csv_content += f"{timestamp.isoformat()},{voltage:.3f},{current:.3f},{temperature:.2f}\n"
    
    return csv_content


def create_csv_file(file_path: str, content: str) -> bool:
    """Create a CSV file with given content"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write content to file
        with open(file_path, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"      Error creating file {file_path}: {e}")
        return False


def seed_sample_telemetry() -> None:
    """Seed sample telemetry data for first few devices with actual CSV files"""
    print("\nSeeding sample telemetry data with CSV files...")
    
    with get_session() as s:
        # Get first 10 devices
        devices = s.query(Device).limit(10).all()
        
        if not devices:
            print("  No devices found. Skipping telemetry seeding.")
            return
        
        csv_created_count = 0
        
        for device in devices:
            # Check if telemetry already exists for this device
            existing = s.query(BatteryData).filter(
                BatteryData.device_id == device.id
            ).first()
            
            if existing:
                print(f"  Telemetry already exists for device: {device.name}")
                continue
            
            # Generate file path
            file_name = f"{device.serial_number}_sample.csv"
            file_directory = f"./data/uploads/telemetry/{device.client_id}/{device.location_id}/{device.id}/{file_name}"
            
            # Generate and create CSV file
            csv_content = generate_sample_csv_data(num_rows=100)
            if create_csv_file(file_directory, csv_content):
                csv_created_count += 1
                
                # Create database entry
                telemetry = BatteryData(
                    client_id=device.client_id,
                    location_id=device.location_id,
                    device_id=device.id,
                    file_name=file_name,
                    directory=file_directory
                )
                s.add(telemetry)
                print(f"  Created telemetry CSV and DB entry for: {device.name}")
                print(f"    File: {file_directory}")
            else:
                print(f"  Failed to create CSV for: {device.name}")
        
        try:
            s.flush()
            print(f"Sample telemetry data seeded ({csv_created_count} CSV files created).")
        except IntegrityError as e:
            s.rollback()
            print(f"Error seeding telemetry: {e.orig}")


def seed_manual_uploads() -> None:
    """Seed sample manual uploads with actual CSV files"""
    print("\nSeeding sample manual uploads with CSV files...")
    
    manual_uploads_data = [
        {
            "author": "Dr. Aroha Morehu",
            "notes": "Laboratory battery stress test - High temperature conditions at Auckland facility",
            "file_directory": "./data/uploads/manual/20250101/1_01012025.csv",
            "days_ago": 25
        },
        {
            "author": "Dr. James Chen",
            "notes": "Capacity degradation analysis - 1000 cycle test for Wellington grid storage",
            "file_directory": "./data/uploads/manual/20250105/2_05012025.csv",
            "days_ago": 20
        },
        {
            "author": "Dr. Sarah Williams",
            "notes": "Fast charging impact study - Multiple C-rates for Christchurch EV fleet",
            "file_directory": "./data/uploads/manual/20250110/3_10012025.csv",
            "days_ago": 15
        },
        {
            "author": "Dr. Raj Patel",
            "notes": "Temperature gradient analysis - Thermal imaging data from Hamilton solar farm",
            "file_directory": "./data/uploads/manual/20250115/4_15012025.csv",
            "days_ago": 10
        },
        {
            "author": "Dr. Emma Thompson",
            "notes": "State of Health estimation - Machine learning validation for Dunedin wind farm batteries",
            "file_directory": "./data/uploads/manual/20250120/5_20012025.csv",
            "days_ago": 5
        }
    ]
    
    csv_created_count = 0
    
    with get_session() as s:
        for upload_data in manual_uploads_data:
            existing = s.query(ManualUpload).filter(
                ManualUpload.file_directory == upload_data["file_directory"]
            ).first()
            
            if existing:
                print(f"  Manual upload already exists: {upload_data['author']}")
                continue
            
            # Generate CSV content with different characteristics for each researcher
            csv_content = generate_sample_csv_data(num_rows=150)
            
            # Create CSV file
            if create_csv_file(upload_data["file_directory"], csv_content):
                csv_created_count += 1
                
                # Create database entry
                recorded_date = datetime.now(timezone.utc) - timedelta(days=upload_data["days_ago"])
                
                manual = ManualUpload(
                    author=upload_data["author"],
                    recorded_date=recorded_date,
                    file_directory=upload_data["file_directory"],
                    notes=upload_data["notes"]
                )
                s.add(manual)
                print(f"  Created manual upload CSV and DB entry by: {upload_data['author']}")
                print(f"    File: {upload_data['file_directory']}")
            else:
                print(f"  Failed to create CSV for: {upload_data['author']}")
        
        try:
            s.flush()
            print(f"Manual uploads seeded ({csv_created_count} CSV files created).")
        except IntegrityError as e:
            s.rollback()
            print(f"Error seeding manual uploads: {e.orig}")


def print_summary() -> None:
    """Print summary of seeded data"""
    print("\n" + "="*70)
    print("DATABASE SEEDING SUMMARY")
    print("="*70)
    
    with get_session() as s:
        user_count = s.query(User).count()
        client_count = s.query(Client).count()
        location_count = s.query(Location).count()
        device_count = s.query(Device).count()
        telemetry_count = s.query(BatteryData).count()
        manual_count = s.query(ManualUpload).count()
        
        print(f"Users:              {user_count}")
        print(f"Clients:            {client_count}")
        print(f"Locations:          {location_count}")
        print(f"Devices:            {device_count}")
        print(f"Telemetry Files:    {telemetry_count}")
        print(f"Manual Uploads:     {manual_count}")
        print("="*70)
        
        # Show clients with their counts
        print("\nCLIENT BREAKDOWN:")
        print("-"*70)
        clients = s.query(Client).all()
        for client in clients:
            locations = s.query(Location).filter(Location.client_id == client.id).count()
            devices = s.query(Device).filter(Device.client_id == client.id).count()
            print(f"  {client.name}")
            print(f"    Locations: {locations} | Devices: {devices}")
        print("="*70)
    
    # Count actual CSV files created
    csv_file_count = 0
    for root, dirs, files in os.walk("./data/uploads"):
        csv_file_count += len([f for f in files if f.endswith('.csv')])
    
    print(f"\nTotal CSV files created: {csv_file_count}")
    print("="*70)


def main() -> None:
    """Main seeding function"""
    print("\n" + "="*70)
    print("BatteryIQ Database Seeding Script")
    print("="*70)
    
    create_schema()
    seed_users()
    seed_clients_locations_devices()
    seed_sample_telemetry()
    seed_manual_uploads()
    print_summary()
    
    print("\nAll seeding complete! Your database is ready to use.")
    print("\nDefault password for all users: password123")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()