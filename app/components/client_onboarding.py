# app/components/client_onboarding.py
import streamlit as st
from backend import services
from app.utils.logging_utils import log_info, log_error, log_warning
import pandas as pd
import time

def initialize_onboarding_state():
    """Initialize session state for onboarding wizard"""
    if 'onboarding' not in st.session_state:
        st.session_state.onboarding = {
            'step': 1,
            'client': {
                'name': '',
            },
            'locations': [],
            'current_location_index': 0,
            'temp_location': {
                'nickname': '',
                'address': '',
            },
            'temp_device': {
                'name': '',
                'serial_number': '',
                'firmware_version': '',
                'status': 'active'
            },
            'refresh_key': 0
        }

def reset_onboarding():
    """Reset onboarding state"""
    if 'onboarding' in st.session_state:
        del st.session_state.onboarding
    initialize_onboarding_state()

def go_to_step(step_number):
    """Navigate to a specific step"""
    st.session_state.onboarding['step'] = step_number
    st.session_state.onboarding['refresh_key'] += 1

def render_progress_bar():
    """Render progress indicator"""
    step = st.session_state.onboarding['step']
    
    steps_info = {
        1: ('Client Info', '1/4'),
        2: ('Location Info', '2/4'),
        3: ('Device Info', '3/4'),
        4: ('Review & Submit', '4/4')
    }
    
    current_step_name, progress = steps_info.get(step, ('Unknown', '0/4'))
    
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            border-left: 4px solid #53CDA8;
        ">
            <div style="color: #53CDA8; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">
                STEP {step} OF 4: {current_step_name.upper()}
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem;">
                Progress: {progress}
            </div>
        </div>
    """, unsafe_allow_html=True)

@st.fragment
def render_step1_client_info():
    """Step 1: Collect client information"""
    st.markdown("### Step 1: Client Information")
    st.markdown("Enter the basic information for the new client.")
    
    refresh = st.session_state.onboarding['refresh_key']
    
    client_name = st.text_input(
        "Client Name",
        value=st.session_state.onboarding['client']['name'],
        placeholder="e.g., Acme Energy Corporation",
        help="Enter the full legal name of the client organization",
        key=f"client_name_input_{refresh}"
    )
    
    st.session_state.onboarding['client']['name'] = client_name
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Next: Add Locations", type="secondary", use_container_width=True, key=f"step1_next_{refresh}"):
            if not client_name or client_name.strip() == '':
                st.error("Client name is required")
            else:
                try:
                    existing_clients = services.get_clients()
                    if any(c.name.lower() == client_name.lower() for c in existing_clients):
                        st.error(f"Client '{client_name}' already exists")
                    else:
                        log_info(f"Client info entered: {client_name}", context="Onboarding")
                        go_to_step(2)
                        st.rerun(scope="app")
                except Exception as e:
                    log_error(f"Error checking client name: {str(e)}", context="Onboarding")
                    st.error("Error validating client name")
    
    with col2:
        if st.button("Cancel", use_container_width=True, key=f"step1_cancel_{refresh}"):
            reset_onboarding()
            st.rerun(scope="app")

@st.fragment
def render_step2_location_info():
    """Step 2: Collect location information"""
    st.markdown("### Step 2: Location Information")
    
    refresh = st.session_state.onboarding['refresh_key']
    
    st.info(f"Adding locations for: **{st.session_state.onboarding['client']['name']}**")
    
    locations = st.session_state.onboarding['locations']
    if locations:
        st.markdown(f"**Locations added so far:** {len(locations)}")
        
        with st.expander("View Added Locations", expanded=False):
            for idx, loc in enumerate(locations, 1):
                device_count = len(loc.get('devices', []))
                nickname = loc.get('nickname', 'N/A')
                st.markdown(f"**{idx}.** {nickname} - {loc['address'][:50]} - {device_count} device(s)")
    
    st.markdown("---")
    st.markdown("#### Add New Location")
    
    location_nickname = st.text_input(
        "Location Nickname",
        value=st.session_state.onboarding['temp_location']['nickname'],
        placeholder="e.g., Main Office, Warehouse #1, Data Center Auckland",
        help="Short, memorable name for this location",
        key=f"location_nickname_input_{refresh}"
    )
    
    st.session_state.onboarding['temp_location']['nickname'] = location_nickname
    
    location_address = st.text_area(
        "Location Address",
        value=st.session_state.onboarding['temp_location']['address'],
        placeholder="e.g., 123 Main Street, Auckland, New Zealand",
        help="Enter the full address of this location",
        height=100,
        key=f"location_address_input_{refresh}"
    )
    
    st.session_state.onboarding['temp_location']['address'] = location_address
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Next: Add Devices", type="primary", use_container_width=True, key=f"step2_next_{refresh}"):
            if not location_nickname or location_nickname.strip() == '':
                st.error("Location nickname is required")
            elif not location_address or location_address.strip() == '':
                st.error("Location address is required")
            else:
                st.session_state.onboarding['temp_location']['devices'] = []
                log_info(f"Location info entered: {location_nickname}", context="Onboarding")
                go_to_step(3)
                st.rerun(scope="app")
    
    with col2:
        if st.button("Back to Client", use_container_width=True, key=f"step2_back_{refresh}"):
            go_to_step(1)
            st.rerun(scope="app")
    
    with col3:
        if st.button("Skip to Review", use_container_width=True, key=f"step2_skip_{refresh}"):
            if len(locations) > 0:
                go_to_step(4)
                st.rerun(scope="app")
            else:
                st.error("Add at least one location before reviewing")

@st.fragment
def render_step3_device_info():
    """Step 3: Collect device information"""
    st.markdown("### Step 3: Device Information")
    
    refresh = st.session_state.onboarding['refresh_key']
    
    client_name = st.session_state.onboarding['client']['name']
    location_nickname = st.session_state.onboarding['temp_location']['nickname']
    location_address = st.session_state.onboarding['temp_location']['address']
    
    st.info(f"**Client:** {client_name}  \n**Location:** {location_nickname}")
    st.caption(f"Address: {location_address[:80]}{'...' if len(location_address) > 80 else ''}")
    
    temp_devices = st.session_state.onboarding['temp_location'].get('devices', [])
    if temp_devices:
        st.markdown(f"**Devices added to this location:** {len(temp_devices)}")
        
        with st.expander("View Added Devices", expanded=False):
            for idx, dev in enumerate(temp_devices, 1):
                st.markdown(f"**{idx}.** {dev['name']} (SN: {dev['serial_number']})")
    
    st.markdown("---")
    st.markdown("#### Add New Device")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        device_name = st.text_input(
            "Device Name",
            value="",
            placeholder="e.g., Battery Monitor Unit 001",
            help="Descriptive name for this device",
            key=f"device_name_input_{refresh}"
        )
    
    with col_b:
        serial_number = st.text_input(
            "Serial Number",
            value="",
            placeholder="e.g., SN-12345678",
            help="Unique serial number for this device",
            key=f"device_serial_input_{refresh}"
        )
    
    col_c, col_d = st.columns(2)
    
    with col_c:
        firmware_version = st.text_input(
            "Firmware Version",
            value="",
            placeholder="e.g., 1.0.0",
            help="Current firmware version (optional)",
            key=f"device_firmware_input_{refresh}"
        )
    
    with col_d:
        status = st.selectbox(
            "Status",
            options=["active", "inactive", "maintenance"],
            index=0,
            help="Current operational status",
            key=f"device_status_input_{refresh}"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Add Device", type="primary", use_container_width=True, key=f"step3_add_{refresh}"):
            if not device_name or not serial_number:
                st.error("Device name and serial number are required")
            else:
                all_serials = []
                for loc in st.session_state.onboarding['locations']:
                    all_serials.extend([d['serial_number'] for d in loc.get('devices', [])])
                all_serials.extend([d['serial_number'] for d in temp_devices])
                
                if serial_number.strip() in all_serials:
                    st.error(f"Serial number '{serial_number}' already exists in this session")
                else:
                    try:
                        existing_device = services.get_device_by_serial(serial_number.strip())
                        if existing_device:
                            st.error(f"Serial number '{serial_number}' already exists in database")
                        else:
                            new_device = {
                                'name': device_name.strip(),
                                'serial_number': serial_number.strip(),
                                'firmware_version': firmware_version.strip() if firmware_version else None,
                                'status': status
                            }
                            st.session_state.onboarding['temp_location']['devices'].append(new_device)
                            
                            log_info(f"Device added: {device_name} ({serial_number})", context="Onboarding")
                            st.success(f"Device '{device_name}' added!")
                            
                            # Only rerun this fragment
                            st.session_state.onboarding['refresh_key'] += 1
                            st.rerun(scope="fragment")
                    except Exception as e:
                        log_error(f"Error checking serial: {str(e)}", context="Onboarding")
                        st.error("Error validating serial number")
    
    with col2:
        if st.button("Finish Location", use_container_width=True, key=f"step3_finish_loc_{refresh}"):
            if len(temp_devices) == 0:
                st.error("Add at least one device to this location")
            else:
                st.session_state.onboarding['locations'].append(
                    st.session_state.onboarding['temp_location'].copy()
                )
                
                st.session_state.onboarding['temp_location'] = {
                    'nickname': '',
                    'address': '',
                    'devices': []
                }
                
                log_info("Location completed, returning to add more locations", context="Onboarding")
                go_to_step(2)
                st.rerun(scope="app")
    
    with col3:
        if st.button("Back to Location", use_container_width=True, key=f"step3_back_{refresh}"):
            go_to_step(2)
            st.rerun(scope="app")
    
    with col4:
        if st.button("Review & Submit", use_container_width=True, key=f"step3_review_{refresh}"):
            if len(temp_devices) == 0:
                st.error("Add at least one device before reviewing")
            else:
                st.session_state.onboarding['locations'].append(
                    st.session_state.onboarding['temp_location'].copy()
                )
                go_to_step(4)
                st.rerun(scope="app")

@st.fragment
def render_step4_review():
    """Step 4: Review and submit"""
    st.markdown("### Step 4: Review & Submit")
    
    refresh = st.session_state.onboarding['refresh_key']
    
    client_name = st.session_state.onboarding['client']['name']
    locations = st.session_state.onboarding['locations']
    
    st.success("Review your configuration before submitting")
    
    total_devices = sum(len(loc.get('devices', [])) for loc in locations)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Client", client_name)
    with col2:
        st.metric("Locations", len(locations))
    with col3:
        st.metric("Total Devices", total_devices)
    
    st.markdown("---")
    
    st.markdown("#### Configuration Details")
    
    for loc_idx, location in enumerate(locations, 1):
        nickname = location.get('nickname', 'N/A')
        with st.expander(f"Location {loc_idx}: {nickname}", expanded=True):
            st.markdown(f"**Nickname:** {nickname}")
            st.markdown(f"**Address:** {location['address']}")
            st.markdown(f"**Devices:** {len(location.get('devices', []))}")
            
            if location.get('devices'):
                device_data = []
                for dev in location['devices']:
                    device_data.append({
                        'Name': dev['name'],
                        'Serial': dev['serial_number'],
                        'Firmware': dev.get('firmware_version', 'N/A'),
                        'Status': dev['status']
                    })
                
                df = pd.DataFrame(device_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Submit All", type="primary", use_container_width=True, key=f"step4_submit_{refresh}"):
            submit_onboarding_data()
    
    with col2:
        if st.button("Back to Edit", use_container_width=True, key=f"step4_back_{refresh}"):
            if locations:
                st.session_state.onboarding['temp_location'] = locations.pop()
            go_to_step(3)
            st.rerun(scope="app")
    
    with col3:
        if st.button("Cancel Everything", type="secondary", use_container_width=True, key=f"step4_cancel_{refresh}"):
            if st.session_state.get('confirm_cancel', False):
                reset_onboarding()
                st.rerun(scope="app")
            else:
                st.session_state.confirm_cancel = True
                st.warning("Click again to confirm cancellation")

def submit_onboarding_data():
    """Submit all collected data to database"""
    try:
        with st.spinner("Creating client and associated data..."):
            client_name = st.session_state.onboarding['client']['name']
            locations = st.session_state.onboarding['locations']
            
            log_info(f"Creating client: {client_name}", context="Onboarding")
            client = services.create_client(client_name)
            
            total_devices = 0
            
            for location in locations:
                address_with_nickname = f"{location['nickname']} - {location['address']}"
                log_info(f"Creating location: {location['nickname']}", context="Onboarding")
                loc = services.create_location(
                    client.id, 
                    location['address'],
                    nickname=location['nickname']
)
                
                for device in location.get('devices', []):
                    log_info(f"Creating device: {device['name']} ({device['serial_number']})", context="Onboarding")
                    services.create_device(
                        client_id=client.id,
                        location_id=loc.id,
                        name=device['name'],
                        serial=device['serial_number'],
                        firmware_version=device.get('firmware_version'),
                        status=device['status']
                    )
                    total_devices += 1
            
            st.success(f"Successfully created '{client_name}' with {len(locations)} location(s) and {total_devices} device(s)!")
            st.balloons()
            
            log_info(f"Onboarding completed: {client_name} - {len(locations)} locations, {total_devices} devices", context="Onboarding")
            
            st.cache_data.clear()
            reset_onboarding()
            
            time.sleep(2)
            st.rerun(scope="app")
            
    except Exception as e:
        log_error(f"Error during onboarding submission: {str(e)}", context="Onboarding")
        st.error(f"Failed to create client setup: {str(e)}")

def render_client_onboarding_wizard():
    """Main wizard orchestrator"""
    initialize_onboarding_state()
    
    st.markdown("## Client Onboarding Wizard")
    st.markdown("Add a new client with their locations and devices in a guided workflow")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    render_progress_bar()
    
    step = st.session_state.onboarding['step']
    
    if step == 1:
        render_step1_client_info()
    elif step == 2:
        render_step2_location_info()
    elif step == 3:
        render_step3_device_info()
    elif step == 4:
        render_step4_review()
    else:
        st.error("Invalid step")
        reset_onboarding()

def go_to_step(step_number):
    """Navigate to a specific step"""
    st.session_state.onboarding['step'] = step_number
    st.session_state.onboarding['refresh_key'] += 1
    # Ensure we stay on the Add Client tab
    st.session_state.admin_active_tab = 'Add Client'