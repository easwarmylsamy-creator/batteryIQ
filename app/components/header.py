# ============================================
# FILE: app/components/header.py
# ============================================
import streamlit as st
from app.session import logout

def render_header():
    """Render dashboard header with user info and logout"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.image("./assets/logo1.png")
    
    with col2:
        role_display = st.session_state.role.title() if st.session_state.role else "User"
        st.markdown(f'<div class="user-badge">{st.session_state.username} ({role_display})</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()