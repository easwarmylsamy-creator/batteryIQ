# User Management System

## Overview
The BatteryIQ platform uses a hybrid storage system for user data:
- **Database (SQLite)**: Core authentication data (username, email, password, role)
- **JSON Files**: Extended profile information (name, phone, designation, etc.)

## User Roles

### Admin
- Full system access
- Can create/manage all users
- Access to all client data

### Scientist
- Research data access
- Can upload manual datasets
- Access to analysis tools

### Client
- View own organization's data
- Limited to assigned devices/locations
- Can see plant in-charge contact info

### Guest
- Limited read-only access
- Can view flagged public datasets only

### Super Admin
- Complete system control
- Database access
- All admin privileges plus system configuration

## Adding a New User

### Via Admin Dashboard
1. Login as Admin or Super Admin
2. Navigate to Dashboard → Manage → Users
3. Click "Add New User" tab
4. Fill in required fields:
   - First Name *
   - Last Name *
   - Email Address *
   - Username *
   - Password * (minimum 8 characters)
   - Role *
   - Phone (optional)
5. For Client role, also provide:
   - Designation * (job title)
   - Department (optional)
   - Assigned Location (optional)
6. Click "Create User"

### Required Fields by Role
| Field | Admin | Scientist | Client | Guest |
|-------|-------|-----------|--------|-------|
| First Name | ✓ | ✓ | ✓ | ✓ |
| Last Name | ✓ | ✓ | ✓ | ✓ |
| Email | ✓ | ✓ | ✓ | ✓ |
| Username | ✓ | ✓ | ✓ | ✓ |
| Password | ✓ | ✓ | ✓ | ✓ |
| Phone | - | - | - | - |
| Designation | - | - | ✓ | - |
| Department | - | - | - | - |
| Location | - | - | - | - |

## User Profile Storage

### Database Schema (users table)
```sql
- id: INTEGER (primary key)
- username: VARCHAR(50) (unique)
- email: VARCHAR(255) (unique)
- hashed_password: VARCHAR(255)
- role: ENUM
- created_at: DATETIME
- updated_at: DATETIME