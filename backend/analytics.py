# backend/analytics.py
import csv
import pandas as pd
import numpy as np
from statistics import mean, median, stdev
from typing import Dict, List, Optional, Tuple
import os
import logging

from db.session import get_session
from db.models import BatteryData, Metrics

logger = logging.getLogger(__name__)

def compute_metrics(file_path: str, battery_data_id: int) -> Optional[Metrics]:
    """
    Compute comprehensive metrics from a battery CSV file.
    
    Args:
        file_path: Path to the CSV file
        battery_data_id: ID of the BatteryData record
        
    Returns:
        Metrics object or None if computation fails
    """
    try:
        voltages, currents, temps = [], [], []

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    if 'voltage' in row and row['voltage']:
                        voltages.append(float(row["voltage"]))
                    if 'current' in row and row['current']:
                        currents.append(float(row["current"]))
                    if 'temperature' in row and row['temperature']:
                        temps.append(float(row["temperature"]))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing row in {file_path}: {e}")
                    continue

        if not voltages and not currents and not temps:
            logger.error(f"No valid data found in {file_path}")
            return None

        metrics = Metrics(
            telemetry_id=battery_data_id,
            avg_voltage=mean(voltages) if voltages else None,
            min_voltage=min(voltages) if voltages else None,
            max_voltage=max(voltages) if voltages else None,
            avg_current=mean(currents) if currents else None,
            avg_temperature=mean(temps) if temps else None,
        )

        with get_session() as s:
            s.add(metrics)
            s.flush()

        return metrics
        
    except Exception as e:
        logger.error(f"Failed to compute metrics for {file_path}: {e}")
        return None


