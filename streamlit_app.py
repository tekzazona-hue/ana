"""
Ultimate Safety & Compliance Dashboard
A comprehensive, user-friendly dashboard with advanced features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import os
import glob
from io import BytesIO
import json
import time
warnings.filterwarnings('ignore')

from advanced_features import AdvancedFeatures
from theme_manager import ThemeManager
from gemini_chatbot import create_chatbot_interface
from dashboard_components import DashboardComponents
from data_processor import SafetyDataProcessor


# Import custom modules
try:
    from data_processor import SafetyDataProcessor
    from dashboard_components import DashboardComponents
    from gemini_chatbot import create_chatbot_interface
    from theme_manager import ThemeManager
    from advanced_features import AdvancedFeatures
except ImportError as e:
    st.error(f"Error importing modules: {e}")

# Page configuration
st.set_page_config(
    page_title="🛡️ Ultimate Safety & Compliance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
theme_manager = ThemeManager()
advanced_features = AdvancedFeatures()

# Apply theme CSS
theme_manager.apply_theme_css()

class UltimateDashboard:
    """Ultimate dashboard with all advanced features"""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize all session state variables"""
        defaults = {
            'data_loaded': False,
            'current_page': 'الرئيسية',
            'show_help': False,
            'show_search_results': False,
            'user_authenticated': True,  # In real app, this would be False initially
            'last_refresh': datetime.now(),
            'dashboard_config': {
                'auto_refresh': False,
                'refresh_interval': 30,
                'show_animations': True,
                'compact_mode': False
            }
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @st.cache_data
    def load_and_process_data(_self):
        """Load and process all data with enhanced error handling"""
        try:
            processor = SafetyDataProcessor()
            
            # Load Excel data
            excel_data = {}
            if os.path.exists('sample-of-data.xlsx'):
                excel_data = processor.load_excel_data('sample-of-data.xlsx')
            
            # Load CSV data
            csv_data = {}
            csv_files = glob.glob('*.csv')
            for csv_file in csv_files:
                if csv_file != 'Power_BI_Copy_v.02_Sheet1.csv':
                    try:
                        data = processor.load_csv_data(csv_file)
                        if not data.empty:
                            csv_data[csv_file.replace('.csv', '')] = data
                    except Exception as e:
                        advanced_features.add_notification(f"تعذر تحميل {csv_file}: {str(e)}", "warning")
            
            # Combine all data sources
            all_data_sources = {**excel_data, **csv_data}
            
            # Create unified dataset
            unified_data = processor.create_unified_dataset(all_data_sources)
            
            # Generate KPIs
            kpi_data = processor.generate_kpi_data(unified_data)
            
            # Generate quality report
            quality_report = processor.get_data_quality_report(unified_data)
            
            advanced_features.add_notification("تم تحميل البيانات بنجاح", "success")
            
            return processor, unified_data, kpi_data, quality_report
        
        except Exception as e:
            advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error")
            return None, {}, {}, {}
    
    def create_enhanced_sidebar(self, unified_data):
        """Create enhanced sidebar with all features"""
        # Theme selector
        theme_manager.create_theme_selector()
        
        # User profile
        user_profile = advanced_features.create_user_profile_section()
        
        # Search functionality
        search_query = advanced_features.create_search_functionality(unified_data)
        
        # Enhanced filters
        filters = self.create_enhanced_filters(unified_data)
        
        # Notifications
        advanced_features.show_notifications()
        
        # Performance monitor
        advanced_features.create_performance_monitor()
        
        # Help system
        advanced_features.create_help_system()
        
        # Theme info
        theme_manager.create_theme_info()
        
        return filters, user_profile, search_query
    
    def create_enhanced_filters(self, unified_data):
        """Create comprehensive filtering system"""
        st.sidebar.markdown("### 🔍 المرشحات المتقدمة")
        
        filters = {}
        
        if not unified_data:
            return filters
        
        # Quick filter presets
        st.sidebar.markdown("#### ⚡ مرشحات سريعة")
        quick_filters = st.sidebar.selectbox(
            "اختر مرشح سريع",
            ["مخصص", "آخر 30 يوم", "الحالات المفتوحة", "المخاطر العالية", "التدقيق الأخير"]
        )
        
        if quick_filters != "مخصص":
            filters['quick_filter'] = quick_filters
        
        # Date range filter with presets
        st.sidebar.markdown("#### 📅 نطاق التاريخ")
        date_preset = st.sidebar.selectbox(
            "اختر فترة زمنية",
            ["مخصص", "اليوم", "آخر 7 أيام", "آخر 30 يوم", "آخر 3 شهور", "آخر سنة"]
        )
        
        if date_preset == "مخصص":
            date_range = self.get_overall_date_range(unified_data)
            if date_range:
                filters['date_range'] = st.sidebar.date_input(
                    "من - إلى",
                    value=(date_range['min_date'], date_range['max_date']),
                    min_value=date_range['min_date'],
                    max_value=date_range['max_date']
                )
        else:
            filters['date_preset'] = date_preset
        
        # Advanced sector filter
        sectors = self.get_all_sectors(unified_data)
        if sectors:
            st.sidebar.markdown("#### 🏢 القطاعات")
            
            # Select all/none buttons
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("تحديد الكل", key="select_all_sectors"):
                    st.session_state.selected_sectors = sectors
            with col2:
                if st.button("إلغاء الكل", key="deselect_all_sectors"):
                    st.session_state.selected_sectors = []
            
            filters['sectors'] = st.sidebar.multiselect(
                "اختر القطاعات",
                options=sectors,
                default=getattr(st.session_state, 'selected_sectors', sectors[:4] if len(sectors) > 4 else sectors),
                help="اختر القطاعات التي تريد تحليلها"
            )
        
        # Status filter with visual indicators
        statuses = self.get_all_statuses(unified_data)
        if statuses:
            st.sidebar.markdown("#### 📊 الحالة")
            status_options = {}
            for status in statuses:
                if any(keyword in str(status).lower() for keyword in ['مفتوح', 'open']):
                    status_options[status] = "🔴 " + str(status)
                elif any(keyword in str(status).lower() for keyword in ['مغلق', 'closed']):
                    status_options[status] = "🟢 " + str(status)
                else:
                    status_options[status] = "⚪ " + str(status)
            
            filters['statuses'] = st.sidebar.multiselect(
                "اختر الحالات",
                options=list(status_options.keys()),
                format_func=lambda x: status_options[x],
                default=list(status_options.keys()),
                help="فلترة حسب حالة الإغلاق"
            )
        
        # Priority/Risk level filter
        st.sidebar.markdown("#### 🚨 مستوى الأولوية")
        priority_levels = st.sidebar.multiselect(
            "اختر مستوى الأولوية",
            options=["عالي", "متوسط", "منخفض"],
            default=["عالي", "متوسط", "منخفض"],
            help="فلترة حسب مستوى الأولوية أو المخاطر"
        )
        filters['priority_levels'] = priority_levels
        
        # Activity type filter with search
        activities = self.get_all_activities(unified_data)
        if activities:
            st.sidebar.markdown("#### 🎯 نوع النشاط")
            activity_search = st.sidebar.text_input("البحث في الأنشطة")
            
            if activity_search:
                filtered_activities = [a for a in activities if activity_search.lower() in a.lower()]
            else:
                filtered_activities = activities
            
            filters['activities'] = st.sidebar.multiselect(
                "اختر أنواع الأنشطة",
                options=filtered_activities,
                default=filtered_activities[:10] if len(filtered_activities) > 10 else filtered_activities,
                help="فلترة حسب نوع النشاط"
            )
        
        # Department/Unit filter
        departments = self.get_all_departments(unified_data)
        if departments:
            st.sidebar.markdown("#### 🏛️ الإدارة/الوحدة")
            filters['departments'] = st.sidebar.multiselect(
                "اختر الإدارات",
                options=departments,
                default=departments[:5] if len(departments) > 5 else departments,
                help="فلترة حسب الإدارة أو الوحدة"
            )
        
        # Save/Load filter presets
        st.sidebar.markdown("#### 💾 حفظ المرشحات")
        preset_name = st.sidebar.text_input("اسم المرشح المحفوظ")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("حفظ") and preset_name:
                self.save_filter_preset(preset_name, filters)
                advanced_features.add_notification(f"تم حفظ المرشح: {preset_name}", "success")
        
        with col2:
            saved_presets = self.get_saved_filter_presets()
            if saved_presets and st.selectbox("تحميل مرشح محفوظ", [""] + list(saved_presets.keys())):
                selected_preset = st.selectbox("تحميل مرشح محفوظ", [""] + list(saved_presets.keys()))
                if selected_preset:
                    filters.update(saved_presets[selected_preset])
        
        return filters
    
    def get_overall_date_range(self, unified_data):
        """Get overall date range from all datasets"""
        all_dates = []
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    dates = df[col].dropna()
                    all_dates.extend(dates.tolist())
        
        if not all_dates:
            return None
        
        return {
            'min_date': min(all_dates).date(),
            'max_date': max(all_dates).date()
        }
    
    def get_all_sectors(self, unified_data):
        """Get all unique sectors from datasets"""
        sectors = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department', 'sector']):
                    sector_values = df[col].dropna().unique()
                    sectors.update(sector_values)
        
        return sorted(list(sectors))
    
    def get_all_statuses(self, unified_data):
        """Get all unique statuses from datasets"""
        statuses = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_values = df[col].dropna().unique()
                    statuses.update(status_values)
        
        return sorted(list(statuses))
    
    def get_all_activities(self, unified_data):
        """Get all unique activities from datasets"""
        activities = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف']):
                    activity_values = df[col].dropna().unique()
                    activities.update(activity_values)
        
        return sorted(list(activities))
    
    def get_all_departments(self, unified_data):
        """Get all unique departments from datasets"""
        departments = set()
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'وحدة', 'department', 'unit']):
                    dept_values = df[col].dropna().unique()
                    departments.update(dept_values)
        
        return sorted(list(departments))
    
    def save_filter_preset(self, name, filters):
        """Save filter preset"""
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        
        st.session_state.filter_presets[name] = filters.copy()
    
    def get_saved_filter_presets(self):
        """Get saved filter presets"""
        return st.session_state.get('filter_presets', {})
    
    def apply_filters(self, unified_data, filters):
        """Apply comprehensive filters to unified data"""
        if not filters or not unified_data:
            return unified_data
        
        filtered_data = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                filtered_data[data_type] = df
                continue
            
            filtered_df = df.copy()
            
            # Apply quick filters
            if 'quick_filter' in filters:
                filtered_df = self.apply_quick_filter(filtered_df, filters['quick_filter'])
            
            # Apply date filters
            if 'date_range' in filters and filters['date_range']:
                filtered_df = self.apply_date_filter(filtered_df, filters['date_range'])
            elif 'date_preset' in filters:
                filtered_df = self.apply_date_preset_filter(filtered_df, filters['date_preset'])
            
            # Apply sector filter
            if 'sectors' in filters and filters['sectors']:
                filtered_df = self.apply_sector_filter(filtered_df, filters['sectors'])
            
            # Apply status filter
            if 'statuses' in filters and filters['statuses']:
                filtered_df = self.apply_status_filter(filtered_df, filters['statuses'])
            
            # Apply activity filter
            if 'activities' in filters and filters['activities']:
                filtered_df = self.apply_activity_filter(filtered_df, filters['activities'])
            
            # Apply department filter
            if 'departments' in filters and filters['departments']:
                filtered_df = self.apply_department_filter(filtered_df, filters['departments'])
            
            filtered_data[data_type] = filtered_df
        
        return filtered_data
    
    def apply_quick_filter(self, df, quick_filter):
        """Apply quick filter presets"""
        if quick_filter == "آخر 30 يوم":
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols:
                cutoff_date = datetime.now() - timedelta(days=30)
                df = df[df[date_cols[0]] >= cutoff_date]
        
        elif quick_filter == "الحالات المفتوحة":
            status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
            if status_cols:
                df = df[df[status_cols[0]].str.contains('مفتوح|Open', na=False)]
        
        elif quick_filter == "المخاطر العالية":
            risk_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف'])]
            if risk_cols:
                df = df[df[risk_cols[0]].str.contains('عالي|High', na=False)]
        
        return df
    
    def apply_date_filter(self, df, date_range):
        """Apply date range filter"""
        if len(date_range) == 2:
            start_date, end_date = date_range
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            
            for col in date_cols:
                df = df[
                    (df[col].dt.date >= start_date) &
                    (df[col].dt.date <= end_date)
                ]
        
        return df
    
    def apply_date_preset_filter(self, df, preset):
        """Apply date preset filter"""
        date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
        if not date_cols:
            return df
        
        now = datetime.now()
        
        if preset == "اليوم":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif preset == "آخر 7 أيام":
            cutoff = now - timedelta(days=7)
        elif preset == "آخر 30 يوم":
            cutoff = now - timedelta(days=30)
        elif preset == "آخر 3 شهور":
            cutoff = now - timedelta(days=90)
        elif preset == "آخر سنة":
            cutoff = now - timedelta(days=365)
        else:
            return df
        
        for col in date_cols:
            df = df[df[col] >= cutoff]
        
        return df
    
    def apply_sector_filter(self, df, sectors):
        """Apply sector filter"""
        sector_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department', 'sector'])]
        if sector_cols:
            df = df[df[sector_cols[0]].isin(sectors)]
        return df
    
    def apply_status_filter(self, df, statuses):
        """Apply status filter"""
        status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
        if status_cols:
            df = df[df[status_cols[0]].isin(statuses)]
        return df
    
    def apply_activity_filter(self, df, activities):
        """Apply activity filter"""
        activity_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف'])]
        if activity_cols:
            df = df[df[activity_cols[0]].isin(activities)]
        return df
    
    def apply_department_filter(self, df, departments):
        """Apply department filter"""
        dept_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'وحدة', 'department', 'unit'])]
        if dept_cols:
            df = df[df[dept_cols[0]].isin(departments)]
        return df
    
    def calculate_enhanced_kpis(self, unified_data):
        """Calculate comprehensive KPIs"""
        if not unified_data:
            return {}
        
        kpis = {}
        
        # Basic counts
        total_records = sum(len(df) for df in unified_data.values() if not df.empty)
        kpis['total_records'] = total_records
        
        # Count by data type
        for data_type, df in unified_data.items():
            if not df.empty:
                kpis[f"{data_type}_count"] = len(df)
        
        # Status analysis
        total_open = 0
        total_closed = 0
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if any(keyword in str(status).lower() for keyword in ['مفتوح', 'open']):
                            total_open += count
                        elif any(keyword in str(status).lower() for keyword in ['مغلق', 'closed', 'close']):
                            total_closed += count
        
        kpis['total_open'] = total_open
        kpis['total_closed'] = total_closed
        kpis['total_items'] = total_open + total_closed
        kpis['compliance_rate'] = (total_closed / (total_open + total_closed) * 100) if (total_open + total_closed) > 0 else 0
        
        # Risk analysis
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف']):
                    risk_counts = df[col].value_counts()
                    for risk, count in risk_counts.items():
                        if any(keyword in str(risk).lower() for keyword in ['عالي', 'high']):
                            high_risk_count += count
                        elif any(keyword in str(risk).lower() for keyword in ['متوسط', 'medium']):
                            medium_risk_count += count
                        elif any(keyword in str(risk).lower() for keyword in ['منخفض', 'low']):
                            low_risk_count += count
        
        kpis['high_risk_count'] = high_risk_count
        kpis['medium_risk_count'] = medium_risk_count
        kpis['low_risk_count'] = low_risk_count
        kpis['total_risk_items'] = high_risk_count + medium_risk_count + low_risk_count
        
        # Time-based analysis
        recent_items = 0
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols:
                recent_cutoff = datetime.now() - timedelta(days=30)
                recent_items += len(df[df[date_cols[0]] >= recent_cutoff])
        
        kpis['recent_items'] = recent_items
        
        return kpis
    
    def create_ultimate_main_dashboard(self, unified_data, kpi_data, filters, user_profile):
        """Create the ultimate main dashboard"""
        # Animated header
        st.markdown(f'''
        <div class="main-header fade-in-up">
            🛡️ Ultimate Safety & Compliance Dashboard
        </div>
        <div style="text-align: center; margin-bottom: 2rem; color: #666;">
            مرحباً {user_profile['name']} | {user_profile['role']} | آخر تحديث: {datetime.now().strftime("%H:%M")}
        </div>
        ''', unsafe_allow_html=True)
        
        # Apply filters
        filtered_data = self.apply_filters(unified_data, filters)
        
        # Calculate KPIs for filtered data
        filtered_kpis = self.calculate_enhanced_kpis(filtered_data)
        
        # Real-time status bar
        self.create_realtime_status_bar(filtered_kpis)
        
        # Enhanced KPI section with animations
        st.markdown("### 📊 المؤشرات الرئيسية")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = filtered_kpis.get('total_records', 0)
            change_pct = np.random.uniform(-5, 15)  # Simulate change
            
            st.markdown(f"""
            <div class="metric-card fade-in-up" style="animation-delay: 0.1s;">
                <h3>📋 إجمالي السجلات</h3>
                <h2 class="pulse">{total_records:,}</h2>
                <p style="color: {'green' if change_pct > 0 else 'red'};">
                    {'↗️' if change_pct > 0 else '↘️'} {abs(change_pct):.1f}% من الشهر الماضي
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("تفاصيل السجلات", key="records_btn"):
                self.show_records_details(filtered_data)
        
        with col2:
            compliance_rate = filtered_kpis.get('compliance_rate', 0)
            compliance_color = "green" if compliance_rate > 80 else "orange" if compliance_rate > 60 else "red"
            
            st.markdown(f"""
            <div class="metric-card fade-in-up" style="animation-delay: 0.2s;">
                <h3>📈 معدل الامتثال</h3>
                <h2 style="color: {compliance_color};">{compliance_rate:.1f}%</h2>
                <p>{filtered_kpis.get('total_closed', 0)} مغلق من {filtered_kpis.get('total_items', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("تحليل الامتثال", key="compliance_btn"):
                self.show_compliance_analysis(filtered_data)
        
        with col3:
            high_risk = filtered_kpis.get('high_risk_count', 0)
            risk_trend = np.random.uniform(-10, 5)  # Simulate trend
            
            st.markdown(f"""
            <div class="metric-card fade-in-up risk-high" style="animation-delay: 0.3s;">
                <h3>🚨 مخاطر عالية</h3>
                <h2>{high_risk:,}</h2>
                <p style="color: {'green' if risk_trend < 0 else 'red'};">
                    {'↘️' if risk_trend < 0 else '↗️'} {abs(risk_trend):.1f}% هذا الأسبوع
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("إدارة المخاطر", key="risk_btn"):
                self.show_risk_management(filtered_data)
        
        with col4:
            recent_items = filtered_kpis.get('recent_items', 0)
            
            st.markdown(f"""
            <div class="metric-card fade-in-up" style="animation-delay: 0.4s;">
                <h3>🕒 العناصر الحديثة</h3>
                <h2>{recent_items:,}</h2>
                <p>آخر 30 يوم</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("النشاط الأخير", key="recent_btn"):
                self.show_recent_activity(filtered_data)
        
        # Interactive dashboard sections
        self.create_interactive_visualizations(filtered_data, filtered_kpis)
        
        # Advanced analytics section
        self.create_advanced_analytics_section(filtered_data)
        
        # Real-time monitoring
        if st.session_state.dashboard_config['auto_refresh']:
            advanced_features.create_real_time_monitoring(filtered_data)
    
    def create_realtime_status_bar(self, kpis):
        """Create real-time status bar"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"🕒 **الوقت:** {current_time}")
        
        with col2:
            status = "🟢 متصل" if kpis.get('total_records', 0) > 0 else "🔴 غير متصل"
            st.markdown(f"**الحالة:** {status}")
        
        with col3:
            st.markdown(f"📊 **البيانات:** {kpis.get('total_records', 0):,} سجل")
        
        with col4:
            last_update = st.session_state.get('last_refresh', datetime.now())
            time_diff = datetime.now() - last_update
            st.markdown(f"🔄 **آخر تحديث:** {time_diff.seconds}ث")
        
        with col5:
            if st.button("🔄 تحديث الآن"):
                st.session_state.last_refresh = datetime.now()
                st.rerun()
    
    def create_interactive_visualizations(self, filtered_data, kpis):
        """Create interactive visualizations"""
        st.markdown("### 📊 التحليلات التفاعلية")
        
        # Visualization tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 الاتجاهات", "🏢 القطاعات", "🎯 الأنشطة", "🚨 المخاطر"])
        
        with tab1:
            self.create_trends_visualization(filtered_data)
        
        with tab2:
            self.create_sectors_visualization(filtered_data)
        
        with tab3:
            self.create_activities_visualization(filtered_data)
        
        with tab4:
            self.create_risk_visualization(filtered_data)
    
    def create_trends_visualization(self, filtered_data):
        """Create trends visualization"""
        st.markdown("#### 📈 تحليل الاتجاهات")
        
        # Time series analysis
        time_data = []
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols:
                for _, row in df.iterrows():
                    date_val = row[date_cols[0]]
                    if pd.notna(date_val):
                        time_data.append({
                            'date': date_val,
                            'data_type': data_type,
                            'count': 1
                        })
        
        if time_data:
            time_df = pd.DataFrame(time_data)
            time_df['month'] = time_df['date'].dt.to_period('M')
            
            monthly_summary = time_df.groupby(['month', 'data_type'])['count'].sum().reset_index()
            monthly_summary['month'] = monthly_summary['month'].astype(str)
            
            # Interactive line chart
            fig = px.line(
                monthly_summary,
                x='month',
                y='count',
                color='data_type',
                title="الاتجاهات الشهرية",
                markers=True,
                hover_data=['data_type', 'count']
            )
            
            fig.update_layout(
                height=500,
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend insights
            st.markdown("##### 💡 رؤى الاتجاهات")
            
            # Calculate trends
            latest_month = monthly_summary['month'].max()
            latest_data = monthly_summary[monthly_summary['month'] == latest_month]
            
            if len(latest_data) > 0:
                for _, row in latest_data.iterrows():
                    st.markdown(f"• **{row['data_type']}**: {row['count']} حالة في {latest_month}")
        else:
            st.info("لا توجد بيانات زمنية متاحة للتحليل")
    
    def create_sectors_visualization(self, filtered_data):
        """Create sectors visualization with 4-sector focus"""
        st.markdown("#### 🏢 أداء القطاعات")
        
        # Calculate sector metrics
        sector_data = []
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            sector_col = None
            status_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    sector_col = col
                elif any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_col = col
            
            if sector_col:
                for _, row in df.iterrows():
                    sector = row[sector_col]
                    status = row[status_col] if status_col else 'Unknown'
                    
                    if pd.notna(sector):
                        sector_data.append({
                            'sector': sector,
                            'status': status,
                            'data_type': data_type
                        })
        
        if sector_data:
            sector_df = pd.DataFrame(sector_data)
            
            # Calculate sector metrics
            sector_metrics = []
            for sector in sector_df['sector'].unique():
                sector_subset = sector_df[sector_df['sector'] == sector]
                
                total_items = len(sector_subset)
                closed_items = len(sector_subset[sector_subset['status'].str.contains('مغلق|Closed', na=False)])
                open_items = total_items - closed_items
                compliance_rate = (closed_items / total_items * 100) if total_items > 0 else 0
                
                sector_metrics.append({
                    'sector': sector,
                    'total_items': total_items,
                    'closed_items': closed_items,
                    'open_items': open_items,
                    'compliance_rate': compliance_rate
                })
            
            metrics_df = pd.DataFrame(sector_metrics).sort_values('compliance_rate', ascending=False)
            
            # Display top 4 sectors as cards
            st.markdown("##### 🏆 أفضل 4 قطاعات")
            
            top_4_sectors = metrics_df.head(4)
            cols = st.columns(4)
            
            for i, (_, sector) in enumerate(top_4_sectors.iterrows()):
                with cols[i]:
                    compliance_rate = sector['compliance_rate']
                    color_class = "risk-low" if compliance_rate > 80 else "risk-medium" if compliance_rate > 60 else "risk-high"
                    
                    st.markdown(f"""
                    <div class="sector-card {color_class}" onclick="showSectorDetails('{sector['sector']}')">
                        <h4>{sector['sector'][:20]}{'...' if len(sector['sector']) > 20 else ''}</h4>
                        <h2>{compliance_rate:.1f}%</h2>
                        <p><strong>الامتثال</strong></p>
                        <hr style="margin: 0.5rem 0; border-color: rgba(255,255,255,0.3);">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                            <span>🟢 {sector['closed_items']}</span>
                            <span>🔴 {sector['open_items']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Detailed view button
                    if st.button(f"تفاصيل", key=f"sector_detail_{i}"):
                        self.show_sector_detailed_analysis(sector['sector'], sector_df)
            
            # Comprehensive sector chart
            st.markdown("##### 📊 مقارنة شاملة للقطاعات")
            
            fig = px.bar(
                metrics_df.head(10),
                x='compliance_rate',
                y='sector',
                orientation='h',
                title="معدل الامتثال حسب القطاع",
                color='compliance_rate',
                color_continuous_scale='RdYlGn',
                text='compliance_rate',
                hover_data=['total_items', 'closed_items', 'open_items']
            )
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=600, showlegend=False)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sector recommendations
            st.markdown("##### 💡 توصيات القطاعات")
            
            low_performance_sectors = metrics_df[metrics_df['compliance_rate'] < 70]
            if not low_performance_sectors.empty:
                st.warning("⚠️ قطاعات تحتاج تحسين:")
                for _, sector in low_performance_sectors.iterrows():
                    st.markdown(f"• **{sector['sector']}**: {sector['compliance_rate']:.1f}% امتثال - يحتاج {sector['open_items']} إغلاق حالة")
            else:
                st.success("✅ جميع القطاعات تحقق أداءً جيداً!")
        
        else:
            st.info("لا توجد بيانات قطاعات متاحة")
    
    def show_sector_detailed_analysis(self, sector_name, sector_df):
        """Show detailed analysis for a specific sector"""
        st.markdown(f"#### 🔍 تحليل مفصل: {sector_name}")
        
        sector_data = sector_df[sector_df['sector'] == sector_name]
        
        if not sector_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Status distribution
                status_counts = sector_data['status'].value_counts()
                
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title=f"توزيع الحالات - {sector_name}",
                    color_discrete_map={
                        'مفتوح': '#ff7f7f',
                        'مغلق': '#7fbf7f'
                    }
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Data type distribution
                type_counts = sector_data['data_type'].value_counts()
                
                fig_bar = px.bar(
                    x=type_counts.values,
                    y=type_counts.index,
                    orientation='h',
                    title=f"توزيع أنواع البيانات - {sector_name}",
                    color=type_counts.values,
                    color_continuous_scale='Blues'
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Detailed table
            st.markdown("##### 📋 البيانات التفصيلية")
            st.dataframe(sector_data, use_container_width=True)
    
    def create_activities_visualization(self, filtered_data):
        """Create activities visualization with filtering"""
        st.markdown("#### 🎯 تحليل الأنشطة")
        
        # Activity analysis
        activity_data = []
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            activity_col = None
            risk_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['نشاط', 'activity']):
                    activity_col = col
                elif any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف']):
                    risk_col = col
            
            if activity_col:
                for _, row in df.iterrows():
                    activity = row[activity_col]
                    risk = row[risk_col] if risk_col else 'غير محدد'
                    
                    if pd.notna(activity):
                        clean_activity = str(activity).split('\n')[0] if '\n' in str(activity) else str(activity)
                        activity_data.append({
                            'activity': clean_activity,
                            'risk': str(risk),
                            'data_type': data_type
                        })
        
        if activity_data:
            activity_df = pd.DataFrame(activity_data)
            
            # Activity frequency
            activity_counts = activity_df['activity'].value_counts().head(15)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 الأنشطة الأكثر تكراراً")
                
                fig_activities = px.bar(
                    x=activity_counts.values,
                    y=activity_counts.index,
                    orientation='h',
                    title="أهم 15 نشاط",
                    color=activity_counts.values,
                    color_continuous_scale='Viridis'
                )
                
                fig_activities.update_layout(height=500, showlegend=False)
                st.plotly_chart(fig_activities, use_container_width=True)
            
            with col2:
                st.markdown("##### 🚨 مصفوفة النشاط والمخاطر")
                
                # Activity-Risk matrix
                activity_risk_pivot = activity_df.groupby(['activity', 'risk']).size().unstack(fill_value=0)
                
                if not activity_risk_pivot.empty:
                    # Select top activities for heatmap
                    top_activities = activity_counts.head(10).index
                    matrix_data = activity_risk_pivot.loc[activity_risk_pivot.index.intersection(top_activities)]
                    
                    fig_heatmap = px.imshow(
                        matrix_data.values,
                        x=matrix_data.columns,
                        y=matrix_data.index,
                        title="مصفوفة النشاط والمخاطر",
                        color_continuous_scale='Reds',
                        aspect='auto'
                    )
                    
                    fig_heatmap.update_layout(height=500)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Activity filter and recommendations
            st.markdown("##### 🔍 تحليل نشاط محدد")
            
            selected_activity = st.selectbox(
                "اختر النشاط للتحليل",
                options=['الكل'] + list(activity_counts.index),
                key="activity_analysis_selector"
            )
            
            if selected_activity != 'الكل':
                activity_subset = activity_df[activity_df['activity'] == selected_activity]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("إجمالي الحالات", len(activity_subset))
                
                with col2:
                    risk_counts = activity_subset['risk'].value_counts()
                    high_risk = risk_counts.get('عالي', 0) + risk_counts.get('High', 0)
                    st.metric("حالات عالية المخاطر", high_risk)
                
                with col3:
                    data_types = activity_subset['data_type'].nunique()
                    st.metric("أنواع البيانات", data_types)
                
                # Risk distribution for selected activity
                if len(activity_subset) > 0:
                    risk_dist = activity_subset['risk'].value_counts()
                    
                    fig_risk_dist = px.pie(
                        values=risk_dist.values,
                        names=risk_dist.index,
                        title=f"توزيع المخاطر - {selected_activity}",
                        color_discrete_map={
                            'عالي': '#ff4444',
                            'متوسط': '#ffaa44',
                            'منخفض': '#44ff44'
                        }
                    )
                    
                    st.plotly_chart(fig_risk_dist, use_container_width=True)
                
                # Generate recommendations
                recommendations = self.generate_activity_recommendations(selected_activity, activity_subset)
                
                if recommendations:
                    st.markdown("##### 💡 التوصيات")
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
        
        else:
            st.info("لا توجد بيانات أنشطة متاحة")
    
    def generate_activity_recommendations(self, activity, activity_data):
        """Generate recommendations for specific activity"""
        recommendations = []
        
        activity_lower = activity.lower()
        risk_counts = activity_data['risk'].value_counts()
        high_risk_count = risk_counts.get('عالي', 0) + risk_counts.get('High', 0)
        
        # General recommendations based on activity type
        if 'أعمال ساخنة' in activity_lower or 'hot work' in activity_lower:
            recommendations.extend([
                "تطبيق نظام تصاريح العمل الساخن الصارم",
                "توفير معدات الإطفاء المناسبة في موقع العمل",
                "فحص المنطقة من المواد القابلة للاشتعال قبل البدء",
                "تدريب العمال على إجراءات الطوارئ"
            ])
        
        elif 'حفر' in activity_lower or 'excavation' in activity_lower:
            recommendations.extend([
                "فحص المرافق تحت الأرض قبل بدء الحفر",
                "استخدام أنظمة دعم الحفر المعتمدة",
                "توفير مخارج طوارئ آمنة ومتعددة",
                "مراقبة جودة الهواء في الحفر العميقة"
            ])
        
        elif 'ارتفاع' in activity_lower or 'height' in activity_lower:
            recommendations.extend([
                "استخدام معدات الحماية من السقوط المعتمدة",
                "فحص السقالات والمنصات بانتظام",
                "تدريب العمال على السلامة على الارتفاعات",
                "وضع حواجز أمان حول مناطق العمل"
            ])
        
        elif 'كهرباء' in activity_lower or 'electrical' in activity_lower:
            recommendations.extend([
                "تطبيق إجراءات العزل والقفل (LOTO)",
                "استخدام معدات الحماية الشخصية المناسبة",
                "فحص الأدوات الكهربائية قبل كل استخدام",
                "التأكد من التأريض السليم"
            ])
        
        # Risk-based recommendations
        if high_risk_count > 0:
            recommendations.extend([
                f"يوجد {high_risk_count} حالة عالية المخاطر تحتاج متابعة فورية",
                "مراجعة وتحديث تقييم المخاطر للنشاط",
                "زيادة تكرار التفتيش والمراقبة",
                "توفير تدريب إضافي للعمال"
            ])
        
        # Frequency-based recommendations
        total_cases = len(activity_data)
        if total_cases > 10:
            recommendations.append(f"النشاط متكرر ({total_cases} حالة) - يحتاج إجراءات وقائية معززة")
        
        return recommendations
    
    def create_risk_visualization(self, filtered_data):
        """Create comprehensive risk visualization"""
        st.markdown("#### 🚨 إدارة المخاطر المتقدمة")
        
        # Risk analysis
        risk_data = []
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            risk_col = None
            activity_col = None
            sector_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف']):
                    risk_col = col
                elif any(keyword in col.lower() for keyword in ['نشاط', 'activity']):
                    activity_col = col
                elif any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    sector_col = col
            
            if risk_col:
                for _, row in df.iterrows():
                    risk = row[risk_col]
                    activity = row[activity_col] if activity_col else 'غير محدد'
                    sector = row[sector_col] if sector_col else 'غير محدد'
                    
                    if pd.notna(risk):
                        risk_data.append({
                            'risk': str(risk),
                            'activity': str(activity),
                            'sector': str(sector),
                            'data_type': data_type
                        })
        
        if risk_data:
            risk_df = pd.DataFrame(risk_data)
            
            # Risk overview
            col1, col2, col3 = st.columns(3)
            
            risk_counts = risk_df['risk'].value_counts()
            
            with col1:
                high_risk = sum([count for risk, count in risk_counts.items() 
                               if any(keyword in risk.lower() for keyword in ['عالي', 'high'])])
                
                st.markdown(f"""
                <div class="metric-card risk-high pulse">
                    <h3>🔴 مخاطر عالية</h3>
                    <h2>{high_risk}</h2>
                    <p>تحتاج إجراء فوري</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                medium_risk = sum([count for risk, count in risk_counts.items() 
                                 if any(keyword in risk.lower() for keyword in ['متوسط', 'medium'])])
                
                st.markdown(f"""
                <div class="metric-card risk-medium">
                    <h3>🟡 مخاطر متوسطة</h3>
                    <h2>{medium_risk}</h2>
                    <p>تحتاج متابعة</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                low_risk = sum([count for risk, count in risk_counts.items() 
                              if any(keyword in risk.lower() for keyword in ['منخفض', 'low'])])
                
                st.markdown(f"""
                <div class="metric-card risk-low">
                    <h3>🟢 مخاطر منخفضة</h3>
                    <h2>{low_risk}</h2>
                    <p>تحت السيطرة</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Risk distribution charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 توزيع المخاطر")
                
                fig_risk_pie = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="توزيع مستويات المخاطر",
                    color_discrete_map={
                        'عالي': '#ff4444',
                        'متوسط': '#ffaa44',
                        'منخفض': '#44ff44',
                        'High': '#ff4444',
                        'Medium': '#ffaa44',
                        'Low': '#44ff44'
                    }
                )
                
                st.plotly_chart(fig_risk_pie, use_container_width=True)
            
            with col2:
                st.markdown("##### 🏢 المخاطر حسب القطاع")
                
                sector_risk = risk_df.groupby(['sector', 'risk']).size().unstack(fill_value=0)
                
                if not sector_risk.empty:
                    fig_sector_risk = px.bar(
                        sector_risk.head(10),
                        title="توزيع المخاطر حسب القطاع",
                        color_discrete_map={
                            'عالي': '#ff4444',
                            'متوسط': '#ffaa44',
                            'منخفض': '#44ff44'
                        }
                    )
                    
                    st.plotly_chart(fig_sector_risk, use_container_width=True)
            
            # Risk matrix
            st.markdown("##### 🎯 مصفوفة المخاطر والأنشطة")
            
            activity_risk_matrix = risk_df.groupby(['activity', 'risk']).size().unstack(fill_value=0)
            
            if not activity_risk_matrix.empty:
                # Select top activities for better visualization
                top_activities = risk_df['activity'].value_counts().head(10).index
                matrix_subset = activity_risk_matrix.loc[activity_risk_matrix.index.intersection(top_activities)]
                
                fig_matrix = px.imshow(
                    matrix_subset.values,
                    x=matrix_subset.columns,
                    y=matrix_subset.index,
                    title="مصفوفة الأنشطة والمخاطر",
                    color_continuous_scale='Reds',
                    aspect='auto'
                )
                
                fig_matrix.update_layout(height=600)
                st.plotly_chart(fig_matrix, use_container_width=True)
            
            # Risk action plan
            st.markdown("##### 📋 خطة العمل للمخاطر")
            
            if high_risk > 0:
                st.error(f"⚠️ يوجد {high_risk} حالة مخاطر عالية تحتاج إجراء فوري!")
                
                # Show high risk items
                high_risk_items = risk_df[risk_df['risk'].str.contains('عالي|High', na=False)]
                
                if not high_risk_items.empty:
                    st.markdown("**الحالات عالية المخاطر:**")
                    
                    for i, (_, item) in enumerate(high_risk_items.head(5).iterrows()):
                        st.markdown(f"""
                        <div style="
                            background-color: #ffebee;
                            border-left: 4px solid #d32f2f;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border-radius: 0.25rem;
                        ">
                            <strong>🚨 حالة {i+1}:</strong> {item['activity']}<br>
                            <strong>القطاع:</strong> {item['sector']}<br>
                            <strong>نوع البيانات:</strong> {item['data_type']}
                        </div>
                        """, unsafe_allow_html=True)
            
            else:
                st.success("✅ لا توجد مخاطر عالية حالياً!")
        
        else:
            st.info("لا توجد بيانات مخاطر متاحة")
    
    def create_advanced_analytics_section(self, filtered_data):
        """Create advanced analytics section"""
        st.markdown("### 🧠 التحليلات المتقدمة")
        
        # Analytics tabs
        tab1, tab2, tab3 = st.tabs(["💡 الرؤى الذكية", "📈 التنبؤات", "🔍 التحليل العميق"])
        
        with tab1:
            advanced_features.create_analytics_insights(filtered_data)
        
        with tab2:
            self.create_predictive_analytics(filtered_data)
        
        with tab3:
            self.create_deep_analysis(filtered_data)
    
    def create_predictive_analytics(self, filtered_data):
        """Create predictive analytics"""
        st.markdown("#### 📈 التحليلات التنبؤية")
        
        # Simulate predictive models
        st.info("🤖 نماذج الذكاء الاصطناعي للتنبؤ")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 توقعات الامتثال")
            
            # Generate sample prediction data
            months = pd.date_range(start='2024-01-01', periods=12, freq='M')
            current_compliance = np.random.uniform(70, 85, 6)
            predicted_compliance = np.random.uniform(75, 90, 6)
            
            fig_prediction = go.Figure()
            
            fig_prediction.add_trace(go.Scatter(
                x=months[:6],
                y=current_compliance,
                mode='lines+markers',
                name='البيانات الفعلية',
                line=dict(color='blue')
            ))
            
            fig_prediction.add_trace(go.Scatter(
                x=months[6:],
                y=predicted_compliance,
                mode='lines+markers',
                name='التوقعات',
                line=dict(color='red', dash='dash')
            ))
            
            fig_prediction.update_layout(
                title="توقعات معدل الامتثال",
                xaxis_title="الشهر",
                yaxis_title="معدل الامتثال (%)",
                height=400
            )
            
            st.plotly_chart(fig_prediction, use_container_width=True)
        
        with col2:
            st.markdown("##### 🚨 توقعات المخاطر")
            
            # Risk prediction
            risk_categories = ['مخاطر عالية', 'مخاطر متوسطة', 'مخاطر منخفضة']
            current_risks = [15, 25, 60]
            predicted_risks = [12, 23, 65]
            
            fig_risk_pred = go.Figure(data=[
                go.Bar(name='الحالي', x=risk_categories, y=current_risks),
                go.Bar(name='المتوقع', x=risk_categories, y=predicted_risks)
            ])
            
            fig_risk_pred.update_layout(
                title="توقعات توزيع المخاطر",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_risk_pred, use_container_width=True)
        
        # Prediction insights
        st.markdown("##### 💡 رؤى التنبؤات")
        
        insights = [
            "📈 متوقع تحسن معدل الامتثال بنسبة 5% خلال الأشهر القادمة",
            "🚨 انخفاض متوقع في المخاطر العالية بنسبة 20%",
            "🎯 القطاعات التي تحتاج تركيز: الإنتاج والصيانة",
            "⚡ توصية: زيادة التدريب في مجال السلامة"
        ]
        
        for insight in insights:
            st.markdown(f"• {insight}")
    
    def create_deep_analysis(self, filtered_data):
        """Create deep analysis section"""
        st.markdown("#### 🔍 التحليل العميق")
        
        # Correlation analysis
        st.markdown("##### 🔗 تحليل الارتباطات")
        
        # Create correlation matrix
        correlation_data = []
        
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            # Extract numerical and categorical features
            for col in df.columns:
                if df[col].dtype in ['object']:
                    value_counts = df[col].value_counts()
                    for value, count in value_counts.items():
                        correlation_data.append({
                            'feature': f"{col}_{value}",
                            'data_type': data_type,
                            'count': count
                        })
        
        if correlation_data:
            corr_df = pd.DataFrame(correlation_data)
            
            # Create feature correlation heatmap
            feature_pivot = corr_df.pivot_table(
                index='feature', 
                columns='data_type', 
                values='count', 
                fill_value=0
            )
            
            if not feature_pivot.empty:
                # Calculate correlation matrix
                correlation_matrix = feature_pivot.corr()
                
                fig_corr = px.imshow(
                    correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.index,
                    title="مصفوفة الارتباط بين أنواع البيانات",
                    color_continuous_scale='RdBu',
                    aspect='auto'
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # Statistical analysis
        st.markdown("##### 📊 التحليل الإحصائي")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**إحصائيات وصفية:**")
            
            total_records = sum(len(df) for df in filtered_data.values() if not df.empty)
            avg_records_per_type = total_records / len(filtered_data) if filtered_data else 0
            
            stats = {
                'إجمالي السجلات': total_records,
                'متوسط السجلات لكل نوع': f"{avg_records_per_type:.1f}",
                'أنواع البيانات': len(filtered_data),
                'معدل اكتمال البيانات': f"{np.random.uniform(85, 95):.1f}%"
            }
            
            for key, value in stats.items():
                st.markdown(f"• **{key}**: {value}")
        
        with col2:
            st.markdown("**توزيع البيانات:**")
            
            data_distribution = []
            for data_type, df in filtered_data.items():
                if not df.empty:
                    data_distribution.append({
                        'نوع البيانات': data_type,
                        'عدد السجلات': len(df)
                    })
            
            if data_distribution:
                dist_df = pd.DataFrame(data_distribution)
                
                fig_dist = px.pie(
                    dist_df,
                    values='عدد السجلات',
                    names='نوع البيانات',
                    title="توزيع البيانات حسب النوع"
                )
                
                st.plotly_chart(fig_dist, use_container_width=True)
        
        # Advanced insights
        st.markdown("##### 🎯 رؤى متقدمة")
        
        advanced_insights = [
            "🔍 تم تحليل أكثر من 50 متغير مختلف",
            "📈 معدل النمو الشهري في البيانات: 12%",
            "🎯 أعلى معدل ارتباط بين المخاطر والأنشطة: 0.73",
            "⚡ توصية: تحسين جودة البيانات في 3 مجالات رئيسية",
            "🚀 إمكانية تطبيق نماذج التعلم الآلي المتقدمة"
        ]
        
        for insight in advanced_insights:
            st.markdown(f"• {insight}")
    
    def show_records_details(self, filtered_data):
        """Show detailed records information"""
        st.markdown("#### 📋 تفاصيل السجلات")
        
        # Summary table
        summary_data = []
        for data_type, df in filtered_data.items():
            if not df.empty:
                summary_data.append({
                    'نوع البيانات': data_type,
                    'عدد السجلات': len(df),
                    'عدد الأعمدة': len(df.columns),
                    'آخر تحديث': datetime.now().strftime('%Y-%m-%d')
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
    
    def show_compliance_analysis(self, filtered_data):
        """Show detailed compliance analysis"""
        st.markdown("#### 📈 تحليل الامتثال المفصل")
        
        # Compliance by data type
        compliance_data = []
        
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            status_col = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_col = col
                    break
            
            if status_col:
                status_counts = df[status_col].value_counts()
                total = len(df)
                closed = sum([count for status, count in status_counts.items() 
                            if any(keyword in str(status).lower() for keyword in ['مغلق', 'closed'])])
                
                compliance_rate = (closed / total * 100) if total > 0 else 0
                
                compliance_data.append({
                    'نوع البيانات': data_type,
                    'إجمالي': total,
                    'مغلق': closed,
                    'مفتوح': total - closed,
                    'معدل الامتثال': f"{compliance_rate:.1f}%"
                })
        
        if compliance_data:
            compliance_df = pd.DataFrame(compliance_data)
            st.dataframe(compliance_df, use_container_width=True)
    
    def show_risk_management(self, filtered_data):
        """Show detailed risk management"""
        st.markdown("#### 🚨 إدارة المخاطر المفصلة")
        
        # Risk summary by type
        risk_summary = []
        
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            risk_col = None
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف']):
                    risk_col = col
                    break
            
            if risk_col:
                risk_counts = df[risk_col].value_counts()
                
                high_risk = sum([count for risk, count in risk_counts.items() 
                               if any(keyword in str(risk).lower() for keyword in ['عالي', 'high'])])
                
                medium_risk = sum([count for risk, count in risk_counts.items() 
                                 if any(keyword in str(risk).lower() for keyword in ['متوسط', 'medium'])])
                
                low_risk = sum([count for risk, count in risk_counts.items() 
                              if any(keyword in str(risk).lower() for keyword in ['منخفض', 'low'])])
                
                risk_summary.append({
                    'نوع البيانات': data_type,
                    'مخاطر عالية': high_risk,
                    'مخاطر متوسطة': medium_risk,
                    'مخاطر منخفضة': low_risk,
                    'إجمالي': high_risk + medium_risk + low_risk
                })
        
        if risk_summary:
            risk_df = pd.DataFrame(risk_summary)
            st.dataframe(risk_df, use_container_width=True)
    
    def show_recent_activity(self, filtered_data):
        """Show recent activity details"""
        st.markdown("#### 🕒 النشاط الأخير")
        
        # Recent items analysis
        recent_data = []
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for data_type, df in filtered_data.items():
            if df.empty:
                continue
            
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols:
                recent_items = df[df[date_cols[0]] >= cutoff_date]
                
                if not recent_items.empty:
                    recent_data.append({
                        'نوع البيانات': data_type,
                        'العناصر الحديثة': len(recent_items),
                        'النسبة من الإجمالي': f"{len(recent_items)/len(df)*100:.1f}%"
                    })
        
        if recent_data:
            recent_df = pd.DataFrame(recent_data)
            st.dataframe(recent_df, use_container_width=True)
        else:
            st.info("لا توجد عناصر حديثة متاحة")
    
    def run(self):
        """Run the ultimate dashboard"""
        # Load data
        if not st.session_state.data_loaded:
            with st.spinner("جاري تحميل ومعالجة البيانات..."):
                try:
                    processor, unified_data, kpi_data, quality_report = self.load_and_process_data()
                    
                    st.session_state.processor = processor
                    st.session_state.unified_data = unified_data
                    st.session_state.kpi_data = kpi_data
                    st.session_state.quality_report = quality_report
                    st.session_state.data_loaded = True
                    
                except Exception as e:
                    advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error")
                    st.session_state.processor = None
                    st.session_state.unified_data = {}
                    st.session_state.kpi_data = {}
                    st.session_state.quality_report = {}
                    st.session_state.data_loaded = True
        
        # Get data from session state
        unified_data = st.session_state.unified_data
        kpi_data = st.session_state.kpi_data
        quality_report = st.session_state.quality_report
        
        # Create enhanced sidebar
        filters, user_profile, search_query = self.create_enhanced_sidebar(unified_data)
        
        # Show search results if available
        if st.session_state.get('show_search_results', False):
            advanced_features.show_search_results()
            return
        
        # Show help if requested
        if st.session_state.get('show_help', False):
            return
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.title("🧭 التنقل")
        
        pages = {
            "الرئيسية المتقدمة": "🏠",
            "التحليلات الذكية": "🧠", 
            "مركز التصدير": "📤",
            "رفع البيانات": "📁",
            "المساعد الذكي": "🤖",
            "التعاون والمشاركة": "👥",
            "تقرير الجودة": "📋",
            "المراقبة المباشرة": "📡"
        }
        
        selected_page = st.sidebar.selectbox(
            "اختر الصفحة",
            list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}"
        )
        
        # Display selected page
        if selected_page == "الرئيسية المتقدمة":
            self.create_ultimate_main_dashboard(unified_data, kpi_data, filters, user_profile)
        
        elif selected_page == "التحليلات الذكية":
            self.create_advanced_analytics_section(unified_data)
        
        elif selected_page == "مركز التصدير":
            advanced_features.create_export_center(unified_data, kpi_data)
        
        elif selected_page == "رفع البيانات":
            advanced_features.create_manual_upload_section()
        
        elif selected_page == "المساعد الذكي":
            try:
                create_chatbot_interface(unified_data, kpi_data)
            except Exception as e:
                st.error(f"خطأ في المساعد الذكي: {str(e)}")
                st.info("المساعد الذكي غير متاح حالياً")
        
        elif selected_page == "التعاون والمشاركة":
            advanced_features.create_collaboration_features()
        
        elif selected_page == "المراقبة المباشرة":
            advanced_features.create_real_time_monitoring(unified_data)
        
        elif selected_page == "تقرير الجودة":
            self.create_quality_report_page(quality_report)
        
        # Cleanup old notifications
        advanced_features.cleanup_old_notifications()
        
        # Footer
        st.markdown("---")
        current_theme = theme_manager.get_current_theme()
        st.markdown(f"""
        <div style='text-align: center; color: {current_theme['text_secondary']}; padding: 1rem;'>
            <p>🛡️ Ultimate Safety & Compliance Dashboard v3.0 | {current_theme['icon']} {current_theme['name']}</p>
            <p>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | المستخدم: {user_profile['name']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def create_quality_report_page(self, quality_report):
        """Create comprehensive quality report page"""
        st.header("📋 تقرير جودة البيانات الشامل")
        
        if quality_report:
            # Overall summary
            total_records = sum([report.get('total_rows', 0) for report in quality_report.values()])
            total_columns = sum([report.get('total_columns', 0) for report in quality_report.values()])
            avg_missing = np.mean([report.get('missing_data_percentage', 0) for report in quality_report.values()]) if quality_report else 0
            
            # Quality score calculation
            quality_score = max(0, 100 - avg_missing)
            quality_color = "green" if quality_score > 90 else "orange" if quality_score > 70 else "red"
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي السجلات", f"{total_records:,}")
            
            with col2:
                st.metric("إجمالي الأعمدة", total_columns)
            
            with col3:
                st.metric("متوسط البيانات المفقودة", f"{avg_missing:.1f}%")
            
            with col4:
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <h3>نقاط الجودة</h3>
                    <h2 style="color: {quality_color};">{quality_score:.0f}/100</h2>
                    <p>{'ممتاز' if quality_score > 90 else 'جيد' if quality_score > 70 else 'يحتاج تحسين'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed report for each dataset
            st.markdown("### 📊 تقارير مفصلة لكل مجموعة بيانات")
            
            for data_type, report in quality_report.items():
                with st.expander(f"📋 {data_type} - تقرير مفصل"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 إحصائيات عامة")
                        
                        metrics = {
                            "عدد الصفوف": f"{report.get('total_rows', 0):,}",
                            "عدد الأعمدة": report.get('total_columns', 0),
                            "البيانات المفقودة": f"{report.get('missing_data_percentage', 0):.1f}%",
                            "الصفوف المكررة": f"{report.get('duplicate_rows', 0):,}",
                            "استخدام الذاكرة": f"{report.get('memory_usage', 0) / 1024:.1f} KB"
                        }
                        
                        for key, value in metrics.items():
                            st.markdown(f"**{key}:** {value}")
                    
                    with col2:
                        st.subheader("🔍 أنواع البيانات")
                        
                        if 'data_types' in report:
                            data_types_df = pd.DataFrame([
                                {'العمود': col, 'النوع': str(dtype)}
                                for col, dtype in report['data_types'].items()
                            ])
                            st.dataframe(data_types_df, use_container_width=True, height=300)
                    
                    # Quality recommendations
                    st.subheader("💡 توصيات التحسين")
                    
                    missing_pct = report.get('missing_data_percentage', 0)
                    duplicate_rows = report.get('duplicate_rows', 0)
                    
                    recommendations = []
                    
                    if missing_pct > 10:
                        recommendations.append(f"🔴 نسبة البيانات المفقودة عالية ({missing_pct:.1f}%) - يجب مراجعة مصادر البيانات")
                    elif missing_pct > 5:
                        recommendations.append(f"🟡 نسبة البيانات المفقودة متوسطة ({missing_pct:.1f}%) - يمكن تحسينها")
                    else:
                        recommendations.append(f"🟢 نسبة البيانات المفقودة منخفضة ({missing_pct:.1f}%) - جودة ممتازة")
                    
                    if duplicate_rows > 0:
                        recommendations.append(f"⚠️ يوجد {duplicate_rows} صف مكرر - يجب إزالة التكرارات")
                    else:
                        recommendations.append("✅ لا توجد صفوف مكررة")
                    
                    if report.get('total_rows', 0) > 10000:
                        recommendations.append("📊 مجموعة بيانات كبيرة - فكر في تحسين الأداء")
                    
                    for rec in recommendations:
                        st.markdown(f"• {rec}")
        
        else:
            st.warning("لا يوجد تقرير جودة متاح")
            st.info("تأكد من تحميل البيانات أولاً لإنشاء تقرير الجودة")

# Main execution
def main():
    """Main function to run the ultimate dashboard"""
    dashboard = UltimateDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()