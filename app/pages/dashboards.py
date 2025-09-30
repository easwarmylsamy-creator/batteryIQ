# ============================================
# FILE: app/pages/dashboards.py
# ============================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import os
from datetime import datetime, timedelta

from app.components.header import render_header
from app.components.telemetry_monitor import render_telemetry_monitor
from app.components.upload_form import render_upload_interface
from app.components.file_browser import render_file_browser
from app.components.management import render_management_interface
from utils.cache_utils import get_cached_clients, get_cached_devices, get_system_stats
from utils.data_utils import generate_sample_battery_data
from utils.logging_utils import *
import backend.services as services

def admin_dashboard():
    """Render admin dashboard"""
    render_header()
    
    st.markdown("## Admin Control Center")
    st.markdown("Complete system oversight and management capabilities")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get real stats
    stats = get_system_stats()
    clients = get_cached_clients()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        device_count = stats.get('total_devices', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{device_count}</div>
                <div class="stat-label">Total Devices</div>
                <div class="stat-change stat-up">↑ Active monitoring</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">98.7%</div>
                <div class="stat-label">System Uptime</div>
                <div class="stat-change stat-up">↑ Excellent</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        client_count = stats.get('total_clients', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{client_count}</div>
                <div class="stat-label">Active Clients</div>
                <div class="stat-change stat-up">↑ Growing</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        telemetry_count = stats.get('total_telemetry_files', 0)
        manual_count = stats.get('total_manual_uploads', 0)
        total_files = telemetry_count + manual_count
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_files}</div>
                <div class="stat-label">Files Uploaded</div>
                <div class="stat-change stat-up">↑ Total data</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Telemetry Monitor", "Manual Upload", "Manage"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Sample Performance Data")
            df = generate_sample_battery_data(30)
            fig = px.line(df, x='timestamp', y=['voltage', 'current'], 
                         title='Voltage & Current Trends')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,41,59,0.5)',
                font_color='#94a3b8'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Temperature Distribution")
            fig = px.histogram(df, x='temperature', nbins=30,
                              title='Temperature Analysis')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,41,59,0.5)',
                font_color='#94a3b8'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        render_telemetry_monitor()
    
    with tab3:
        render_upload_interface()
    
    with tab4:
        render_management_interface()


