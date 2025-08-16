"""
Configuration settings for the Safety & Compliance Dashboard
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"

# Application settings
APP_TITLE = "🛡️ Ultimate Safety & Compliance Dashboard"
APP_VERSION = "4.0"
APP_DESCRIPTION = "Professional Arabic-supported dashboard for safety and compliance management"

# Data file configurations
EXCEL_FILES = {
    'sample_data': 'sample-of-data.xlsx'
}

CSV_FILES = [
    'ملاحظات_التفتيش.csv',
    'تقييم_المخاطر.csv', 
    'الحوادث.csv',
    'العلى_المقاولين.csv',
    'تدقيق_المقاولين.csv',
    'توصيات_التدقيق_على_المقاولين.csv',
    'توصيات_الحوادث.csv',
    'توصيات_ملاحظات_التفتيش.csv',
    'توصيات_تقييم_المخاطر.csv'
]

# UI Configuration
SECTORS = [
    "قطاع المشاريع", 
    "قطاع التشغيل", 
    "قطاع الخدمات", 
    "قطاع التخصيص", 
    "أخرى"
]

RISK_ACTIVITIES = [
    "الأماكن المغلقة", 
    "الارتفاعات", 
    "الحفريات", 
    "الكهرباء"
]

STATUS_OPTIONS = [
    "الكل", 
    "مفتوح", 
    "مغلق", 
    "قيد المراجعة", 
    "مكتمل"
]

PRIORITY_OPTIONS = [
    "الكل", 
    "عالي", 
    "متوسط", 
    "منخفض"
]

RISK_LEVELS = [
    "الكل", 
    "مرتفع", 
    "متوسط", 
    "منخفض"
]

# Color schemes
COLORS = {
    'primary': '#1f77b4',
    'success': '#00cc88',
    'warning': '#ffa500',
    'danger': '#ff4b4b',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Chart configurations
CHART_CONFIG = {
    'height': 400,
    'use_container_width': True,
    'theme': 'streamlit'
}

# Performance settings
PERFORMANCE = {
    'max_rows_display': 1000,
    'cache_ttl': 3600,  # 1 hour
    'chunk_size': 10000
}

# Encoding options for CSV files
ENCODING_OPTIONS = [
    'utf-8', 
    'utf-8-sig', 
    'cp1256', 
    'iso-8859-1'
]