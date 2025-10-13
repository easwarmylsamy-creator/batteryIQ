import plotly.express as px
import streamlit as st

from app.components.data_gallery import render_data_gallery
from app.components.header import render_header
from app.components.management import render_management_interface
from app.components.telemetry_monitor import render_telemetry_monitor
from app.components.upload_form import render_upload_interface
from app.utils.cache_utils import get_cached_clients, get_system_stats
from app.utils.data_utils import generate_sample_battery_data
from app.utils.logging_utils import *


def render_admin_dashboard():
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
    
    # Initialize active tab
    if 'admin_active_tab' not in st.session_state:
        st.session_state.admin_active_tab = 'Overview'
    
    # Create navigation buttons
    tab_options = ["Overview", "Add Client", "Manage", "Datasets", "Telemetry Monitor", "Manual Upload"]
    
    # Use columns for horizontal layout
    cols = st.columns(len(tab_options))
    
    for idx, (col, tab_name) in enumerate(zip(cols, tab_options)):
        with col:
            is_active = st.session_state.admin_active_tab == tab_name
            button_type = "primary" if is_active else "secondary"
            
            if st.button(
                tab_name, 
                key=f"nav_btn_{tab_name}",
                use_container_width=True,
                type=button_type
            ):
                st.session_state.admin_active_tab = tab_name
                st.rerun()
    
    st.markdown("---")
    
    # Render content based on active tab
    active_tab = st.session_state.admin_active_tab
    
    if active_tab == "Overview":
        render_overview_content()
    
    elif active_tab == "Manage":
        render_management_interface()
    
    elif active_tab == "Datasets":
        render_data_gallery()
    
    elif active_tab == "Telemetry Monitor":
        render_telemetry_monitor()
    
    elif active_tab == "Manual Upload":
        render_upload_interface()
    
    elif active_tab == "Add Client":
        from app.components.client_onboarding import render_client_onboarding_wizard
        render_client_onboarding_wizard()

def render_overview_content():
    """Render overview tab content"""
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