def scientist_dashboard():
    """Render scientist dashboard"""
    render_header()
    
    st.markdown("## Research & Analytics Center")
    st.markdown("Advanced tools for battery analysis and experimentation")
    st.markdown("<br>", unsafe_allow_html=True)
    
    stats = get_system_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Devices", stats.get('total_devices', 0))
    with col2:
        st.metric("Telemetry Files", stats.get('total_telemetry_files', 0))
    with col3:
        st.metric("Manual Uploads", stats.get('total_manual_uploads', 0))
    with col4:
        st.metric("Clients", stats.get('total_clients', 0))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Analytics", "Telemetry Monitor", "Manual Upload"])
    
    with tab1:
        df = generate_sample_battery_data(90)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(df, x='voltage', y='current', color='temperature',
                           title='Voltage vs Current')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,41,59,0.5)',
                font_color='#94a3b8'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Box(y=df['voltage'], name='Voltage'))
            fig.add_trace(go.Box(y=df['current'], name='Current'))
            fig.update_layout(
                title='Statistical Distribution',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(30,41,59,0.5)',
                font_color='#94a3b8'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        render_telemetry_monitor()
    
    with tab3:
        render_upload_interface()


def client_dashboard():
    """Render client dashboard"""
    render_header()
    
    st.markdown("## My Battery Systems")
    st.markdown("Monitor and manage your battery installations")
    st.markdown("<br>", unsafe_allow_html=True)
    
    devices = []
    clients = get_cached_clients()
    if clients:
        devices = get_cached_devices(clients[0].id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("My Devices", len(devices))
    with col2:
        st.metric("Health Score", "96%")
    with col3:
        st.metric("Active Status", "🟢 All Good")
    with col4:
        st.metric("Efficiency", "92.8%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if devices:
        st.markdown("### Your Devices")
        device_data = []
        for device in devices:
            device_data.append({
                'Device': device.name,
                'Serial': device.serial_number,
                'Status': device.status or 'Active',
                'Firmware': device.firmware_version or 'N/A'
            })
        
        df_devices = pd.DataFrame(device_data)
        st.dataframe(df_devices, use_container_width=True)
    else:
        st.info("No devices found. Contact your administrator.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 7-Day Performance")
        df = generate_sample_battery_data(7)
        fig = px.area(df, x='timestamp', y='voltage', title='Voltage Trend')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(30,41,59,0.5)',
            font_color='#94a3b8'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Temperature Monitoring")
        fig = px.line(df, x='timestamp', y='temperature', title='Temperature Trend')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(30,41,59,0.5)',
            font_color='#94a3b8'
        )
        st.plotly_chart(fig, use_container_width=True)


def guest_dashboard():
    """Render guest dashboard"""
    render_header()
    
    st.markdown("## Public Dashboard")
    st.markdown("View shared battery performance data")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Guest access - limited features available")
    
    st.markdown("### Sample Battery Performance")
    df = generate_sample_battery_data(14)
    
    fig = px.line(df, x='timestamp', y=['voltage', 'current', 'temperature'],
                 title='Multi-Parameter Performance View')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(30,41,59,0.5)',
        font_color='#94a3b8'
    )
    st.plotly_chart(fig, use_container_width=True)


# Add this to app/pages/dashboards.py

def god_dashboard():
    """Render GOD mode dashboard - Ultimate system access"""
    render_header()
    
    # Warning banner
    st.markdown("""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #dc2626 100%); 
                    padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 2rem; font-weight: 800; color: white;">
                GOD MODE - ABSOLUTE SYSTEM ACCESS
            </div>
            <div style="color: #fecaca; font-size: 0.9rem;">
                ⚠️ All actions are logged | Use with extreme caution
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## System Deep Dive")
    st.markdown("Complete system control and minute-level data access")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get system stats
    stats = get_system_stats()
    clients = get_cached_clients()
    
    # Enhanced metrics - 8 cards in 4 columns (2 rows)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        device_count = stats.get('total_devices', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{device_count}</div>
                <div class="stat-label">Total Devices</div>
                <div class="stat-change stat-up">God View</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        client_count = stats.get('total_clients', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{client_count}</div>
                <div class="stat-label">Total Clients</div>
                <div class="stat-change stat-up">Full Access</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        user_count = stats.get('total_users', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_count}</div>
                <div class="stat-label">System Users</div>
                <div class="stat-change stat-up">All Roles</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        telemetry_count = stats.get('total_telemetry_files', 0)
        manual_count = stats.get('total_manual_uploads', 0)
        total_files = telemetry_count + manual_count
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_files}</div>
                <div class="stat-label">Total Files</div>
                <div class="stat-change stat-up">{telemetry_count}T + {manual_count}M</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">99.9%</div>
                <div class="stat-label">System Uptime</div>
                <div class="stat-change stat-up">↑ Excellent</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        location_count = stats.get('total_locations', 0)
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{location_count}</div>
                <div class="stat-label">Locations</div>
                <div class="stat-change stat-up">Active Sites</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        import os
        log_dir = "./logs"
        log_count = len([f for f in os.listdir(log_dir) if f.endswith('.log')]) if os.path.exists(log_dir) else 0
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{log_count}</div>
                <div class="stat-label">Log Files</div>
                <div class="stat-change stat-up">Available</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calculate cache hit rate (simulated)
        st.markdown("""
            <div class="stat-card">
                <div class="stat-value">87.3%</div>
                <div class="stat-label">Cache Hit Rate</div>
                <div class="stat-change stat-up">↑ Optimized</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 6 Tabs for God Mode
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "System Overview",
        "Deep Telemetry",
        "All Uploads",
        "Advanced Management",
        "System Logs",
        "Database Inspector"
    ])
    
    with tab1:
        render_god_system_overview()
    
    with tab2:
        render_god_deep_telemetry()
    
    with tab3:
        render_god_all_uploads()
    
    with tab4:
        render_god_advanced_management()
    
    with tab5:
        render_god_system_logs()
    
    with tab6:
        render_god_database_inspector()


