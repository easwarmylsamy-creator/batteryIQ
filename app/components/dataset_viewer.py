# app/components/dataset_viewer.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend import services
from app.utils.cache_utils import get_cached_clients, get_cached_devices, get_cached_locations
from app.utils.logging_utils import log_info, log_error

def render_dataset_viewer():
    """
    Comprehensive dataset viewer with grid/list views, filtering, and sorting
    """
    st.markdown("###Dataset Browser")
    st.markdown("Browse all available battery datasets with advanced filtering")
    
    # View mode selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### Select View Mode")
    
    with col2:
        view_mode = st.radio(
            "View",
            ["Grid View", "List View"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    st.markdown("---")
    
    # Filtering Section
    render_filters()
    
    st.markdown("---")
    
    # Get filtered data
    datasets = get_filtered_datasets()
    
    if not datasets:
        st.info("No datasets found matching your filters.")
        return
    
    # Display based on view mode
    if view_mode == "Grid View":
        render_grid_view(datasets)
    else:
        render_list_view(datasets)


def render_filters():
    """Render all filter options"""
    st.markdown("#### 🔍 Filters & Sorting")
    
    # Create 4 columns for filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Data Type Filter
        st.session_state.filter_data_type = st.selectbox(
            "Data Type",
            ["All Types", "Telemetry (Auto)", "Manual (Lab)", "Processed", "Raw"],
            key="data_type_filter"
        )
    
    with col2:
        # Client Filter
        clients = get_cached_clients()
        client_names = ["All Clients"] + [c.name for c in clients]
        st.session_state.filter_client = st.selectbox(
            "Client",
            client_names,
            key=f"{COMPONENT_ID}_client_filter"
        )
    
    with col3:
        # Date Range Filter
        st.session_state.filter_date_range = st.selectbox(
            "Date Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days", "This Year", "Custom"],
            key=f"{COMPONENT_ID}_date_filter"
        )
    
    with col4:
        # File Size Filter
        st.session_state.filter_file_size = st.selectbox(
            "File Size",
            ["All Sizes", "< 1 MB", "1-10 MB", "10-100 MB", "> 100 MB"],
            key="size_filter"
        )
    
    # Second row of filters
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        # Status Filter
        st.session_state.filter_status = st.selectbox(
            "✅ Status",
            ["All Status", "Valid", "Processing", "Error", "Archived"],
            key="status_filter"
        )
    
    with col6:
        # Device Filter (if applicable)
        st.session_state.filter_device = st.selectbox(
            "🔌 Device",
            ["All Devices", "Active Only", "Inactive", "Maintenance"],
            key="device_filter"
        )
    
    with col7:
        # Data Quality Filter
        st.session_state.filter_quality = st.selectbox(
            "⭐ Data Quality",
            ["All Quality", "Excellent (>95%)", "Good (80-95%)", "Fair (60-80%)", "Poor (<60%)"],
            key="quality_filter"
        )
    
    with col8:
        # Sort Options
        st.session_state.sort_by = st.selectbox(
            "🔢 Sort By",
            ["Recent First", "Oldest First", "Name A-Z", "Name Z-A", "Size (Large)", "Size (Small)", "Client Name"],
            key="sort_filter"
        )
    
    # Custom date range (if selected)
    if st.session_state.filter_date_range == "Custom":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.session_state.custom_start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=30)
            )
        with col_d2:
            st.session_state.custom_end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
    
    # Search bar
    st.session_state.search_query = st.text_input(
        "🔍 Search datasets",
        placeholder="Search by filename, device, client, or keywords...",
        key=f"{COMPONENT_ID}_search_input"
    )
    
    # Quick action buttons
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        if st.button("🔄 Reset Filters", use_container_width=True):
            reset_filters()
            st.rerun()
    with col_b:
        if st.button("📥 Export Results", use_container_width=True):
            st.info("Export functionality")
    with col_c:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Report generation")
    with col_d:
        if st.button("⚙️ Save Filter Preset", use_container_width=True):
            st.info("Save current filters")


