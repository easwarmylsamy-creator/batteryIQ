# scripts/db_editor.py
"""
Manual Database Editor for BatteryIQ
Allows direct manipulation of database records via command line
"""
from __future__ import annotations

import os
import sys
from typing import Optional, Dict, Any

# Setup path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from db.session import get_session
from db.models import User, Client, Location, Device, BatteryData, ManualUpload, Metrics, UserRole
from sqlalchemy.exc import SQLAlchemyError

# Map table names to model classes
TABLE_MAP = {
    'user': User,
    'users': User,
    'client': Client,
    'clients': Client,
    'location': Location,
    'locations': Location,
    'device': Device,
    'devices': Device,
    'telemetry': BatteryData,
    'battery_data': BatteryData,
    'manual_upload': ManualUpload,
    'manual_uploads': ManualUpload,
    'metrics': Metrics,
}


def update_record(table_name: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a database record
    
    Args:
        table_name: Name of the table
        record_id: ID of the record to update
        updates: Dictionary of column names and new values
        
    Returns:
        Dictionary with operation result
    """
    result = {
        'success': False,
        'message': '',
        'record': None
    }
    
    # Get model class
    model = TABLE_MAP.get(table_name.lower())
    if not model:
        result['message'] = f"Table '{table_name}' not found. Available tables: {', '.join(set(TABLE_MAP.keys()))}"
        return result
    
    try:
        with get_session() as session:
            # Get the record
            record = session.query(model).filter(model.id == record_id).first()
            
            if not record:
                result['message'] = f"Record with ID {record_id} not found in table '{table_name}'"
                return result
            
            # Update fields
            updated_fields = []
            for column, value in updates.items():
                if not hasattr(record, column):
                    result['message'] = f"Column '{column}' does not exist in table '{table_name}'"
                    return result
                
                # Special handling for UserRole enum
                if column == 'role' and isinstance(record, User):
                    if isinstance(value, str):
                        try:
                            value = UserRole[value]
                        except KeyError:
                            result['message'] = f"Invalid role '{value}'. Valid roles: {', '.join([r.name for r in UserRole])}"
                            return result
                
                setattr(record, column, value)
                updated_fields.append(f"{column}={value}")
            
            session.flush()
            
            result['success'] = True
            result['message'] = f"Successfully updated {table_name} ID {record_id}: {', '.join(updated_fields)}"
            result['record'] = record
            
    except SQLAlchemyError as e:
        result['message'] = f"Database error: {str(e)}"
    except Exception as e:
        result['message'] = f"Error: {str(e)}"
    
    return result


def delete_record(table_name: str, record_id: int, force: bool = False) -> Dict[str, Any]:
    """
    Delete a database record
    
    Args:
        table_name: Name of the table
        record_id: ID of the record to delete
        force: Skip confirmation if True
        
    Returns:
        Dictionary with operation result
    """
    result = {
        'success': False,
        'message': '',
        'deleted': None
    }
    
    # Get model class
    model = TABLE_MAP.get(table_name.lower())
    if not model:
        result['message'] = f"Table '{table_name}' not found. Available tables: {', '.join(set(TABLE_MAP.keys()))}"
        return result
    
    try:
        with get_session() as session:
            # Get the record
            record = session.query(model).filter(model.id == record_id).first()
            
            if not record:
                result['message'] = f"Record with ID {record_id} not found in table '{table_name}'"
                return result
            
            # Store record info before deletion
            record_info = str(record)
            
            # Delete the record
            session.delete(record)
            session.flush()
            
            result['success'] = True
            result['message'] = f"Successfully deleted {table_name} ID {record_id}"
            result['deleted'] = record_info
            
    except SQLAlchemyError as e:
        result['message'] = f"Database error: {str(e)}"
    except Exception as e:
        result['message'] = f"Error: {str(e)}"
    
    return result


def view_record(table_name: str, record_id: int) -> Dict[str, Any]:
    """
    View a database record
    
    Args:
        table_name: Name of the table
        record_id: ID of the record to view
        
    Returns:
        Dictionary with record data
    """
    result = {
        'success': False,
        'message': '',
        'record': None,
        'data': {}
    }
    
    # Get model class
    model = TABLE_MAP.get(table_name.lower())
    if not model:
        result['message'] = f"Table '{table_name}' not found. Available tables: {', '.join(set(TABLE_MAP.keys()))}"
        return result
    
    try:
        with get_session() as session:
            record = session.query(model).filter(model.id == record_id).first()
            
            if not record:
                result['message'] = f"Record with ID {record_id} not found in table '{table_name}'"
                return result
            
            # Get all column values
            data = {}
            for column in record.__table__.columns:
                value = getattr(record, column.name)
                # Handle enum types
                if hasattr(value, 'value'):
                    value = value.value
                data[column.name] = value
            
            result['success'] = True
            result['message'] = f"Found record in {table_name}"
            result['record'] = record
            result['data'] = data
            
    except SQLAlchemyError as e:
        result['message'] = f"Database error: {str(e)}"
    except Exception as e:
        result['message'] = f"Error: {str(e)}"
    
    return result


def list_records(table_name: str, limit: int = 10) -> Dict[str, Any]:
    """
    List records from a table
    
    Args:
        table_name: Name of the table
        limit: Maximum number of records to return
        
    Returns:
        Dictionary with list of records
    """
    result = {
        'success': False,
        'message': '',
        'records': [],
        'count': 0
    }
    
    # Get model class
    model = TABLE_MAP.get(table_name.lower())
    if not model:
        result['message'] = f"Table '{table_name}' not found. Available tables: {', '.join(set(TABLE_MAP.keys()))}"
        return result
    
    try:
        with get_session() as session:
            records = session.query(model).limit(limit).all()
            
            records_data = []
            for record in records:
                data = {}
                for column in record.__table__.columns:
                    value = getattr(record, column.name)
                    # Handle enum types
                    if hasattr(value, 'value'):
                        value = value.value
                    data[column.name] = value
                records_data.append(data)
            
            result['success'] = True
            result['message'] = f"Found {len(records)} records in {table_name}"
            result['records'] = records_data
            result['count'] = len(records)
            
    except SQLAlchemyError as e:
        result['message'] = f"Database error: {str(e)}"
    except Exception as e:
        result['message'] = f"Error: {str(e)}"
    
    return result


# ====================
# CLI Interface
# ====================

def print_header():
    """Print CLI header"""
    print("\n" + "="*70)
    print("  ⚡ BatteryIQ Database Manual Editor")
    print("="*70)


def print_menu():
    """Print main menu"""
    print("\nAvailable Commands:")
    print("  1. update  - Update a record")
    print("  2. delete  - Delete a record")
    print("  3. view    - View a record")
    print("  4. list    - List records")
    print("  5. help    - Show detailed help")
    print("  6. exit    - Exit the program")


def interactive_update():
    """Interactive update flow"""
    print("\n" + "-"*70)
    print("UPDATE RECORD")
    print("-"*70)
    
    # Show available tables
    print("\nAvailable tables:")
    tables = sorted(set(TABLE_MAP.keys()))
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")
    
    table = input("\nEnter table name: ").strip()
    if not table:
        print("❌ Table name cannot be empty")
        return
    
    try:
        record_id = int(input("Enter record ID: ").strip())
    except ValueError:
        print("❌ Invalid ID (must be a number)")
        return
    
    # First, show the current record
    print("\nFetching current record...")
    result = view_record(table, record_id)
    
    if not result['success']:
        print(f"❌ {result['message']}")
        return
    
    print("\n📋 Current values:")
    for key, value in result['data'].items():
        print(f"  {key:20} : {value}")
    
    # Get updates
    print("\n📝 Enter updates (format: column=value, press Enter without input to finish):")
    print("   Example: username=admin")
    if table.lower() in ['user', 'users']:
        print("   For roles: role=admin, role=scientist, role=client, role=guest, role=super_admin")
    
    updates = {}
    while True:
        update_input = input("   Update: ").strip()
        if not update_input:
            break
        
        if '=' not in update_input:
            print("   ⚠️  Invalid format (use column=value)")
            continue
        
        column, value = update_input.split('=', 1)
        updates[column.strip()] = value.strip()
        print(f"   ✓ Added: {column}={value}")
    
    if not updates:
        print("❌ No updates provided")
        return
    
    # Confirm
    print("\n⚠️  Confirm updates:")
    for col, val in updates.items():
        print(f"  {col} = {val}")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Update cancelled")
        return
    
    # Execute update
    result = update_record(table, record_id, updates)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
    else:
        print(f"\n❌ {result['message']}")


def interactive_delete():
    """Interactive delete flow"""
    print("\n" + "-"*70)
    print("DELETE RECORD")
    print("-"*70)
    
    # Show available tables
    print("\nAvailable tables:")
    tables = sorted(set(TABLE_MAP.keys()))
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")
    
    table = input("\nEnter table name: ").strip()
    if not table:
        print("❌ Table name cannot be empty")
        return
    
    try:
        record_id = int(input("Enter record ID to delete: ").strip())
    except ValueError:
        print("❌ Invalid ID (must be a number)")
        return
    
    # Show the record first
    print("\nFetching record...")
    result = view_record(table, record_id)
    
    if not result['success']:
        print(f"❌ {result['message']}")
        return
    
    print("\n⚠️  You are about to DELETE this record:")
    print("-"*70)
    for key, value in result['data'].items():
        print(f"  {key:20} : {value}")
    print("-"*70)
    
    confirm = input("\n⚠️  Type 'DELETE' to confirm: ").strip()
    if confirm != 'DELETE':
        print("❌ Deletion cancelled")
        return
    
    # Execute delete
    result = delete_record(table, record_id)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
    else:
        print(f"\n❌ {result['message']}")


def interactive_view():
    """Interactive view flow"""
    print("\n" + "-"*70)
    print("VIEW RECORD")
    print("-"*70)
    
    # Show available tables
    print("\nAvailable tables:")
    tables = sorted(set(TABLE_MAP.keys()))
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")
    
    table = input("\nEnter table name: ").strip()
    if not table:
        print("❌ Table name cannot be empty")
        return
    
    try:
        record_id = int(input("Enter record ID: ").strip())
    except ValueError:
        print("❌ Invalid ID (must be a number)")
        return
    
    result = view_record(table, record_id)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print("\n" + "="*70)
        print(f"Table: {table.upper()}")
        print("="*70)
        for key, value in result['data'].items():
            print(f"{key:20} : {value}")
        print("="*70)
    else:
        print(f"\n❌ {result['message']}")


def interactive_list():
    """Interactive list flow"""
    print("\n" + "-"*70)
    print("LIST RECORDS")
    print("-"*70)
    
    # Show available tables
    print("\nAvailable tables:")
    tables = sorted(set(TABLE_MAP.keys()))
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")
    
    table = input("\nEnter table name: ").strip()
    if not table:
        print("❌ Table name cannot be empty")
        return
    
    limit_input = input("Enter limit (default 10, press Enter to skip): ").strip()
    limit = 10
    if limit_input:
        try:
            limit = int(limit_input)
        except ValueError:
            print("⚠️  Invalid limit, using default (10)")
    
    result = list_records(table, limit)
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print("\n" + "="*70)
        print(f"Table: {table.upper()} (showing up to {limit} records)")
        print("="*70 + "\n")
        
        for i, record in enumerate(result['records'], 1):
            print(f"📄 Record #{i}:")
            for key, value in record.items():
                print(f"  {key:20} : {value}")
            print()
        
        if result['count'] == limit:
            print(f"⚠️  Showing only first {limit} records. Rerun with higher limit to see more.")
        print("="*70)
    else:
        print(f"\n❌ {result['message']}")


def show_help():
    """Show detailed help"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║               BatteryIQ Database Manual Editor                   ║
║                        HELP GUIDE                                ║
╚══════════════════════════════════════════════════════════════════╝

INTERACTIVE MODE:
-----------------
Just run: python scripts/db_editor.py
Then follow the on-screen prompts!

COMMAND LINE MODE:
------------------

1. UPDATE RECORD
   python scripts/db_editor.py update <table> <id> <column>=<value> ...
   
   Examples:
   python scripts/db_editor.py update user 2 username=admin
   python scripts/db_editor.py update user 2 username=admin email=admin@local
   python scripts/db_editor.py update device 1 status=inactive

2. DELETE RECORD
   python scripts/db_editor.py delete <table> <id>
   
   Examples:
   python scripts/db_editor.py delete user 2
   python scripts/db_editor.py delete device 5

3. VIEW RECORD
   python scripts/db_editor.py view <table> <id>
   
   Examples:
   python scripts/db_editor.py view user 2
   python scripts/db_editor.py view client 1

4. LIST RECORDS
   python scripts/db_editor.py list <table> [limit]
   
   Examples:
   python scripts/db_editor.py list users
   python scripts/db_editor.py list devices 20

AVAILABLE TABLES:
-----------------
- users, user
- clients, client
- locations, location
- devices, device
- telemetry, battery_data
- manual_uploads, manual_upload
- metrics

SPECIAL NOTES:
--------------
✓ For user roles: admin, scientist, client, guest, super_admin
✓ IDs must be integers
✓ String values with spaces should be in quotes: "John Doe"
✓ Interactive mode has built-in safeguards and confirmations

TIPS:
-----
→ Use interactive mode for safety (with confirmations)
→ Use command line mode for automation/scripts
→ Always backup your database before bulk operations!

═══════════════════════════════════════════════════════════════════
""")


def interactive_mode():
    """Main interactive CLI loop"""
    print_header()
    print("\n🎯 Interactive Mode - Follow the prompts for safe operations")
    
    while True:
        print_menu()
        choice = input("\nEnter command (1-6): ").strip().lower()
        
        if choice in ['1', 'update']:
            interactive_update()
        elif choice in ['2', 'delete']:
            interactive_delete()
        elif choice in ['3', 'view']:
            interactive_view()
        elif choice in ['4', 'list']:
            interactive_list()
        elif choice in ['5', 'help']:
            show_help()
        elif choice in ['6', 'exit', 'quit', 'q']:
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-6 or a command name.")
        
        input("\nPress Enter to continue...")


def command_line_mode():
    """Command line argument mode"""
    command = sys.argv[1].lower()
    
    if command in ['help', '--help', '-h']:
        show_help()
        return
    
    try:
        if command == 'update':
            if len(sys.argv) < 5:
                print("❌ Error: UPDATE requires table, id, and at least one column=value pair")
                print("Usage: python scripts/db_editor.py update <table> <id> <column>=<value> ...")
                return
            
            table = sys.argv[2]
            record_id = int(sys.argv[3])
            
            # Parse column=value pairs
            updates = {}
            for arg in sys.argv[4:]:
                if '=' not in arg:
                    print(f"⚠️  Warning: Skipping invalid argument '{arg}' (must be column=value)")
                    continue
                column, value = arg.split('=', 1)
                updates[column] = value
            
            if not updates:
                print("❌ Error: No valid column=value pairs provided")
                return
            
            result = update_record(table, record_id, updates)
            print(f"\n✅ {result['message']}" if result['success'] else f"\n❌ {result['message']}")
        
        elif command == 'delete':
            if len(sys.argv) < 4:
                print("❌ Error: DELETE requires table and id")
                print("Usage: python scripts/db_editor.py delete <table> <id>")
                return
            
            table = sys.argv[2]
            record_id = int(sys.argv[3])
            
            # No confirmation in command line mode - add --force flag if needed
            print(f"⚠️  Deleting {table} ID {record_id}...")
            result = delete_record(table, record_id)
            
            if result['success']:
                print(f"✅ {result['message']}")
            else:
                print(f"❌ {result['message']}")
        
        elif command == 'view':
            if len(sys.argv) < 4:
                print("❌ Error: VIEW requires table and id")
                print("Usage: python scripts/db_editor.py view <table> <id>")
                return
            
            table = sys.argv[2]
            record_id = int(sys.argv[3])
            
            result = view_record(table, record_id)
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"\n{'='*70}")
                print(f"Table: {table.upper()}")
                print(f"{'='*70}")
                for key, value in result['data'].items():
                    print(f"{key:20} : {value}")
                print(f"{'='*70}\n")
            else:
                print(f"❌ {result['message']}")
        
        elif command == 'list':
            if len(sys.argv) < 3:
                print("❌ Error: LIST requires table name")
                print("Usage: python scripts/db_editor.py list <table> [limit]")
                return
            
            table = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            
            result = list_records(table, limit)
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"\n{'='*70}")
                print(f"Table: {table.upper()} (showing up to {limit} records)")
                print(f"{'='*70}\n")
                
                for i, record in enumerate(result['records'], 1):
                    print(f"📄 Record #{i}:")
                    for key, value in record.items():
                        print(f"  {key:18} : {value}")
                    print()
                
                if result['count'] == limit:
                    print(f"⚠️  Showing only first {limit} records.")
                print(f"{'='*70}\n")
            else:
                print(f"❌ {result['message']}")
        
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python scripts/db_editor.py help' for usage information")
    
    except ValueError:
        print("❌ Error: Invalid ID (must be an integer)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Main entry point - detect mode"""
    if len(sys.argv) < 2:
        # No arguments - run interactive mode
        interactive_mode()
    else:
        # Arguments provided - run command line mode
        command_line_mode()


if __name__ == "__main__":
    main()