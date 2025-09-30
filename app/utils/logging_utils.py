# ============================================
# FILE: app/utils/logging_utils.py
# ============================================
import streamlit as st
from backend.file_utils import writeLog

def log_error(error_message, context=""):
    """Log errors to the logs directory"""
    try:
        full_message = f"{context}: {error_message}" if context else error_message
        writeLog(full_message, level="ERROR", log_dir="./logs")
    except Exception as e:
        print(f"Logging failed: {e}")

def log_info(message, context=""):
    """Log info messages to the logs directory"""
    try:
        full_message = f"{context}: {message}" if context else message
        writeLog(full_message, level="INFO", log_dir="./logs")
    except Exception as e:
        print(f"Logging failed: {e}")

def log_warning(message, context=""):
    """Log warning messages to the logs directory"""
    try:
        full_message = f"{context}: {message}" if context else message
        writeLog(full_message, level="WARNING", log_dir="./logs")
    except Exception as e:
        print(f"Logging failed: {e}")

