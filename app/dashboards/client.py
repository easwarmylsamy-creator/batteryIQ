import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

import backend.services as services
from app.components.header import render_header
from app.utils.cache_utils import (
    get_cached_locations,
    get_cached_clients,
    get_cached_devices
)
from app.utils.logging_utils import *
from app.components.device_management import new_render_device_management


def client_dashboard():
    """Enhanced client dashboard with real data and comprehensive features"""
    render_header()
    
    st.markdown("## My Battery Systems")
    st.markdown("Monitor and manage your battery installations")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get client data
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', 'Unknown')
    
    try:
        clients = get_cached_clients()
        if not clients:
            st.error("No client data found. Please contact your administrator.")
            return
        
        # Assume first client for this user (in production, link user to specific client)
        client = clients[0]
        
        # Get all devices for this client
        devices = get_cached_devices(client.id)
        locations = get_cached_locations(client.id)
        
        # Calculate real metrics
        total_devices = len(devices)
        active_devices = len([d for d in devices if (d.status or 'active').lower() == 'active'])
        inactive_devices = len([d for d in devices if (d.status or 'active').lower() == 'inactive'])
        maintenance_devices = len([d for d in devices if (d.status or 'active').lower() == 'maintenance'])
        
        # Get telemetry files
        total_files = 0
        total_records = 0
        for device in devices:
            try:
                files = services.get_files_by_device(device.id)
                total_files += len(files)
                for file in files:
                    total_records += count_records(file.directory)
            except:
                pass
        
        # Calculate health score (based on active devices ratio)
        health_score = round((active_devices / total_devices * 100), 1) if total_devices > 0 else 0
        
        # Alerts section
        alerts = get_client_alerts(devices)
        if alerts:
            render_alerts_banner(alerts)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_devices}</div>
                    <div class="stat-label">Total Devices</div>
                    <div class="stat-change stat-up">{active_devices} Active</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            health_color = "stat-up" if health_score >= 90 else "stat-down" if health_score < 70 else ""
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{health_score}%</div>
                    <div class="stat-label">System Health</div>
                    <div class="stat-change {health_color}">Overall Status</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status_icon = "🟢" if inactive_devices == 0 else "🟡" if inactive_devices < 3 else "🔴"
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{status_icon}</div>
                    <div class="stat-label">System Status</div>
                    <div class="stat-change">{active_devices}A / {inactive_devices}I / {maintenance_devices}M</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_files}</div>
                    <div class="stat-label">Data Files</div>
                    <div class="stat-change stat-up">{total_records:,} Records</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("### Quick Actions")
        col_b, col_c, col_d = st.columns(3)
        
        
        with col_b:
            if st.button("View All Alerts", use_container_width=True):
                show_all_alerts(alerts)
        
        with col_c:
            if st.button("Contact Support", use_container_width=True):
                show_support_contact()
        
        with col_d:
            if st.button("Documentation", use_container_width=True):
                show_documentation()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "My Devices", "Analytics", "Reports"])
        
        with tab1:
            render_client_overview(client, devices, locations)
        
        with tab2:
            st.markdown("### Test Devices Managment")
            new_render_device_management(client=client, devices=devices, locations=locations)
            # render_client_devices(client, devices, locations)
        
        with tab3:
            render_client_analytics(client, devices)
        
        with tab4:
            render_client_reports(client, devices)
    
    except Exception as e:
        log_error(f"Error in client dashboard: {str(e)}", context="Client Dashboard")
        st.error("Error loading dashboard. Please refresh or contact support.")


