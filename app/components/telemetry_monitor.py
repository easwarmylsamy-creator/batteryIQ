# ============================================
# FILE: app/components/telemetry_monitor.py
# ============================================
import streamlit as st
import pandas as pd
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
    
    try:
        all_devices = []
        log_info("Loading telemetry monitor", context="Telemetry Monitor")
        
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
                                file_count = len(telemetry_files)
                            except Exception as e:
                                log_error(f"Error getting files for device {device.id}: {str(e)}", context="Telemetry Monitor")
                                file_count = 0
                            
                            status = device.status or "active"
                            status_emoji = "🟢" if status.lower() == "active" else "🟡"
                            
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                                        {status_emoji} {device.name}
                                    </div>
                                    <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">
                                        {device_info['client']}
                                    </div>
                                    <div style="color: #60a5fa; font-size: 1.2rem; margin: 0.5rem 0;">
                                        {file_count} data files
                                    </div>
                                    <div style="color: #94a3b8; font-size: 0.8rem;">
                                        Serial: {device.serial_number}<br>
                                        Firmware: {device.firmware_version or 'N/A'}
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
                    for file in files[-10:]:
                        all_telemetry.append({
                            'Device': device_info['device'].name,
                            'Client': device_info['client'],
                            'File Name': file.file_name,
                            'Location': file.directory
                        })
                
                if all_telemetry:
                    df = pd.DataFrame(all_telemetry)
                    st.dataframe(df, use_container_width=True)
                    st.info(f"Showing {len(all_telemetry)} most recent telemetry uploads")
                else:
                    st.info("No telemetry data available yet.")
            except Exception as e:
                log_error(f"Error loading recent telemetry: {str(e)}", context="Telemetry Monitor")
                st.error("Error loading recent telemetry data")
        
        else:
            st.info("No devices found matching the selected filters.")
    
    except Exception as e:
        log_error(f"Error in telemetry monitor: {str(e)}", context="Telemetry Monitor")
        st.error("Error loading telemetry data. Please check logs.")