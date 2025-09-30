# ============================================
# FILE: app/utils/data_utils.py
# ============================================
import pandas as pd
import numpy as np
from datetime import datetime

def generate_sample_battery_data(days=30):
    """Generate sample battery data for visualization"""
    dates = pd.date_range(end=datetime.now(), periods=days*24, freq='H')
    np.random.seed(42)
    
    voltage = 3.7 + 0.3 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 0.05, len(dates))
    current = 0.5 + 0.2 * np.cos(np.arange(len(dates)) * 0.15) + np.random.normal(0, 0.03, len(dates))
    temperature = 25 + 5 * np.sin(np.arange(len(dates)) * 0.08) + np.random.normal(0, 1, len(dates))
    
    return pd.DataFrame({
        'timestamp': dates,
        'voltage': voltage,
        'current': current,
        'temperature': temperature
    })
