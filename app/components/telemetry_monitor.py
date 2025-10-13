# app/components/telemetry_monitor.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend import services
from utils.cache_utils import get_cached_clients, get_cached_devices
from app.utils.logging_utils import *

def render_telemetry_monitor():
    """Render telemetry monitoring interface"""
    st.markdown("### Live Telemetry Monitor")
    
    st.info("**Automatic Data Collection:** Telemetry data is automatically collected from connected devices via backend services.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.spinner("Loading clients..."):
            clients = get_cached_clients()
        if clients:
            client_options = {f"{c.name}": c for c in clients}
            selected_client_name = st.selectbox(
                "Filter by Client",
                ["All Clients"] + list(client_options.keys())
            )
        else:
            st.warning("No clients configured in the system.")
            return
    
    with col2:
        status_filter = st.selectbox(
            "Device Status",
            ["All Status", "Active", "Inactive", "Maintenance"]
        )
    
    with col3:
        time_range = st.selectbox(
            "Data Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Connected Devices")
    
    with st.spinner("Loading devices and telemetry data..."):
        try:
            all_devices = []
            log_info("Loading telemetry monitor", context="Telemetry Monitor")
            
            # Get devices based on client filter
            if selected_client_name == "All Clients":
                for client in clients:
                    devices = get_cached_devices(client.id)
                    for device in devices:
                        all_devices.append({
                            'client': client.name,
                            'device': device,
                            'client_id': client.id
                        })
            else:
                selected_client = client_options[selected_client_name]
                devices = get_cached_devices(selected_client.id)
                for device in devices:
                    all_devices.append({
                        'client': selected_client.name,
                        'device': device,
                        'client_id': selected_client.id
                    })
            
            # Apply device status filter
            if status_filter != "All Status":
                all_devices = filter_by_status(all_devices, status_filter)
                log_info(f"Applied status filter: {status_filter}, {len(all_devices)} devices match", context="Telemetry Monitor")
            
            if all_devices:
                # Create device cards
                cols_per_row = 3
                for i in range(0, len(all_devices), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        if i + j < len(all_devices):
                            device_info = all_devices[i + j]
                            device = device_info['device']
                            
                            with col:
                                try:
                                    telemetry_files = services.get_files_by_device(device.id)
                                    
                                    # Apply time range filter to files
                                    filtered_files = filter_by_time_range(telemetry_files, time_range)
                                    file_count = len(filtered_files)
                                except Exception as e:
                                    log_error(f"Error getting files for device {device.id}: {str(e)}", context="Telemetry Monitor")
                                    file_count = 0
                                
                                status = device.status or "active"
                                status_icon = get_status_icon(status)
                                
                                st.markdown(f"""
                                    <div class="stat-card">
                                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                                            {status_icon} {device.name}
                                        </div>
                                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">
                                            {device_info['client']}
                                        </div>
                                        <div style="color: #53CDA8; font-size: 1.2rem; margin: 0.5rem 0;">
                                            {file_count} data files
                                        </div>
                                        <div style="color: #94a3b8; font-size: 0.8rem;">
                                            Serial: {device.serial_number}<br>
                                            Firmware: {device.firmware_version or 'N/A'}<br>
                                            Status: {status.title()}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                
                # Recent telemetry
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Recent Telemetry Data")
                
                try:
                    all_telemetry = []
                    for device_info in all_devices:
                        files = services.get_files_by_device(device_info['device'].id)
                        
                        # Apply time range filter
                        filtered_files = filter_by_time_range(files, time_range)
                        
                        for file in filtered_files[-10:]:
                            all_telemetry.append({
                                'Device': device_info['device'].name,
                                'Client': device_info['client'],
                                'File Name': file.file_name,
                                'Location': file.directory,
                                'Status': device_info['device'].status or 'Active'
                            })
                    
                    if all_telemetry:
                        df = pd.DataFrame(all_telemetry)
                        st.dataframe(df, width='stretch')
                        
                        # Show filter summary
                        filter_info = []
                        if selected_client_name != "All Clients":
                            filter_info.append(f"Client: {selected_client_name}")
                        if status_filter != "All Status":
                            filter_info.append(f"Status: {status_filter}")
                        if time_range != "All Time":
                            filter_info.append(f"Range: {time_range}")
                        
                        filter_text = " | ".join(filter_info) if filter_info else "No filters applied"
                        st.info(f"Showing {len(all_telemetry)} telemetry uploads ({filter_text})")
                    else:
                        st.info("No telemetry data available matching the selected filters.")
                except Exception as e:
                    log_error(f"Error loading recent telemetry: {str(e)}", context="Telemetry Monitor")
                    st.error("Error loading recent telemetry data")
            
            else:
                st.info("No devices found matching the selected filters.")
        
        except Exception as e:
            log_error(f"Error in telemetry monitor: {str(e)}", context="Telemetry Monitor")
            st.error("Error loading telemetry data. Please check logs.")


def filter_by_status(devices_list, status_filter):
    """
    Filter devices by status
    
    Args:
        devices_list: List of device dictionaries
        status_filter: Status to filter by (Active, Inactive, Maintenance)
    
    Returns:
        Filtered list of devices
    """
    if status_filter == "All Status":
        return devices_list
    
    filtered = []
    for device_info in devices_list:
        device = device_info['device']
        device_status = (device.status or "active").lower()
        
        if status_filter.lower() == device_status:
            filtered.append(device_info)
    
    return filtered


def filter_by_time_range(files_list, time_range):
    """
    Filter files by time range based on file naming convention or creation time
    
    Args:
        files_list: List of BatteryData objects
        time_range: Time range filter (Last 24 Hours, Last 7 Days, etc.)
    
    Returns:
        Filtered list of files
    """
    if time_range == "All Time":
        return files_list
    
    # Calculate cutoff date
    now = datetime.now()
    if time_range == "Last 24 Hours":
        cutoff = now - timedelta(hours=24)
    elif time_range == "Last 7 Days":
        cutoff = now - timedelta(days=7)
    elif time_range == "Last 30 Days":
        cutoff = now - timedelta(days=30)
    else:
        return files_list
    
    filtered = []
    for file in files_list:
        try:
            # Try to extract date from filename
            # Expected format: {client_id}_{device_id}_{YYYYMMDD_HHMMSS}.csv
            filename = file.file_name
            parts = filename.split('_')
            
            if len(parts) >= 3:
                # Try to parse date from filename
                date_str = parts[2].replace('.csv', '')
                time_str = parts[3].replace('.csv', '') if len(parts) > 3 else '000000'
                
                try:
                    file_date = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    if file_date >= cutoff:
                        filtered.append(file)
                except ValueError:
                    # If date parsing fails, include the file
                    filtered.append(file)
            else:
                # If filename doesn't match expected format, include the file
                filtered.append(file)
                
        except Exception:
            # If any error occurs, include the file to avoid losing data
            filtered.append(file)
    
    return filtered


def get_status_icon(status):
    """
    Get appropriate icon for device status
    
    Args:
        status: Device status string
    
    Returns:
        Icon string
    """
    status_lower = status.lower()
    
    if status_lower == "active":
        return "🟢"
    elif status_lower == "inactive":
        return "🔴"
    elif status_lower == "maintenance":
        return "🟡"
    else:
        return "⚪"