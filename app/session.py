# ============================================
# FILE: app/session.py
# ============================================
import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'page': 'welcome',
        'user': None,
        'username': None,
        'role': None,
        'user_id': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def logout():
    """Logout user and clear session"""
    st.session_state.user = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.page = 'welcome'

