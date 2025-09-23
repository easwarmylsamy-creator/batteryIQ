# app/main.py
import streamlit as st
import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.auth import login_user

st.set_page_config(page_title="BatteryIQ", layout="wide", page_icon="./assets/logo0.png")

# -----------------------
# Session Setup
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None


def go_to(page: str):
    st.session_state.page = page
    st.rerun()


def topbar(login=True):
    if login:
        col1, col2 = st.columns([3,1])
        with col1:
            st.image("./assets/logo1.png", width=175)
        with col2:
            st.markdown(
                f"<div style='text-align:right;'>👤 {st.session_state.username} ({st.session_state.role})</div>",
                unsafe_allow_html=True,
            )
    else:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.image("./assets/logo1.png", width=175)
        with col2:

            if st.button("Login"):
                go_to("login")
            st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)


# -----------------------
# Pages
# -----------------------
def page_welcome():
    topbar(login=False)
    # Styling
    st.markdown(
        """
        <style>
        .centered {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 1rem;
        }
        .welcome-title {
            font-size: 2.5rem;
            font-weight: bold;
            margin-top: 1rem;
        }
        .welcome-sub {
            font-size: 1.2rem;
            color: #888;
            margin-bottom: 1.5rem;
        }
        .welcome-text {
            font-size: 1rem;
            max-width: 700px;
            color: #444;
            line-height: 1.6;
            margin-bottom: 2rem;
        }
        .login-btn button {
            font-size: 1.2rem !important;
            padding: 0.75rem 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Welcome Section
    st.markdown("<div class='centered'>", unsafe_allow_html=True)

    # Logo
    # st.image("./assets/logo1.png", width=260)

    # Title + Subheading
    st.markdown("<div class='welcome-title'>Welcome to BatteryIQ</div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-sub'>Smarter battery data. Clearer decisions.</div>", unsafe_allow_html=True)

    # Project Description
    st.markdown(
        """
        <div class='welcome-text'>
        BatteryIQ is a data-driven platform designed to **collect, manage, and analyze battery health and performance data**.  
        Whether it’s **telemetry uploads from devices** or **manual lab records**, BatteryIQ provides a unified space for
        scientists, clients, and administrators to work together.  

        With role-based access, powerful analytics, and a streamlined interface,  
        BatteryIQ helps transform raw data into meaningful insights — ensuring **better reliability, efficiency, and innovation in energy systems**.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # # Login Button
    # if st.button("Login", key="welcome_login"):
    #     go_to("login")

    # st.markdown("</div>", unsafe_allow_html=True)



def page_login():
    st.markdown("<h2 style='text-align:center;'>Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login", key="login_button"):
        user = login_user(username, password)
        if user:
            st.session_state.username = user.username
            st.session_state.role = user.role.value
            go_to("dashboard")
        else:
            st.error("Invalid username or password")

def page_dashboard():
    topbar()

    role = st.session_state.role
    st.markdown(f"<h2>Dashboard — {role.title()}</h2>", unsafe_allow_html=True)
    st.write(f"Welcome back, **{st.session_state.username}**!")

    # -------------------------
    # Sidebar Navigation (Role-based)
    # -------------------------
    st.sidebar.header("Navigation")

    if role == "admin":
        st.sidebar.write("🏠 Home")
        st.sidebar.write("📂 Telemetry Upload")
        st.sidebar.write("📂 Manual Upload")
        st.sidebar.write("🗄 File Browser")
        st.sidebar.write("📊 Analytics")
        st.sidebar.write("👥 Clients & Locations")
        st.sidebar.write("🔌 Devices")
        st.sidebar.write("👤 User & Role Management")
        st.sidebar.write("⚙️ Settings")
        st.sidebar.write("📑 Logs")

    elif role == "scientist":
        st.sidebar.write("🏠 Home")
        st.sidebar.write("📂 Telemetry Upload")
        st.sidebar.write("📂 Manual Upload")
        st.sidebar.write("🗄 File Browser")
        st.sidebar.write("📊 Analytics")

    elif role == "client":
        st.sidebar.write("🏠 Home")
        st.sidebar.write("📂 Telemetry Upload (My Devices)")
        st.sidebar.write("🗄 My Files")
        st.sidebar.write("📊 My Analytics")

    elif role == "guest":
        st.sidebar.write("🏠 Home")
        st.sidebar.write("📂 Manual Upload")
        st.sidebar.write("🗄 Shared Data")

    elif role == "god":
        st.sidebar.write("🧠 System Overview")
        st.sidebar.write("📂 All Uploads")
        st.sidebar.write("🗄 Deep Data Browser")
        st.sidebar.write("📊 Advanced Analytics")
        st.sidebar.write("⚙️ Global Settings")
        st.sidebar.write("📑 System Logs")
        st.sidebar.write("👥 Admin Control")

    else:
        st.sidebar.info("No sidebar available for this role.")

    # -------------------------
    # Main dashboard content
    # -------------------------
    if role == "admin":
        st.success("Admin: Manage users, clients, devices, and view all data.")
    elif role == "scientist":
        st.info("Scientist: Access telemetry + manual uploads, run analytics.")
    elif role == "client":
        st.info("Client: View and upload your own device data.")
    elif role == "guest":
        st.warning("Guest: Upload manual files and view shared data.")
    elif role == "god":
        st.error("God Mode: Full system-level access, minute-level data.")
    else:
        st.write("No role assigned.")

# -----------------------
# Router
# -----------------------
if st.session_state.page == "welcome":
    page_welcome()
elif st.session_state.page == "login":
    page_login()
elif st.session_state.page == "dashboard":
    page_dashboard()
