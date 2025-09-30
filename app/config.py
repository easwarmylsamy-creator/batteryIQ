# ============================================
# FILE: app/config.py
# ============================================
import streamlit as st

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="BatteryIQ",
        page_icon="assets\logo0.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )