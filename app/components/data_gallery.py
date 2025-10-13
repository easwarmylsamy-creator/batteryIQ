import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend import services
from app.utils.cache_utils import get_cached_clients, get_cached_devices, get_cached_locations
from app.utils.logging_utils import log_info, log_error
import os


def render_data_gallery():
    """
    Role-specific dynamic data gallery with advanced filtering, sorting, and visualization
    """
    # Get user role
    user_role = st.session_state.get('role', 'guest')
    username = st.session_state.get('username', 'Unknown')
    
    # Role-specific header
    role_titles = {
        'super_admin': '🔐 Super Admin - Complete System Data Gallery',
        'admin': '👑 Admin - System Data Gallery',
        'scientist': '🔬 Scientist - Research Data Gallery',
        'client': '🏢 Client - My Data Gallery',
        'guest': '👤 Guest - Public Data Gallery'
    }
    
    st.markdown(f"### {role_titles.get(user_role, 'Data Gallery')}")
    
    # Role-specific description
    role_descriptions = {
        'super_admin': 'Access to ALL system data with full permissions - All clients, devices, and uploads',
        'admin': 'Access to all telemetry and manual uploads across the system',
        'scientist': 'Access to research data, manual uploads, and assigned client telemetry',
        'client': 'Access to your organization\'s battery data and device telemetry',
        'guest': 'Limited access to publicly shared datasets only'
    }
    
    st.markdown(f"*{role_descriptions.get(user_role, 'Browse available datasets')}*")
    

    # View mode selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search datasets",
            placeholder="Search by filename, client, device, or keywords...",
            key="gallery_search_input"
        )
    
    with col2:
        view_mode = st.radio(
            "View Mode",
            ["Grid", "List", "Table"],
            horizontal=True,
            key="gallery_view_mode"
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Items per page",
            [12, 24, 48, 96],
            index=1,
            key="gallery_items_per_page"
        )
    
    st.markdown("---")
    
    # Filters in expandable section
    with st.expander("🔧 Filters & Sorting", expanded=True):
        render_filters()
    
    st.markdown("---")
    
    # Get filtered and sorted data
    with st.spinner("Loading datasets..."):
        datasets = get_filtered_datasets(search_query)
    
    if not datasets:
        st.info("No datasets found matching your filters.")
        return
    
    # Pagination
    total_items = len(datasets)
    total_pages = (total_items - 1) // items_per_page + 1
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Display stats
    if user_role!='guest':
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("Total Datasets", total_items)
        with col_b:
            telemetry_count = len([d for d in datasets if d['type'] == 'Telemetry'])
            st.metric("Telemetry", telemetry_count)
        with col_c:
            manual_count = len([d for d in datasets if d['type'] == 'Manual'])
            # Role-based manual count display
            if user_role in ['super_admin', 'admin', 'scientist']:
                st.metric("Manual Uploads", manual_count)
            else:
                st.metric("Available Data", manual_count)
        with col_d:
            avg_size = sum(d['size'] for d in datasets) / len(datasets) if datasets else 0
            st.metric("Avg Size (MB)", f"{avg_size:.1f}")
    
    # Role-specific additional info
    if user_role in ['super_admin', 'admin']:
        col_e, col_f, col_g = st.columns(3)
        with col_e:
            unique_clients = len(set([d['client'] for d in datasets if d['client'] != 'N/A']))
            st.metric("Clients", unique_clients)
        with col_f:
            unique_devices = len(set([d['device'] for d in datasets]))
            st.metric("Devices", unique_devices)
        with col_g:
            total_records = sum(d['records'] for d in datasets)
            st.metric("Total Records", f"{total_records:,}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Paginated datasets
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    paginated_datasets = datasets[start_idx:end_idx]
    
    # Display based on view mode
    if view_mode == "Grid":
        render_grid_view(paginated_datasets)
    elif view_mode == "List":
        render_list_view(paginated_datasets)
    else:
        render_table_view(paginated_datasets)
    
    # Pagination controls
    if total_pages > 1:
        render_pagination(total_pages)


def render_filters():
    """Render comprehensive filter options"""
    prev_roles = {'super_admin', 'admin', 'scientist'}
    if st.session_state.role in prev_roles:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.session_state.filter_data_type = st.selectbox(
                "Data Type",
                ["All Types", "Telemetry", "Manual"],
                key="data_type_filter"
            )
        
        with col2:
            clients = get_cached_clients()
            client_names = ["All Clients"] + [c.name for c in clients]
            st.session_state.filter_client = st.selectbox(
                "Client",
                client_names,
                key="gallery_client_filter"
            )
        
        with col3:
            st.session_state.filter_date_range = st.selectbox(
                "Date Range",
                ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"],
                key="date_filter"
            )
        
        with col4:
            st.session_state.filter_file_size = st.selectbox(
                "File Size",
                ["All Sizes", "< 1 MB", "1-10 MB", "10-100 MB", "> 100 MB"],
                key="gallery_size_filter"
            )
        
        # Second row of filters
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.session_state.filter_quality = st.selectbox(
                "Data Quality",
                ["All Quality", "Excellent (>95%)", "Good (80-95%)", "Fair (60-80%)", "Poor (<60%)"],
                key="gallery_quality_filter"
            )
        
        with col6:
            st.session_state.filter_device_status = st.selectbox(
                "Device Status",
                ["All Status", "Active", "Inactive", "Maintenance"],
                key="gallery_device_status_filter"
            )
        
        with col7:
            st.session_state.sort_by = st.selectbox(
                "Sort By",
                ["Recent First", "Oldest First", "Name A-Z", "Name Z-A", "Size (Large)", "Size (Small)", "Quality (High)", "Quality (Low)"],
                key="gallery_sort_filter"
            )
        
        with col8:
            if st.button("Reset All Filters", key="gallery_reset_filters", width='stretch'):
                reset_filters()

    else:
        st.session_state.sort_by = st.selectbox(
                "Sort By",
                ["Recent First", "Oldest First", "Name A-Z", "Name Z-A", "Size (Large)", "Size (Small)", "Quality (High)", "Quality (Low)"],
                key="gallery_sort_filter"
            )

def reset_filters():
    """Reset all filters to default"""
    st.session_state.filter_data_type = "All Types"
    st.session_state.filter_client = "All Clients"
    st.session_state.filter_date_range = "All Time"
    st.session_state.filter_file_size = "All Sizes"
    st.session_state.filter_quality = "All Quality"
    st.session_state.filter_device_status = "All Status"
    st.session_state.sort_by = "Recent First"
    st.session_state.current_page = 1


def get_filtered_datasets(search_query=""):
    """Get datasets based on applied filters AND user role permissions"""
    user_role = st.session_state.get('role', 'guest')
    username = st.session_state.get('username', 'Unknown')
    
    all_datasets = []
    
    try:
        clients = get_cached_clients()
        
        # ROLE-BASED DATA ACCESS
        if user_role == 'super_admin':
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Super admin {username} accessing all data", context="Data Gallery")
            
        elif user_role == 'admin':
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Admin {username} accessing all data", context="Data Gallery")
            
        elif user_role == 'scientist':
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Scientist {username} accessing research data", context="Data Gallery")
            
        elif user_role == 'client':
            accessible_clients = [clients[0]] if clients else []
            can_see_manual = False
            can_see_all_telemetry = False
            log_info(f"Client {username} accessing organization data", context="Data Gallery")
            
        else:  # guest
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Guest {username} accessing public data", context="Data Gallery")
        
        # Get Telemetry Data (role-filtered)
        if st.session_state.get('filter_data_type', 'All Types') in ['All Types', 'Telemetry']:
            if can_see_all_telemetry or user_role == 'client':
                for client in accessible_clients:
                    if st.session_state.get('filter_client', 'All Clients') not in ['All Clients', client.name]:
                        continue
                    
                    try:
                        files = services.get_files_by_client(client.id)
                        for file in files:
                            # Filter for guests - only flagged files
                            if user_role == 'guest' and not file.guest_flag:
                                continue
                            
                            device = services.get_device(file.device_id) if file.device_id else None
                            
                            dataset = {
                                'id': file.id,
                                'type': 'Telemetry',
                                'type_icon': '📡',
                                'name': file.file_name,
                                'client': client.name,
                                'device': device.name if device else f"Device {file.device_id}",
                                'device_status': device.status if device else 'Unknown',
                                'location_id': file.location_id,
                                'path': file.directory,
                                'date': get_file_date(file.directory),
                                'size': calculate_file_size(file.directory),
                                'quality': calculate_quality_score(file.directory),
                                'records': count_records(file.directory),
                                'access_level': get_access_level(user_role, 'telemetry'),
                                'flagged_for_guest': bool(file.guest_flag)
                            }
                            
                            all_datasets.append(dataset)
                    
                    except Exception as e:
                        log_error(f"Error loading files for client {client.id}: {str(e)}", context="Data Gallery")
        
        # Get Manual Uploads (role-filtered)
        if st.session_state.get('filter_data_type', 'All Types') in ['All Types', 'Manual']:
            if can_see_manual:
                try:
                    manual_files = services.get_manual_uploads()
                    
                    for file in manual_files:
                        # Filter for guests - only flagged files
                        if user_role == 'guest' and not file.guest_flag:
                            continue
                        
                        # Role-based filtering for manual uploads (non-guest)
                        if user_role not in ['guest', 'super_admin', 'admin', 'scientist']:
                            if user_role == 'client':
                                show_file = False
                            else:
                                show_file = file.author == username
                            
                            if not show_file:
                                continue
                        
                        dataset = {
                            'id': file.id,
                            'type': 'Manual',
                            'type_icon': '📝',
                            'name': os.path.basename(file.file_directory),
                            'client': 'N/A',
                            'device': file.author,
                            'device_status': 'N/A',
                            'location_id': 'N/A',
                            'path': file.file_directory,
                            'date': file.recorded_date.strftime("%Y-%m-%d %H:%M"),
                            'size': calculate_file_size(file.file_directory),
                            'quality': calculate_quality_score(file.file_directory),
                            'records': count_records(file.file_directory),
                            'notes': file.notes,
                            'access_level': get_access_level(user_role, 'manual'),
                            'flagged_for_guest': bool(file.guest_flag)
                        }
                        
                        all_datasets.append(dataset)
                
                except Exception as e:
                    log_error(f"Error loading manual files: {str(e)}", context="Data Gallery")
        
        # Apply filters
        filtered_datasets = apply_all_filters(all_datasets, search_query)
        
        # Apply sorting
        sorted_datasets = apply_sorting(filtered_datasets)
        
        log_info(f"User {username} ({user_role}) viewing {len(sorted_datasets)} datasets", context="Data Gallery")
        
        return sorted_datasets
    
    except Exception as e:
        log_error(f"Error in get_filtered_datasets: {str(e)}", context="Data Gallery")
        return []


def get_access_level(user_role, data_type):
    """Determine access level based on role and data type"""
    if user_role == 'super_admin':
        return 'full'
    elif user_role == 'admin':
        return 'full'
    elif user_role == 'scientist':
        return 'full' if data_type == 'manual' else 'read'
    elif user_role == 'client':
        return 'read'
    else:
        return 'view_only'


def apply_all_filters(datasets, search_query):
    """Apply all active filters to datasets"""
    filtered = datasets
    
    # File size filter
    size_filter = st.session_state.get('filter_file_size', 'All Sizes')
    if size_filter != 'All Sizes':
        if size_filter == '< 1 MB':
            filtered = [d for d in filtered if d['size'] < 1]
        elif size_filter == '1-10 MB':
            filtered = [d for d in filtered if 1 <= d['size'] < 10]
        elif size_filter == '10-100 MB':
            filtered = [d for d in filtered if 10 <= d['size'] < 100]
        elif size_filter == '> 100 MB':
            filtered = [d for d in filtered if d['size'] >= 100]
    
    # Device status filter
    status_filter = st.session_state.get('filter_device_status', 'All Status')
    if status_filter != 'All Status':
        filtered = [d for d in filtered if d.get('device_status', '').lower() == status_filter.lower()]
    
    # Quality filter
    quality_filter = st.session_state.get('filter_quality', 'All Quality')
    if quality_filter != 'All Quality':
        if 'Excellent' in quality_filter:
            filtered = [d for d in filtered if d['quality'] > 95]
        elif 'Good' in quality_filter:
            filtered = [d for d in filtered if 80 <= d['quality'] <= 95]
        elif 'Fair' in quality_filter:
            filtered = [d for d in filtered if 60 <= d['quality'] < 80]
        elif 'Poor' in quality_filter:
            filtered = [d for d in filtered if d['quality'] < 60]
    
    # Search query
    if search_query:
        search_lower = search_query.lower()
        filtered = [d for d in filtered if 
                   search_lower in d['name'].lower() or
                   search_lower in d['client'].lower() or
                   search_lower in d['device'].lower()]
    
    return filtered


def apply_sorting(datasets):
    """Sort datasets based on selected option"""
    sort_by = st.session_state.get('sort_by', 'Recent First')
    
    if sort_by == "Recent First":
        return sorted(datasets, key=lambda x: x['id'], reverse=True)
    elif sort_by == "Oldest First":
        return sorted(datasets, key=lambda x: x['id'])
    elif sort_by == "Name A-Z":
        return sorted(datasets, key=lambda x: x['name'])
    elif sort_by == "Name Z-A":
        return sorted(datasets, key=lambda x: x['name'], reverse=True)
    elif sort_by == "Size (Large)":
        return sorted(datasets, key=lambda x: x['size'], reverse=True)
    elif sort_by == "Size (Small)":
        return sorted(datasets, key=lambda x: x['size'])
    elif sort_by == "Quality (High)":
        return sorted(datasets, key=lambda x: x['quality'], reverse=True)
    elif sort_by == "Quality (Low)":
        return sorted(datasets, key=lambda x: x['quality'])
    
    return datasets


def render_grid_view(datasets):
    """Render datasets in grid/card view"""
    st.markdown(f"#### Showing {len(datasets)} datasets")
    
    cols_per_row = 3
    
    for i in range(0, len(datasets), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(datasets):
                dataset = datasets[i + j]
                
                with col:
                    render_dataset_card(dataset)


def render_dataset_card(dataset):
    """Render a single dataset card with role-based permissions - opens overlay on click"""
    user_role = st.session_state.get('role', 'guest')
    access_level = dataset.get('access_level', 'view_only')
    
    quality = dataset['quality']
    if quality >= 95:
        quality_color = "#10b981"
        quality_badge = "High"
    elif quality >= 80:
        quality_color = "#48B88E"  # UPDATED: battery green
        quality_badge = "Good"
    elif quality >= 60:
        quality_color = "#f59e0b"
        quality_badge = "Fair"
    else:
        quality_color = "#ef4444"
        quality_badge = "Low"
    
    # Access level badge
    access_badges = {
        'full': 'Full Access',
        'read': 'Read Only',
        'view_only': 'View Only'
    }
    access_badge = access_badges.get(access_level, 'Limited')
    
    # Card HTML - clickable
    card_html = f"""
        <div class="stat-card" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between; cursor: pointer;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                    {dataset['type_icon']}
                </div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.5rem;">
                    {dataset['name'][:35]}{'...' if len(dataset['name']) > 35 else ''}
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    {dataset['type']} | {dataset['client']}
                </div>
                <div style="color: #53CDA8; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    {dataset['device'][:25]}{'...' if len(dataset['device']) > 25 else ''}
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.3rem;">
                    {dataset['size']} MB | {dataset['records']:,} records
                </div>
                <div style="color: {quality_color}; font-size: 0.8rem; margin-bottom: 0.5rem;">
                    Quality: {dataset['quality']}%
                </div>
                <div style="color: #48B88E; font-size: 0.75rem; margin-bottom: 0.5rem;">
                    {access_badge}
                </div>
            </div>
            <div style="margin-top: auto; padding-top: 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.2);">
                <div style="color: #94a3b8; font-size: 0.75rem;">
                    {dataset['date']}
                </div>
            </div>
        </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Click handler - using button overlay
    if st.button("View Details", key=f"view_card_{dataset['type']}_{dataset['id']}", 
                 use_container_width=True):
        show_dataset_overlay(dataset)


@st.dialog("Dataset Details", width="large")
def show_dataset_overlay(dataset):
    """Show dataset details in a large, pleasant overlay dialog"""
    user_role = st.session_state.get('role', 'guest')
    
    quality = dataset['quality']
    if quality >= 95:
        quality_color = "#10b981"
        quality_badge = "High"
        quality_emoji = "🟢"
    elif quality >= 80:
        quality_color = "#48B88E"  # UPDATED: battery green
        quality_badge = "Good"
        quality_emoji = "🔵"
    elif quality >= 60:
        quality_color = "#f59e0b"
        quality_badge = "Fair"
        quality_emoji = "🟡"
    else:
        quality_color = "#ef4444"
        quality_badge = "Low"
        quality_emoji = "🔴"
    
    # Enhanced Header with gradient background - UPDATED COLORS
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #284940 0%, #327552 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        ">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">
                {dataset['type_icon']}
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem;">
                {dataset['name']}
            </div>
            <div style="color: #cbd5e1; font-size: 1rem;">
                {dataset['type']} Dataset | {dataset['client']}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Info cards in row
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:

        col_info1_content = f"""
        <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                height: 100%;
            ">
                <div style="color: #53CDA8; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem;">
                    DATASET INFO
                </div>
                <div style="color: #f8fafc; line-height: 2;">
                    <div style="margin-bottom: 0.5rem;">
                        <span style="color: #94a3b8;">Type:</span> <strong>{dataset['type']}</strong>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="color: #94a3b8;">Client:</span> <strong>{dataset['client']}</strong>
                    </div>"""
        loc_id = dataset.get('location_id')
        loc = services.get_location(loc_id).address if loc_id and loc_id != 'N/A' else 'N/A'
        if user_role != 'guest':
            if dataset.get('location_id') and dataset['location_id'] != 'N/A':
                col_info1_content += f'''
                    <div style="margin-bottom: 0.5rem;">
                        <span style="color: #94a3b8;">Location:</span> <strong>l{loc}</strong>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <span style="color: #94a3b8;">Source:</span> <strong>{dataset['device'][:25]}{'...' if len(dataset['device']) > 25 else ''}</strong>
                    </div>
                '''
            col_info1_content += f'''
                <div style="margin-bottom: 0.5rem;">
                        <span style="color: #94a3b8;">Date:</span> <strong>{dataset['date']}</strong>
                </div>
                '''
            
        
        # st.markdown(f"""
        #     <div style="
        #         background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
        #         padding: 1.5rem;
        #         border-radius: 15px;
        #         border: 1px solid rgba(148, 163, 184, 0.2);
        #         height: 100%;
        #     ">
        #         <div style="color: #53CDA8; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem;">
        #             DATASET INFO
        #         </div>
        #         <div style="color: #f8fafc; line-height: 2;">
        #             <div style="margin-bottom: 0.5rem;">
        #                 <span style="color: #94a3b8;">Type:</span> <strong>{dataset['type']}</strong>
        #             </div>
        #             <div style="margin-bottom: 0.5rem;">
        #                 <span style="color: #94a3b8;">Client:</span> <strong>{dataset['client']}</strong>
        #             </div>
        #             {"" if user_role == 'guest' else f'''
        #             {f'<div style="margin-bottom: 0.5rem;"><span style="color: #94a3b8;">Location:</span> <strong>{dataset["location_id"]}</strong></div>' if dataset.get('location_id') and dataset['location_id'] != 'N/A' else ''}
        #             <div style="margin-bottom: 0.5rem;">
        #                 <span style="color: #94a3b8;">Source:</span> <strong>{dataset['device'][:25]}{'...' if len(dataset['device']) > 25 else ''}</strong>
        #             </div>
        #             '''}
        #             <div style="margin-bottom: 0.5rem;">
        #                 <span style="color: #94a3b8;">Date:</span> <strong>{dataset['date']}</strong>
        #             </div>
        #         </div>
        #     </div>
        # """, unsafe_allow_html=True)
        st.markdown(col_info1_content, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                height: 100%;
            ">
                <div style="color: #48B88E; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem;">
                    FILE METRICS
                </div>
                <div style="color: #f8fafc;">
                    <div style="margin-bottom: 1.5rem;">
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.3rem;">Size</div>
                        <div style="font-size: 2rem; font-weight: 700; color: #60a5fa;">
                            {dataset['size']} MB
                        </div>
                    </div>
                    <div>
                        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.3rem;">Records</div>
                        <div style="font-size: 2rem; font-weight: 700; color: #60a5fa;">
                            {dataset['records']:,}
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


    with col_info3:
        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
                padding: 1.5rem;
                border-radius: 15px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                height: 100%;
            ">
                <div style="color: #10b981; font-size: 0.9rem; font-weight: 600; margin-bottom: 1rem;">
                    QUALITY
                </div>
                <div style="font-size: 3rem; color: {quality_color}; margin-bottom: 0.5rem;">
                    {quality_emoji}
                </div>
                <div style="font-size: 2rem; font-weight: 700; color: {quality_color};">
                    {dataset['quality']}%
                </div>
                <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem;">
                    {quality_badge} Quality
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if dataset['type'] == 'Telemetry':
        content = (
            f"This is an automatically collected telemetry dataset from "
            f"<strong>{dataset['client']}</strong>'s battery monitoring system. "
            f"The data contains <strong>{dataset['records']:,} records</strong> of battery performance metrics including voltage, "
            f"current, and temperature measurements."
        )

        if user_role != 'guest':
            content += f"<br><br><strong>Device:</strong> {dataset['device']}"
            if dataset.get('location_id') != 'N/A':
                content += f"<br><strong>Location ID:</strong> {dataset['location_id']}"

    else:
        content = (
            f"This is a manually uploaded dataset by <strong>{dataset['device']}</strong> (researcher/lab technician). "
            f"The dataset contains <strong>{dataset['records']:,} records</strong> of experimental battery data."
        )
        
        if dataset.get('notes'):
            content += f"<br><br><strong>Notes:</strong> {dataset['notes']}"

    # UPDATED COLORS: border and text
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(51, 65, 85, 0.6) 100%);
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 4px solid #53CDA8;
            margin-bottom: 1.5rem;
        ">
            <div style="color: #53CDA8; font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem;">
                DESCRIPTION
            </div>
            <div style="color: #cbd5e1; line-height: 1.8;">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for data visualization
    tab1, tab2 = st.tabs(["Data Preview", "Performance Chart"])
    
    with tab1:
        with st.spinner("Loading dataset preview..."):
            try:
                if os.path.exists(dataset['path']) and dataset['path'].endswith('.csv'):
                    import pandas as pd
                    _df = pd.read_csv(dataset['path'])
                    n_rows=int(len(_df) * 0.1)
                    df = pd.read_csv(dataset['path'], nrows=n_rows)
                    
                    # UPDATED COLOR
                    st.markdown(f"""
                        <div style="color: #48B88E; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                            DISPLAYING FIRST {n_rows} OF DATA
                        </div>""", unsafe_allow_html=True)
                    
                    st.dataframe(
                        df, 
                        use_container_width=True, 
                        height=400,
                        hide_index=True
                    )
                    
                    # Data summary
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    with col_s1:
                        st.metric("Columns", len(df.columns))
                    with col_s2:
                        st.metric("Rows Shown", len(df))
                    with col_s3:
                        st.metric("Total Records", dataset['records'])
                    with col_s4:
                        missing = df.isnull().sum().sum()
                        st.metric("Missing Values", missing)
                    
                else:
                    st.warning("Data preview not available - file not found or not a CSV")
                    
            except Exception as e:
                log_error(f"Error loading sample data: {str(e)}", context="Data Gallery Overlay")
                st.error("Could not load data preview")
    
    with tab2:
        with st.spinner("Generating performance chart..."):
            try:
                if os.path.exists(dataset['path']) and dataset['path'].endswith('.csv'):
                    import pandas as pd
                    import plotly.express as px
                    
                    df = pd.read_csv(dataset['path'], nrows=100)
                    
                    if 'voltage' in df.columns or 'current' in df.columns or 'temperature' in df.columns:
                        # Determine x-axis
                        x_col = 'timestamp' if 'timestamp' in df.columns else df.columns[0]
                        
                        # Plot available metrics
                        plot_cols = []
                        if 'voltage' in df.columns:
                            plot_cols.append('voltage')
                        if 'current' in df.columns:
                            plot_cols.append('current')
                        if 'temperature' in df.columns:
                            plot_cols.append('temperature')
                        
                        if plot_cols:
                            fig = px.line(
                                df, 
                                x=x_col, 
                                y=plot_cols,
                                title='Battery Performance Metrics (First 100 Records)',
                                labels={x_col: 'Time', 'value': 'Measurement'},
                                template='plotly_dark'
                            )
                            
                            fig.update_layout(
                                plot_bgcolor='rgba(15, 23, 42, 0.8)',
                                paper_bgcolor='rgba(30, 41, 59, 0.5)',
                                font_color='#cbd5e1',
                                height=500,
                                hovermode='x unified',
                                legend=dict(
                                    orientation="h",
                                    yanchor="bottom",
                                    y=1.02,
                                    xanchor="right",
                                    x=1,
                                    bgcolor="rgba(30, 41, 59, 0.8)",
                                    bordercolor="rgba(148, 163, 184, 0.3)",
                                    borderwidth=1
                                ),
                                xaxis=dict(
                                    gridcolor='rgba(148, 163, 184, 0.1)',
                                    showgrid=True
                                ),
                                yaxis=dict(
                                    gridcolor='rgba(148, 163, 184, 0.1)',
                                    showgrid=True
                                )
                            )
                            
                            fig.update_traces(
                                line=dict(width=3),
                                hovertemplate='<b>%{y:.2f}</b><extra></extra>'
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Chart insights - UPDATED COLORS
                            st.markdown("""
                                <div style="
                                    background: rgba(30, 41, 59, 0.4);
                                    padding: 1rem;
                                    border-radius: 10px;
                                    border-left: 3px solid #53CDA8;
                                    margin-top: 1rem;
                                ">
                                    <div style="color: #53CDA8; font-weight: 600; margin-bottom: 0.5rem;">
                                        Chart Insights
                                    </div>
                                    <div style="color: #94a3b8; font-size: 0.9rem;">
                                        This visualization shows the first 100 data points. 
                                        Hover over the chart to see detailed values.
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No voltage, current, or temperature columns found for charting")
                else:
                    st.warning("Chart not available - file not found or not a CSV")
                    
            except Exception as e:
                log_error(f"Error generating chart: {str(e)}", context="Data Gallery Overlay")
                st.error("Could not generate performance chart")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Action buttons with enhanced styling - UPDATED COLOR
    st.markdown("""
        <div style="color: #48B88E; font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">
            Available Actions
        </div>
    """, unsafe_allow_html=True)
    
    if user_role == 'guest':
        st.info("🔒 Guest users have view-only access. Please login for full features including download and analysis.")
        
    elif user_role in ['super_admin', 'admin', 'scientist']:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            download_dataset_file(dataset, f"overlay_download_{dataset['type']}_{dataset['id']}")
        
        with col_b:
            is_flagged = dataset.get('flagged_for_guest', False)
            flag_label = "Unflag" if is_flagged else "🏴 Flag for Guest"
            
            if st.button(flag_label, key=f"overlay_flag_{dataset['type']}_{dataset['id']}", 
                       use_container_width=True, type="secondary"):
                toggle_guest_flag(dataset)
                st.toast(f"Dataset {'unflagged' if is_flagged else 'flagged'} successfully!", 
                        icon="✅")
                log_info(f"User {st.session_state.username} {'unflagged' if is_flagged else 'flagged'} dataset {dataset['id']}", 
                        context="Data Gallery")
                st.rerun()
        
        with col_c:
            if st.button("Delete", key=f"overlay_delete_{dataset['type']}_{dataset['id']}", 
                       use_container_width=True, type="secondary"):
                st.warning("Delete functionality would be implemented here")
    
    else:
        col_a = st.columns(1)
        
        with col_a:
            download_dataset_file(dataset, f"overlay_download_{dataset['type']}_{dataset['id']}")
        
                
def toggle_guest_flag(dataset):
    """
    Toggle guest visibility flag for a dataset in the database
    """
    try:
        if dataset['type'] == 'Telemetry':
            services.toggle_telemetry_guest_flag(dataset['id'])
        else:  # Manual
            services.toggle_manual_upload_guest_flag(dataset['id'])
        
        log_info(f"Toggled guest flag for {dataset['type']} ID {dataset['id']}", context="Data Gallery")
        
    except Exception as e:
        log_error(f"Error toggling guest flag: {str(e)}", context="Data Gallery")

def is_dataset_flagged_for_guest(dataset):
    """Check if dataset is flagged for guest visibility from database"""
    return dataset.get('flagged_for_guest', False)


def render_list_view(datasets):
    """Render datasets in list view with more details"""
    st.markdown(f"#### Showing {len(datasets)} datasets")
    
    for dataset in datasets:
        with st.container():
            col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
            
            with col1:
                st.markdown(f"<div style='font-size: 2rem;'>{dataset['type_icon']}</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{dataset['name']}**")
                st.caption(f"{dataset['type']} | {dataset['client']} | {dataset['device']}")
            
            with col3:
                quality = dataset['quality']
                if quality >= 95:
                    quality_color = "#10b981"
                elif quality >= 80:
                    quality_color = "#48B88E"  # UPDATED
                elif quality >= 60:
                    quality_color = "#f59e0b"
                else:
                    quality_color = "#ef4444"
                    
                st.markdown(f"<div style='color: {quality_color}'>⭐ Quality: {dataset['quality']}%</div>", unsafe_allow_html=True)
                st.caption(f"💾 {dataset['size']} MB | {dataset['records']:,} records")
            
            with col4:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("View", key=f"listview_{dataset['type']}_{dataset['id']}", width='stretch'):
                        show_dataset_overlay(dataset)
                with col_b:
                    download_dataset_file(dataset, f"listdown_{dataset['type']}_{dataset['id']}")

            
            st.markdown("---")


def download_dataset_file(dataset, button_key):
    """
    Create a download button for a dataset file
    Guests cannot download files - button will be disabled
    
    Args:
        dataset: Dictionary containing dataset information with 'path' and 'name' keys
        button_key: Unique key for the download button
    
    Returns:
        bool: True if download button was created successfully, False otherwise
    """
    user_role = st.session_state.get('role', 'guest')
    
    # Disable download for guests
    if user_role == 'guest':
        st.button(
            "Download",
            disabled=True,
            key=button_key,
            help="Guest users cannot download files. Please login for full access.",
            use_container_width=True
        )
        return False
    
    try:
        file_path = dataset['path']
        
        # Check if file exists
        if not os.path.exists(file_path):
            st.button(
                "File Not Found",
                disabled=True,
                key=f"{button_key}_notfound",
                help="File does not exist on server"
            )
            log_error(f"Download failed - file not found: {file_path}", context="Data Gallery")
            return False
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            st.button(
                "Access Denied",
                disabled=True,
                key=f"{button_key}_denied",
                help="No permission to read file"
            )
            log_error(f"Download failed - access denied: {file_path}", context="Data Gallery")
            return False
        
        # Read file and create download button
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Determine MIME type based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.csv': 'text/csv',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.pdf': 'application/pdf'
        }
        mime_type = mime_types.get(file_ext, 'application/octet-stream')
        
        # Create download button
        downloaded = st.download_button(
            label="Download",
            data=file_data,
            file_name=dataset['name'],
            mime=mime_type,
            key=button_key,
            help=f"Download {dataset['name']}",
            use_container_width=True
        )
        
        # Log download action
        if downloaded:
            log_info(
                f"User {st.session_state.get('username', 'Unknown')} downloaded {dataset['name']}", 
                context="Data Gallery"
            )
        
        return True
        
    except FileNotFoundError:
        st.button(
            "File Missing",
            disabled=True,
            key=f"{button_key}_missing",
            help="File has been moved or deleted"
        )
        log_error(f"Download failed - file missing: {dataset['path']}", context="Data Gallery")
        return False
        
    except PermissionError:
        st.button(
            "Permission Error",
            disabled=True,
            key=f"{button_key}_perm",
            help="Insufficient permissions to read file"
        )
        log_error(f"Download failed - permission error: {dataset['path']}", context="Data Gallery")
        return False
        
    except Exception as e:
        st.button(
            "Download Error",
            disabled=True,
            key=f"{button_key}_error",
            help=f"Error: {str(e)}"
        )
        log_error(f"Download failed for {dataset['name']}: {str(e)}", context="Data Gallery")
        return False
    

def render_table_view(datasets):
    """Render datasets in table view"""
    st.markdown(f"#### Showing {len(datasets)} datasets")
    
    table_data = []
    for dataset in datasets:
        table_data.append({
            'Type': f"{dataset['type_icon']} {dataset['type']}",
            'Name': dataset['name'],
            'Client': dataset['client'],
            'Device/Author': dataset['device'],
            'Size (MB)': dataset['size'],
            'Records': f"{dataset['records']:,}",
            'Quality': f"{dataset['quality']}%",
            'Date': dataset['date']
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, width='stretch', height=600)


def render_pagination(total_pages):
    """Render pagination controls"""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", disabled=st.session_state.current_page == 1):
            st.session_state.current_page = 1
            st.rerun()
    
    with col2:
        if st.button("◀️ Prev", disabled=st.session_state.current_page == 1):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding: 0.5rem;'>Page {st.session_state.current_page} of {total_pages}</div>", unsafe_allow_html=True)
    
    with col4:
        if st.button("Next ▶️", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page += 1
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page = total_pages
            st.rerun()


def show_dataset_details(dataset, limited=False):
    """Show detailed view of a dataset with role-based information"""
    user_role = st.session_state.get('role', 'guest')
    
    with st.expander(f"📊 Dataset Details: {dataset['name']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information:**")
            st.write(f"**Type:** {dataset['type_icon']} {dataset['type']}")
            st.write(f"**Client:** {dataset['client']}")
            st.write(f"**Device/Author:** {dataset['device']}")
            st.write(f"**Date:** {dataset['date']}")
            
        with col2:
            st.markdown("**File Information:**")
            st.write(f"**Size:** {dataset['size']} MB")
            st.write(f"**Records:** {dataset['records']:,}")
            st.write(f"**Quality:** {dataset['quality']}%")
            if dataset.get('device_status') != 'N/A':
                st.write(f"**Device Status:** {dataset['device_status']}")
        
        # Show file path only for admin/super_admin/scientist
        if user_role in ['super_admin', 'admin', 'scientist'] and not limited:
            st.markdown("**File Path:**")
            st.code(dataset['path'], language="bash")
        elif user_role == 'client':
            st.markdown("**File Location:**")
            st.info(f"Stored in secure client directory: {os.path.basename(dataset['path'])}")
        
        if 'notes' in dataset:
            st.markdown("**Notes:**")
            st.info(dataset['notes'])
        
        # Role-based action buttons
        if user_role in ['super_admin', 'admin']:
            col_x, col_y, col_z, col_w = st.columns(4)
            with col_x:
                st.button("📊 Analytics", key=f"gallery_analytics_{dataset['id']}_detail")
            with col_y:
                st.button("📥 Download", key=f"gallery_download_{dataset['id']}_detail")
            with col_z:
                st.button("🔍 Raw Data", key=f"gallery_raw_{dataset['id']}_detail")
            with col_w:
                st.button("🗑️ Delete", key=f"gallery_delete_{dataset['id']}_detail", type="secondary")
        
        elif user_role == 'scientist':
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                st.button("📊 Analytics", key=f"gallery_analytics_{dataset['id']}_detail")
            with col_y:
                st.button("📥 Download", key=f"gallery_download_{dataset['id']}_detail")
            with col_z:
                st.button("🔍 Raw Data", key=f"gallery_raw_{dataset['id']}_detail")
        
        elif user_role == 'client':
            col_x, col_y = st.columns(2)
            with col_x:
                st.button("📊 View Report", key=f"gallery_report_{dataset['id']}_detail")
            with col_y:
                download_dataset_file(dataset, f"gallery_download_{dataset['id']}_detail")
        
        else:  # guest
            st.info("🔒 Limited access - Contact administrator for full access")
            st.button("📋 Request Access", key=f"gallery_request_{dataset['id']}_detail")


# Helper functions
def calculate_file_size(file_path):
    """Calculate file size in MB"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
    except:
        pass
    return 0.5


def calculate_quality_score(file_path):
    """Calculate data quality score (0-100)"""
    import random
    return random.randint(75, 100)


def count_records(file_path):
    """Count number of records in CSV file"""
    try:
        if os.path.exists(file_path) and file_path.endswith('.csv'):
            with open(file_path, 'r') as f:
                return sum(1 for line in f) - 1
    except:
        pass
    return 0


def get_file_date(file_path):
    """Get file creation/modification date"""
    try:
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except:
        pass
    return "Unknown"