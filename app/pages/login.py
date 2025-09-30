# ============================================
# FILE: app/pages/login.py
# ============================================
import streamlit as st
import time
from backend.auth import login_user
from app.utils.logging_utils import *

def render():
    """Render the login page"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-title">Welcome</div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col_b:
                back = st.form_submit_button("Back", use_container_width=True)
            
            if submit:
                if username and password:
                    try:
                        log_info(f"Login attempt for user: {username}", context="Authentication")
                        user = login_user(username, password)
                        if user:
                            st.session_state.username = user.username
                            st.session_state.user = user.username
                            st.session_state.role = user.role.value
                            st.session_state.user_id = user.id
                            st.session_state.page = 'dashboard'
                            log_info(f"Successful login for user: {username} (Role: {user.role.value})", context="Authentication")
                            st.success(f"Welcome, {user.username}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            log_warning(f"Failed login attempt for user: {username}", context="Authentication")
                            st.error("Invalid credentials. Please try again.")
                    except Exception as e:
                        log_error(f"Login error for user {username}: {str(e)}", context="Authentication")
                        st.error("An error occurred during login. Please try again.")
                else:
                    st.warning("Please enter both username and password.")
            
            if back:
                st.session_state.page = 'welcome'
                st.rerun()

            with st.expander("🔑 Demo Credentials"):
                st.markdown("""
                    Use the following demo credentials to log in:
                    
                    **Admin:** admin / password123  
                    **Scientist:** scientist / password123  
                    **Client:** client / password123  
                    **Guest:** guest / password123  
                    **Super Admin:** super_admin / password123
                """, unsafe_allow_html=True)