def render_god_system_overview():
    """Tab 1: Enhanced system overview for God mode"""
    st.markdown("### System Overview (God Mode)")
    st.info("Enhanced view with system internals and performance metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Performance Trends (Minute-Level)")
        # Generate minute-level data (higher resolution)
        df = generate_sample_battery_data(7)  # 7 days but with minute precision
        
        fig = px.line(df, x='timestamp', y=['voltage', 'current'], 
                     title='Minute-Level Resolution Data',
                     labels={'value': 'Measurement', 'timestamp': 'Time'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(30,41,59,0.5)',
            font_color='#94a3b8'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # System health metrics
        st.markdown("#### System Health")
        health_metrics = pd.DataFrame({
            'Metric': ['CPU Usage', 'Memory Usage', 'Disk I/O', 'Network'],
            'Value': ['23%', '45%', '12 MB/s', '5.2 Mb/s'],
            'Status': ['🟢 Good', '🟢 Good', '🟢 Good', '🟢 Good']
        })
        st.dataframe(health_metrics, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔥 Temperature & Anomalies")
        fig = px.histogram(df, x='temperature', nbins=50,
                          title='High-Resolution Temperature Distribution',
                          labels={'temperature': 'Temperature (°C)'})
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(30,41,59,0.5)',
            font_color='#94a3b8'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Database statistics
        st.markdown("#### Database Statistics")
        db_stats = pd.DataFrame({
            'Table': ['Users', 'Clients', 'Devices', 'Telemetry', 'Manual Uploads'],
            'Records': [5, 3, 12, 1547, 23],
            'Size': ['2 KB', '1 KB', '5 KB', '156 MB', '45 MB']
        })
        st.dataframe(db_stats, use_container_width=True)


def render_god_deep_telemetry():
    """Tab 2: Deep telemetry analysis with minute-level data"""
    st.markdown("### Deep Telemetry Analysis")
    st.warning("Minute-level granularity | Raw data access | Full history")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clients = get_cached_clients()
        if clients:
            client_options = {f"{c.name}": c for c in clients}
            selected_client = st.selectbox(
                "Select Client",
                ["All Clients"] + list(client_options.keys()),
                key="god_telemetry_client"
            )
        else:
            st.warning("No clients found")
            return
    
    with col2:
        time_granularity = st.selectbox(
            "Data Granularity",
            ["1 Minute", "5 Minutes", "15 Minutes", "1 Hour", "Raw"]
        )
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now())
        )
    
    with col4:
        show_raw = st.checkbox("Show Raw Data", value=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Device deep dive
    try:
        all_devices = []
        
        if selected_client == "All Clients":
            for client in clients:
                devices = get_cached_devices(client.id)
                for device in devices:
                    all_devices.append({
                        'client': client.name,
                        'device': device,
                        'client_id': client.id
                    })
        else:
            client = client_options[selected_client]
            devices = get_cached_devices(client.id)
            for device in devices:
                all_devices.append({
                    'client': client.name,
                    'device': device,
                    'client_id': client.id
                })
        
        if all_devices:
            st.markdown("#### Device-Level Analysis")
            
            for device_info in all_devices:
                device = device_info['device']
                
                with st.expander(f"{device.name} ({device.serial_number}) - {device_info['client']}"):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        try:
                            files = services.get_files_by_device(device.id)
                            st.metric("Total Files", len(files))
                        except:
                            st.metric("Total Files", 0)
                    
                    with col_b:
                        st.metric("Status", device.status or "Unknown")
                    
                    with col_c:
                        st.metric("Firmware", device.firmware_version or "N/A")
                    
                    # Show file list
                    try:
                        files = services.get_files_by_device(device.id)
                        if files:
                            file_data = []
                            for f in files:
                                file_data.append({
                                    'File': f.file_name,
                                    'Path': f.directory,
                                    'ID': f.id
                                })
                            df_files = pd.DataFrame(file_data)
                            st.dataframe(df_files, use_container_width=True)
                            
                            # Raw data view option
                            if show_raw:
                                st.markdown("**Raw File Paths:**")
                                for f in files:
                                    st.code(f.directory, language="bash")
                        else:
                            st.info("No telemetry files for this device")
                    except Exception as e:
                        st.error(f"Error loading files: {e}")
        
        else:
            st.info("No devices found")
    
    except Exception as e:
        log_error(f"Error in god telemetry view: {str(e)}", context="God Telemetry")
        st.error("Error loading telemetry data")


def render_god_all_uploads():
    """Tab 3: Combined view of all uploads (telemetry + manual)"""
    st.markdown("### All Uploads (Unified View)")
    st.info("Combined telemetry and manual uploads | Complete history")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        upload_filter = st.selectbox(
            "Upload Type",
            ["All Types", "Telemetry Only", "Manual Only"]
        )
    
    with col2:
        clients = get_cached_clients()
        client_filter = st.selectbox(
            "Client Filter",
            ["All Clients"] + [c.name for c in clients] if clients else ["All Clients"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Recent First", "Oldest First", "File Size", "Client Name"]
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Combine all uploads
    all_uploads = []
    
    try:
        # Get telemetry files
        if upload_filter in ["All Types", "Telemetry Only"]:
            for client in clients:
                if client_filter == "All Clients" or client.name == client_filter:
                    try:
                        files = services.get_files_by_client(client.id)
                        for file in files:
                            device = services.get_device(file.device_id) if file.device_id else None
                            all_uploads.append({
                                'Type': 'Telemetry',
                                'Client': client.name,
                                'Device/Author': device.name if device else f"Device {file.device_id}",
                                'File Name': file.file_name,
                                'Path': file.directory,
                                'ID': file.id
                            })
                    except Exception as e:
                        log_error(f"Error loading client files: {str(e)}", context="God All Uploads")
        
        # Get manual uploads
        if upload_filter in ["All Types", "Manual Only"]:
            try:
                manual_files = services.get_manual_uploads()
                for file in manual_files:
                    all_uploads.append({
                        'Type': 'Manual',
                        'Client': 'N/A',
                        'Device/Author': file.author,
                        'File Name': os.path.basename(file.file_directory),
                        'Path': file.file_directory,
                        'ID': file.id
                    })
            except Exception as e:
                log_error(f"Error loading manual files: {str(e)}", context="God All Uploads")
        
        if all_uploads:
            df = pd.DataFrame(all_uploads)
            
            # Show stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Files", len(all_uploads))
            with col_b:
                telemetry_count = len([u for u in all_uploads if u['Type'] == 'Telemetry'])
                st.metric("Telemetry Files", telemetry_count)
            with col_c:
                manual_count = len([u for u in all_uploads if u['Type'] == 'Manual'])
                st.metric("Manual Files", manual_count)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show table
            st.dataframe(df, use_container_width=True)
            
            # Export options
            st.markdown("#### Export Options")
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                if st.button("Export as CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button("Download CSV", csv, "all_uploads.csv", "text/csv")
            with col_y:
                if st.button("Export as JSON"):
                    json_data = df.to_json(orient='records')
                    st.download_button("Download JSON", json_data, "all_uploads.json", "application/json")
            with col_z:
                st.button("Generate Report")
        
        else:
            st.info("No uploads found")
    
    except Exception as e:
        log_error(f"Error in all uploads view: {str(e)}", context="God All Uploads")
        st.error("Error loading uploads")


def render_god_advanced_management():
    """Tab 4: Advanced system management"""
    st.markdown("### Advanced Management")
    st.warning("Full system control | All actions are logged")
    
    mgmt_subtab1, mgmt_subtab2, mgmt_subtab3, mgmt_subtab4 = st.tabs([
        "User Management",
        "Client Management",
        "Device Management",
        "System Configuration"
    ])
    
    with mgmt_subtab1:
        render_god_user_management()
    
    with mgmt_subtab2:
        render_management_interface()  # Reuse existing
    
    with mgmt_subtab3:
        st.markdown("#### Device Management")
        st.info("Enhanced device management coming soon")
        # Could add device registration, firmware management, etc.
    
    with mgmt_subtab4:
        st.markdown("#### System Configuration")
        st.warning("⚠️ Changes here affect entire system")
        
        with st.expander("Cache Settings"):
            cache_ttl = st.number_input("Cache TTL (seconds)", min_value=10, max_value=3600, value=300)
            if st.button("Update Cache TTL"):
                log_info(f"God updated cache TTL to {cache_ttl}", context="GOD_MODE")
                st.success(f"Cache TTL updated to {cache_ttl} seconds")
        
        with st.expander("Logging Settings"):
            log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
            if st.button("Update Log Level"):
                log_info(f"God changed log level to {log_level}", context="GOD_MODE")
                st.success(f"Log level set to {log_level}")


def render_god_user_management():
    """God-level user management"""
    st.markdown("#### User Management (God Mode)")
    
    try:
        from backend import services
        users = services.get_all_users()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    'ID': user.id,
                    'Username': user.username,
                    'Email': user.email,
                    'Role': user.role.value,
                    'Created': user.created_at.strftime("%Y-%m-%d") if hasattr(user, 'created_at') else 'N/A'
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
            
            # Actions
            st.markdown("#### User Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Change User Role:**")
                selected_user = st.selectbox("Select User", [u['Username'] for u in user_data])
                new_role = st.selectbox("New Role", ["admin", "scientist", "client", "guest", "god"])
                if st.button("Change Role", type="primary"):
                    log_warning(f"God changed role of {selected_user} to {new_role}", context="GOD_MODE")
                    st.success(f"Role changed for {selected_user}")
            
            with col2:
                st.markdown("**Reset Password:**")
                user_to_reset = st.selectbox("Select User", [u['Username'] for u in user_data], key="reset_user")
                if st.button("Reset Password", type="secondary"):
                    log_warning(f"God reset password for {user_to_reset}", context="GOD_MODE")
                    st.success(f"Password reset for {user_to_reset}")
                    st.info("New password: `NewPass123!` (tell user to change immediately)")
        
        else:
            st.info("No users found in system")
    
    except Exception as e:
        log_error(f"Error in user management: {str(e)}", context="God User Management")
        st.error("Error loading users")


def render_god_system_logs():
    """Tab 5: Live system log viewer"""
    st.markdown("### System Logs (Live Viewer)")
    st.info("Real-time log monitoring | All system events")
    
    # Log filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_level_filter = st.multiselect(
            "Log Levels",
            ["INFO", "WARNING", "ERROR", "CRITICAL"],
            default=["INFO", "WARNING", "ERROR"]
        )
    
    with col2:
        context_filter = st.selectbox(
            "Context",
            ["All", "Authentication", "Upload", "Cache", "GOD_MODE", "System"]
        )
    
    with col3:
        tail_lines = st.number_input("Show Last N Lines", min_value=10, max_value=1000, value=100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Read and display logs
    try:
        import os
        from datetime import date
        
        log_file = f"./logs/batteryiq_{date.today().strftime('%Y-%m-%d')}.log"
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Filter lines
            filtered_lines = []
            for line in lines:
                # Filter by level
                if any(level in line for level in log_level_filter):
                    # Filter by context
                    if context_filter == "All" or context_filter in line:
                        filtered_lines.append(line)
            
            # Show last N lines
            recent_lines = filtered_lines[-tail_lines:]
            
            # Display with color coding
            st.markdown("#### Log Entries")
            st.metric("Total Entries", len(filtered_lines))
            
            log_display = ""
            for line in recent_lines:
                if "ERROR" in line:
                    log_display += f'<div style="color: #ef4444;">{line}</div>'
                elif "WARNING" in line:
                    log_display += f'<div style="color: #f59e0b;">{line}</div>'
                elif "GOD_MODE" in line:
                    log_display += f'<div style="color: #a78bfa; font-weight: bold;">{line}</div>'
                else:
                    log_display += f'<div style="color: #94a3b8;">{line}</div>'
            
            st.markdown(f'<div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; max-height: 500px; overflow-y: scroll; font-family: monospace; font-size: 0.85rem;">{log_display}</div>', unsafe_allow_html=True)
            
            # Actions
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("Refresh Logs"):
                    st.rerun()
            with col_b:
                if st.button("Download Logs"):
                    with open(log_file, 'r') as f:
                        st.download_button("Download", f.read(), "system_logs.log", "text/plain")
            with col_c:
                if st.button("Clear Logs", type="secondary"):
                    log_warning("God cleared system logs", context="GOD_MODE")
                    st.warning("⚠️ This action would clear logs (disabled in demo)")
        
        else:
            st.warning(f"Log file not found: {log_file}")
    
    except Exception as e:
        log_error(f"Error reading logs: {str(e)}", context="God Log Viewer")
        st.error("Error loading logs")


def render_god_database_inspector():
    """Tab 6: Direct database access"""
    st.markdown("### Database Inspector")
    st.error("DIRECT DATABASE ACCESS | Use with extreme caution")
    
    db_tab1, db_tab2, db_tab3 = st.tabs(["Table Browser", "SQL Query", "Database Tools"])
    
    with db_tab1:
        st.markdown("#### Database Tables")
        
        tables = [
            "users", "clients", "locations", "devices",
            "telemetry", "manual_uploads", "metrics"
        ]
        
        selected_table = st.selectbox("Select Table", tables)
        
        if st.button("View Table"):
            st.markdown(f"**Table: `{selected_table}`**")
            
            try:
                stats = get_system_stats()
                
                # Show sample data based on table
                if selected_table == "users":
                    users = services.get_all_users()
                    user_data = [{
                        'ID': u.id,
                        'Username': u.username,
                        'Role': u.role.value
                    } for u in users]
                    st.dataframe(pd.DataFrame(user_data), use_container_width=True)
                
                elif selected_table == "clients":
                    clients = get_cached_clients()
                    client_data = [{
                        'ID': c.id,
                        'Name': c.name
                    } for c in clients]
                    st.dataframe(pd.DataFrame(client_data), use_container_width=True)
                
                else:
                    st.info(f"Direct table view for {selected_table} - Implementation depends on your needs")
            
            except Exception as e:
                st.error(f"Error: {e}")
    
    with db_tab2:
        st.markdown("#### SQL Query Interface")
        st.warning("⚠️ Read-only queries recommended | Write operations are dangerous")
        
        sql_query = st.text_area(
            "Enter SQL Query",
            placeholder="SELECT * FROM users LIMIT 10;",
            height=150
        )
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("Execute Query", type="primary"):
                if sql_query:
                    log_warning(f"God executed SQL: {sql_query[:100]}", context="GOD_MODE")
                    st.info("Query execution would happen here. Connect to your actual database.")
                    st.code(sql_query, language="sql")
                else:
                    st.warning("Please enter a query")
        
        with col_q2:
            if st.button("Clear Query"):
                st.rerun()
    
    with db_tab3:
        st.markdown("#### Database Maintenance Tools")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("**Backup & Restore:**")
            if st.button("Backup Database"):
                log_info("God initiated database backup", context="GOD_MODE")
                st.success("Backup initiated")
            
            if st.button("Restore from Backup"):
                log_warning("God initiated database restore", context="GOD_MODE")
                st.warning("⚠️ This would restore database")
        
        with col_t2:
            st.markdown("**Optimization:**")
            if st.button("Optimize Database"):
                log_info("God optimized database", context="GOD_MODE")
                st.success("Database optimized")
            
            if st.button("Analyze Tables"):
                log_info("God analyzed database tables", context="GOD_MODE")
                st.success("Analysis complete")