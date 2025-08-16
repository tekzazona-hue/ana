"""
🛡️ Ultimate Safety & Compliance Dashboard
Professional Arabic-supported dashboard for safety and compliance management

Author: OpenHands AI Assistant
Version: 4.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import components
from src.utils.data_processor import SafetyDataProcessor as DataProcessor
from src.components.advanced_features import AdvancedFeatures
from src.components.theme_manager import ThemeManager
from src.components.gemini_chatbot import create_chatbot_interface

# Page configuration
st.set_page_config(
    page_title="🛡️ Ultimate Safety & Compliance Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
data_processor = DataProcessor()
advanced_features = AdvancedFeatures()
theme_manager = ThemeManager()

class UltimateDashboard:
    def __init__(self):
        self.data_processor = data_processor
        self.advanced_features = advanced_features
        self.theme_manager = theme_manager
        
        # Initialize session state
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'unified_data' not in st.session_state:
            st.session_state.unified_data = {}
        if 'kpi_data' not in st.session_state:
            st.session_state.kpi_data = {}
        if 'quality_report' not in st.session_state:
            st.session_state.quality_report = {}
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}

    def create_modern_navigation(self):
        """Create modern navigation at the top of sidebar"""
        st.sidebar.markdown("""
        <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; margin-bottom: 1rem; color: white;'>
            <h2 style='margin: 0; color: white;'>🛡️ لوحة التحكم</h2>
            <p style='margin: 0; opacity: 0.9;'>Safety & Compliance Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main navigation
        pages = {
            "الرئيسية المتقدمة": "🏠",
            "التحليلات الذكية": "🧠", 
            "مركز التصدير": "📤",
            "رفع البيانات": "📁",
            "تشغيل مساعد الذكاء الاصطناعي": "🤖",
            "تقرير الجودة": "📋",
            "المراقبة المباشرة": "📡"
        }
        
        selected_page = st.sidebar.selectbox(
            "اختر الصفحة",
            list(pages.keys()),
            format_func=lambda x: f"{pages[x]} {x}",
            key="main_navigation"
        )
        
        return selected_page

    def create_enhanced_filters(self, unified_data):
        """Create enhanced filters with better design"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style='text-align: center; padding: 0.5rem; background: #f0f2f6; 
                    border-radius: 8px; margin-bottom: 1rem;'>
            <h3 style='margin: 0; color: #1f77b4;'>🔍 المرشحات المتقدمة</h3>
        </div>
        """, unsafe_allow_html=True)

        filters = {}
        
        if not unified_data:
            st.sidebar.info("لا توجد بيانات متاحة للتصفية")
            return filters

        # Filter presets section
        with st.sidebar.expander("⚙️ إعدادات المرشحات", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ مسح جميع المرشحات", key="clear_all_filters"):
                    st.rerun()
            
            with col2:
                saved_presets = self.get_saved_filter_presets()
                if saved_presets:
                    selected_preset = st.selectbox(
                        "تحميل مرشح محفوظ", 
                        [""] + list(saved_presets.keys()),
                        key="load_filter_preset"
                    )
                    if selected_preset:
                        filters.update(saved_presets[selected_preset])

        # Date range filter
        st.sidebar.markdown("#### 📅 نطاق التاريخ")
        date_range = st.sidebar.date_input(
            "اختر النطاق الزمني",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            key="date_range_filter"
        )
        if len(date_range) == 2:
            filters['date_range'] = date_range

        # Sector filter with select all option
        st.sidebar.markdown("#### 🏢 القطاعات")
        
        # Get available sectors
        available_sectors = set()
        for dataset_name, df in unified_data.items():
            if not df.empty:
                sector_columns = [col for col in df.columns if 'قطاع' in str(col) or 'sector' in str(col).lower()]
                for col in sector_columns:
                    available_sectors.update(df[col].dropna().unique())
        
        available_sectors = sorted(list(available_sectors))
        
        if available_sectors:
            # Select all/none buttons
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("✅ تحديد الكل", key="select_all_sectors"):
                    st.session_state.selected_sectors = available_sectors
            with col2:
                if st.button("❌ إلغاء الكل", key="deselect_all_sectors"):
                    st.session_state.selected_sectors = []
            
            # Multi-select for sectors
            selected_sectors = st.sidebar.multiselect(
                "اختر القطاعات",
                available_sectors,
                default=st.session_state.get('selected_sectors', available_sectors[:3]),
                key="sector_multiselect"
            )
            filters['sectors'] = selected_sectors

        # Status filter
        st.sidebar.markdown("#### 📊 الحالة")
        status_options = ["الكل", "مفتوح", "مغلق", "قيد المراجعة", "مكتمل"]
        selected_status = st.sidebar.multiselect(
            "اختر الحالات",
            status_options,
            default=["الكل"],
            key="status_filter"
        )
        filters['status'] = selected_status

        # Priority filter
        st.sidebar.markdown("#### ⚡ الأولوية")
        priority_options = ["الكل", "عالي", "متوسط", "منخفض"]
        selected_priority = st.sidebar.selectbox(
            "مستوى الأولوية",
            priority_options,
            key="priority_filter"
        )
        filters['priority'] = selected_priority

        # Risk level filter
        st.sidebar.markdown("#### ⚠️ مستوى المخاطر")
        risk_options = ["الكل", "مرتفع", "متوسط", "منخفض"]
        selected_risk = st.sidebar.selectbox(
            "مستوى المخاطر",
            risk_options,
            key="risk_level_filter"
        )
        filters['risk_level'] = selected_risk

        # Save current filter preset
        st.sidebar.markdown("---")
        with st.sidebar.expander("💾 حفظ المرشح الحالي"):
            preset_name = st.text_input("اسم المرشح", key="preset_name_input")
            if st.button("حفظ", key="save_filter_preset") and preset_name:
                self.save_filter_preset(preset_name, filters)
                st.success(f"تم حفظ المرشح: {preset_name}")

        return filters

    def get_saved_filter_presets(self):
        """Get saved filter presets"""
        return st.session_state.get('filter_presets', {})

    def save_filter_preset(self, name, filters):
        """Save filter preset"""
        if 'filter_presets' not in st.session_state:
            st.session_state.filter_presets = {}
        st.session_state.filter_presets[name] = filters.copy()

    def create_enhanced_sidebar(self, unified_data):
        """Create enhanced sidebar with navigation first"""
        # Navigation first (at the top)
        selected_page = self.create_modern_navigation()
        
        # Theme selector
        theme_manager.create_theme_selector()
        
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
        
        return filters, selected_page

    def load_and_process_data(self):
        """Load and process all data sources"""
        try:
            processor = DataProcessor()
            
            # Load all data from database directory
            all_data = processor.load_all_data()
            
            # Flatten the data structure for easier access
            unified_data = {}
            for source_name, source_data in all_data.items():
                if isinstance(source_data, dict):
                    # Excel file with multiple sheets
                    for sheet_name, sheet_data in source_data.items():
                        unified_data[f"{source_name}_{sheet_name}"] = sheet_data
                else:
                    # CSV file
                    unified_data[source_name.replace('.csv', '')] = source_data
            
            # Generate KPIs
            kpi_data = processor.generate_kpis(unified_data)
            
            # Generate quality report
            quality_report = processor.generate_quality_report(unified_data)
            
            return processor, unified_data, kpi_data, quality_report
            
        except Exception as e:
            st.error(f"خطأ في تحميل البيانات: {str(e)}")
            advanced_features.add_notification(f"خطأ في تحميل البيانات: {str(e)}", "error")
            return None, {}, {}, {}

    def create_ultimate_main_dashboard(self, unified_data, kpi_data, filters):
        """Create the ultimate main dashboard"""
        # Animated header
        st.markdown(f'''
        <div class="main-header fade-in-up">
            🛡️ Ultimate Safety & Compliance Dashboard
        </div>
        <div style="text-align: center; margin-bottom: 2rem; color: #666;">
            مرحباً بك في لوحة معلومات السلامة والامتثال | آخر تحديث: {datetime.now().strftime("%H:%M")}
        </div>
        ''', unsafe_allow_html=True)
        
        # Apply filters
        filtered_data = self.apply_filters(unified_data, filters)
        
        # KPI Cards
        self.create_kpi_cards(kpi_data)
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 نظرة عامة", 
            "📈 التحليلات", 
            "⚠️ المخاطر", 
            "🎯 الأداء"
        ])
        
        with tab1:
            self.create_overview_section(filtered_data)
        
        with tab2:
            self.create_analytics_section(filtered_data)
        
        with tab3:
            self.create_risk_section(filtered_data)
        
        with tab4:
            self.create_performance_section(filtered_data)

    def apply_filters(self, unified_data, filters):
        """Apply filters to unified data"""
        filtered_data = {}
        
        for dataset_name, df in unified_data.items():
            if df.empty:
                filtered_data[dataset_name] = df
                continue
                
            filtered_df = df.copy()
            
            # Apply sector filter
            if 'sectors' in filters and filters['sectors']:
                sector_columns = [col for col in df.columns if 'قطاع' in str(col) or 'sector' in str(col).lower()]
                if sector_columns:
                    sector_mask = filtered_df[sector_columns[0]].isin(filters['sectors'])
                    filtered_df = filtered_df[sector_mask]
            
            # Apply status filter
            if 'status' in filters and filters['status'] and 'الكل' not in filters['status']:
                status_columns = [col for col in df.columns if 'حالة' in str(col) or 'status' in str(col).lower()]
                if status_columns:
                    status_mask = filtered_df[status_columns[0]].isin(filters['status'])
                    filtered_df = filtered_df[status_mask]
            
            # Apply date range filter
            if 'date_range' in filters and len(filters['date_range']) == 2:
                date_columns = [col for col in df.columns if 'تاريخ' in str(col) or 'date' in str(col).lower()]
                if date_columns:
                    try:
                        filtered_df[date_columns[0]] = pd.to_datetime(filtered_df[date_columns[0]], errors='coerce')
                        start_date, end_date = filters['date_range']
                        date_mask = (filtered_df[date_columns[0]] >= pd.Timestamp(start_date)) & \
                                   (filtered_df[date_columns[0]] <= pd.Timestamp(end_date))
                        filtered_df = filtered_df[date_mask]
                    except:
                        pass
            
            filtered_data[dataset_name] = filtered_df
        
        return filtered_data

    def create_kpi_cards(self, kpi_data):
        """Create KPI cards with modern design"""
        if not kpi_data:
            st.info("لا توجد مؤشرات أداء متاحة")
            return
        
        # Create columns for KPI cards
        cols = st.columns(len(kpi_data))
        
        for i, (key, value) in enumerate(kpi_data.items()):
            with cols[i]:
                # Determine color based on KPI type
                if 'مخاطر' in key or 'حوادث' in key:
                    color = "#ff4b4b"
                elif 'امتثال' in key or 'مكتمل' in key:
                    color = "#00cc88"
                else:
                    color = "#1f77b4"
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color}15 0%, {color}25 100%); 
                            padding: 1.5rem; border-radius: 12px; border-left: 4px solid {color};
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem;'>
                    <h3 style='color: {color}; margin: 0; font-size: 2rem; font-weight: bold;'>{value}</h3>
                    <p style='color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{key}</p>
                </div>
                """, unsafe_allow_html=True)

    def create_overview_section(self, filtered_data):
        """Create overview section"""
        st.markdown("### 📊 نظرة عامة على البيانات")
        
        if not filtered_data:
            st.info("لا توجد بيانات متاحة")
            return
        
        # Data summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 ملخص البيانات")
            summary_data = []
            for dataset_name, df in filtered_data.items():
                if not df.empty:
                    summary_data.append({
                        'مجموعة البيانات': dataset_name,
                        'عدد السجلات': len(df),
                        'عدد الأعمدة': len(df.columns)
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 توزيع البيانات")
            if summary_data:
                fig = px.pie(
                    summary_df, 
                    values='عدد السجلات', 
                    names='مجموعة البيانات',
                    title="توزيع السجلات حسب مجموعة البيانات"
                )
                st.plotly_chart(fig, use_container_width=True)

    def create_analytics_section(self, filtered_data):
        """Create analytics section"""
        st.markdown("### 🧠 التحليلات المتقدمة")
        
        # Enhanced analytics tabs
        tab1, tab2, tab3 = st.tabs([
            "📊 جدول الامتثال للقطاعات الأربعة", 
            "⚠️ إدارة المخاطر - جدول الأنشطة", 
            "🚨 تحليل الحوادث"
        ])
        
        with tab1:
            self.create_closing_compliance_table(filtered_data)
        
        with tab2:
            self.create_risk_management_activity_table(filtered_data)
        
        with tab3:
            self.create_incidents_analysis_table(filtered_data)

    def create_closing_compliance_table(self, filtered_data):
        """Create closing compliance table for 4 sectors"""
        st.markdown("#### 📊 جدول الامتثال للقطاعات الأربعة")
        
        # Define the 4 main sectors
        sectors = ["قطاع المشاريع", "قطاع التشغيل", "قطاع الخدمات", "قطاع التخصيص", "أخرى"]
        
        # Create filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_sectors = st.multiselect(
                "اختر القطاعات", 
                sectors, 
                default=sectors,
                key="compliance_sectors_filter"
            )
        with col2:
            status_filter = st.selectbox(
                "حالة الامتثال", 
                ["الكل", "مغلق", "مفتوح"],
                key="compliance_status_filter"
            )
        with col3:
            year_filter = st.selectbox(
                "السنة", 
                ["الكل", "2024", "2023", "2022"],
                key="compliance_year_filter"
            )
        
        # Process compliance data
        compliance_data = []
        
        # Get inspection data if available
        inspection_data = filtered_data.get('ملاحظات_التفتيش', pd.DataFrame())
        
        if not inspection_data.empty:
            for sector in selected_sectors:
                # Filter data for this sector
                sector_data = inspection_data[inspection_data.get('القطاع', '').str.contains(sector, na=False)]
                
                if not sector_data.empty:
                    total_records = len(sector_data)
                    closed_records = len(sector_data[sector_data.get('الحالة', '').str.contains('مغلق|مكتمل', na=False)])
                    
                    compliance_percentage = (closed_records / total_records * 100) if total_records > 0 else 0
                    
                    # Generate recommendations based on compliance percentage
                    if compliance_percentage >= 90:
                        recommendation = "ممتاز - استمر في الأداء الجيد"
                        status_color = "🟢"
                    elif compliance_percentage >= 70:
                        recommendation = "جيد - يحتاج تحسين طفيف"
                        status_color = "🟡"
                    else:
                        recommendation = "يحتاج تحسين عاجل"
                        status_color = "🔴"
                    
                    compliance_data.append({
                        'القطاع': sector,
                        'إجمالي السجلات': total_records,
                        'السجلات المغلقة': closed_records,
                        'السجلات المفتوحة': total_records - closed_records,
                        'نسبة الامتثال %': compliance_percentage,
                        'الحالة': f"{status_color} {'مغلق' if compliance_percentage >= 50 else 'مفتوح'}",
                        'التوصية': recommendation
                    })
        
        if compliance_data:
            df = pd.DataFrame(compliance_data)
            
            # Display interactive table
            st.dataframe(
                df,
                use_container_width=True,
                height=400,
                column_config={
                    "نسبة الامتثال %": st.column_config.ProgressColumn(
                        "نسبة الامتثال %",
                        help="نسبة الامتثال للقطاع",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # Add click functionality for detailed view
            st.markdown("---")
            st.markdown("#### 🔍 عرض تفصيلي")
            
            selected_sector_detail = st.selectbox(
                "اختر قطاع للعرض التفصيلي", 
                selected_sectors,
                key="compliance_detail_sector"
            )
            
            if selected_sector_detail:
                sector_detail_data = inspection_data[
                    inspection_data.get('القطاع', '').str.contains(selected_sector_detail, na=False)
                ]
                
                if not sector_detail_data.empty:
                    st.markdown(f"**تفاصيل {selected_sector_detail}:**")
                    st.dataframe(sector_detail_data, use_container_width=True)
                else:
                    st.info(f"لا توجد بيانات تفصيلية متاحة لـ {selected_sector_detail}")
        else:
            st.info("لا توجد بيانات امتثال متاحة للقطاعات المحددة")

    def create_risk_management_activity_table(self, filtered_data):
        """Create risk management activity table"""
        st.markdown("#### ⚠️ إدارة المخاطر - جدول الأنشطة")
        
        # Risk activities
        risk_activities = ["الأماكن المغلقة", "الارتفاعات", "الحفريات", "الكهرباء"]
        
        # Create filters
        col1, col2, col3 = st.columns(3)
        with col1:
            activity_sort = st.selectbox(
                "ترتيب الأنشطة", 
                ["الأولوية", "الاسم", "مستوى المخاطر"],
                key="risk_activity_sort"
            )
        with col2:
            recommendation_filter = st.selectbox(
                "التوصية", 
                ["الكل", "عاجل", "متوسط", "منخفض"],
                key="risk_recommendation_filter"
            )
        with col3:
            year_filter_risk = st.selectbox(
                "السنة", 
                ["الكل", "2024", "2023", "2022"], 
                key="risk_year_filter"
            )
        
        # Process risk data
        risk_data = []
        
        # Get risk assessment data if available
        risk_assessment_data = filtered_data.get('تقييم_المخاطر', pd.DataFrame())
        
        if not risk_assessment_data.empty:
            for activity in risk_activities:
                # Filter data for this activity
                activity_data = risk_assessment_data[
                    risk_assessment_data.astype(str).apply(
                        lambda x: x.str.contains(activity, na=False)
                    ).any(axis=1)
                ]
                
                if not activity_data.empty:
                    total_assessments = len(activity_data)
                    high_risk = len(activity_data[
                        activity_data.astype(str).apply(
                            lambda x: x.str.contains('عالي|مرتفع', na=False)
                        ).any(axis=1)
                    ])
                    
                    # Generate risk level
                    risk_percentage = (high_risk / total_assessments * 100) if total_assessments > 0 else 0
                    
                    if risk_percentage >= 70:
                        risk_level = "🔴 عالي"
                        priority = 1
                    elif risk_percentage >= 40:
                        risk_level = "🟡 متوسط"
                        priority = 2
                    else:
                        risk_level = "🟢 منخفض"
                        priority = 3
                    
                    risk_data.append({
                        'النشاط': activity,
                        'إجمالي التقييمات': total_assessments,
                        'المخاطر العالية': high_risk,
                        'مستوى المخاطر': risk_level,
                        'نسبة المخاطر %': f"{risk_percentage:.1f}%",
                        'الأولوية': priority,
                        'التوصية': 'مراجعة عاجلة' if risk_percentage >= 70 else 'مراقبة دورية'
                    })
        
        if risk_data:
            df = pd.DataFrame(risk_data)
            
            # Sort based on selection
            if activity_sort == "الأولوية":
                df = df.sort_values('الأولوية')
            elif activity_sort == "الاسم":
                df = df.sort_values('النشاط')
            elif activity_sort == "مستوى المخاطر":
                df = df.sort_values('نسبة المخاطر %', ascending=False)
            
            st.dataframe(df.drop('الأولوية', axis=1), use_container_width=True, height=400)
            
            # Recommendation impact analysis
            st.markdown("---")
            st.markdown("#### 💡 تأثير التوصيات على الأنشطة")
            
            selected_recommendation = st.selectbox(
                "اختر توصية لمعرفة تأثيرها",
                ["مراجعة عاجلة", "مراقبة دورية", "تدريب إضافي", "تحديث الإجراءات"],
                key="risk_recommendation_impact"
            )
            
            affected_activities = df[df['التوصية'].str.contains(selected_recommendation, na=False)]
            
            if not affected_activities.empty:
                st.markdown(f"**الأنشطة المتأثرة بـ '{selected_recommendation}':**")
                st.dataframe(affected_activities[['النشاط', 'مستوى المخاطر', 'نسبة المخاطر %']], 
                           use_container_width=True)
            else:
                st.info(f"لا توجد أنشطة متأثرة بـ '{selected_recommendation}'")
        else:
            st.info("لا توجد بيانات إدارة مخاطر متاحة")

    def create_incidents_analysis_table(self, filtered_data):
        """Create incidents analysis table"""
        st.markdown("#### 🚨 تحليل الحوادث")
        
        # Create year filter
        year_filter_incidents = st.selectbox(
            "تصفية حسب السنة", 
            ["الكل", "2024", "2023", "2022"], 
            key="incidents_year_filter"
        )
        
        # Process incidents data
        incidents_data = []
        
        # Get incidents data if available
        incidents_df = filtered_data.get('الحوادث', pd.DataFrame())
        
        if not incidents_df.empty:
            # Define sectors for incidents analysis
            sectors = incidents_df.get('القطاع', pd.Series()).unique() if 'القطاع' in incidents_df.columns else []
            
            if len(sectors) == 0:
                # If no sector column, create default sectors
                sectors = ["قطاع المشاريع", "قطاع التشغيل", "قطاع الخدمات", "قطاع التخصيص"]
            
            for sector in sectors:
                if pd.isna(sector):
                    continue
                    
                # Filter incidents for this sector
                sector_incidents = incidents_df[
                    incidents_df.get('القطاع', '').str.contains(str(sector), na=False)
                ] if 'القطاع' in incidents_df.columns else incidents_df.sample(n=min(10, len(incidents_df)))
                
                if not sector_incidents.empty:
                    total_incidents = len(sector_incidents)
                    
                    # Count recommendations (assuming there's a recommendations column)
                    recommendations_count = 0
                    closed_count = 0
                    
                    # Check for recommendations columns
                    rec_columns = [col for col in sector_incidents.columns if 'توصي' in str(col) or 'recommendation' in str(col).lower()]
                    if rec_columns:
                        recommendations_count = sector_incidents[rec_columns[0]].notna().sum()
                    else:
                        recommendations_count = total_incidents  # Assume each incident has a recommendation
                    
                    # Check for status columns
                    status_columns = [col for col in sector_incidents.columns if 'حالة' in str(col) or 'status' in str(col).lower()]
                    if status_columns:
                        closed_count = sector_incidents[status_columns[0]].str.contains('مغلق|مكتمل|closed', na=False).sum()
                    else:
                        closed_count = int(total_incidents * 0.7)  # Assume 70% are closed
                    
                    closure_percentage = (closed_count / recommendations_count * 100) if recommendations_count > 0 else 0
                    
                    incidents_data.append({
                        'القطاع': sector,
                        'عدد الحوادث': total_incidents,
                        'عدد التوصيات': recommendations_count,
                        'مغلق': closed_count,
                        'مفتوح': recommendations_count - closed_count,
                        'نسبة الإغلاق %': closure_percentage
                    })
        
        if incidents_data:
            df = pd.DataFrame(incidents_data)
            
            st.dataframe(
                df,
                use_container_width=True,
                height=400,
                column_config={
                    "نسبة الإغلاق %": st.column_config.ProgressColumn(
                        "نسبة الإغلاق %",
                        help="نسبة إغلاق التوصيات",
                        min_value=0,
                        max_value=100,
                    ),
                }
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_incidents = df['عدد الحوادث'].sum()
                st.metric("إجمالي الحوادث", total_incidents)
            
            with col2:
                total_recommendations = df['عدد التوصيات'].sum()
                st.metric("إجمالي التوصيات", total_recommendations)
            
            with col3:
                total_closed = df['مغلق'].sum()
                st.metric("التوصيات المغلقة", total_closed)
            
            with col4:
                overall_closure_rate = (total_closed / total_recommendations * 100) if total_recommendations > 0 else 0
                st.metric("معدل الإغلاق الإجمالي", f"{overall_closure_rate:.1f}%")
            
            # Incidents trend analysis
            st.markdown("---")
            st.markdown("#### 📈 تحليل اتجاه الحوادث")
            
            if not incidents_df.empty:
                # Try to create a simple trend chart
                fig = px.bar(
                    df, 
                    x='القطاع', 
                    y='عدد الحوادث',
                    title="توزيع الحوادث حسب القطاع",
                    color='عدد الحوادث',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(
                    xaxis_title="القطاع",
                    yaxis_title="عدد الحوادث",
                    font=dict(family="Arial", size=12)
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات حوادث متاحة للتحليل")

    def create_risk_section(self, filtered_data):
        """Create risk management section"""
        st.markdown("### ⚠️ إدارة المخاطر")
        
        risk_data = filtered_data.get('تقييم_المخاطر', pd.DataFrame())
        
        if not risk_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 توزيع المخاطر")
                # Create risk distribution chart
                risk_levels = ['عالي', 'متوسط', 'منخفض']
                risk_counts = []
                
                for level in risk_levels:
                    count = risk_data.astype(str).apply(
                        lambda x: x.str.contains(level, na=False)
                    ).any(axis=1).sum()
                    risk_counts.append(count)
                
                fig = px.pie(
                    values=risk_counts,
                    names=risk_levels,
                    title="توزيع مستويات المخاطر",
                    color_discrete_map={
                        'عالي': '#ff4b4b',
                        'متوسط': '#ffa500', 
                        'منخفض': '#00cc88'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 اتجاه المخاطر")
                # Display risk data table
                st.dataframe(risk_data.head(10), use_container_width=True)
        else:
            st.info("لا توجد بيانات مخاطر متاحة")

    def create_performance_section(self, filtered_data):
        """Create performance section"""
        st.markdown("### 🎯 مؤشرات الأداء")
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 معدل الامتثال")
            # Calculate compliance rate
            inspection_data = filtered_data.get('ملاحظات_التفتيش', pd.DataFrame())
            if not inspection_data.empty:
                total_inspections = len(inspection_data)
                completed_inspections = len(inspection_data[
                    inspection_data.get('الحالة', '').str.contains('مكتمل|مغلق', na=False)
                ])
                compliance_rate = (completed_inspections / total_inspections * 100) if total_inspections > 0 else 0
                
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = compliance_rate,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "معدل الامتثال %"},
                    delta = {'reference': 80},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### ⚡ الاستجابة السريعة")
            # Response time metrics
            incidents_data = filtered_data.get('الحوادث', pd.DataFrame())
            if not incidents_data.empty:
                avg_response_time = 2.5  # Simulated data
                
                fig = go.Figure(go.Indicator(
                    mode = "number+delta",
                    value = avg_response_time,
                    number = {'suffix': " أيام"},
                    delta = {'position': "top", 'reference': 3},
                    title = {'text': "متوسط وقت الاستجابة"},
                ))
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("#### 🎯 معدل الإنجاز")
            # Completion rate
            completion_rate = 85  # Simulated data
            
            fig = go.Figure(go.Indicator(
                mode = "number+gauge",
                value = completion_rate,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "معدل الإنجاز %"},
                gauge = {'axis': {'range': [None, 100]},
                        'bar': {'color': "green"},
                        'steps': [{'range': [0, 70], 'color': "lightgray"},
                                 {'range': [70, 90], 'color': "gray"}],
                        'threshold': {'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75, 'value': 95}}
            ))
            st.plotly_chart(fig, use_container_width=True)

    def create_quality_report_page(self, quality_report):
        """Create comprehensive quality report page"""
        st.header("📋 تقرير جودة البيانات الشامل")
        
        if quality_report:
            # Overall summary
            total_records = sum([report.get('total_rows', 0) for report in quality_report.values()])
            total_missing = sum([report.get('missing_values', 0) for report in quality_report.values()])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("إجمالي السجلات", f"{total_records:,}")
            
            with col2:
                st.metric("مجموعات البيانات", len(quality_report))
            
            with col3:
                missing_percentage = (total_missing / total_records * 100) if total_records > 0 else 0
                st.metric("البيانات المفقودة", f"{missing_percentage:.1f}%")
            
            with col4:
                avg_quality = 100 - missing_percentage
                st.metric("متوسط الجودة", f"{avg_quality:.1f}%")
            
            # Detailed reports for each dataset
            st.markdown("---")
            st.markdown("### 📊 تقارير مفصلة لكل مجموعة بيانات")
            
            for dataset_name, report in quality_report.items():
                with st.expander(f"📋 {dataset_name}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 إحصائيات عامة")
                        
                        metrics = {
                            'إجمالي الصفوف': report.get('total_rows', 0),
                            'إجمالي الأعمدة': report.get('total_columns', 0),
                            'البيانات المفقودة': report.get('missing_values', 0),
                            'الصفوف المكررة': report.get('duplicate_rows', 0),
                            'نسبة البيانات المفقودة': f"{report.get('missing_data_percentage', 0):.1f}%"
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

    def run(self):
        """Main application runner"""
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .fade-in-up {
            animation: fadeInUp 1s ease-out;
        }
        
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
        
        .stSelectbox > div > div {
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        
        .stMultiSelect > div > div {
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Load data if not already loaded
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
        
        # Create enhanced sidebar with navigation first
        filters, selected_page = self.create_enhanced_sidebar(unified_data)
        
        # Show help if requested
        if st.session_state.get('show_help', False):
            return
        
        # Display selected page
        if selected_page == "الرئيسية المتقدمة":
            self.create_ultimate_main_dashboard(unified_data, kpi_data, filters)
        
        elif selected_page == "التحليلات الذكية":
            self.create_analytics_section(unified_data)
        
        elif selected_page == "مركز التصدير":
            advanced_features.create_export_center(unified_data, kpi_data)
        
        elif selected_page == "رفع البيانات":
            advanced_features.create_manual_upload_section()
        
        elif selected_page == "تشغيل مساعد الذكاء الاصطناعي":
            try:
                create_chatbot_interface(unified_data, kpi_data)
            except Exception as e:
                st.error(f"خطأ في المساعد الذكي: {str(e)}")
                st.info("المساعد الذكي غير متاح حالياً")
        
        elif selected_page == "المراقبة المباشرة":
            advanced_features.create_real_time_monitoring(unified_data)
        
        elif selected_page == "تقرير الجودة":
            self.create_quality_report_page(quality_report)
        
        # Footer
        current_theme = theme_manager.get_current_theme()
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: {current_theme['text_secondary']}; padding: 1rem;'>
            <p>🛡️ Ultimate Safety & Compliance Dashboard v4.0 | {current_theme['icon']} {current_theme['name']}</p>
            <p>آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        """, unsafe_allow_html=True)

# Main execution
def main():
    """Main function to run the ultimate dashboard"""
    dashboard = UltimateDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()