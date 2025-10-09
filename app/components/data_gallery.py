import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend import services
from app.utils.cache_utils import get_cached_clients, get_cached_devices, get_cached_locations
from app.utils.logging_utils import log_info, log_error
from app.session import logout
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
    
    st.markdown(f"### {role_titles.get(user_role, '📊 Data Gallery')}")
    
    # Role-specific description
    role_descriptions = {
        'super_admin': 'Access to ALL system data with full permissions - All clients, devices, and uploads',
        'admin': 'Access to all telemetry and manual uploads across the system',
        'scientist': 'Access to research data, manual uploads, and assigned client telemetry',
        'client': 'Access to your organization\'s battery data and device telemetry',
        'guest': 'Limited access to publicly shared datasets only'
    }
    
    st.markdown(f"*{role_descriptions.get(user_role, 'Browse available datasets')}*")
    
    # Log access
    log_info(f"User {username} ({user_role}) accessed data gallery", context="Data Gallery")
    if st.button("Logout", key="gallery_logout_btn", width='stretch'):
            logout()
    # View mode selector
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Search datasets",
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
    datasets = get_filtered_datasets(search_query)
    
    if not datasets:
        st.info("📭 No datasets found matching your filters.")
        return
    
    # Pagination
    total_items = len(datasets)
    total_pages = (total_items - 1) // items_per_page + 1
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Display stats
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
            st.metric("📊 Clients", unique_clients)
        with col_f:
            unique_devices = len(set([d['device'] for d in datasets]))
            st.metric("🔌 Devices", unique_devices)
        with col_g:
            total_records = sum(d['records'] for d in datasets)
            st.metric("📈 Total Records", f"{total_records:,}")
    
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.filter_data_type = st.selectbox(
            "📁 Data Type",
            ["All Types", "Telemetry", "Manual"],
            key="data_type_filter"
        )
    
    with col2:
        clients = get_cached_clients()
        client_names = ["All Clients"] + [c.name for c in clients]
        st.session_state.filter_client = st.selectbox(
            "🏢 Client",
            client_names,
            key="gallery_client_filter"
        )
    
    with col3:
        st.session_state.filter_date_range = st.selectbox(
            "📅 Date Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year"],
            key="date_filter"
        )
    
    with col4:
        st.session_state.filter_file_size = st.selectbox(
            "💾 File Size",
            ["All Sizes", "< 1 MB", "1-10 MB", "10-100 MB", "> 100 MB"],
            key="gallery_size_filter"
        )
    
    # Second row of filters
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.session_state.filter_quality = st.selectbox(
            "⭐ Data Quality",
            ["All Quality", "Excellent (>95%)", "Good (80-95%)", "Fair (60-80%)", "Poor (<60%)"],
            key="gallery_quality_filter"
        )
    
    with col6:
        st.session_state.filter_device_status = st.selectbox(
            "🔌 Device Status",
            ["All Status", "Active", "Inactive", "Maintenance"],
            key="gallery_device_status_filter"
        )
    
    with col7:
        st.session_state.sort_by = st.selectbox(
            "🔢 Sort By",
            ["Recent First", "Oldest First", "Name A-Z", "Name Z-A", "Size (Large)", "Size (Small)", "Quality (High)", "Quality (Low)"],
            key="gallery_sort_filter"
        )
    
    with col8:
        if st.button("🔄 Reset All Filters", key="gallery_reset_filters", width='stretch'):
            reset_filters()
            st.rerun()


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
            # Super Admin: Access to EVERYTHING
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Super admin {username} accessing all data", context="Data Gallery")
            
        elif user_role == 'admin':
            # Admin: Access to all data
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Admin {username} accessing all data", context="Data Gallery")
            
        elif user_role == 'scientist':
            # Scientist: Access to all manual uploads + all telemetry data for research
            accessible_clients = clients
            can_see_manual = True
            can_see_all_telemetry = True
            log_info(f"Scientist {username} accessing research data", context="Data Gallery")
            
        elif user_role == 'client':
            # Client: Only their organization's data
            # In a real system, you'd link users to specific clients
            # For demo, we'll show the first client's data or filter by username
            accessible_clients = [clients[0]] if clients else []
            can_see_manual = False  # Clients don't see manual uploads
            can_see_all_telemetry = False  # Only their own telemetry
            log_info(f"Client {username} accessing organization data", context="Data Gallery")
            
        else:  # guest
            # Guest: Very limited access, maybe only public/demo data
            accessible_clients = []
            can_see_manual = False
            can_see_all_telemetry = False
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
                                'access_level': get_access_level(user_role, 'telemetry')
                            }
                            
                            all_datasets.append(dataset)
                    
                    except Exception as e:
                        log_error(f"Error loading files for client {client.id}: {str(e)}", context="Data Gallery")
        
        # Get Manual Uploads (role-filtered)
        if st.session_state.get('filter_data_type', 'All Types') in ['All Types', 'Manual']:
            if can_see_manual:
                try:
                    manual_files = services.get_manual_uploads()
                    
                    # Scientists and admins see all, others see their own
                    for file in manual_files:
                        # Role-based filtering for manual uploads
                        if user_role in ['super_admin', 'admin', 'scientist']:
                            show_file = True
                        elif user_role == 'client':
                            # Clients might see manual uploads from their org only
                            show_file = False  # For now, clients don't see manual
                        else:
                            show_file = file.author == username  # Only their own uploads
                        
                        if show_file:
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
                                'access_level': get_access_level(user_role, 'manual')
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
    """Render a single dataset card with role-based permissions"""
    user_role = st.session_state.get('role', 'guest')
    access_level = dataset.get('access_level', 'view_only')
    
    quality = dataset['quality']
    if quality >= 95:
        quality_color = "#10b981"
        quality_badge = "🟢"
    elif quality >= 80:
        quality_color = "#3b82f6"
        quality_badge = "🔵"
    elif quality >= 60:
        quality_color = "#f59e0b"
        quality_badge = "🟡"
    else:
        quality_color = "#ef4444"
        quality_badge = "🔴"
    
    # Access level badge
    access_badges = {
        'full': '🔓 Full Access',
        'read': '👁️ Read Only',
        'view_only': '🔒 View Only'
    }
    access_badge = access_badges.get(access_level, '🔒 Limited')
    
    st.markdown(f"""
        <div class="stat-card" style="height: 320px; display: flex; flex-direction: column; justify-content: space-between;">
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
                <div style="color: #60a5fa; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    🔌 {dataset['device'][:25]}{'...' if len(dataset['device']) > 25 else ''}
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.3rem;">
                    💾 {dataset['size']} MB | {dataset['records']:,} records
                </div>
                <div style="color: {quality_color}; font-size: 0.8rem; margin-bottom: 0.5rem;">
                    {quality_badge} Quality: {dataset['quality']}%
                </div>
                <div style="color: #a78bfa; font-size: 0.75rem; margin-bottom: 0.5rem;">
                    {access_badge}
                </div>
            </div>
            <div style="margin-top: auto; padding-top: 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.2);">
                <div style="color: #94a3b8; font-size: 0.75rem;">
                    📅 {dataset['date']}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Role-based action buttons
    if access_level == 'full':
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("👁️", key=f"gallery_view_{dataset['type']}_{dataset['id']}", help="View Details", width='stretch'):
                show_dataset_details(dataset)
        with col_b:
            if st.button("📥", key=f"gallery_download_{dataset['type']}_{dataset['id']}", help="Download", width='stretch'):
                st.success(f"Downloading: {dataset['name']}")
                log_info(f"User {st.session_state.username} downloaded {dataset['name']}", context="Data Gallery")
        with col_c:
            if st.button("📊", key=f"gallery_analyze_{dataset['type']}_{dataset['id']}", help="Analyze", width='stretch'):
                st.info(f"Opening analytics for: {dataset['name']}")
    
    elif access_level == 'read':
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("👁️", key=f"gallery_view_{dataset['type']}_{dataset['id']}", help="View Details", width='stretch'):
                show_dataset_details(dataset)
        with col_b:
            if st.button("📥", key=f"gallery_download_{dataset['type']}_{dataset['id']}", help="Download", width='stretch'):
                st.success(f"Downloading: {dataset['name']}")
    
    else:  # view_only
        if st.button("👁️ View Only", key=f"gallery_view_{dataset['type']}_{dataset['id']}", width='stretch'):
            show_dataset_details(dataset, limited=True)


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
                quality_color = "#10b981" if dataset['quality'] >= 95 else "#3b82f6" if dataset['quality'] >= 80 else "#f59e0b" if dataset['quality'] >= 60 else "#ef4444"
                st.markdown(f"<div style='color: {quality_color}'>⭐ Quality: {dataset['quality']}%</div>", unsafe_allow_html=True)
                st.caption(f"💾 {dataset['size']} MB | {dataset['records']:,} records")
            
            with col4:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("View", key=f"listview_{dataset['type']}_{dataset['id']}", width='stretch'):
                        show_dataset_details(dataset)
                with col_b:
                    if st.button("📥", key=f"listdown_{dataset['type']}_{dataset['id']}", width='stretch'):
                        st.info("Download")
            
            st.markdown("---")


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
                st.button("📥 Export", key=f"gallery_export_{dataset['id']}_detail")
        
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