import streamlit as st
import time
from backend.auth import login_user , testMode# For testing without password hashing
from app.utils.logging_utils import *

def render():
    """Render the login page"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-title">Test Login</div>', unsafe_allow_html=True)

    option = st.selectbox(
        "Select the role to login as:",
    ("admin", "scientist", "client", "guest", "super_admin"),
    )
    submit = st.button("Login", use_container_width=True, type="secondary")


    if submit:
        try:
            log_info(f"Test Login", context="Test Authentication")
            username = option
            password = "test"  # Dummy password for testing
            user = testMode(username, password)
            if user:
                st.session_state.username = user.username
                st.session_state.user = user.username
                st.session_state.role = user.role.value
                st.session_state.user_id = user.id
                st.session_state.page = 'dashboard'
                log_info(f" Successful login for user: {username} (Role: {user.role.value})", context="Authentication")
                st.success(f"Welcome, {user.username}!")
                time.sleep(0.5)
                st.rerun()
            else:
                log_warning(f"Failed login attempt for user: {username}", context="Authentication")
                st.error("Invalid credentials. Please try again.")
        except Exception as e:
            log_error(f"Login error for user {username}: {str(e)}", context="Authentication")
            st.error("An error occurred during login. Please try again.")