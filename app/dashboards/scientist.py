import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.components.header import render_header
from app.utils.cache_utils import get_system_stats
from app.components.data_gallery import render_data_gallery
from app.components.telemetry_monitor import render_telemetry_monitor
from app.components.upload_form import render_upload_interface
from app.utils.data_utils import generate_sample_battery_data


def render_scientist_dashboard():
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["Analytics", "Datasets", "Telemetry Monitor", "Manual Upload"])
    
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
        render_data_gallery()

    with tab3:
        render_telemetry_monitor()
    
    with tab4:
        render_upload_interface()

