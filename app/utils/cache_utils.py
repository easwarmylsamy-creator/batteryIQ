# ============================================
# FILE: app/utils/cache_utils.py
# ============================================
import streamlit as st
from backend import services
from app.utils.logging_utils import *

@st.cache_data(ttl=300)
def get_cached_clients():
    """Get clients with caching and error logging"""
    try:
        log_info("Fetching clients from database", context="Cache")
        clients = services.get_clients()
        log_info(f"Successfully fetched {len(clients)} clients", context="Cache")
        return clients
    except Exception as e:
        log_error(f"Failed to fetch clients: {str(e)}", context="get_cached_clients")
        st.error("Error loading clients. Please check logs.")
        return []

@st.cache_data(ttl=300)
def get_cached_devices(client_id):
    """Get devices with caching and error logging"""
    try:
        log_info(f"Fetching devices for client {client_id}", context="Cache")
        devices = services.get_devices_by_client(client_id)
        log_info(f"Successfully fetched {len(devices)} devices", context="Cache")
        return devices
    except Exception as e:
        log_error(f"Failed to fetch devices for client {client_id}: {str(e)}", context="get_cached_devices")
        st.error("Error loading devices. Please check logs.")
        return []

@st.cache_data(ttl=300)
def get_cached_locations(client_id):
    """Get locations with caching and error logging"""
    try:
        log_info(f"Fetching locations for client {client_id}", context="Cache")
        locations = services.get_locations_by_client(client_id)
        log_info(f"Successfully fetched {len(locations)} locations", context="Cache")
        return locations
    except Exception as e:
        log_error(f"Failed to fetch locations for client {client_id}: {str(e)}", context="get_cached_locations")
        st.error("Error loading locations. Please check logs.")
        return []

@st.cache_data(ttl=60)
def get_system_stats():
    """Get system statistics with error logging"""
    try:
        log_info("Fetching system statistics", context="Cache")
        stats = services.get_system_overview()
        log_info("Successfully fetched system statistics", context="Cache")
        return stats
    except Exception as e:
        log_error(f"Failed to fetch system statistics: {str(e)}", context="get_system_stats")
        st.error("Error loading system statistics. Please check logs.")
        return {}