# ============================================
# FILE: app/main.py
# ============================================
import streamlit as st
import sys
import os

# Setup paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import modules
from app.config import setup_page_config
from app.styles import apply_custom_styles
from app.session import initialize_session_state
from app.pages import welcome, login,testLogin, dashboards
from app.utils.logging_utils import *

def main():
    """Main application entry point"""
    
    # Setup
    setup_page_config()
    apply_custom_styles()
    initialize_session_state()
    
    # Route to appropriate page
    page = st.session_state.page
    
    try:
        if page == 'welcome':
            welcome.render()
        
        elif page == 'login':
            login.render()
            # testLogin.render()
        
        elif page == 'dashboard':
            role = st.session_state.role
            log_info(f"User {st.session_state.username} accessing {role} dashboard", context="Navigation")
            
            if role == 'admin':
                dashboards.admin_dashboard()
            elif role == 'scientist':
                dashboards.scientist_dashboard()
            elif role == 'client':
                dashboards.client_dashboard()
            elif role == 'guest':
                dashboards.guest_dashboard()
            elif role == 'super_admin': 
                dashboards.super_admin_dashboard()
            else:
                log_error(f"Invalid role '{role}' for user {st.session_state.username}", context="Navigation")
                st.error("Invalid role. Please login again.")
                from app.session import logout
                logout()
                st.rerun()
        
        else:
            log_warning(f"Unknown page requested: {page}", context="Navigation")
            st.session_state.page = 'welcome'
            st.rerun()
    
    except Exception as e:
        log_error(f"Critical error in main router: {str(e)}", context="Main")
        st.error("A critical error occurred. Please refresh the page.")
        if st.session_state.get('debug_mode', False):
            st.exception(e)
    

if __name__ == "__main__":
    log_info("BatteryIQ application started", context="System")
    main()