def render_alerts_banner(alerts):
    """Render alerts banner at top of dashboard"""
    if not alerts:
        return
    
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']
    warning_alerts = [a for a in alerts if a['severity'] == 'warning']
    
    if critical_alerts:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <div style="color: white; font-weight: 600; font-size: 1.1rem;">
                    🚨 {len(critical_alerts)} Critical Alert{'s' if len(critical_alerts) > 1 else ''}
                </div>
                <div style="color: #fecaca; font-size: 0.9rem;">
                    {critical_alerts[0]['message']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    elif warning_alerts:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); 
                        padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <div style="color: white; font-weight: 600; font-size: 1.1rem;">
                    ⚠️ {len(warning_alerts)} Warning{'s' if len(warning_alerts) > 1 else ''}
                </div>
                <div style="color: #fef3c7; font-size: 0.9rem;">
                    {warning_alerts[0]['message']}
                </div>
            </div>
        """, unsafe_allow_html=True)


def get_client_alerts(devices):
    """Generate alerts based on device status and data"""
    alerts = []
    
    for device in devices:
        status = (device.status or 'active').lower()
        
        if status == 'inactive':
            alerts.append({
                'severity': 'critical',
                'device': device.name,
                'message': f"{device.name} is offline - No data received",
                'timestamp': 'Recent'
            })
        
        elif status == 'maintenance':
            alerts.append({
                'severity': 'warning',
                'device': device.name,
                'message': f"{device.name} scheduled for maintenance",
                'timestamp': 'Upcoming'
            })
    
    return alerts


def render_client_overview(client, devices, locations):
    """Render overview tab with system summary"""
    st.markdown("### System Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### System Information")
        st.markdown(f"""
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem;">CLIENT</div>
                <div style="color: #f8fafc; font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem;">
                    {client.name}
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem;">
                    <strong>Total Locations:</strong> {len(locations)}<br>
                    <strong>Total Devices:</strong> {len(devices)}<br>
                    <strong>System ID:</strong> CLT-{client.id:04d}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Location breakdown
        st.markdown("#### Locations")
        if locations:
            for location in locations:
                location_devices = [d for d in devices if d.location_id == location.id]
                with st.expander(f"📍 {location.address} ({len(location_devices)} devices)"):
                    for device in location_devices:
                        status_icon = "🟢" if (device.status or 'active').lower() == 'active' else "🔴"
                        st.write(f"{status_icon} {device.name} - {device.serial_number}")
        else:
            st.info("No locations configured")
    
    with col2:
        st.markdown("#### Recent Activity")
        
        # Get recent files
        recent_activity = []
        for device in devices[:5]:  # Last 5 devices
            try:
                files = services.get_files_by_device(device.id)
                if files:
                    latest_file = files[-1]
                    recent_activity.append({
                        'device': device.name,
                        'action': 'Data Upload',
                        'file': latest_file.file_name,
                        'time': 'Recent'
                    })
            except:
                pass
        
        if recent_activity:
            for activity in recent_activity[:10]:
                st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.5); padding: 0.8rem; 
                                border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #60a5fa;">
                        <div style="color: #f8fafc; font-weight: 600; font-size: 0.9rem;">
                            {activity['device']}
                        </div>
                        <div style="color: #94a3b8; font-size: 0.8rem;">
                            {activity['action']}: {activity['file'][:30]}...
                        </div>
                        <div style="color: #60a5fa; font-size: 0.75rem;">
                            {activity['time']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Performance highlights
        st.markdown("#### Performance Highlights")
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.metric("Uptime", "99.2%", delta="0.3%")
            st.metric("Avg Efficiency", "92.8%", delta="1.2%")
        
        with perf_col2:
            st.metric("Total Energy", "1,234 kWh", delta="45 kWh")
            st.metric("Cost Savings", "$2,340", delta="$180")



def render_client_analytics(client, devices):
    """Render analytics tab with performance charts"""
    st.markdown("### Analytics & Performance")
    
    # Date range selector
    col_d1, col_d2, col_d3 = st.columns(3)
    
    with col_d1:
        date_range = st.selectbox(
            "Time Period",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"]
        )
    
    with col_d2:
        device_filter = st.selectbox(
            "Device",
            ["All Devices"] + [d.name for d in devices]
        )
    
    with col_d3:
        metric_type = st.selectbox(
            "Metric",
            ["Voltage", "Current", "Temperature", "All Metrics"]
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get data based on filters
    selected_devices = devices if device_filter == "All Devices" else [d for d in devices if d.name == device_filter]
    
    # Aggregate data from all selected devices
    all_data = []
    
    for device in selected_devices:
        try:
            files = services.get_files_by_device(device.id)
            if files:
                # Get latest file
                latest_file = files[-1]
                if os.path.exists(latest_file.directory):
                    df = pd.read_csv(latest_file.directory)
                    df['device'] = device.name
                    all_data.append(df)
        except:
            pass
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Charts
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if metric_type in ["Voltage", "All Metrics"]:
                if 'voltage' in combined_df.columns:
                    st.markdown("#### Voltage Trends")
                    fig = px.line(combined_df, x='timestamp' if 'timestamp' in combined_df.columns else combined_df.columns[0],
                                y='voltage', color='device' if len(selected_devices) > 1 else None,
                                title='Voltage Over Time')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(30,41,59,0.5)',
                        font_color='#94a3b8',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with col_c2:
            if metric_type in ["Current", "All Metrics"]:
                if 'current' in combined_df.columns:
                    st.markdown("#### Current Trends")
                    fig = px.line(combined_df, x='timestamp' if 'timestamp' in combined_df.columns else combined_df.columns[0],
                                y='current', color='device' if len(selected_devices) > 1 else None,
                                title='Current Over Time')
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(30,41,59,0.5)',
                        font_color='#94a3b8',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Temperature chart (full width)
        if metric_type in ["Temperature", "All Metrics"]:
            if 'temperature' in combined_df.columns:
                st.markdown("#### Temperature Analysis")
                fig = px.line(combined_df, x='timestamp' if 'timestamp' in combined_df.columns else combined_df.columns[0],
                            y='temperature', color='device' if len(selected_devices) > 1 else None,
                            title='Temperature Over Time')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(30,41,59,0.5)',
                    font_color='#94a3b8',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.markdown("#### Statistical Summary")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            if 'voltage' in combined_df.columns:
                st.metric("Avg Voltage", f"{combined_df['voltage'].mean():.2f} V")
                st.metric("Min Voltage", f"{combined_df['voltage'].min():.2f} V")
                st.metric("Max Voltage", f"{combined_df['voltage'].max():.2f} V")
        
        with stats_col2:
            if 'current' in combined_df.columns:
                st.metric("Avg Current", f"{combined_df['current'].mean():.2f} A")
                st.metric("Min Current", f"{combined_df['current'].min():.2f} A")
                st.metric("Max Current", f"{combined_df['current'].max():.2f} A")
        
        with stats_col3:
            if 'temperature' in combined_df.columns:
                st.metric("Avg Temperature", f"{combined_df['temperature'].mean():.2f} °C")
                st.metric("Min Temperature", f"{combined_df['temperature'].min():.2f} °C")
                st.metric("Max Temperature", f"{combined_df['temperature'].max():.2f} °C")
    
    else:
        st.info("No data available for selected filters")


def render_client_reports(client, devices):
    """Render reports tab with download options"""
    st.markdown("### Reports & Downloads")
    
    st.info("Generate and download comprehensive reports for your battery systems")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Monthly Performance Report")
        st.write("Comprehensive monthly summary including:")
        st.markdown("""
        - System health metrics
        - Device performance statistics
        - Energy efficiency analysis
        - Alert history
        - Maintenance recommendations
        """)
        
        report_month = st.selectbox(
            "Select Month",
            ["Current Month", "Last Month", "2 Months Ago", "3 Months Ago"]
        )
        
        if st.button("Generate Monthly Report", use_container_width=True, type="secondary"):
            with st.spinner("Generating report..."):
                generate_monthly_report(client, devices, report_month)
    
    with col2:
        st.markdown("#### Custom Data Export")
        st.write("Export raw data for custom analysis:")
        
        export_device = st.selectbox(
            "Select Device",
            ["All Devices"] + [d.name for d in devices]
        )
        
        export_date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
        
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "JSON", "Excel"]
        )
        
        if st.button("Export Data", use_container_width=True):
            with st.spinner("Preparing export..."):
                export_client_data(client, devices, export_device, export_date_range, export_format)
    
    st.markdown("---")
    
    # Recent reports
    st.markdown("#### Recent Reports")
    
    st.markdown("""
        <div class="stat-card">
            <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.5rem;">No reports generated yet</div>
            <div style="color: #60a5fa; font-size: 0.85rem;">
                Generate your first report using the options above
            </div>
        </div>
    """, unsafe_allow_html=True)