def reset_filters():
    """Reset all filters to default"""
    st.session_state.filter_data_type = "All Types"
    st.session_state.filter_client = "All Clients"
    st.session_state.filter_date_range = "All Time"
    st.session_state.filter_file_size = "All Sizes"
    st.session_state.filter_status = "All Status"
    st.session_state.filter_device = "All Devices"
    st.session_state.filter_quality = "All Quality"
    st.session_state.sort_by = "Recent First"
    st.session_state.search_query = ""


def get_filtered_datasets():
    """
    Get datasets based on applied filters
    Returns list of dataset dictionaries
    """
    all_datasets = []
    
    try:
        clients = get_cached_clients()
        
        # Get Telemetry Data
        if st.session_state.get('filter_data_type', 'All Types') in ['All Types', 'Telemetry (Auto)']:
            for client in clients:
                # Apply client filter
                if st.session_state.get('filter_client', 'All Clients') not in ['All Clients', client.name]:
                    continue
                
                try:
                    files = services.get_files_by_client(client.id)
                    for file in files:
                        device = services.get_device(file.device_id) if file.device_id else None
                        
                        # Build dataset object
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
                            'date': 'Recent',  # You might want to add timestamp field
                            'size': calculate_file_size(file.directory),
                            'status': 'Valid',
                            'quality': calculate_quality_score(file.directory),
                            'records': count_records(file.directory)
                        }
                        
                        all_datasets.append(dataset)
                
                except Exception as e:
                    log_error(f"Error loading files for client {client.id}: {str(e)}", context="Dataset Viewer")
        
        # Get Manual Uploads
        if st.session_state.get('filter_data_type', 'All Types') in ['All Types', 'Manual (Lab)']:
            try:
                manual_files = services.get_manual_uploads()
                for file in manual_files:
                    dataset = {
                        'id': file.id,
                        'type': 'Manual',
                        'type_icon': '📝',
                        'name': file.file_directory.split('/')[-1],
                        'client': 'N/A',
                        'device': file.author,
                        'device_status': 'N/A',
                        'location_id': 'N/A',
                        'path': file.file_directory,
                        'date': file.recorded_date.strftime("%Y-%m-%d %H:%M"),
                        'size': calculate_file_size(file.file_directory),
                        'status': 'Valid',
                        'quality': calculate_quality_score(file.file_directory),
                        'records': count_records(file.file_directory),
                        'notes': file.notes
                    }
                    
                    all_datasets.append(dataset)
            
            except Exception as e:
                log_error(f"Error loading manual files: {str(e)}", context="Dataset Viewer")
        
        # Apply filters
        filtered_datasets = apply_filters(all_datasets)
        
        # Apply sorting
        sorted_datasets = apply_sorting(filtered_datasets)
        
        return sorted_datasets
    
    except Exception as e:
        log_error(f"Error in get_filtered_datasets: {str(e)}", context="Dataset Viewer")
        return []


def apply_filters(datasets):
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
    
    # Status filter
    status_filter = st.session_state.get('filter_status', 'All Status')
    if status_filter != 'All Status':
        filtered = [d for d in filtered if d['status'] == status_filter]
    
    # Device filter
    device_filter = st.session_state.get('filter_device', 'All Devices')
    if device_filter != 'All Devices':
        if device_filter == 'Active Only':
            filtered = [d for d in filtered if d.get('device_status', '').lower() == 'active']
        elif device_filter == 'Inactive':
            filtered = [d for d in filtered if d.get('device_status', '').lower() == 'inactive']
    
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
    search_query = st.session_state.get('search_query', '').lower()
    if search_query:
        filtered = [d for d in filtered if 
                   search_query in d['name'].lower() or
                   search_query in d['client'].lower() or
                   search_query in d['device'].lower()]
    
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
    elif sort_by == "Client Name":
        return sorted(datasets, key=lambda x: x['client'])
    
    return datasets


def calculate_file_size(file_path):
    """Calculate file size in MB"""
    try:
        import os
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
    except:
        pass
    return 0.5  # Default size if can't calculate


def calculate_quality_score(file_path):
    """Calculate data quality score (0-100)"""
    # This is a placeholder - implement your actual quality scoring logic
    import random
    return random.randint(75, 100)


def count_records(file_path):
    """Count number of records in CSV file"""
    try:
        import os
        if os.path.exists(file_path) and file_path.endswith('.csv'):
            with open(file_path, 'r') as f:
                return sum(1 for line in f) - 1  # Subtract header
    except:
        pass
    return 0


