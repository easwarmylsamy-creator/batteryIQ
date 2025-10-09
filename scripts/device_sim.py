"""
CLI Telemetry Upload Tool
Interactive command-line interface for uploading telemetry data
Allows selection of client, location, and device from database
"""
import os
import sys
import requests
from datetime import datetime

# Add project root to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from db.session import get_session
from db.models import Client, Location, Device
from backend import services

# Configuration
TELEMETRY_URL = "http://localhost:8080/telemetry/upload"
HEALTH_URL = "http://localhost:8080/health"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}! {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_service_status():
    """Check if telemetry service is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Telemetry service is running")
            print(f"  Uptime: {data['uptime_seconds']:.2f} seconds")
            print(f"  Total uploads: {data['total_uploads']}")
            return True
        else:
            print_error("Telemetry service returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to telemetry service on port 8080")
        print_info("Make sure the service is running: python backend/telemetry_service.py")
        return False
    except Exception as e:
        print_error(f"Error checking service: {str(e)}")
        return False


def get_all_clients():
    """Get all clients from database"""
    try:
        clients = services.get_clients()
        return clients
    except Exception as e:
        print_error(f"Error loading clients: {str(e)}")
        return []


def get_locations_for_client(client_id):
    """Get locations for a specific client"""
    try:
        locations = services.get_locations_by_client(client_id)
        return locations
    except Exception as e:
        print_error(f"Error loading locations: {str(e)}")
        return []


def get_devices_for_location(location_id):
    """Get devices for a specific location"""
    try:
        devices = services.get_devices_by_location(location_id)
        return devices
    except Exception as e:
        print_error(f"Error loading devices: {str(e)}")
        return []


def display_selection_menu(items, item_type, display_func):
    """
    Display a selection menu for items
    
    Args:
        items: List of items to display
        item_type: Type of item (for display)
        display_func: Function to format item display
    
    Returns:
        Selected item or None
    """
    if not items:
        print_warning(f"No {item_type}s found")
        return None
    
    print(f"\n{Colors.BOLD}Available {item_type}s:{Colors.END}")
    print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
    
    for idx, item in enumerate(items, 1):
        print(f"  {Colors.BOLD}[{idx}]{Colors.END} {display_func(item)}")
    
    print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select {item_type} (1-{len(items)}) or 0 to cancel: {Colors.END}")
            choice = int(choice)
            
            if choice == 0:
                print_warning("Selection cancelled")
                return None
            
            if 1 <= choice <= len(items):
                selected = items[choice - 1]
                print_success(f"Selected: {display_func(selected)}")
                return selected
            else:
                print_error(f"Please enter a number between 1 and {len(items)}")
        
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n")
            print_warning("Selection cancelled")
            return None


def select_client():
    """Interactive client selection"""
    clients = get_all_clients()
    
    if not clients:
        print_error("No clients found in database")
        return None
    
    return display_selection_menu(
        clients,
        "Client",
        lambda c: f"{c.name} (ID: {c.id})"
    )


def select_location(client):
    """Interactive location selection"""
    locations = get_locations_for_client(client.id)
    
    if not locations:
        print_error(f"No locations found for client '{client.name}'")
        return None
    
    return display_selection_menu(
        locations,
        "Location",
        lambda l: f"{l.address} (ID: {l.id})"
    )


def select_device(location):
    """Interactive device selection"""
    devices = get_devices_for_location(location.id)
    
    if not devices:
        print_error(f"No devices found for this location")
        return None
    
    return display_selection_menu(
        devices,
        "Device",
        lambda d: f"{d.name} - Serial: {d.serial_number} - Status: {d.status or 'Active'} (ID: {d.id})"
    )


def select_file():
    """Interactive file selection"""
    print(f"\n{Colors.BOLD}File Selection:{Colors.END}")
    
    while True:
        file_path = input(f"{Colors.BOLD}Enter CSV file path (or 'cancel' to abort): {Colors.END}").strip()
        
        if file_path.lower() == 'cancel':
            print_warning("File selection cancelled")
            return None
        
        # Remove quotes if present
        file_path = file_path.strip('"').strip("'")
        
        if not os.path.exists(file_path):
            print_error(f"File not found: {file_path}")
            continue
        
        if not os.path.isfile(file_path):
            print_error(f"Path is not a file: {file_path}")
            continue
        
        if not file_path.endswith('.csv'):
            print_error("File must be a CSV file (.csv extension)")
            continue
        
        file_size = os.path.getsize(file_path)
        print_success(f"Selected file: {os.path.basename(file_path)}")
        print(f"  Path: {file_path}")
        print(f"  Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        
        return file_path


def upload_telemetry(file_path, client, location, device):
    """Upload telemetry file to service"""
    print(f"\n{Colors.BOLD}Uploading telemetry data...{Colors.END}")
    
    try:
        # Prepare headers
        headers = {
            'X-Device-Serial': device.serial_number,
            'X-Client-ID': str(client.id),
            'X-Location-ID': str(location.id),
            'X-Device-ID': str(device.id)
        }
        
        # Prepare file
        with open(file_path, 'rb') as f:
            files = {
                'file': (os.path.basename(file_path), f, 'text/csv')
            }
            
            # Display upload info
            print(f"\n{Colors.CYAN}Upload Details:{Colors.END}")
            print(f"  Client: {client.name} (ID: {client.id})")
            print(f"  Location: {location.address} (ID: {location.id})")
            print(f"  Device: {device.name} - {device.serial_number} (ID: {device.id})")
            print(f"  File: {os.path.basename(file_path)}")
            print(f"\n{Colors.YELLOW}Sending request...{Colors.END}")
            
            # Send request
            response = requests.post(
                TELEMETRY_URL,
                headers=headers,
                files=files,
                timeout=60
            )
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}UPLOAD SUCCESSFUL{Colors.END}")
            print(f"{Colors.GREEN}{Colors.BOLD}{'='*70}{Colors.END}\n")
            
            print(f"{Colors.BOLD}Response Details:{Colors.END}")
            print(f"  Message: {result['message']}")
            print(f"  File ID: {result.get('file_id')}")
            print(f"  Filename: {result.get('filename')}")
            print(f"  Path: {result.get('file_path')}")
            
            if 'validation_info' in result:
                val_info = result['validation_info']
                print(f"\n{Colors.BOLD}Validation Info:{Colors.END}")
                print(f"  Row count: {val_info.get('row_count')}")
                print(f"  File size: {val_info.get('file_size'):,} bytes")
                print(f"  Encoding: {val_info.get('encoding')}")
                
                if val_info.get('warnings'):
                    print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.END}")
                    for warning in val_info['warnings']:
                        print(f"  - {warning}")
            
            return True
        
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}{'='*70}{Colors.END}")
            print(f"{Colors.RED}{Colors.BOLD}UPLOAD FAILED{Colors.END}")
            print(f"{Colors.RED}{Colors.BOLD}{'='*70}{Colors.END}\n")
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("\nCannot connect to telemetry service")
        print_info("Make sure the service is running on port 8080")
        return False
    
    except Exception as e:
        print_error(f"\nUpload error: {str(e)}")
        return False


def confirm_upload(client, location, device, file_path):
    """Ask user to confirm upload details"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}Please confirm upload details:{Colors.END}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}\n")
    
    print(f"  Client:   {Colors.BOLD}{client.name}{Colors.END} (ID: {client.id})")
    print(f"  Location: {Colors.BOLD}{location.address}{Colors.END} (ID: {location.id})")
    print(f"  Device:   {Colors.BOLD}{device.name} - {device.serial_number}{Colors.END} (ID: {device.id})")
    print(f"  File:     {Colors.BOLD}{os.path.basename(file_path)}{Colors.END}")
    print(f"  Path:     {file_path}")
    
    print()
    
    while True:
        confirm = input(f"{Colors.BOLD}Proceed with upload? (yes/no): {Colors.END}").strip().lower()
        
        if confirm in ['yes', 'y']:
            return True
        elif confirm in ['no', 'n']:
            print_warning("Upload cancelled by user")
            return False
        else:
            print_error("Please enter 'yes' or 'no'")


def main():
    """Main CLI program"""
    print_header("BatteryIQ Telemetry Upload Tool")
    
    # Check service
    print_info("Checking telemetry service status...")
    if not check_service_status():
        print_error("\nCannot proceed without telemetry service running")
        return 1
    
    # Selection process
    print_header("Step 1: Select Client")
    client = select_client()
    if not client:
        return 1
    
    print_header("Step 2: Select Location")
    location = select_location(client)
    if not location:
        return 1
    
    print_header("Step 3: Select Device")
    device = select_device(location)
    if not device:
        return 1
    
    print_header("Step 4: Select File")
    file_path = select_file()
    if not file_path:
        return 1
    
    # Confirm
    print_header("Step 5: Confirm Upload")
    if not confirm_upload(client, location, device, file_path):
        return 1
    
    # Upload
    print_header("Step 6: Upload")
    success = upload_telemetry(file_path, client, location, device)
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}Process completed successfully!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Upload failed. Check logs for details.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Program interrupted by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)