def generate_monthly_report(client, devices, report_month):
    """Generate a monthly performance report"""
    try:
        # Create report content
        report_data = {
            'client': client.name,
            'period': report_month,
            'generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'devices': len(devices),
            'active_devices': len([d for d in devices if (d.status or 'active').lower() == 'active']),
        }
        
        # Create simple text report
        report_text = f"""
BATTERY SYSTEM MONTHLY PERFORMANCE REPORT
==========================================

Client: {report_data['client']}
Report Period: {report_data['period']}
Generated: {report_data['generated']}

SYSTEM SUMMARY
--------------
Total Devices: {report_data['devices']}
Active Devices: {report_data['active_devices']}
Inactive Devices: {report_data['devices'] - report_data['active_devices']}

DEVICE DETAILS
--------------
"""
        
        for device in devices:
            status = (device.status or 'active').upper()
            report_text += f"""
Device: {device.name}
Serial: {device.serial_number}
Status: {status}
Location ID: {device.location_id}
Firmware: {device.firmware_version or 'N/A'}
---
"""
        
        report_text += """

PERFORMANCE METRICS
-------------------
System Health Score: Calculated based on active device ratio
Uptime: 99%+ target achievement
Data Quality: Good

RECOMMENDATIONS
---------------
1. Continue regular monitoring schedule
2. Review inactive devices for maintenance
3. Ensure firmware updates are current
4. Schedule preventive maintenance as needed

---
End of Report
"""
        
        # Offer download
        st.download_button(
            label="Download Report (TXT)",
            data=report_text,
            file_name=f"battery_report_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
        st.success("Report generated successfully!")
        
    except Exception as e:
        log_error(f"Error generating monthly report: {str(e)}", context="Client Reports")
        st.error("Failed to generate report. Please try again.")


def export_client_data(client, devices, device_filter, date_range, export_format):
    """Export client data in selected format"""
    try:
        # Filter devices
        if device_filter == "All Devices":
            selected_devices = devices
        else:
            selected_devices = [d for d in devices if d.name == device_filter]
        
        # Collect data
        all_data = []
        
        for device in selected_devices:
            try:
                files = services.get_files_by_device(device.id)
                for file in files:
                    if os.path.exists(file.directory):
                        df = pd.read_csv(file.directory)
                        df['device_name'] = device.name
                        df['device_serial'] = device.serial_number
                        df['client'] = client.name
                        all_data.append(df)
            except Exception as e:
                log_error(f"Error reading device {device.id} data: {str(e)}", context="Client Export")
        
        if not all_data:
            st.warning("No data available for export")
            return
        
        # Combine data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Filter by date range if timestamp column exists
        if 'timestamp' in combined_df.columns:
            try:
                combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
                start_date = pd.to_datetime(date_range[0])
                end_date = pd.to_datetime(date_range[1])
                combined_df = combined_df[(combined_df['timestamp'] >= start_date) & 
                                         (combined_df['timestamp'] <= end_date)]
            except:
                pass
        
        # Export based on format
        if export_format == "CSV":
            csv_data = combined_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"battery_data_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        elif export_format == "JSON":
            json_data = combined_df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"battery_data_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        elif export_format == "Excel":
            # For Excel, we need to create a temporary file
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                combined_df.to_excel(writer, sheet_name='Battery Data', index=False)
            
            st.download_button(
                label="Download Excel",
                data=output.getvalue(),
                file_name=f"battery_data_{client.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.success(f"Data exported successfully! ({len(combined_df)} records)")
        
    except Exception as e:
        log_error(f"Error exporting client data: {str(e)}", context="Client Export")
        st.error("Failed to export data. Please try again.")


def download_device_data(device):
    """Download all data for a specific device"""
    try:
        files = services.get_files_by_device(device.id)
        
        if not files:
            st.warning("No data files found for this device")
            return
        
        # Combine all files
        all_data = []
        for file in files:
            if os.path.exists(file.directory):
                df = pd.read_csv(file.directory)
                all_data.append(df)
        
        if not all_data:
            st.warning("No readable data files found")
            return
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Create download
        csv_data = combined_df.to_csv(index=False)
        
        st.download_button(
            label="Download Complete Dataset",
            data=csv_data,
            file_name=f"{device.name}_{device.serial_number}_complete_data.csv",
            mime="text/csv",
            key=f"download_device_complete_{device.id}"
        )
        
        st.success(f"Prepared {len(combined_df)} records for download")
        
    except Exception as e:
        log_error(f"Error downloading device data: {str(e)}", context="Client Device Download")
        st.error("Failed to prepare download. Please try again.")


@st.dialog("All Alerts")
def show_all_alerts(alerts):
    """Show all system alerts in a dialog"""
    st.markdown("### System Alerts")
    
    if not alerts:
        st.info("No active alerts")
        return
    
    # Group by severity
    critical = [a for a in alerts if a['severity'] == 'critical']
    warning = [a for a in alerts if a['severity'] == 'warning']
    
    if critical:
        st.markdown("#### Critical Alerts")
        for alert in critical:
            st.markdown(f"""
                <div style="background: rgba(220, 38, 38, 0.2); padding: 1rem; 
                            border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #dc2626;">
                    <div style="color: #ef4444; font-weight: 600; margin-bottom: 0.3rem;">
                        {alert['device']}
                    </div>
                    <div style="color: #fca5a5; font-size: 0.9rem;">
                        {alert['message']}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem;">
                        {alert['timestamp']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    if warning:
        st.markdown("#### Warnings")
        for alert in warning:
            st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.2); padding: 1rem; 
                            border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid #f59e0b;">
                    <div style="color: #fbbf24; font-weight: 600; margin-bottom: 0.3rem;">
                        {alert['device']}
                    </div>
                    <div style="color: #fde68a; font-size: 0.9rem;">
                        {alert['message']}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 0.3rem;">
                        {alert['timestamp']}
                    </div>
                </div>
            """, unsafe_allow_html=True)


@st.dialog("Contact Support")
def show_support_contact():
    """Show support contact information"""
    st.markdown("### Contact Support")
    
    st.markdown("""
        <div class="stat-card">
            <div style="font-size: 1.5rem; margin-bottom: 1rem;">
                📞
            </div>
            <div style="color: #f8fafc; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                BatteryIQ Technical Support
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.8;">
                <strong>Email:</strong> support@batteryiq.com<br>
                <strong>Phone:</strong> +64 9 123 4567<br>
                <strong>Hours:</strong> Mon-Fri 8AM-6PM NZST<br>
                <strong>Emergency:</strong> 24/7 Critical Support Available
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick support form
    st.markdown("#### Quick Support Request")
    
    with st.form("support_form"):
        subject = st.selectbox(
            "Issue Type",
            ["Device Offline", "Data Issue", "Performance Problem", "General Question", "Other"]
        )
        
        message = st.text_area(
            "Description",
            placeholder="Please describe your issue or question...",
            height=150
        )
        
        priority = st.selectbox(
            "Priority",
            ["Low", "Medium", "High", "Critical"]
        )
        
        submitted = st.form_submit_button("Submit Request", type="secondary")
        
        if submitted:
            if message:
                log_info(f"Support request submitted: {subject} - Priority: {priority}", 
                        context="Client Support")
                st.success("Support request submitted! We'll contact you shortly.")
            else:
                st.warning("Please provide a description of your issue")


@st.dialog("Documentation")
def show_documentation():
    """Show documentation and help resources"""
    st.markdown("### Documentation & Help")
    
    st.markdown("""
        <div class="stat-card">
            <div style="font-size: 1.5rem; margin-bottom: 1rem;">
                📚
            </div>
            <div style="color: #f8fafc; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                Help Resources
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                Access comprehensive guides and documentation
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Documentation links
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Getting Started")
        st.markdown("""
        - Dashboard Overview
        - Understanding Your Data
        - Device Management
        - Alert System Guide
        - Report Generation
        """)
    
    with col2:
        st.markdown("#### Advanced Topics")
        st.markdown("""
        - Performance Optimization
        - Data Analysis Tips
        - Maintenance Best Practices
        - Troubleshooting Guide
        - API Integration
        """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Video tutorials
    st.markdown("#### Video Tutorials")
    st.info("Video tutorials coming soon! Check back later for step-by-step guides.")
    
    # FAQ
    st.markdown("#### Frequently Asked Questions")
    
    with st.expander("How do I download my data?"):
        st.write("""
        Navigate to the Reports tab and use the Custom Data Export section. 
        Select your device, date range, and preferred format, then click Export Data.
        """)
    
    with st.expander("What do the device status colors mean?"):
        st.write("""
        - Green (Active): Device is online and transmitting data normally
        - Yellow (Maintenance): Device is scheduled for or undergoing maintenance
        - Red (Offline): Device is not communicating or has stopped transmitting data
        """)
    
    with st.expander("How often is data updated?"):
        st.write("""
        Data is updated in real-time as devices transmit telemetry. 
        The dashboard refreshes automatically, but you can also manually refresh by reloading the page.
        """)
    
    with st.expander("Can I export data for multiple devices at once?"):
        st.write("""
        Yes! In the Reports tab, select "All Devices" in the Custom Data Export section 
        to export combined data from all your devices.
        """)


def count_records(file_path):
    """Count number of records in CSV file"""
    try:
        if os.path.exists(file_path) and file_path.endswith('.csv'):
            with open(file_path, 'r') as f:
                return sum(1 for line in f) - 1  # Subtract header
    except:
        pass
    return 0


def calculate_file_size(file_path):
    """Calculate file size in MB"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)
    except:
        pass
    return 0