def render_grid_view(datasets):
    """Render datasets in grid/card view"""
    st.markdown(f"### 📊 Grid View - {len(datasets)} datasets found")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display in grid (3 cards per row)
    cols_per_row = 3
    
    for i in range(0, len(datasets), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(datasets):
                dataset = datasets[i + j]
                
                with col:
                    render_dataset_card(dataset)


def render_dataset_card(dataset):
    """Render a single dataset card"""
    
    # Quality color
    quality = dataset['quality']
    if quality >= 95:
        quality_color = "#10b981"  # Green
    elif quality >= 80:
        quality_color = "#3b82f6"  # Blue
    elif quality >= 60:
        quality_color = "#f59e0b"  # Yellow
    else:
        quality_color = "#ef4444"  # Red
    
    # Card HTML
    st.markdown(f"""
        <div class="stat-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                    {dataset['type_icon']}
                </div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-bottom: 0.5rem;">
                    {dataset['name'][:30]}{'...' if len(dataset['name']) > 30 else ''}
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    {dataset['type']} | {dataset['client']}
                </div>
                <div style="color: #60a5fa; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    🔌 {dataset['device'][:20]}{'...' if len(dataset['device']) > 20 else ''}
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.3rem;">
                    💾 {dataset['size']} MB | {dataset['records']} records
                </div>
                <div style="color: {quality_color}; font-size: 0.8rem; margin-bottom: 0.5rem;">
                    ⭐ Quality: {dataset['quality']}%
                </div>
            </div>
            <div style="margin-top: auto; padding-top: 0.5rem; border-top: 1px solid rgba(148, 163, 184, 0.2);">
                <div style="color: #94a3b8; font-size: 0.75rem;">
                    📅 {dataset['date']}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("👁️", key=f"{COMPONENT_ID}_view_{dataset['id']}", help="View", use_container_width=True):
            show_dataset_details(dataset)
    with col_b:
        if st.button("📥", key=f"download_{dataset['id']}", help="Download", use_container_width=True):
            st.info(f"Download: {dataset['name']}")
    with col_c:
        if st.button("📊", key=f"analyze_{dataset['id']}", help="Analyze", use_container_width=True):
            st.info(f"Analyze: {dataset['name']}")


def render_list_view(datasets):
    """Render datasets in list/table view"""
    st.markdown(f"### 📋 List View - {len(datasets)} datasets found")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Prepare data for table
    table_data = []
    for dataset in datasets:
        table_data.append({
            'Type': f"{dataset['type_icon']} {dataset['type']}",
            'Name': dataset['name'],
            'Client': dataset['client'],
            'Device/Author': dataset['device'],
            'Size (MB)': dataset['size'],
            'Records': dataset['records'],
            'Quality': f"{dataset['quality']}%",
            'Status': dataset['status'],
            'Date': dataset['date']
        })
    
    df = pd.DataFrame(table_data)
    
    # Display table
    st.dataframe(df, use_container_width=True, height=600)
    
    # Selection for bulk actions
    st.markdown("#### 🔧 Bulk Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Download Selected", use_container_width=True):
            st.info("Bulk download feature")
    with col2:
        if st.button("🗑️ Delete Selected", use_container_width=True):
            st.warning("Bulk delete feature")
    with col3:
        if st.button("📊 Analyze Selected", use_container_width=True):
            st.info("Bulk analysis feature")
    with col4:
        if st.button("📤 Export Table", use_container_width=True):
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "datasets.csv", "text/csv")


def show_dataset_details(dataset):
    """Show detailed view of a dataset in a modal-like expander"""
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
            st.write(f"**Status:** {dataset['status']}")
        
        st.markdown("**File Path:**")
        st.code(dataset['path'], language="bash")
        
        if 'notes' in dataset:
            st.markdown("**Notes:**")
            st.info(dataset['notes'])
        
        # Actions
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.button("📊 Open in Analytics", key=f"analytics_{dataset['id']}_detail")
        with col_y:
            st.button("📥 Download File", key=f"download_{dataset['id']}_detail")
        with col_z:
            st.button("🔍 View Raw Data", key=f"raw_{dataset['id']}_detail")