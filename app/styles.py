# ============================================
# FILE: app/styles.py
# ============================================
import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styling to the application"""
    st.markdown("""
    <style>
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 0 !important;
        }
        
        .block-container {
            padding: 2rem 3rem !important;
            max-width: 1400px !important;
        }
        
        /* Welcome page hero */
        .hero-section {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            color: #cbd5e1;
            margin-bottom: 2rem;
            animation: fadeInUp 1s ease-out;
        }
        
        .hero-description {
            font-size: 1.1rem;
            color: #94a3b8;
            max-width: 800px;
            margin: 0 auto 2rem auto;
            line-height: 1.8;
            animation: fadeInUp 1.2s ease-out;
        }
        
        /* Feature cards */
        .feature-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: rgba(99, 102, 241, 0.5);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .feature-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 0.5rem;
        }
        
        .feature-text {
            color: #94a3b8;
            line-height: 1.6;
        }
        
        /* Login card */
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Dashboard cards */
        .stat-card {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #60a5fa;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .stat-change {
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }
        
        .stat-up {
            color: #10b981;
        }
        
        .stat-down {
            color: #ef4444;
        }
        
        /* Navigation */
        .nav-title {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .user-badge {
            background: rgba(99, 102, 241, 0.2);
            color: #a78bfa;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
            display: flex;
            align-items: center;  /* centers text vertically */
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #60a5fa;
        }
        
        /* Forms */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            color: #f8fafc;
            padding: 0.75rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: rgba(30, 41, 59, 0.5);
            border: 2px dashed rgba(148, 163, 184, 0.3);
            border-radius: 10px;
            padding: 2rem;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            color: #94a3b8;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            color: white;
        }
        
        /* Dataframe */
        .dataframe {
            background: rgba(30, 41, 59, 0.5) !important;
            border-radius: 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)
