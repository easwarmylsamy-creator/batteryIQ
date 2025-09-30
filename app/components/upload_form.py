# ============================================
# FILE: app/components/upload_form.py
# ============================================
import streamlit as st
import pandas as pd
from datetime import datetime
from backend.ingestion import process_file
from app.utils.logging_utils import *

def render_upload_interface():
    """Render manual upload interface"""
    st.markdown("### Manual Data Upload")
    
    st.info("**Note:** Telemetry data is automatically collected from devices. Use this form to upload manual lab results or experimental data.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("manual_upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            author = st.text_input(
                "Author/Researcher Name *", 
                value=st.session_state.username or "",
                help="Name of the person conducting the experiment"
            )
        
        with col2:
            upload_date = st.date_input(
                "Experiment Date",
                value=datetime.now(),
                help="Date when the data was collected"
            )
        
        notes = st.text_area(
            "Notes/Description *", 
            placeholder="Describe the experiment, conditions, battery type, testing parameters, etc.",
            help="Provide detailed information about this upload",
            height=100
        )
        
        uploaded_file = st.file_uploader(
            "Choose CSV file *",
            type="csv",
            help="Upload battery test data in CSV format"
        )
        
        # File preview
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                uploaded_file.seek(0)
                
                st.markdown("#### File Preview")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Rows", len(df))
                with col_b:
                    st.metric("Columns", len(df.columns))
                with col_c:
                    st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
                
                st.dataframe(df.head(10), use_container_width=True)
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Upload Manual Data", type="primary", use_container_width=True)
        
        if submitted:
            if not author or not notes or not uploaded_file:
                log_warning("Manual upload attempted with missing fields", context="Upload")
                st.error("Please fill in all required fields (marked with *)")
            else:
                log_info(f"Manual upload started by {author}", context="Upload")
                with st.spinner("Processing upload..."):
                    try:
                        result = process_file(
                            uploaded_file=uploaded_file,
                            author=author,
                            notes=notes
                        )
                        
                        if result["success"]:
                            log_info(f"Manual upload successful by {author}: {uploaded_file.name}", context="Upload")
                            st.success("Manual file uploaded successfully!")
                            st.balloons()
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            log_error(f"Manual upload failed for {author}: {result['message']}", context="Upload")
                            st.error(f"Upload failed: {result['message']}")
                    
                    except Exception as e:
                        log_error(f"Manual upload exception for {author}: {str(e)}", context="Upload")
                        st.error(f"Error: {str(e)}")