def load_csv_data(file_path: str) -> Optional[pd.DataFrame]:
    """
    Load CSV data into a pandas DataFrame with error handling.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame or None if loading fails
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['timestamp', 'voltage', 'current', 'temperature']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns in {file_path}: {missing_cols}")
        
        # Convert timestamp to datetime if possible
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Could not parse timestamps in {file_path}: {e}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load CSV data from {file_path}: {e}")
        return None


def compute_advanced_metrics(df: pd.DataFrame) -> Dict:
    """
    Compute advanced battery metrics from DataFrame.
    
    Args:
        df: DataFrame with battery data
        
    Returns:
        Dictionary with computed metrics
    """
    metrics = {}
    
    try:
        # Voltage metrics
        if 'voltage' in df.columns:
            voltage_data = df['voltage'].dropna()
            if len(voltage_data) > 0:
                metrics.update({
                    'voltage_mean': voltage_data.mean(),
                    'voltage_median': voltage_data.median(),
                    'voltage_std': voltage_data.std(),
                    'voltage_min': voltage_data.min(),
                    'voltage_max': voltage_data.max(),
                    'voltage_range': voltage_data.max() - voltage_data.min(),
                    'voltage_q25': voltage_data.quantile(0.25),
                    'voltage_q75': voltage_data.quantile(0.75),
                })
        
        # Current metrics
        if 'current' in df.columns:
            current_data = df['current'].dropna()
            if len(current_data) > 0:
                metrics.update({
                    'current_mean': current_data.mean(),
                    'current_median': current_data.median(),
                    'current_std': current_data.std(),
                    'current_min': current_data.min(),
                    'current_max': current_data.max(),
                    'current_range': current_data.max() - current_data.min(),
                })
        
        # Temperature metrics
        if 'temperature' in df.columns:
            temp_data = df['temperature'].dropna()
            if len(temp_data) > 0:
                metrics.update({
                    'temperature_mean': temp_data.mean(),
                    'temperature_median': temp_data.median(),
                    'temperature_std': temp_data.std(),
                    'temperature_min': temp_data.min(),
                    'temperature_max': temp_data.max(),
                    'temperature_range': temp_data.max() - temp_data.min(),
                })
        
        # Power calculation (if both voltage and current available)
        if 'voltage' in df.columns and 'current' in df.columns:
            power_data = (df['voltage'] * df['current']).dropna()
            if len(power_data) > 0:
                metrics.update({
                    'power_mean': power_data.mean(),
                    'power_max': power_data.max(),
                    'power_min': power_data.min(),
                })
        
        # Data quality metrics
        metrics.update({
            'total_records': len(df),
            'valid_voltage_records': df['voltage'].notna().sum() if 'voltage' in df.columns else 0,
            'valid_current_records': df['current'].notna().sum() if 'current' in df.columns else 0,
            'valid_temperature_records': df['temperature'].notna().sum() if 'temperature' in df.columns else 0,
        })
        
        # Time-based metrics (if timestamp available)
        if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            time_data = df['timestamp'].dropna()
            if len(time_data) > 1:
                duration = (time_data.max() - time_data.min()).total_seconds()
                metrics.update({
                    'duration_seconds': duration,
                    'duration_hours': duration / 3600,
                    'sampling_frequency': len(time_data) / (duration / 3600) if duration > 0 else 0,
                    'start_time': time_data.min(),
                    'end_time': time_data.max(),
                })
        
    except Exception as e:
        logger.error(f"Error computing advanced metrics: {e}")
    
    return metrics


def analyze_battery_health(df: pd.DataFrame) -> Dict:
    """
    Analyze battery health indicators from the data.
    
    Args:
        df: DataFrame with battery data
        
    Returns:
        Dictionary with health analysis results
    """
    health_analysis = {}
    
    try:
        # Voltage health indicators
        if 'voltage' in df.columns:
            voltage_data = df['voltage'].dropna()
            if len(voltage_data) > 0:
                # Check for voltage drops
                voltage_drops = (voltage_data.diff() < -0.1).sum()
                
                # Check for consistent voltage levels
                voltage_stability = voltage_data.std() / voltage_data.mean() if voltage_data.mean() != 0 else float('inf')
                
                health_analysis.update({
                    'voltage_drops_count': voltage_drops,
                    'voltage_stability_coefficient': voltage_stability,
                    'voltage_health_score': max(0, 100 - (voltage_stability * 100)),
                })
        
        # Temperature health indicators
        if 'temperature' in df.columns:
            temp_data = df['temperature'].dropna()
            if len(temp_data) > 0:
                # Check for overheating
                overheating_threshold = 60  # Celsius
                overheating_events = (temp_data > overheating_threshold).sum()
                
                # Temperature variation
                temp_variation = temp_data.std()
                
                health_analysis.update({
                    'overheating_events': overheating_events,
                    'temperature_variation': temp_variation,
                    'max_temperature_recorded': temp_data.max(),
                })
        
        # Current health indicators
        if 'current' in df.columns:
            current_data = df['current'].dropna()
            if len(current_data) > 0:
                # Check for current spikes
                current_mean = current_data.mean()
                current_spikes = (current_data > current_mean * 2).sum()
                
                health_analysis.update({
                    'current_spikes_count': current_spikes,
                    'current_variation': current_data.std(),
                })
        
        # Overall health score (0-100)
        health_factors = []
        
        if 'voltage_health_score' in health_analysis:
            health_factors.append(health_analysis['voltage_health_score'])
        
        if 'overheating_events' in health_analysis:
            temp_score = max(0, 100 - health_analysis['overheating_events'] * 10)
            health_factors.append(temp_score)
        
        if 'current_spikes_count' in health_analysis:
            current_score = max(0, 100 - health_analysis['current_spikes_count'] * 5)
            health_factors.append(current_score)
        
        if health_factors:
            health_analysis['overall_health_score'] = sum(health_factors) / len(health_factors)
        else:
            health_analysis['overall_health_score'] = 0
        
    except Exception as e:
        logger.error(f"Error analyzing battery health: {e}")
        health_analysis['error'] = str(e)
    
    return health_analysis


def detect_anomalies(df: pd.DataFrame, threshold: float = 2.0) -> Dict:
    """
    Detect anomalies in battery data using statistical methods.
    
    Args:
        df: DataFrame with battery data
        threshold: Z-score threshold for anomaly detection
        
    Returns:
        Dictionary with anomaly detection results
    """
    anomalies = {}
    
    try:
        for column in ['voltage', 'current', 'temperature']:
            if column in df.columns:
                data = df[column].dropna()
                if len(data) > 3:  # Need at least 3 points for meaningful stats
                    mean_val = data.mean()
                    std_val = data.std()
                    
                    if std_val > 0:
                        z_scores = np.abs((data - mean_val) / std_val)
                        anomaly_indices = data[z_scores > threshold].index.tolist()
                        
                        anomalies[f'{column}_anomalies'] = {
                            'count': len(anomaly_indices),
                            'indices': anomaly_indices,
                            'values': data[z_scores > threshold].tolist(),
                            'percentage': (len(anomaly_indices) / len(data)) * 100
                        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        anomalies['error'] = str(e)
    
    return anomalies


def generate_summary_report(file_path: str) -> Dict:
    """
    Generate a comprehensive summary report for a battery data file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with complete analysis results
    """
    report = {
        'file_path': file_path,
        'analysis_timestamp': pd.Timestamp.now().isoformat(),
        'status': 'success'
    }
    
    try:
        # Load data
        df = load_csv_data(file_path)
        if df is None:
            report['status'] = 'error'
            report['error'] = 'Failed to load data'
            return report
        
        # Basic info
        report['basic_info'] = {
            'file_size_bytes': os.path.getsize(file_path),
            'total_records': len(df),
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Compute metrics
        report['metrics'] = compute_advanced_metrics(df)
        
        # Health analysis
        report['health_analysis'] = analyze_battery_health(df)
        
        # Anomaly detection
        report['anomalies'] = detect_anomalies(df)
        
        # Data quality assessment
        report['data_quality'] = {
            'missing_data_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'data_completeness_score': ((df.notna().sum() / len(df)).mean() * 100) if len(df) > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error generating summary report for {file_path}: {e}")
        report['status'] = 'error'
        report['error'] = str(e)
    
    return report


def compare_battery_files(file_paths: List[str]) -> Dict:
    """
    Compare multiple battery data files and generate comparative analysis.
    
    Args:
        file_paths: List of paths to CSV files
        
    Returns:
        Dictionary with comparative analysis results
    """
    comparison = {
        'files_analyzed': len(file_paths),
        'analysis_timestamp': pd.Timestamp.now().isoformat(),
        'comparisons': {}
    }
    
    try:
        all_metrics = []
        file_names = []
        
        for file_path in file_paths:
            df = load_csv_data(file_path)
            if df is not None:
                metrics = compute_advanced_metrics(df)
                metrics['file_name'] = os.path.basename(file_path)
                all_metrics.append(metrics)
                file_names.append(os.path.basename(file_path))
        
        if len(all_metrics) < 2:
            comparison['error'] = 'Need at least 2 valid files for comparison'
            return comparison
        
        # Compare key metrics across files
        comparison_metrics = ['voltage_mean', 'current_mean', 'temperature_mean', 'overall_health_score']
        
        for metric in comparison_metrics:
            values = [m.get(metric) for m in all_metrics if m.get(metric) is not None]
            if values:
                comparison['comparisons'][metric] = {
                    'files': file_names[:len(values)],
                    'values': values,
                    'best_file': file_names[values.index(max(values))],
                    'worst_file': file_names[values.index(min(values))],
                    'average': sum(values) / len(values),
                    'range': max(values) - min(values)
                }
        
    except Exception as e:
        logger.error(f"Error in file comparison: {e}")
        comparison['error'] = str(e)
    
    return comparison