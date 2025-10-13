import streamlit as st
from app.utils.cache_utils import get_cached_clients, get_cached_devices, get_cached_locations
from app.utils.logging_utils import log_info, log_error, log_warning
from backend.services import get_location, get_client
import backend.services as services
import time


def display_device_list(device, client=None, role=None):
    try:
        if device:
            location = get_location(device.location_id)
            device_status = device.status
            
            if device_status == "active":
                exp_header = f"🟢 {device.name} (SN: {device.serial_number})"
                status_color = "#10b981"
            elif device_status == "inactive":
                exp_header = f"🔴 {device.name} (SN: {device.serial_number})"
                status_color = "#ef4444"
            else:
                exp_header = f"🟡 {device.name} (SN: {device.serial_number})"
                status_color = "#f59e0b"

            with st.expander(exp_header, expanded=False):
                
                # Display current info in columns with smaller font
                st.markdown("""
                    <style>
                    .device-info {
                        font-size: 0.85rem;
                        line-height: 1.4;
                    }
                    .device-info strong {
                        font-size: 0.8rem;
                        color: #94a3b8;
                    }
                    .device-label {
                        font-size: 0.75rem;
                        color: #64748b;
                        margin-bottom: 0.2rem;
                    }
                    .device-value {
                        font-size: 0.85rem;
                        color: #e2e8f0;
                        margin-bottom: 0.5rem;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                info_col1, info_col2, info_col3 = st.columns(3)
                
                with info_col1:
                    st.markdown(f'<div class="device-label">SERIAL NUMBER</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="device-value">{device.serial_number}</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="device-label">FIRMWARE</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="device-value">{device.firmware_version or "N/A"}</div>', unsafe_allow_html=True)
                
                with info_col2:
                    st.markdown(f'<div class="device-label">LOCATION</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="device-value">{location.nickname if location else "N/A"}</div>', unsafe_allow_html=True)
                    
                    if role == "admin" and client:
                        st.markdown(f'<div class="device-label">CLIENT</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="device-value">{client.name}</div>', unsafe_allow_html=True)
                
                with info_col3:
                    st.markdown(f'<div class="device-label">STATUS</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="device-value" style="color: {status_color};">{device.status or "active"}</div>', unsafe_allow_html=True)

                st.markdown("---")
                
                # Action buttons - Compact layout
                action_col1, action_col2, action_col3 = st.columns(3)
                
                with action_col1:
                    # Status change - more compact
                    st.markdown('<p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.25rem;">Change Status</p>', unsafe_allow_html=True)
                    new_status = st.selectbox(
                        "Status",
                        options=["active", "inactive", "maintenance"],
                        index=["active", "inactive", "maintenance"].index(
                            (device.status or "active").lower()
                        ),
                        key=f"status_{device.id}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != (device.status or "active").lower():
                        if st.button("✓ Update", key=f"update_status_{device.id}", type="primary", use_container_width=True):
                            update_device_status(device.id, new_status)
                
                with action_col2:
                    st.markdown('<p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.25rem;">Manage</p>', unsafe_allow_html=True)
                    if st.button("✏️ Edit", key=f"edit_{device.id}", type="secondary", use_container_width=True):
                        st.session_state[f'edit_device_{device.id}'] = True
                        st.rerun()
                
                with action_col3:
                    st.markdown('<p style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 0.25rem;">Remove</p>', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"delete_{device.id}", type="secondary", use_container_width=True):
                        confirm_delete_device(device.id, device.name)
                
                # Show edit form if editing
                if st.session_state.get(f'edit_device_{device.id}', False):
                    st.markdown("---")
                    render_edit_device_form(device, client.id if client else device.client_id)
        
        else:
            st.info("No devices found for this client.")
        
    except Exception as e:
        log_error(f"Error displaying device list: {str(e)}", context="Device Management")
        st.error("An error occurred while fetching devices. Please try again later.")


def render_device_management(client=None, devices=None, locations=None):
    print("Rendering new device management interface")
    st.markdown("### Devices Management")
    role = st.session_state.get('role')
    print("Role:", role)
    
    if role == "admin":
        clients = get_cached_clients()
            
        if clients:
            selected_client = st.selectbox(
                "Select Client to View Devices",
                clients,
                format_func=lambda x: f"{x.name} (ID: {x.id})",
                key="device_mgmt_client_select"
            )
            devices = get_cached_devices(selected_client.id) if selected_client else []
            
            if devices:
                st.markdown(f"**Found {len(devices)} device(s)**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Use 2 columns for larger cards
                cols_per_row = 2
                for i in range(0, len(devices), cols_per_row):
                    cols = st.columns(cols_per_row, gap="medium")
                    
                    for j, col in enumerate(cols):
                        if i + j < len(devices):
                            device = devices[i + j]
                            
                            with col:
                                display_device_list(device=device, client=selected_client, role=role)
            else:
                st.info("No devices found for this client.")
        else:
            st.info("No clients found. Please add a client first.")
    
    else:
        if client:
            st.markdown(f"### Devices for Client: {client.name} (ID: {client.id})")
            
            # Filters in a more compact layout
            st.markdown("#### Filters")
            col_f1, col_f2, col_f3 = st.columns(3)
            
            with col_f1:
                location_filter = st.selectbox(
                    "Location",
                    ["All Locations"] + [loc.address for loc in locations],
                    key="location_filter"
                )
            
            with col_f2:
                status_filter = st.selectbox(
                    "Status",
                    ["All Status", "Active", "Inactive", "Maintenance"],
                    key="status_filter"
                )
            
            with col_f3:
                sort_by = st.selectbox(
                    "Sort By",
                    ["Name A-Z", "Name Z-A", "Status", "Location"],
                    key="sort_by"
                )
            
            st.markdown("---")
            
            # Apply filters
            filtered_devices = devices
            
            if location_filter != "All Locations":
                location = next((l for l in locations if l.address == location_filter), None)
                if location:
                    filtered_devices = [d for d in filtered_devices if d.location_id == location.id]
            
            if status_filter != "All Status":
                filtered_devices = [d for d in filtered_devices 
                                if (d.status or 'active').lower() == status_filter.lower()]
            
            # Sort devices
            if sort_by == "Name A-Z":
                filtered_devices = sorted(filtered_devices, key=lambda x: x.name)
            elif sort_by == "Name Z-A":
                filtered_devices = sorted(filtered_devices, key=lambda x: x.name, reverse=True)
            elif sort_by == "Status":
                filtered_devices = sorted(filtered_devices, key=lambda x: x.status or 'active')
            elif sort_by == "Location":
                filtered_devices = sorted(filtered_devices, key=lambda x: x.location_id)
            
            if filtered_devices:
                st.markdown(f"**Showing {len(filtered_devices)} device(s)**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Use 2 columns for larger cards
                cols_per_row = 2
                for i in range(0, len(filtered_devices), cols_per_row):
                    cols = st.columns(cols_per_row, gap="medium")
                    
                    for j, col in enumerate(cols):
                        if i + j < len(filtered_devices):
                            device = filtered_devices[i + j]
                            
                            with col:
                                display_device_list(device=device, client=client, role=role)
            else:
                st.info("No devices found matching filters")


def update_device_status(device_id: int, new_status: str):
    """Update device status"""
    try:
        result = services.update_device(device_id, status=new_status)
        
        if result:
            log_info(
                f"Admin {st.session_state.username} changed device {device_id} status to {new_status}",
                context="Device Management"
            )
            st.success(f"Device status updated to '{new_status}'")
            st.cache_data.clear()
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Failed to update device status")
    
    except Exception as e:
        log_error(f"Error updating device status: {str(e)}", context="Device Management")
        st.error(f"Error: {str(e)}")


def render_edit_device_form(device, client_id: int):
    """Render edit form for device"""
    st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: #60a5fa; margin-top: 1rem;">Edit Device Details</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_name = st.text_input(
            "Device Name",
            value=device.name,
            key=f"edit_name_{device.id}"
        )
    
    with col2:
        new_serial = st.text_input(
            "Serial Number",
            value=device.serial_number,
            key=f"edit_serial_{device.id}"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        new_firmware = st.text_input(
            "Firmware Version",
            value=device.firmware_version or "",
            key=f"edit_firmware_{device.id}"
        )
    
    with col4:
        # Get locations for this client
        locations = get_cached_locations(client_id)
        location_options = {loc.id: f"{loc.nickname} - {loc.address[:50]}" for loc in locations}
        
        current_location_idx = list(location_options.keys()).index(device.location_id) if device.location_id in location_options else 0
        
        new_location_id = st.selectbox(
            "Location",
            options=list(location_options.keys()),
            format_func=lambda x: location_options[x],
            index=current_location_idx,
            key=f"edit_location_{device.id}"
        )
    
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        if st.button("💾 Save Changes", key=f"save_{device.id}", type="primary", use_container_width=True):
            if not new_name or not new_serial:
                st.error("Name and Serial Number are required")
            else:
                try:
                    # Check if serial number changed and if it already exists
                    if new_serial != device.serial_number:
                        existing = services.get_device_by_serial(new_serial)
                        if existing and existing.id != device.id:
                            st.error(f"Serial number '{new_serial}' already exists")
                            return
                    
                    # Update device
                    result = services.update_device(
                        device.id,
                        name=new_name.strip(),
                        serial_number=new_serial.strip(),
                        firmware_version=new_firmware.strip() if new_firmware else None,
                        location_id=new_location_id
                    )
                    
                    if result:
                        log_info(
                            f"Admin {st.session_state.username} updated device {device.id}",
                            context="Device Management"
                        )
                        st.success(f"Device '{new_name}' updated successfully!")
                        del st.session_state[f'edit_device_{device.id}']
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Failed to update device")
                
                except Exception as e:
                    log_error(f"Error updating device: {str(e)}", context="Device Management")
                    st.error(f"Error: {str(e)}")
    
    with button_col2:
        if st.button("✖ Cancel", key=f"cancel_{device.id}", use_container_width=True):
            del st.session_state[f'edit_device_{device.id}']
            st.rerun()


@st.dialog("Confirm Delete Device")
def confirm_delete_device(device_id: int, device_name: str):
    """Confirm device deletion with dialog"""
    try:
        device = services.get_device(device_id)
        
        if not device:
            st.error("Device not found")
            return
        
        st.warning("You are about to delete this device:")
        
        st.markdown(f"""
            <div style="
                background: rgba(239, 68, 68, 0.1);
                border: 2px solid #ef4444;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
            ">
                <div style="font-size: 1.3rem; font-weight: 700; color: #ef4444; margin-bottom: 0.5rem;">
                    {device.name}
                </div>
                <div style="color: #94a3b8;">
                    Serial Number: {device.serial_number}<br>
                    Status: {device.status or 'active'}<br>
                    Firmware: {device.firmware_version or 'N/A'}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.error("This action cannot be undone! All associated telemetry data will also be deleted.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Device", type="primary", use_container_width=True):
                try:
                    result = services.delete_device(device_id)
                    
                    if result:
                        log_warning(
                            f"Admin {st.session_state.username} deleted device: {device_name} (ID: {device_id})",
                            context="Device Management"
                        )
                        st.success(f"Device '{device_name}' deleted successfully!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete device")
                
                except Exception as e:
                    log_error(f"Error deleting device: {str(e)}", context="Device Management")
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
    
    except Exception as e:
        log_error(f"Error in delete confirmation: {str(e)}", context="Device Management")
        st.error("Error loading device details")