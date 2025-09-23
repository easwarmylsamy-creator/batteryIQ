import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from backend import services

# List clients
clients = services.get_clients()
print(clients)

# Add new device
dev = services.create_device(client_id=1, location_id=1,
                             name="Test Device", serial="SN-9999")
print(dev)

# List files for a device
files = services.get_files_by_device(dev.id)
print("files-",files)

# Manual uploads
manuals = services.get_manual_uploads()
print(manuals)
