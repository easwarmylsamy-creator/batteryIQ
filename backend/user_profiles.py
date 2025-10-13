# backend/user_profiles.py
"""
User Profile Management System
Handles extended user information stored in JSON files
"""
from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

# Configuration
PROFILES_DIR = os.path.join(os.getcwd(), "data", "user_profiles")


def ensure_profiles_directory():
    """Ensure the profiles directory exists"""
    os.makedirs(PROFILES_DIR, exist_ok=True)


def get_profile_path(user_id: int) -> str:
    """Get the file path for a user's profile"""
    return os.path.join(PROFILES_DIR, f"{user_id}.json")


def create_user_profile(user_id: int, profile_data: Dict) -> Dict:
    """
    Create a new user profile
    
    Args:
        user_id: Database user ID
        profile_data: Dictionary containing profile information
        
    Returns:
        Created profile data
    """
    try:
        ensure_profiles_directory()
        
        # Build profile structure
        profile = {
            "user_id": user_id,
            "first_name": profile_data.get("first_name", ""),
            "last_name": profile_data.get("last_name", ""),
            "phone": profile_data.get("phone", ""),
            "client_id": profile_data.get("client_id"),  # For client role
            "designation": profile_data.get("designation", ""),  # For client role
            "department": profile_data.get("department", ""),
            "location_id": profile_data.get("location_id"),
            "created_by": profile_data.get("created_by"),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to file
        profile_path = get_profile_path(user_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created profile for user {user_id}")
        return profile
        
    except Exception as e:
        logger.error(f"Error creating profile for user {user_id}: {str(e)}")
        raise


def get_user_profile(user_id: int) -> Optional[Dict]:
    """
    Get a user's profile
    
    Args:
        user_id: Database user ID
        
    Returns:
        Profile data or None if not found
    """
    try:
        profile_path = get_profile_path(user_id)
        
        if not os.path.exists(profile_path):
            logger.warning(f"Profile not found for user {user_id}")
            return None
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        
        return profile
        
    except Exception as e:
        logger.error(f"Error reading profile for user {user_id}: {str(e)}")
        return None


def update_user_profile(user_id: int, profile_data: Dict) -> Optional[Dict]:
    """
    Update an existing user profile
    
    Args:
        user_id: Database user ID
        profile_data: Dictionary containing updated profile information
        
    Returns:
        Updated profile data or None if not found
    """
    try:
        existing_profile = get_user_profile(user_id)
        
        if not existing_profile:
            logger.error(f"Cannot update - profile not found for user {user_id}")
            return None
        
        # Update fields
        existing_profile.update({
            "first_name": profile_data.get("first_name", existing_profile.get("first_name")),
            "last_name": profile_data.get("last_name", existing_profile.get("last_name")),
            "phone": profile_data.get("phone", existing_profile.get("phone")),
            "designation": profile_data.get("designation", existing_profile.get("designation")),
            "department": profile_data.get("department", existing_profile.get("department")),
            "location_id": profile_data.get("location_id", existing_profile.get("location_id")),
            "last_updated": datetime.now().isoformat()
        })
        
        # Save updated profile
        profile_path = get_profile_path(user_id)
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(existing_profile, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Updated profile for user {user_id}")
        return existing_profile
        
    except Exception as e:
        logger.error(f"Error updating profile for user {user_id}: {str(e)}")
        raise


def delete_user_profile(user_id: int) -> bool:
    """
    Delete a user's profile
    
    Args:
        user_id: Database user ID
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        profile_path = get_profile_path(user_id)
        
        if not os.path.exists(profile_path):
            logger.warning(f"Profile not found for deletion: user {user_id}")
            return False
        
        os.remove(profile_path)
        logger.info(f"Deleted profile for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
        return False


def get_all_profiles() -> List[Dict]:
    """
    Get all user profiles
    
    Returns:
        List of all profile dictionaries
    """
    try:
        ensure_profiles_directory()
        profiles = []
        
        for filename in os.listdir(PROFILES_DIR):
            if filename.endswith('.json'):
                try:
                    user_id = int(filename.replace('.json', ''))
                    profile = get_user_profile(user_id)
                    if profile:
                        profiles.append(profile)
                except ValueError:
                    logger.warning(f"Invalid profile filename: {filename}")
                    continue
        
        return profiles
        
    except Exception as e:
        logger.error(f"Error getting all profiles: {str(e)}")
        return []


def validate_profile_data(role: str, profile_data: Dict) -> Dict:
    """
    Validate profile data based on role
    
    Args:
        role: User role (admin, scientist, client, guest, super_admin)
        profile_data: Profile data to validate
        
    Returns:
        Dictionary with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Required fields for all roles
    if not profile_data.get("first_name"):
        errors.append("First name is required")
    
    if not profile_data.get("last_name"):
        errors.append("Last name is required")
    
    # Phone format validation (optional but if provided must be valid)
    phone = profile_data.get("phone", "")
    if phone:
        # Basic NZ phone validation
        phone_clean = phone.replace(" ", "").replace("-", "")
        if not (phone_clean.startswith("+64") or phone_clean.startswith("0")):
            errors.append("Phone must start with +64 or 0")
        if not any(char.isdigit() for char in phone_clean):
            errors.append("Phone must contain digits")
    
    # Role-specific validation
    if role == "client":
        if not profile_data.get("designation"):
            errors.append("Designation is required for client role")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def search_profiles(query: str) -> List[Dict]:
    """
    Search profiles by name, designation, or department
    
    Args:
        query: Search query string
        
    Returns:
        List of matching profiles
    """
    try:
        all_profiles = get_all_profiles()
        query_lower = query.lower()
        
        matching_profiles = []
        
        for profile in all_profiles:
            if (query_lower in profile.get("first_name", "").lower() or
                query_lower in profile.get("last_name", "").lower() or
                query_lower in profile.get("designation", "").lower() or
                query_lower in profile.get("department", "").lower()):
                matching_profiles.append(profile)
        
        return matching_profiles
        
    except Exception as e:
        logger.error(f"Error searching profiles: {str(e)}")
        return []


def get_client_incharge_info(location_id: int) -> Optional[Dict]:
    """
    Get in-charge information for a specific location
    Used by client dashboard to show plant in-charge details
    
    Args:
        location_id: Location ID
        
    Returns:
        Profile of in-charge or None
    """
    try:
        from backend import services
        
        # Get all users with client role at this location
        all_profiles = get_all_profiles()
        
        for profile in all_profiles:
            if profile.get("location_id") == location_id:
                # Get user from database to check role
                user = services.get_user_by_id(profile["user_id"])
                if user and user.role.value == "client":
                    # Add email from user object
                    profile["email"] = user.email
                    return profile
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting in-charge info for location {location_id}: {str(e)}")
        return None