# ============================================
# FILE: app/components/management.py
# ============================================
import streamlit as st
import pandas as pd
import plotly.express as px
from backend import services
from utils.cache_utils import get_cached_clients, get_cached_devices, get_cached_locations, get_system_stats
from app.utils.logging_utils import *
from app.components.user_management import render_user_management_interface

def render_management_interface():
    """Render management interface"""
    st.markdown("### System Management")
    
    # UPDATED: Back to 4 tabs, removed "Add Client Setup"
    mgmt_tab1, mgmt_tab2, mgmt_tab3, mgmt_tab4 = st.tabs([
        "Clients", 
        "Devices", 
        "Statistics", 
        "Users"
    ])
    
    with mgmt_tab1:
        render_client_management()
    
    with mgmt_tab2:
        render_device_management()
    
    with mgmt_tab3:
        render_statistics()
    
    with mgmt_tab4:
        render_user_management_interface()


def render_client_management():
    """Render client management interface"""
    st.markdown("#### Client Management")
    
    with st.spinner("Loading clients..."):
        try:
            clients = get_cached_clients()
            
            if clients:
                client_data = []
                for client in clients:
                    devices = get_cached_devices(client.id)
                    locations = get_cached_locations(client.id)
                    
                    client_data.append({
                        "ID": client.id,
                        "Name": client.name,
                        "Locations": len(locations),
                        "Devices": len(devices)
                    })
                
                df = pd.DataFrame(client_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No clients found.")
        
        except Exception as e:
            st.error(f"Error loading clients: {e}")
    


def render_device_management():
    """Render device management interface"""
    st.markdown("#### Device Management")
    
    try:
        clients = get_cached_clients()
        
        if clients:
            selected_client = st.selectbox(
                "Select Client to View Devices",
                clients,
                format_func=lambda x: f"{x.name} (ID: {x.id})"
            )
            
            if selected_client:
                devices = get_cached_devices(selected_client.id)
                
                if devices:
                    device_data = []
                    for device in devices:
                        device_data.append({
                            "ID": device.id,
                            "Name": device.name,
                            "Serial": device.serial_number,
                            "Status": device.status or "Active",
                            "Firmware": device.firmware_version or "N/A"
                        })
                    
                    df = pd.DataFrame(device_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No devices found for this client.")
        else:
            st.info("No clients found. Please add a client first.")
    
    except Exception as e:
        st.error(f"Error loading devices: {e}")


def render_statistics():
    """Render system statistics"""
    st.markdown("#### System Statistics")
    
    try:
        stats = get_system_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Clients", stats.get('total_clients', 0))
            st.metric("Total Locations", stats.get('total_locations', 0))
        
        with col2:
            st.metric("Total Devices", stats.get('total_devices', 0))
            st.metric("Total Users", stats.get('total_users', 0))
        
        with col3:
            st.metric("Telemetry Files", stats.get('total_telemetry_files', 0))
            st.metric("Manual Uploads", stats.get('total_manual_uploads', 0))
        
        # Visualize client distribution
        clients = get_cached_clients()
        if clients:
            client_device_counts = []
            for client in clients:
                devices = get_cached_devices(client.id)
                client_device_counts.append({
                    'Client': client.name,
                    'Devices': len(devices)
                })
            
            if client_device_counts:
                df = pd.DataFrame(client_device_counts)
                fig = px.bar(df, x='Client', y='Devices',
                           title='Devices per Client',
                           labels={'Devices': 'Number of Devices'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(30,41,59,0.5)',
                    font_color='#94a3b8'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")