# ============================================
# FILE: app/pages/welcome.py
# ============================================
import streamlit as st

def render():
    """Render the welcome page"""
    st.markdown("""
        <div class="hero-section">
            <div class="hero-title">BatteryIQ</div>
            <div class="hero-subtitle">Intelligent Battery Management Platform</div>
            <div class="hero-description">
                Transform your battery data into actionable insights. Monitor performance, 
                predict failures, and optimize energy systems with our advanced analytics platform.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Real-Time Analytics</div>
                <div class="feature-text">
                    Monitor battery performance with live dashboards, 
                    advanced metrics, and predictive insights.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Secure & Role-Based</div>
                <div class="feature-text">
                    Enterprise-grade security with granular access control 
                    for different user roles and permissions.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🚀</div>
                <div class="feature-title">Easy Integration</div>
                <div class="feature-text">
                    Seamlessly integrate with your existing systems via 
                    APIs, file uploads, or automated telemetry.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # CTA button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Get Started", width='stretch', type="primary"):
            st.session_state.page = 'login'
            st.rerun()
        if st.button("Test", width='stretch'):
            st.session_state.page = 'testLogin'
            st.rerun()