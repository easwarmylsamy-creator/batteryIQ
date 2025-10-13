# app/components/user_management.py
import streamlit as st
import pandas as pd
import time
from passlib.hash import bcrypt
from backend import services

from app.utils.logging_utils import log_info, log_error, log_warning
from app.utils.cache_utils import get_cached_locations, get_cached_clients
from backend.services import  get_client

def render_user_management_interface():
    """Render user management interface for admins"""
    user_role = st.session_state.get('role', 'guest')
    
    # Access control
    if user_role not in ['admin', 'super_admin']:
        st.error("Access Denied: Only administrators can manage users")
        return
    
    st.markdown("#### User Management")
    
    user_tab1, user_tab2 = st.tabs(["Add New User", "Manage Users"])
    
    with user_tab1:
        render_add_user_form()
    
    with user_tab2:
        render_users_list()


def render_add_user_form():
    """Render form to add new user with dynamic field visibility"""
    st.markdown("##### Add New User")
    
    # Initialize session state for form fields if not exists
    if 'form_role' not in st.session_state:
        st.session_state.form_role = 'admin'
    if 'form_password' not in st.session_state:
        st.session_state.form_password = ''
    if 'form_confirm_password' not in st.session_state:
        st.session_state.form_confirm_password = ''
    
    # Use regular inputs (not form) for dynamic behavior
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input(
            "First Name",
            placeholder="Enter first name",
            help="User's first name",
            key="input_first_name"
        )
        if not first_name:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    with col2:
        last_name = st.text_input(
            "Last Name",
            placeholder="Enter last name",
            help="User's last name",
            key="input_last_name"
        )
        if not last_name:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        email = st.text_input(
            "Email Address",
            placeholder="user@example.com",
            help="Email address for login and notifications",
            key="input_email"
        )
        # Email validation
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Invalid email format</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    with col4:
        username = st.text_input(
            "Username",
            placeholder="username",
            help="Username for login",
            key="input_username"
        )
        if not username:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
        elif len(username) < 3:
            st.markdown('<p style="color: #f59e0b; font-size: 0.85rem; margin-top: -0.5rem;">Username should be at least 3 characters</p>', unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            help="Minimum 8 characters",
            key="input_password",
            on_change=lambda: setattr(st.session_state, 'form_password', st.session_state.input_password)
        )
        
        # Real-time password validation
        if password:
            password_strength = validate_password_strength(password)
            
            if len(password) < 8:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Password must be at least 8 characters</p>', unsafe_allow_html=True)
            else:
                # Show strength indicator
                if password_strength['score'] >= 3:
                    st.markdown(f'<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Strong password</p>', unsafe_allow_html=True)
                elif password_strength['score'] >= 2:
                    st.markdown(f'<p style="color: #f59e0b; font-size: 0.85rem; margin-top: -0.5rem;">Moderate password - consider adding numbers or symbols</p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Weak password - use mix of letters, numbers, and symbols</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    with col6:
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter password",
            key="input_confirm_password",
            on_change=lambda: setattr(st.session_state, 'form_confirm_password', st.session_state.input_confirm_password)
        )
        
        # Real-time password match validation
        if confirm_password:
            if password and confirm_password != password:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Passwords do not match</p>', unsafe_allow_html=True)
            elif confirm_password == password:
                st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Passwords match</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    col7, col8 = st.columns(2)
    
    with col7:
        # Role selector with callback
        role = st.selectbox(
            "User Role",
            ["admin", "scientist", "client", "guest"],
            help="Select user role and permissions",
            key="input_role",
            on_change=lambda: setattr(st.session_state, 'form_role', st.session_state.input_role)
        )
        if not role:
            st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
    
    with col8:
        phone = st.text_input(
            "Phone Number",
            placeholder="+64-21-XXX-XXXX",
            help="Contact phone number (optional)",
            key="input_phone"
        )
        
        # Phone validation
        if phone:
            phone_validation = validate_phone_number(phone)
            if not phone_validation['valid']:
                st.markdown(f'<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">{phone_validation["message"]}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Valid phone number</p>', unsafe_allow_html=True)
    
    # Dynamic role-specific fields
    designation = None
    department = None
    location_id = None
    selected_client_id = None
    
    if st.session_state.input_role == "client":
        st.markdown("---")
        st.markdown("##### Client-Specific Information")
        
        col9, col10 = st.columns(2)
        
        with col9:
            designation = st.text_input(
                "Designation",
                placeholder="e.g., Plant Technician",
                help="Job title/designation (required for client role)",
                key="input_designation"
            )
            if not designation:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required for client role</p>', unsafe_allow_html=True)
        
        with col10:
            department = st.text_input(
                "Department",
                placeholder="e.g., Operations",
                help="Department name (optional)",
                key="input_department"
            )
        
        # Client and Location selection
        col11, col12 = st.columns(2)
        
        with col11:
            try:
                clients = get_cached_clients()
                if clients:
                    client_options = {f"{client.name}": client.id for client in clients}
                    selected_client_name = st.selectbox(
                        "Assign to Client",
                        ["Select Client"] + list(client_options.keys()),
                        help="Select which client organization this user belongs to",
                        key="input_client"
                    )
                    
                    if selected_client_name != "Select Client":
                        selected_client_id = client_options[selected_client_name]
                    else:
                        st.markdown('<p style="color: #f59e0b; font-size: 0.85rem; margin-top: -0.5rem;">Please select a client</p>', unsafe_allow_html=True)
                else:
                    st.warning("No clients available. Please create a client first.")
            except Exception as e:
                log_error(f"Error loading clients: {str(e)}", context="User Management")
                st.error("Error loading clients")
        
        with col12:
            # Location dropdown - only show if client is selected
            if selected_client_id:
                try:
                    locations = get_cached_locations(selected_client_id)
                    if locations:
                        location_options = {f"{loc.nickname}": loc.id for loc in locations}
                        selected_location_name = st.selectbox(
                            "Assign to Location",
                            ["Select Location"] + list(location_options.keys()),
                            help="Assign user to a specific location",
                            key="input_location"
                        )
                        
                        if selected_location_name != "Select Location":
                            location_id = location_options[selected_location_name]
                        else:
                            st.markdown('<p style="color: #f59e0b; font-size: 0.85rem; margin-top: -0.5rem;">Please select a location</p>', unsafe_allow_html=True)
                    else:
                        st.info(f"No locations available for this client")
                except Exception as e:
                    log_error(f"Error loading locations: {str(e)}", context="User Management")
                    st.error("Error loading locations")
            else:
                st.selectbox(
                    "Assign to Location",
                    ["Select Client First"],
                    disabled=True,
                    help="Select a client first to see available locations",
                    key="input_location_disabled"
                )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Action buttons
    col_submit, col_reset = st.columns([1, 1])
    
    with col_submit:
        submit_button = st.button("Create User", type="secondary", use_container_width=True, key="btn_submit")
    
    with col_reset:
        reset_button = st.button("Reset Form", use_container_width=True, key="btn_reset")
    
    # Handle reset
    if reset_button:
        # Clear all session state form fields
        for key in list(st.session_state.keys()):
            if key.startswith('input_'):
                del st.session_state[key]
        st.session_state.form_role = 'admin'
        st.session_state.form_password = ''
        st.session_state.form_confirm_password = ''
        st.rerun()
    
    # Handle submit
    if submit_button:
        # Final validation
        errors = []
        
        if not all([first_name, last_name, email, username, password, confirm_password, role]):
            errors.append("Please fill in all required fields")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if "@" not in email or "." not in email.split("@")[-1]:
            errors.append("Invalid email address format")
        
        if len(username) < 3:
            errors.append("Username must be at least 3 characters")
        
        # Phone validation
        if phone:
            phone_validation = validate_phone_number(phone)
            if not phone_validation['valid']:
                errors.append(f"Phone: {phone_validation['message']}")
        
        # Role-specific validation
        if role == "client":
            if not designation:
                errors.append("Designation is required for client role")
            if not selected_client_id:
                errors.append("Please select a client organization")
            if not location_id:
                errors.append("Please select a location for the client")
        
        if errors:
            st.error("Please fix the following errors:")
            for error in errors:
                st.markdown(f"- {error}")
        else:
            # Create user
            try:
                with st.spinner("Creating user..."):
                    # Check if username or email already exists
                    existing_user_by_username = services.get_user_by_username(username)
                    if existing_user_by_username:
                        st.error(f"Username '{username}' is already taken. Please choose a different username.")
                        return
                    
                    # Hash password
                    hashed_password = bcrypt.hash(password)
                    
                    # Get current admin ID
                    admin_id = st.session_state.get('user_id')
                    
                    # Prepare profile data
                    profile_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone": phone,
                        "client_id": selected_client_id,
                        "designation": designation or "",
                        "department": department or "",
                        "location_id": location_id
                    }
                    
                    # Create user with profile
                    result = services.create_user_with_profile(
                        username=username,
                        email=email,
                        hashed_password=hashed_password,
                        role=role,
                        profile_data=profile_data,
                        created_by=admin_id
                    )
                    
                    if result["success"]:
                        log_info(
                            f"Admin {st.session_state.username} created user: {username} ({role})",
                            context="User Management"
                        )
                        st.success(f"User '{username}' created successfully!")
                        st.balloons()
                        
                        # Clear form
                        for key in list(st.session_state.keys()):
                            if key.startswith('input_'):
                                del st.session_state[key]
                        
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to create user")
            
            except Exception as e:
                log_error(f"Error creating user: {str(e)}", context="User Management")
                if "UNIQUE constraint failed" in str(e):
                    if "email" in str(e):
                        st.error(f"Email '{email}' is already registered. Please use a different email.")
                    elif "username" in str(e):
                        st.error(f"Username '{username}' is already taken. Please choose a different username.")
                    else:
                        st.error("This user already exists in the system.")
                else:
                    st.error(f"Error creating user: {str(e)}")


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    
    Returns:
        dict with 'score' (0-4) and 'feedback'
    """
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Complexity checks
    if any(c.isupper() for c in password):
        score += 1
    
    if any(c.isdigit() for c in password):
        score += 1
    
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 1
    
    # Feedback
    if score <= 1:
        feedback.append("Very weak - add length and variety")
    elif score == 2:
        feedback.append("Weak - consider adding numbers or symbols")
    elif score == 3:
        feedback.append("Moderate - good password")
    else:
        feedback.append("Strong password!")
    
    return {
        "score": min(score, 4),
        "feedback": feedback
    }


def validate_phone_number(phone: str) -> dict:
    """
    Validate phone number format
    
    Returns:
        dict with 'valid' boolean and 'message'
    """
    # Remove spaces and dashes
    phone_clean = phone.replace(" ", "").replace("-", "")
    
    # Check if it has digits
    if not any(char.isdigit() for char in phone_clean):
        return {
            "valid": False,
            "message": "Phone must contain digits"
        }
    
    # Check NZ format
    if not (phone_clean.startswith("+64") or phone_clean.startswith("0")):
        return {
            "valid": False,
            "message": "Phone must start with +64 or 0 (NZ format)"
        }
    
    # Check minimum length
    digits_only = ''.join(filter(str.isdigit, phone_clean))
    if len(digits_only) < 9:
        return {
            "valid": False,
            "message": "Phone number too short"
        }
    
    return {
        "valid": True,
        "message": "Valid phone number"
    }

def render_users_list():
    """Render list of all users with management options"""
    st.markdown("##### Manage Existing Users")
    
    try:
        with st.spinner("Loading users..."):
            users_with_profiles = services.get_all_users_with_profiles()
        
        if not users_with_profiles:
            st.info("No users found in the system")
            return
        
        # Prepare data for display
        user_data = []
        
        for item in users_with_profiles:
            user = item["user"]
            profile = item["profile"]
            
            full_name = "N/A"
            designation = "N/A"
            phone = "N/A"
            
            if profile:
                first_name = profile.get("first_name", "")
                last_name = profile.get("last_name", "")
                full_name = f"{first_name} {last_name}".strip() or "N/A"
                designation = profile.get("designation", "N/A")
                phone = profile.get("phone", "N/A")
            
            user_data.append({
                "ID": user.id,
                "Full Name": full_name,
                "Username": user.username,
                "Email": user.email,
                "Role": user.role.value.title(),
                "Designation": designation,
                "Phone": phone
            })
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(users_with_profiles))
        
        with col2:
            admin_count = len([u for u in user_data if u["Role"].lower() == "admin"])
            st.metric("Admins", admin_count)
        
        with col3:
            scientist_count = len([u for u in user_data if u["Role"].lower() == "scientist"])
            st.metric("Scientists", scientist_count)
        
        with col4:
            client_count = len([u for u in user_data if u["Role"].lower() == "client"])
            st.metric("Clients", client_count)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display table
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # User management actions
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### User Actions")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            # Create user selection dictionary
            user_options = {
                f"{u['Full Name']} ({u['Username']})": u['ID'] 
                for u in user_data
            }
            
            selected_user_display = st.selectbox(
                "Select User",
                list(user_options.keys()),
                key="manage_user_select"
            )
            selected_user_id = user_options[selected_user_display]
        
        with col_b:
            if st.button("View Details", type="secondary", use_container_width=True):
                show_user_details_dialog(selected_user_id)
        
        with col_c:
            if st.button("Edit User", type="secondary", use_container_width=True):
                st.session_state.edit_user_id = selected_user_id
                st.rerun()
        
        with col_d:
            if st.button("Delete User", type="secondary", use_container_width=True):
                confirm_delete_user(selected_user_id)
        
        # Show edit form if user is selected for editing
        if 'edit_user_id' in st.session_state:
            st.markdown("---")
            render_edit_user_form(st.session_state.edit_user_id)
    
    except Exception as e:
        log_error(f"Error loading users list: {str(e)}", context="User Management")
        st.error("Error loading users. Please check logs.")

def render_user_details_card(user, profile):
    """Render detailed user information card"""
    full_name = "Unknown User"
    
    if profile:
        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or user.username
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid rgba(148, 163, 184, 0.2);
        ">
            <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-bottom: 1rem;">
                {full_name}
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                <strong>Role:</strong> {user.role.value.title()}<br>
                <strong>Email:</strong> {user.email}<br>
                <strong>Username:</strong> {user.username}
            </div>
    """, unsafe_allow_html=True)
    
    if profile:
        st.markdown(f"""
            <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 1rem;">
        """, unsafe_allow_html=True)
        
        if profile.get("phone"):
            st.markdown(f"<strong>Phone:</strong> {profile['phone']}<br>", unsafe_allow_html=True)
        
        if profile.get("designation"):
            st.markdown(f"<strong>Designation:</strong> {profile['designation']}<br>", unsafe_allow_html=True)
        
        if profile.get("department"):
            st.markdown(f"<strong>Department:</strong> {profile['department']}<br>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("User Details", width="large")
def show_user_details_dialog(user_id: int):
    """Show detailed user information in a dialog"""
    try:
        user_data = services.get_user_with_profile(user_id)
        
        if not user_data:
            st.error("User not found")
            return
        
        user = user_data["user"]
        profile = user_data["profile"]
        
        # Header
        full_name = "Unknown User"
        if profile:
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #48B88E 0%, #53CDA8 100%);
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                    👤
                </div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">
                    {full_name}
                </div>
                <div style="color: #cbd5e1; font-size: 1rem;">
                    @{user.username} | {user.role.value.title()}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Details in columns
        col1, col2 = st.columns(2)
        client_id = profile.get("client_id") if profile else None
        client_name = get_client(client_id).name if client_id else "N/A"


        with col1:
            st.markdown(f"""
                <div style="
                    background: rgba(30, 41, 59, 0.8);
                    padding: 1.5rem;
                    border-radius: 15px;
                    border: 1px solid rgba(83, 205, 168, 0.2);
                    min-height: 350px;
                ">
                    <div style="color: #53CDA8; font-size: 0.9rem; font-weight: 700; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                        ACCOUNT INFORMATION
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">User ID</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{user.id}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Username</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{user.username}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Email</span><br>
                        <span style="color: #60a5fa; font-size: 1rem; font-weight: 600;">{user.email}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Role</span><br>
                        <span style="color: #53CDA8; font-size: 1rem; font-weight: 600;">{user.role.value.title()}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Created At</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{user.created_at.strftime('%Y-%m-%d %H:%M')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            if not profile:
                st.info("No profile information available for this user")
                return
            
            st.markdown(f"""
                <div style="
                    background: rgba(30, 41, 59, 0.8);
                    padding: 1.5rem;
                    border-radius: 15px;
                    border: 1px solid rgba(83, 205, 168, 0.2);
                    min-height: 350px;
                ">
                    <div style="color: #53CDA8; font-size: 0.9rem; font-weight: 700; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                        PROFILE INFORMATION
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">First Name</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{profile.get('first_name', 'N/A')}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Last Name</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{profile.get('last_name', 'N/A')}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Phone</span><br>
                        <span style="color: #10b981; font-size: 1rem; font-weight: 600;">{profile.get('phone')}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Client Organization</span><br>
                        <span style="color: #53CDA8; font-size: 1rem; font-weight: 700;">{client_name}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Department</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{profile.get('department')}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <span style="color: #94a3b8; font-size: 0.85rem;">Location ID</span><br>
                        <span style="color: #f8fafc; font-size: 1rem; font-weight: 600;">{profile.get('location_id')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    
    except Exception as e:
        log_error(f"Error showing user details: {str(e)}", context="User Management")
        st.error("Error loading user details")


def render_edit_user_form(user_id: int):
    """Render form to edit existing user"""
    st.markdown("##### Edit User")
    
    try:
        # Get user data
        user_data = services.get_user_with_profile(user_id)
        
        if not user_data:
            st.error("User not found")
            if st.button("Cancel Edit"):
                del st.session_state.edit_user_id
                st.rerun()
            return
        
        user = user_data["user"]
        profile = user_data["profile"] or {}
        
        # Pre-fill form with existing data
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input(
                "First Name",
                value=profile.get("first_name", ""),
                placeholder="Enter first name",
                key=f"edit_first_name_{user_id}"
            )
            if not first_name:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
        
        with col2:
            last_name = st.text_input(
                "Last Name",
                value=profile.get("last_name", ""),
                placeholder="Enter last name",
                key=f"edit_last_name_{user_id}"
            )
            if not last_name:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            email = st.text_input(
                "Email Address",
                value=user.email,
                placeholder="user@example.com",
                key=f"edit_email_{user_id}"
            )
            if email:
                if "@" not in email or "." not in email.split("@")[-1]:
                    st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Invalid email format</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required field</p>', unsafe_allow_html=True)
        
        with col4:
            # Username is read-only (display only)
            st.text_input(
                "Username",
                value=user.username,
                disabled=True,
                help="Username cannot be changed",
                key=f"edit_username_{user_id}"
            )
        
        col5, col6 = st.columns(2)
        
        with col5:
            # Role selection
            current_role = user.role.value
            role_index = ["admin", "scientist", "client", "guest", "super_admin"].index(current_role) if current_role in ["admin", "scientist", "client", "guest", "super_admin"] else 0
            
            new_role = st.selectbox(
                "User Role",
                ["admin", "scientist", "client", "guest", "super_admin"],
                index=role_index,
                help="Select user role and permissions",
                key=f"edit_role_{user_id}"
            )
        
        with col6:
            phone = st.text_input(
                "Phone Number",
                value=profile.get("phone", ""),
                placeholder="+64-21-XXX-XXXX",
                key=f"edit_phone_{user_id}"
            )
            
            if phone:
                phone_validation = validate_phone_number(phone)
                if not phone_validation['valid']:
                    st.markdown(f'<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">{phone_validation["message"]}</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Valid phone number</p>', unsafe_allow_html=True)
        
        # Role-specific fields
        designation = None
        department = None
        location_id = profile.get("location_id")
        selected_client_id = None
        
        if new_role == "client":
            st.markdown("---")
            st.markdown("##### Client-Specific Information")
            
            col9, col10 = st.columns(2)
            
            with col9:
                designation = st.text_input(
                    "Designation",
                    value=profile.get("designation", ""),
                    placeholder="e.g., Plant Technician",
                    key=f"edit_designation_{user_id}"
                )
                if not designation:
                    st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Required for client role</p>', unsafe_allow_html=True)
            
            with col10:
                department = st.text_input(
                    "Department",
                    value=profile.get("department", ""),
                    placeholder="e.g., Operations",
                    key=f"edit_department_{user_id}"
                )
            
            # Client and Location selection
            col11, col12 = st.columns(2)
            
            with col11:
                try:
                    clients = get_cached_clients()
                    if clients:
                        client_options = {f"{client.name}": client.id for client in clients}
                        client_names = ["Select Client"] + list(client_options.keys())
                        
                        # Try to pre-select current client based on location
                        current_client_index = 0
                        if location_id:
                            try:
                                location = services.get_location(location_id)
                                if location:
                                    current_client = services.get_client(location.client_id)
                                    if current_client and current_client.name in client_options:
                                        current_client_index = client_names.index(current_client.name)
                            except:
                                pass
                        
                        selected_client_name = st.selectbox(
                            "Assign to Client",
                            client_names,
                            index=current_client_index,
                            key=f"edit_client_{user_id}"
                        )
                        
                        if selected_client_name != "Select Client":
                            selected_client_id = client_options[selected_client_name]
                    else:
                        st.warning("No clients available")
                except Exception as e:
                    log_error(f"Error loading clients for edit: {str(e)}", context="User Management")
                    st.error("Error loading clients")
            
            with col12:
                if selected_client_id:
                    try:
                        locations = get_cached_locations(selected_client_id)
                        if locations:
                            location_options = {f"{loc.address}": loc.id for loc in locations}
                            location_names = ["Select Location"] + list(location_options.keys())
                            
                            # Try to pre-select current location
                            current_location_index = 0
                            if location_id and location_id in location_options.values():
                                for idx, (name, loc_id) in enumerate(location_options.items()):
                                    if loc_id == location_id:
                                        current_location_index = location_names.index(name)
                                        break
                            
                            selected_location_name = st.selectbox(
                                "Assign to Location",
                                location_names,
                                index=current_location_index,
                                key=f"edit_location_{user_id}"
                            )
                            
                            if selected_location_name != "Select Location":
                                location_id = location_options[selected_location_name]
                            else:
                                location_id = None
                        else:
                            st.info("No locations available for this client")
                            location_id = None
                    except Exception as e:
                        log_error(f"Error loading locations for edit: {str(e)}", context="User Management")
                        st.error("Error loading locations")
                else:
                    st.selectbox(
                        "Assign to Location",
                        ["Select Client First"],
                        disabled=True,
                        key=f"edit_location_disabled_{user_id}"
                    )
        
        # Password change section
        st.markdown("---")
        st.markdown("##### Change Password (Optional)")
        st.info("Leave blank to keep current password")
        
        col7, col8 = st.columns(2)
        
        with col7:
            new_password = st.text_input(
                "New Password",
                type="password",
                placeholder="Leave blank to keep current",
                key=f"edit_password_{user_id}"
            )
            
            if new_password:
                if len(new_password) < 8:
                    st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Password must be at least 8 characters</p>', unsafe_allow_html=True)
                else:
                    password_strength = validate_password_strength(new_password)
                    if password_strength['score'] >= 3:
                        st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Strong password</p>', unsafe_allow_html=True)
                    elif password_strength['score'] >= 2:
                        st.markdown('<p style="color: #f59e0b; font-size: 0.85rem; margin-top: -0.5rem;">Moderate password</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Weak password</p>', unsafe_allow_html=True)
        
        with col8:
            confirm_new_password = st.text_input(
                "Confirm New Password",
                type="password",
                placeholder="Re-enter new password",
                key=f"edit_confirm_password_{user_id}"
            )
            
            if new_password and confirm_new_password:
                if new_password != confirm_new_password:
                    st.markdown('<p style="color: #ef4444; font-size: 0.85rem; margin-top: -0.5rem;">Passwords do not match</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -0.5rem;">Passwords match</p>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Action buttons
        col_save, col_cancel = st.columns([1, 1])
        
        with col_save:
            save_button = st.button("Save Changes", type="primary", use_container_width=True, key=f"btn_save_{user_id}")
        
        with col_cancel:
            cancel_button = st.button("Cancel", use_container_width=True, key=f"btn_cancel_{user_id}")
        
        if cancel_button:
            del st.session_state.edit_user_id
            st.rerun()
        
        if save_button:
            # Validation
            errors = []
            
            if not all([first_name, last_name, email]):
                errors.append("Please fill in all required fields")
            
            if "@" not in email or "." not in email.split("@")[-1]:
                errors.append("Invalid email address format")
            
            # Password validation if provided
            if new_password:
                if len(new_password) < 8:
                    errors.append("New password must be at least 8 characters")
                if new_password != confirm_new_password:
                    errors.append("Passwords do not match")
            
            # Phone validation
            if phone:
                phone_validation = validate_phone_number(phone)
                if not phone_validation['valid']:
                    errors.append(f"Phone: {phone_validation['message']}")
            
            # Role-specific validation
            if new_role == "client":
                if not designation:
                    errors.append("Designation is required for client role")
                if not selected_client_id:
                    errors.append("Please select a client")
                if not location_id:
                    errors.append("Please select a location")
            
            if errors:
                st.error("Please fix the following errors:")
                for error in errors:
                    st.markdown(f"- {error}")
            else:
                # Update user
                try:
                    with st.spinner("Updating user..."):
                        # Prepare user data (database fields)
                        user_update_data = {
                            "email": email,
                            "role": new_role
                        }
                        
                        # Add password if changed
                        if new_password:
                            user_update_data["hashed_password"] = bcrypt.hash(new_password)
                        
                        # Prepare profile data
                        profile_update_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "phone": phone,
                            "designation": designation or "",
                            "department": department or "",
                            "location_id": location_id
                        }
                        
                        # Update user with profile
                        result = services.update_user_with_profile(
                            user_id=user_id,
                            user_data=user_update_data,
                            profile_data=profile_update_data
                        )
                        
                        if result and result["success"]:
                            log_info(
                                f"Admin {st.session_state.username} updated user: {user.username}",
                                context="User Management"
                            )
                            st.success(f"User '{user.username}' updated successfully!")
                            
                            # Clear edit mode
                            del st.session_state.edit_user_id
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to update user")
                
                except Exception as e:
                    log_error(f"Error updating user: {str(e)}", context="User Management")
                    if "UNIQUE constraint failed" in str(e):
                        if "email" in str(e):
                            st.error(f"Email '{email}' is already registered by another user.")
                        else:
                            st.error("Update failed due to duplicate data.")
                    else:
                        st.error(f"Error updating user: {str(e)}")
    
    except Exception as e:
        log_error(f"Error rendering edit form: {str(e)}", context="User Management")
        st.error("Error loading edit form")
        if st.button("Cancel Edit"):
            del st.session_state.edit_user_id
            st.rerun()


@st.dialog("Confirm Delete User")
def confirm_delete_user(user_id: int):
    """Confirm user deletion with dialog"""
    try:
        user_data = services.get_user_with_profile(user_id)
        
        if not user_data:
            st.error("User not found")
            return
        
        user = user_data["user"]
        profile = user_data["profile"]
        
        full_name = "Unknown User"
        if profile:
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        
        st.warning("You are about to delete this user:")
        
        st.markdown(f"""
            <div style="
                background: rgba(239, 68, 68, 0.1);
                border: 2px solid #ef4444;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
            ">
                <div style="font-size: 1.3rem; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem;">
                    {full_name}
                </div>
                <div style="color: #94a3b8;">
                    Username: {user.username}<br>
                    Email: {user.email}<br>
                    Role: {user.role.value.title()}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.error("This action cannot be undone!")
        
        # Prevent deleting yourself
        current_user_id = st.session_state.get('user_id')
        if user_id == current_user_id:
            st.error("You cannot delete your own account!")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Delete User", type="primary", use_container_width=True):
                try:
                    result = services.delete_user_with_profile(user_id)
                    
                    if result:
                        log_warning(
                            f"Admin {st.session_state.username} deleted user: {user.username}",
                            context="User Management"
                        )
                        st.success(f"User '{user.username}' deleted successfully!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete user")
                
                except Exception as e:
                    log_error(f"Error deleting user: {str(e)}", context="User Management")
                    st.error(f"Error deleting user: {str(e)}")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
    
    except Exception as e:
        log_error(f"Error in delete confirmation: {str(e)}", context="User Management")
        st.error("Error loading user data")