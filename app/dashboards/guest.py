import streamlit as st

from app.components.header import render_header
from app.components.upload_form import render_upload_interface
from app.components.data_gallery import render_data_gallery

def render_guest_dashboard():
    """Render guest dashboard"""
    render_header()
    st.markdown("## Public Dashboard")
    st.markdown("View shared battery performance data")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("Guest access - limited features available")
    
    tab1,tab2 = st.tabs(["Upload Datasets","Data Gallery"])
    with tab1:
        render_upload_interface()
    with tab2:
        render_data_gallery()

