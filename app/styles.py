# app/styles.py
import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styling to the application - Battery Theme"""
    st.markdown("""
    <style>
        /* ============================================
           GLOBAL STYLES
           ============================================ */
        
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
        
        /* ============================================
           WELCOME PAGE
           ============================================ */
        
        /* Hero section */
        .hero-section {
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #284940 0%, #327552 100%);
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            background: linear-gradient(135deg, #48B88E 0%, #53CDA8 100%);
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
            border: 1px solid rgba(83, 205, 168, 0.2);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: rgba(83, 205, 168, 0.5);
            box-shadow: 0 10px 30px rgba(83, 205, 168, 0.2);
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
        
        /* ============================================
           LOGIN PAGE
           ============================================ */
        
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* ============================================
           DASHBOARD COMPONENTS
           ============================================ */
        
        /* Stat cards */
        .stat-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
            border: 1px solid rgba(83, 205, 168, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(83, 205, 168, 0.3);
            border-color: rgba(83, 205, 168, 0.4);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #53CDA8;
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
            color: #48B88E;
        }
        
        .stat-down {
            color: #ef4444;
        }
        
        /* ============================================
           NAVIGATION
           ============================================ */
        
        .nav-title {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #48B88E 0%, #53CDA8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .user-badge {
            background: rgba(83, 205, 168, 0.2);
            color: #53CDA8;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(83, 205, 168, 0.3);
        }
        
        /* Tab Navigation Buttons (custom button-based tabs) */
        div[data-testid="column"] > div > div > div > button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        /* Inactive tab style */
        div[data-testid="column"] > div > div > div > button[kind="secondary"] {
            background: linear-gradient(135deg, rgba(40, 73, 64, 0.6) 0%, rgba(50, 117, 82, 0.6) 100%);
            color: #94a3b8;
            border: 1px solid rgba(83, 205, 168, 0.2);
        }
        
        div[data-testid="column"] > div > div > div > button[kind="secondary"]:hover {
            background: linear-gradient(135deg, rgba(50, 117, 82, 0.8) 0%, rgba(60, 159, 113, 0.8) 100%);
            color: #cbd5e1;
            transform: translateY(-2px);
            border-color: rgba(83, 205, 168, 0.4);
            box-shadow: 0 4px 12px rgba(83, 205, 168, 0.2);
        }
        
        /* Active tab style */
        div[data-testid="column"] > div > div > div > button[kind="primary"] {
            background: linear-gradient(135deg, #327552 0%, #48B88E 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(83, 205, 168, 0.4);
            border: 1px solid rgba(83, 205, 168, 0.3);
        }
        
        div[data-testid="column"] > div > div > div > button[kind="primary"]:hover {
            background: linear-gradient(135deg, rgba(40, 73, 64, 0.6) 0%, rgba(50, 117, 82, 0.6) 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(83, 205, 168, 0.5);
        }
        
        /* ============================================
           BUTTONS (ALL TYPES)
           ============================================ */
        
        /* Base button styles */
        button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        /* Regular primary buttons */
        .stButton > button,
        button[kind="primary"]:not([data-testid="stFormSubmitButton"] *) {
            background: linear-gradient(135deg, #327552 0%, #48B88E 100%) !important;
            color: white !important;
            padding: 0.75rem 2rem !important;
            box-shadow: 0 4px 15px rgba(83, 205, 168, 0.3) !important;
            border: none !important;
        }
        
        .stButton > button:hover,
        button[kind="primary"]:not([data-testid="stFormSubmitButton"] *):hover {
            background: linear-gradient(135deg, #48B88E 0%, #53CDA8 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(83, 205, 168, 0.4) !important;
        }
        
        /* Secondary buttons */
        .stButton > button[kind="secondary"],
        button[kind="secondary"]:not([data-testid="stFormSubmitButton"] *) {
            background: linear-gradient(135deg, rgba(40, 73, 64, 0.6) 0%, rgba(50, 117, 82, 0.6) 100%) !important;
            border: 1px solid rgba(83, 205, 168, 0.3) !important;
            color: #94a3b8 !important;
        }
        
        .stButton > button[kind="secondary"]:hover,
        button[kind="secondary"]:not([data-testid="stFormSubmitButton"] *):hover {
            background: linear-gradient(135deg, rgba(50, 117, 82, 0.8) 0%, rgba(60, 159, 113, 0.8) 100%) !important;
            color: #cbd5e1 !important;
        }
        
        /* Form submit buttons */
        button[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #327552 0%, #48B88E 100%) !important;
            color: white !important;
            padding: 0.75rem 2rem !important;
            box-shadow: 0 4px 15px rgba(83, 205, 168, 0.3) !important;
            border: none !important;
        }
        
        button[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #48B88E 0%, #53CDA8 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(83, 205, 168, 0.4) !important;
        }
        
                
        /* ============================================
           ANIMATIONS
           ============================================ */
        
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
        
        /* ============================================
           METRICS
           ============================================ */
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            color: #53CDA8 !important;
        }
        
        [data-testid="stMetricDelta"] svg {
            fill: #48B88E !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #48B88E !important;
        }
        
        /* ============================================
           FORMS
           ============================================ */
        
        /* Text inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            border-radius: 10px !important;
            color: #f8fafc !important;
            padding: 0.75rem !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #53CDA8 !important;
            box-shadow: 0 0 0 2px rgba(83, 205, 168, 0.2) !important;
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            border-radius: 10px !important;
        }
        
        .stSelectbox > div > div:focus-within {
            border-color: #53CDA8 !important;
        }
        
        /* File uploader */
        [data-testid="stFileUploader"] {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 2px dashed rgba(83, 205, 168, 0.3) !important;
            border-radius: 10px !important;
            padding: 2rem !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(83, 205, 168, 0.5) !important;
            background: rgba(40, 73, 64, 0.3) !important;
        }
        
        /* ============================================
           TABS (Streamlit native tabs)
           ============================================ */
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            border-bottom: 2px solid rgba(83, 205, 168, 0.2);
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(40, 73, 64, 0.5);
            border-radius: 10px 10px 0 0;
            padding: 0.75rem 1.5rem;
            color: #94a3b8;
            border: 1px solid rgba(83, 205, 168, 0.2);
            border-bottom: none;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(50, 117, 82, 0.6);
            color: #cbd5e1;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #327552 0%, #48B88E 100%);
            color: white !important;
            border-color: rgba(83, 205, 168, 0.4);
        }
        
        /* ============================================
           DATAFRAME
           ============================================ */
        
        .dataframe {
            background: rgba(30, 41, 59, 0.5) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
        }
        
        /* Dataframe headers */
        .dataframe thead tr th {
            background: rgba(40, 73, 64, 0.6) !important;
            color: #53CDA8 !important;
            border-bottom: 2px solid rgba(83, 205, 168, 0.3) !important;
            font-weight: 600 !important;
        }
        
        /* Dataframe rows */
        .dataframe tbody tr:hover {
            background: rgba(83, 205, 168, 0.1) !important;
        }
        
        .dataframe tbody tr td {
            border-bottom: 1px solid rgba(83, 205, 168, 0.1) !important;
        }
        
        /* ============================================
           ALERTS & MESSAGES
           ============================================ */
        
        /* Info boxes */
        [data-testid="stAlert"] {
            background: rgba(30, 41, 59, 0.8) !important;
            border-left: 4px solid #53CDA8 !important;
            border-radius: 10px !important;
        }
        
        /* Success messages */
        [data-testid="stSuccess"] {
            background: rgba(72, 184, 142, 0.1) !important;
            border-left: 4px solid #48B88E !important;
            color: #53CDA8 !important;
        }
        
        /* Error messages */
        [data-testid="stError"] {
            background: rgba(239, 68, 68, 0.1) !important;
            border-left: 4px solid #ef4444 !important;
        }
        
        /* Warning messages */
        [data-testid="stWarning"] {
            background: rgba(245, 158, 11, 0.1) !important;
            border-left: 4px solid #f59e0b !important;
        }
        
        /* Info messages */
        [data-testid="stInfo"] {
            background: rgba(83, 205, 168, 0.1) !important;
            border-left: 4px solid #53CDA8 !important;
        }
        
        /* ============================================
           EXPANDER
           ============================================ */
        
        [data-testid="stExpander"] {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            border-radius: 10px !important;
        }
        
        [data-testid="stExpander"]:hover {
            border-color: rgba(83, 205, 168, 0.4) !important;
        }
        
        details[data-testid="stExpander"] summary {
            background: rgba(40, 73, 64, 0.5) !important;
            border-radius: 10px !important;
            padding: 1rem !important;
        }
        
        details[data-testid="stExpander"] summary:hover {
            background: rgba(50, 117, 82, 0.6) !important;
        }
        
        /* ============================================
           PROGRESS & LOADING
           ============================================ */
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(135deg, #327552 0%, #53CDA8 100%) !important;
        }
        
        /* Spinner */
        .stSpinner > div > div {
            border-top-color: #53CDA8 !important;
            border-right-color: rgba(83, 205, 168, 0.3) !important;
            border-bottom-color: rgba(83, 205, 168, 0.3) !important;
            border-left-color: rgba(83, 205, 168, 0.3) !important;
        }
        
        /* ============================================
           FORM CONTROLS
           ============================================ */
        
        /* Slider */
        .stSlider > div > div > div > div {
            background: #53CDA8 !important;
        }
        
        /* Checkbox */
        .stCheckbox > label > div[data-checked="true"] {
            background: #48B88E !important;
            border-color: #48B88E !important;
        }
        
        /* Radio buttons */
        .stRadio > label > div[data-checked="true"] {
            background: #48B88E !important;
        }
        
        .stRadio > label > div[data-checked="true"]::before {
            background: #53CDA8 !important;
        }
        
        /* Toggle/Switch */
        input[type="checkbox"][role="switch"]:checked {
            background: #48B88E !important;
        }
        
        /* ============================================
           LINKS
           ============================================ */
        
        a {
            color: #53CDA8 !important;
            text-decoration: none;
        }
        
        a:hover {
            color: #48B88E !important;
            text-decoration: underline;
        }
        
        /* ============================================
           SIDEBAR
           ============================================ */
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
            border-right: 1px solid rgba(83, 205, 168, 0.2) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
        }
        
        /* ============================================
           MULTISELECT
           ============================================ */
        
        .stMultiSelect [data-baseweb="tag"] {
            background: rgba(83, 205, 168, 0.2) !important;
            border: 1px solid rgba(83, 205, 168, 0.3) !important;
            color: #53CDA8 !important;
        }
        
        /* ============================================
           DATE & TIME INPUTS
           ============================================ */
        
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input {
            background: rgba(30, 41, 59, 0.8) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            color: #f8fafc !important;
            border-radius: 10px !important;
        }
        
        /* ============================================
           PLOTLY CHARTS
           ============================================ */
        
        .js-plotly-plot .plotly {
            border-radius: 10px !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
        }
        
        /* ============================================
           CODE BLOCKS
           ============================================ */
        
        .stCodeBlock {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            border-radius: 10px !important;
        }
        
        code {
            color: #53CDA8 !important;
            background: rgba(40, 73, 64, 0.3) !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
        }
        
        pre {
            background: rgba(15, 23, 42, 0.8) !important;
            border: 1px solid rgba(83, 205, 168, 0.2) !important;
            border-radius: 10px !important;
        }
        
        /* ============================================
           TOOLTIPS
           ============================================ */
        
        [data-testid="stTooltipIcon"] {
            color: #53CDA8 !important;
        }
        
        /* ============================================
           MARKDOWN HEADERS
           ============================================ */
        
        h1, h2, h3 {
            color: #f8fafc !important;
        }
        
        h1 {
            border-bottom: 2px solid rgba(83, 205, 168, 0.3);
            padding-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    