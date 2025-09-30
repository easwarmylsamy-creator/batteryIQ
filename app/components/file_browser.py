# ============================================
# FILE: app/components/file_browser.py
# ============================================
import streamlit as st
import pandas as pd
from backend import services
from utils.cache_utils import get_cached_clients
from app.utils.logging_utils import *

def render_file_browser():
    """Render file browsing interface"""
    st.markdown("### 🗄️ Data Repository")
    
    tab1, tab2 = st.tabs(["Telemetry Data (Auto-Collected)", "Manual Uploads (Lab Data)"])
    
    with tab1:
        st.markdown("#### Automatic Telemetry Collection")
        st.info("This data is automatically collected from connected battery devices via backend services.")
        
        try:
            log_info("Loading telemetry file browser", context="File Browser")
            clients = get_cached_clients()
            
            if clients:
                client_filter = st.selectbox(
                    "Filter by Client",
                    ["All Clients"] + [f"{c.name} (ID: {c.id})" for c in clients],
                    key="telemetry_client_filter"
                )
                
                all_files = []
                for client in clients:
                    if client_filter == "All Clients" or client.name in client_filter:
                        try:
                            files = services.get_files_by_client(client.id)
                            for file in files:
                                try:
                                    device = services.get_device(file.device_id) if file.device_id else None
                                except Exception as e:
                                    log_error(f"Error getting device {file.device_id}: {str(e)}", context="File Browser")
                                    device = None
                                
                                all_files.append({
                                    "File Name": file.file_name,
                                    "Client": client.name,
                                    "Device": device.name if device else f"Device {file.device_id}",
                                    "Location ID": file.location_id,
                                    "File Path": file.directory
                                })
                        except Exception as e:
                            log_error(f"Error loading files for client {client.id}: {str(e)}", context="File Browser")
                            continue
                
                if all_files:
                    df = pd.DataFrame(all_files)
                    st.dataframe(df, use_container_width=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Files", len(all_files))
                    with col2:
                        unique_clients = len(set([f["Client"] for f in all_files]))
                        st.metric("Clients", unique_clients)
                    with col3:
                        unique_devices = len(set([f["Device"] for f in all_files]))
                        st.metric("Devices", unique_devices)
                    
                    log_info(f"Displayed {len(all_files)} telemetry files", context="File Browser")
                else:
                    st.info("No telemetry data collected yet.")
            else:
                st.info("No clients configured.")
        
        except Exception as e:
            log_error(f"Error in telemetry file browser: {str(e)}", context="File Browser")
            st.error("Error loading telemetry files. Please check logs.")
    
    with tab2:
        st.markdown("#### Manual Laboratory Uploads")
        st.info("This data is manually uploaded by researchers through the upload interface.")
        
        try:
            log_info("Loading manual uploads browser", context="File Browser")
            manual_files = services.get_manual_uploads()
            
            if manual_files:
                manual_data = []
                for file in manual_files:
                    manual_data.append({
                        "Author": file.author,
                        "Upload Date": file.recorded_date.strftime("%Y-%m-%d %H:%M"),
                        "Description": (file.notes[:60] + "...") if file.notes and len(file.notes) > 60 else (file.notes or "No description"),
                        "File Path": file.file_directory
                    })
                
                df = pd.DataFrame(manual_data)
                st.dataframe(df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Manual Uploads", len(manual_files))
                with col2:
                    unique_authors = len(set([f["Author"] for f in manual_data]))
                    st.metric("Contributors", unique_authors)
                
                log_info(f"Displayed {len(manual_files)} manual uploads", context="File Browser")
            else:
                st.info("No manual uploads yet.")
        
        except Exception as e:
            log_error(f"Error in manual uploads browser: {str(e)}", context="File Browser")
            st.error("Error loading manual uploads. Please check logs.")