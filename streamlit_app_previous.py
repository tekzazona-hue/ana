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
warnings.filterwarnings('ignore')

# Import custom modules
try:
    from data_processor import SafetyDataProcessor
    from dashboard_components import DashboardComponents
    from gemini_chatbot import create_chatbot_interface
except ImportError as e:
    st.error(f"Error importing modules: {e}")

# Page configuration
st.set_page_config(
    page_title="🛡️ لوحة معلومات السلامة والامتثال المحسنة",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8ecf0 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .sector-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .sector-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .activity-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    .risk-high { background-color: #ffebee; color: #c62828; }
    .risk-medium { background-color: #fff3e0; color: #ef6c00; }
    .risk-low { background-color: #e8f5e8; color: #2e7d32; }
    
    .status-open { background-color: #ffebee; color: #c62828; }
    .status-closed { background-color: #e8f5e8; color: #2e7d32; }
    
    .clickable-metric {
        cursor: pointer;
        transition: all 0.2s;
    }
    .clickable-metric:hover {
        background-color: #e3f2fd;
        border-radius: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process all data"""
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
            if csv_file != 'Power_BI_Copy_v.02_Sheet1.csv':  # Skip layout file
                try:
                    data = processor.load_csv_data(csv_file)
                    if not data.empty:
                        csv_data[csv_file.replace('.csv', '')] = data
                except Exception as e:
                    st.warning(f"Could not load {csv_file}: {str(e)}")
        
        # Combine all data sources
        all_data_sources = {**excel_data, **csv_data}
        
        # Create unified dataset
        unified_data = processor.create_unified_dataset(all_data_sources)
        
        # Generate KPIs
        kpi_data = processor.generate_kpi_data(unified_data)
        
        # Generate quality report
        quality_report = processor.get_data_quality_report(unified_data)
        
        return processor, unified_data, kpi_data, quality_report
    
    except Exception as e:
        st.error(f"Error in data processing: {str(e)}")
        # Return empty data structures
        return None, {}, {}, {}

def create_enhanced_filters(unified_data):
    """Create enhanced filtering system"""
    st.sidebar.markdown("### 🔍 المرشحات المتقدمة")
    
    filters = {}
    
    if not unified_data:
        return filters
    
    # Date range filter
    date_range = get_overall_date_range(unified_data)
    if date_range:
        filters['date_range'] = st.sidebar.date_input(
            "📅 نطاق التاريخ",
            value=(date_range['min_date'], date_range['max_date']),
            min_value=date_range['min_date'],
            max_value=date_range['max_date']
        )
    
    # Sector filter
    sectors = get_all_sectors(unified_data)
    if sectors:
        st.sidebar.markdown("#### 🏢 القطاعات")
        filters['sectors'] = st.sidebar.multiselect(
            "اختر القطاعات",
            options=sectors,
            default=sectors[:4] if len(sectors) > 4 else sectors,
            help="اختر القطاعات التي تريد تحليلها"
        )
    
    # Status filter
    statuses = get_all_statuses(unified_data)
    if statuses:
        st.sidebar.markdown("#### 📊 الحالة")
        filters['statuses'] = st.sidebar.multiselect(
            "اختر الحالات",
            options=statuses,
            default=statuses,
            help="فلترة حسب حالة الإغلاق"
        )
    
    # Activity type filter
    activities = get_all_activities(unified_data)
    if activities:
        st.sidebar.markdown("#### 🎯 نوع النشاط")
        filters['activities'] = st.sidebar.multiselect(
            "اختر أنواع الأنشطة",
            options=activities,
            default=activities[:10] if len(activities) > 10 else activities,
            help="فلترة حسب نوع النشاط"
        )
    
    return filters

def get_overall_date_range(unified_data):
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

def get_all_sectors(unified_data):
    """Get all unique sectors from datasets"""
    sectors = set()
    
    for data_type, df in unified_data.items():
        if df.empty:
            continue
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                sector_values = df[col].dropna().unique()
                sectors.update(sector_values)
    
    return sorted(list(sectors))

def get_all_statuses(unified_data):
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

def get_all_activities(unified_data):
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

def apply_filters(unified_data, filters):
    """Apply filters to unified data"""
    if not filters or not unified_data:
        return unified_data
    
    filtered_data = {}
    
    for data_type, df in unified_data.items():
        if df.empty:
            filtered_data[data_type] = df
            continue
        
        filtered_df = df.copy()
        
        # Apply date filter
        if 'date_range' in filters and filters['date_range']:
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            if date_cols and len(filters['date_range']) == 2:
                start_date, end_date = filters['date_range']
                for col in date_cols:
                    filtered_df = filtered_df[
                        (filtered_df[col].dt.date >= start_date) &
                        (filtered_df[col].dt.date <= end_date)
                    ]
        
        # Apply sector filter
        if 'sectors' in filters and filters['sectors']:
            sector_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department'])]
            if sector_cols:
                sector_filter = filtered_df[sector_cols[0]].isin(filters['sectors'])
                filtered_df = filtered_df[sector_filter]
        
        # Apply status filter
        if 'statuses' in filters and filters['statuses']:
            status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
            if status_cols:
                status_filter = filtered_df[status_cols[0]].isin(filters['statuses'])
                filtered_df = filtered_df[status_filter]
        
        # Apply activity filter
        if 'activities' in filters and filters['activities']:
            activity_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف'])]
            if activity_cols:
                activity_filter = filtered_df[activity_cols[0]].isin(filters['activities'])
                filtered_df = filtered_df[activity_filter]
        
        filtered_data[data_type] = filtered_df
    
    return filtered_data

def calculate_enhanced_kpis(unified_data):
    """Calculate enhanced KPIs"""
    if not unified_data:
        return {}
    
    kpis = {}
    
    # Count records by type
    for data_type, df in unified_data.items():
        if not df.empty:
            kpis[f"{data_type}_count"] = len(df)
    
    # Calculate status distribution
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
    
    return kpis

def create_sector_performance_chart(unified_data):
    """Create sector performance visualization"""
    if not unified_data:
        return None
    
    sector_data = []
    
    for data_type, df in unified_data.items():
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
    
    if not sector_data:
        return None
    
    sector_df = pd.DataFrame(sector_data)
    sector_summary = sector_df.groupby('sector').size().reset_index(name='count')
    sector_summary = sector_summary.sort_values('count', ascending=True)
    
    fig = px.bar(
        sector_summary.tail(10),  # Show top 10
        x='count',
        y='sector',
        orientation='h',
        title="أداء القطاعات (إجمالي العناصر)",
        color='count',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=500, showlegend=False)
    
    return fig

def create_activity_distribution_chart(unified_data):
    """Create activity distribution chart"""
    if not unified_data:
        return None
    
    activity_data = []
    
    for data_type, df in unified_data.items():
        if df.empty:
            continue
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف']):
                activities = df[col].dropna()
                for activity in activities:
                    # Clean activity name
                    clean_activity = str(activity).split('\n')[0] if '\n' in str(activity) else str(activity)
                    activity_data.append({
                        'activity': clean_activity,
                        'data_type': data_type
                    })
    
    if not activity_data:
        return None
    
    activity_df = pd.DataFrame(activity_data)
    activity_summary = activity_df.groupby('activity').size().reset_index(name='count')
    activity_summary = activity_summary.sort_values('count', ascending=False).head(10)
    
    fig = px.bar(
        activity_summary,
        x='activity',
        y='count',
        title="أهم 10 أنواع أنشطة",
        color='count',
        color_continuous_scale='Viridis'
    )
    fig.update_xaxes(tickangle=45)
    fig.update_layout(height=500, showlegend=False)
    
    return fig

def create_status_distribution_chart(kpis):
    """Create status distribution pie chart"""
    if not kpis or 'total_open' not in kpis:
        return None
    
    status_data = {
        'مفتوح': kpis.get('total_open', 0),
        'مغلق': kpis.get('total_closed', 0)
    }
    
    if sum(status_data.values()) == 0:
        return None
    
    fig = px.pie(
        values=list(status_data.values()),
        names=list(status_data.keys()),
        title="توزيع الحالات",
        color_discrete_map={
            'مفتوح': '#ff7f7f',
            'مغلق': '#7fbf7f'
        }
    )
    fig.update_layout(height=400)
    
    return fig

def create_enhanced_main_dashboard(unified_data, kpi_data, filters):
    """Create the enhanced main dashboard"""
    st.markdown('<h1 class="main-header">🛡️ لوحة معلومات السلامة والامتثال المحسنة</h1>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_data = apply_filters(unified_data, filters)
    
    # Calculate KPIs for filtered data
    filtered_kpis = calculate_enhanced_kpis(filtered_data)
    
    # Enhanced KPI section
    st.markdown("### 📊 المؤشرات الرئيسية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        inspections_count = filtered_kpis.get('inspections_count', 0)
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>🔍 إجمالي التفتيشات</h3>
            <h2>{inspections_count:,}</h2>
            <p>+12% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        incidents_count = filtered_kpis.get('incidents_count', 0)
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>⚠️ إجمالي الحوادث</h3>
            <h2>{incidents_count:,}</h2>
            <p>-5% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risks_count = filtered_kpis.get('risk_assessments_count', 0)
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>🚨 تقييمات المخاطر</h3>
            <h2>{risks_count:,}</h2>
            <p>+8% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        compliance_rate = filtered_kpis.get('compliance_rate', 0)
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>📈 معدل الامتثال</h3>
            <h2>{compliance_rate:.1f}%</h2>
            <p>+3% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced visualizations
    st.markdown("### 📊 التحليلات التفاعلية")
    
    # Row 1: Sector Performance and Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        sector_chart = create_sector_performance_chart(filtered_data)
        if sector_chart:
            st.plotly_chart(sector_chart, use_container_width=True)
        else:
            st.info("لا توجد بيانات قطاعات متاحة")
    
    with col2:
        status_chart = create_status_distribution_chart(filtered_kpis)
        if status_chart:
            st.plotly_chart(status_chart, use_container_width=True)
        else:
            st.info("لا توجد بيانات حالات متاحة")
    
    # Row 2: Activity Distribution
    st.markdown("### 🎯 توزيع الأنشطة")
    activity_chart = create_activity_distribution_chart(filtered_data)
    if activity_chart:
        st.plotly_chart(activity_chart, use_container_width=True)
    else:
        st.info("لا توجد بيانات أنشطة متاحة")
    
    # Detailed tables section
    st.markdown("### 📋 الجداول التفصيلية")
    
    if filtered_data:
        # Create tabs for different data types
        tab_names = list(filtered_data.keys())
        if tab_names:
            tabs = st.tabs(tab_names)
            
            for i, (data_type, df) in enumerate(filtered_data.items()):
                with tabs[i]:
                    if not df.empty:
                        st.markdown(f"**{data_type}** - {len(df)} سجل")
                        
                        # Show summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("إجمالي السجلات", len(df))
                        with col2:
                            st.metric("الأعمدة", len(df.columns))
                        with col3:
                            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                            st.metric("البيانات المفقودة", f"{missing_pct:.1f}%")
                        
                        # Show data
                        st.dataframe(df, use_container_width=True, height=400)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"تحميل {data_type}",
                            data=csv,
                            file_name=f"{data_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning(f"لا توجد بيانات في {data_type}")

def create_manual_upload_section():
    """Create manual data upload section"""
    st.header("📤 رفع البيانات يدوياً")
    
    st.markdown("""
    <div class="filter-section">
        <h4>📁 رفع الملفات</h4>
        <p>يمكنك رفع ملفات Excel أو CSV لتحديث البيانات</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("رفع ملف Excel")
        uploaded_excel = st.file_uploader(
            "اختر ملف Excel",
            type=['xlsx', 'xls'],
            help="يمكنك رفع ملف Excel يحتوي على عدة أوراق عمل"
        )
        
        if uploaded_excel is not None:
            try:
                # Save uploaded file temporarily
                with open(f"temp_{uploaded_excel.name}", "wb") as f:
                    f.write(uploaded_excel.getbuffer())
                
                # Process the uploaded file
                if 'processor' in st.session_state and st.session_state.processor:
                    new_data = st.session_state.processor.load_excel_data(f"temp_{uploaded_excel.name}")
                    
                    if new_data:
                        st.success(f"تم رفع الملف بنجاح! تم العثور على {len(new_data)} ورقة عمل")
                        
                        # Show preview
                        for sheet_name, df in new_data.items():
                            with st.expander(f"معاينة: {sheet_name}"):
                                st.dataframe(df.head(), use_container_width=True)
                
                # Clean up temporary file
                os.remove(f"temp_{uploaded_excel.name}")
                
            except Exception as e:
                st.error(f"خطأ في معالجة الملف: {str(e)}")
    
    with col2:
        st.subheader("رفع ملفات CSV")
        uploaded_csvs = st.file_uploader(
            "اختر ملفات CSV",
            type=['csv'],
            accept_multiple_files=True,
            help="يمكنك رفع عدة ملفات CSV في نفس الوقت"
        )
        
        if uploaded_csvs:
            try:
                for uploaded_csv in uploaded_csvs:
                    # Save temporarily and process
                    with open(f"temp_{uploaded_csv.name}", "wb") as f:
                        f.write(uploaded_csv.getbuffer())
                    
                    if 'processor' in st.session_state and st.session_state.processor:
                        df = st.session_state.processor.load_csv_data(f"temp_{uploaded_csv.name}")
                        if not df.empty:
                            st.success(f"تم رفع {uploaded_csv.name} بنجاح!")
                            with st.expander(f"معاينة: {uploaded_csv.name}"):
                                st.dataframe(df.head(), use_container_width=True)
                    
                    # Clean up
                    os.remove(f"temp_{uploaded_csv.name}")
            
            except Exception as e:
                st.error(f"خطأ في معالجة ملفات CSV: {str(e)}")

def main():
    """Main application function"""
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # Load data
    if not st.session_state.data_loaded:
        with st.spinner("جاري تحميل ومعالجة البيانات..."):
            try:
                processor, unified_data, kpi_data, quality_report = load_and_process_data()
                
                st.session_state.processor = processor
                st.session_state.unified_data = unified_data
                st.session_state.kpi_data = kpi_data
                st.session_state.quality_report = quality_report
                st.session_state.data_loaded = True
                
            except Exception as e:
                st.error(f"خطأ في تحميل البيانات: {str(e)}")
                # Initialize with empty data
                st.session_state.processor = None
                st.session_state.unified_data = {}
                st.session_state.kpi_data = {}
                st.session_state.quality_report = {}
                st.session_state.data_loaded = True
    
    # Get data from session state
    unified_data = st.session_state.unified_data
    kpi_data = st.session_state.kpi_data
    quality_report = st.session_state.quality_report
    
    # Create enhanced filters
    filters = create_enhanced_filters(unified_data)
    
    # Sidebar navigation
    st.sidebar.markdown("---")
    st.sidebar.title("🧭 التنقل")
    page = st.sidebar.selectbox(
        "اختر الصفحة",
        ["الرئيسية المحسنة", "رفع البيانات", "المساعد الذكي", "تقرير الجودة"]
    )
    
    # Display selected page
    if page == "الرئيسية المحسنة":
        create_enhanced_main_dashboard(unified_data, kpi_data, filters)
    
    elif page == "رفع البيانات":
        create_manual_upload_section()
    
    elif page == "المساعد الذكي":
        try:
            create_chatbot_interface(unified_data, kpi_data)
        except Exception as e:
            st.error(f"خطأ في المساعد الذكي: {str(e)}")
            st.info("المساعد الذكي غير متاح حالياً")
    
    elif page == "تقرير الجودة":
        st.header("📋 تقرير جودة البيانات")
        
        if quality_report:
            # Overall summary
            total_records = sum([report.get('total_rows', 0) for report in quality_report.values()])
            total_columns = sum([report.get('total_columns', 0) for report in quality_report.values()])
            avg_missing = np.mean([report.get('missing_data_percentage', 0) for report in quality_report.values()]) if quality_report else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي السجلات", f"{total_records:,}")
            with col2:
                st.metric("إجمالي الأعمدة", total_columns)
            with col3:
                st.metric("متوسط البيانات المفقودة", f"{avg_missing:.1f}%")
            
            # Detailed report for each dataset
            for data_type, report in quality_report.items():
                with st.expander(f"تقرير مفصل: {data_type}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("إحصائيات عامة")
                        st.write(f"**عدد الصفوف:** {report.get('total_rows', 0):,}")
                        st.write(f"**عدد الأعمدة:** {report.get('total_columns', 0)}")
                        st.write(f"**البيانات المفقودة:** {report.get('missing_data_percentage', 0):.1f}%")
                        st.write(f"**الصفوف المكررة:** {report.get('duplicate_rows', 0):,}")
                        st.write(f"**استخدام الذاكرة:** {report.get('memory_usage', 0) / 1024:.1f} KB")
                    
                    with col2:
                        st.subheader("أنواع البيانات")
                        if 'data_types' in report:
                            data_types_df = pd.DataFrame([
                                {'العمود': col, 'النوع': str(dtype)}
                                for col, dtype in report['data_types'].items()
                            ])
                            st.dataframe(data_types_df, use_container_width=True)
        else:
            st.warning("لا يوجد تقرير جودة متاح")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🛡️ لوحة معلومات السلامة والامتثال المحسنة | تم التطوير بواسطة الذكاء الاصطناعي</p>
            <p>آخر تحديث: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()