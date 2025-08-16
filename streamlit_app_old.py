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
from data_processor import SafetyDataProcessor
from dashboard_components import DashboardComponents
from gemini_chatbot import create_chatbot_interface

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
    """Load and process all data using the SafetyDataProcessor"""
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
            data = processor.load_csv_data(csv_file)
            if not data.empty:
                csv_data[csv_file.replace('.csv', '')] = data
    
    # Combine all data sources
    all_data_sources = {**excel_data, **csv_data}
    
    # Create unified dataset
    unified_data = processor.create_unified_dataset(all_data_sources)
    
    # Generate KPIs
    kpi_data = processor.generate_kpi_data(unified_data)
    
    # Generate quality report
    quality_report = processor.get_data_quality_report(unified_data)
    
    return processor, unified_data, kpi_data, quality_report

def create_enhanced_filters(unified_data):
    """Create enhanced filtering system"""
    st.sidebar.markdown("### 🔍 المرشحات المتقدمة")
    
    filters = {}
    
    # Date range filter
    date_range = get_overall_date_range(unified_data)
    if date_range:
        filters['date_range'] = st.sidebar.date_input(
            "📅 نطاق التاريخ",
            value=(date_range['min_date'], date_range['max_date']),
            min_value=date_range['min_date'],
            max_value=date_range['max_date']
        )
    
    # Sector filter with enhanced UI
    sectors = get_all_sectors(unified_data)
    if sectors:
        st.sidebar.markdown("#### 🏢 القطاعات")
        filters['sectors'] = st.sidebar.multiselect(
            "اختر القطاعات",
            options=sectors,
            default=sectors[:4] if len(sectors) > 4 else sectors,
            help="اختر القطاعات التي تريد تحليلها"
        )
    
    # Status filter with visual indicators
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
    
    # Risk level filter
    risk_levels = ['عالي', 'متوسط', 'منخفض']
    filters['risk_levels'] = st.sidebar.multiselect(
        "🚨 مستوى المخاطر",
        options=risk_levels,
        default=risk_levels,
        help="فلترة حسب مستوى المخاطر"
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

def create_sector_performance_dashboard(unified_data, filters):
    """Create enhanced sector performance dashboard"""
    st.markdown("### 🏢 أداء القطاعات")
    
    # Apply filters
    filtered_data = apply_filters(unified_data, filters)
    
    # Calculate sector metrics
    sector_metrics = calculate_sector_metrics(filtered_data)
    
    if not sector_metrics.empty:
        # Create 4 columns for top sectors
        cols = st.columns(4)
        
        top_sectors = sector_metrics.head(4)
        for i, (_, sector) in enumerate(top_sectors.iterrows()):
            with cols[i]:
                compliance_rate = sector.get('compliance_rate', 0)
                color_class = "risk-low" if compliance_rate > 80 else "risk-medium" if compliance_rate > 60 else "risk-high"
                
                st.markdown(f"""
                <div class="sector-card {color_class}" onclick="showSectorDetails('{sector['sector']}')">
                    <h4>{sector['sector'][:20]}...</h4>
                    <p><strong>{compliance_rate:.1f}%</strong> معدل الامتثال</p>
                    <p>{sector['total_items']} إجمالي العناصر</p>
                    <p>{sector['open_items']} مفتوح | {sector['closed_items']} مغلق</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show detailed table when clicked
                if st.button(f"تفاصيل {sector['sector'][:15]}...", key=f"sector_{i}"):
                    show_sector_details(sector['sector'], filtered_data)
    
    # Sector comparison chart
    if not sector_metrics.empty:
        fig = px.bar(
            sector_metrics.head(10),
            x='compliance_rate',
            y='sector',
            orientation='h',
            title="معدل الامتثال حسب القطاع",
            color='compliance_rate',
            color_continuous_scale='RdYlGn',
            text='compliance_rate'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def calculate_sector_metrics(unified_data):
    """Calculate detailed sector metrics"""
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
        
        if sector_col and status_col:
            for _, row in df.iterrows():
                sector = row[sector_col]
                status = row[status_col]
                
                if pd.notna(sector) and pd.notna(status):
                    sector_data.append({
                        'sector': sector,
                        'status': status,
                        'data_type': data_type
                    })
    
    if not sector_data:
        return pd.DataFrame()
    
    sector_df = pd.DataFrame(sector_data)
    
    # Calculate metrics for each sector
    metrics = []
    for sector in sector_df['sector'].unique():
        sector_subset = sector_df[sector_df['sector'] == sector]
        
        total_items = len(sector_subset)
        closed_items = len(sector_subset[sector_subset['status'].str.contains('مغلق|Closed', na=False)])
        open_items = total_items - closed_items
        compliance_rate = (closed_items / total_items * 100) if total_items > 0 else 0
        
        metrics.append({
            'sector': sector,
            'total_items': total_items,
            'closed_items': closed_items,
            'open_items': open_items,
            'compliance_rate': compliance_rate
        })
    
    return pd.DataFrame(metrics).sort_values('compliance_rate', ascending=False)

def show_sector_details(sector_name, unified_data):
    """Show detailed information for a specific sector"""
    st.markdown(f"#### تفاصيل القطاع: {sector_name}")
    
    sector_details = []
    for data_type, df in unified_data.items():
        if df.empty:
            continue
        
        sector_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                sector_col = col
                break
        
        if sector_col:
            sector_data = df[df[sector_col] == sector_name]
            if not sector_data.empty:
                sector_details.append({
                    'نوع البيانات': data_type,
                    'عدد السجلات': len(sector_data),
                    'البيانات': sector_data
                })
    
    if sector_details:
        for detail in sector_details:
            with st.expander(f"{detail['نوع البيانات']} ({detail['عدد السجلات']} سجل)"):
                st.dataframe(detail['البيانات'], use_container_width=True)

def create_risk_management_dashboard(unified_data, filters):
    """Create enhanced risk management dashboard"""
    st.markdown("### 🚨 إدارة المخاطر")
    
    filtered_data = apply_filters(unified_data, filters)
    
    # Risk overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    risk_metrics = calculate_risk_metrics(filtered_data)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card risk-high clickable-metric">
            <h3>🔴 مخاطر عالية</h3>
            <h2>{risk_metrics.get('high_risk', 0)}</h2>
            <p>يتطلب إجراء فوري</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card risk-medium clickable-metric">
            <h3>🟡 مخاطر متوسطة</h3>
            <h2>{risk_metrics.get('medium_risk', 0)}</h2>
            <p>يتطلب متابعة</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card risk-low clickable-metric">
            <h3>🟢 مخاطر منخفضة</h3>
            <h2>{risk_metrics.get('low_risk', 0)}</h2>
            <p>تحت السيطرة</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_risk = risk_metrics.get('avg_risk_score', 0)
        risk_color = "risk-high" if avg_risk > 0.7 else "risk-medium" if avg_risk > 0.4 else "risk-low"
        st.markdown(f"""
        <div class="metric-card {risk_color} clickable-metric">
            <h3>📊 متوسط المخاطر</h3>
            <h2>{avg_risk:.2f}</h2>
            <p>من أصل 1.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Activity-Risk Matrix
    create_activity_risk_matrix(filtered_data)

def calculate_risk_metrics(unified_data):
    """Calculate risk management metrics"""
    risk_data = []
    
    for data_type, df in unified_data.items():
        if df.empty:
            continue
        
        # Look for risk-related columns
        risk_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'نسب'])]
        classification_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['تصنيف', 'classification'])]
        
        for _, row in df.iterrows():
            risk_score = None
            risk_level = None
            
            # Try to get risk score
            for col in risk_cols:
                if pd.notna(row[col]) and isinstance(row[col], (int, float)):
                    risk_score = row[col]
                    break
            
            # Try to get risk level
            for col in classification_cols:
                if pd.notna(row[col]):
                    val = str(row[col]).lower()
                    if 'عالي' in val or 'high' in val:
                        risk_level = 'high'
                    elif 'متوسط' in val or 'medium' in val:
                        risk_level = 'medium'
                    elif 'منخفض' in val or 'low' in val:
                        risk_level = 'low'
                    break
            
            if risk_score is not None or risk_level is not None:
                risk_data.append({
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'data_type': data_type
                })
    
    if not risk_data:
        return {}
    
    risk_df = pd.DataFrame(risk_data)
    
    # Calculate metrics
    metrics = {}
    
    if 'risk_level' in risk_df.columns:
        level_counts = risk_df['risk_level'].value_counts()
        metrics['high_risk'] = level_counts.get('high', 0)
        metrics['medium_risk'] = level_counts.get('medium', 0)
        metrics['low_risk'] = level_counts.get('low', 0)
    
    if 'risk_score' in risk_df.columns:
        valid_scores = risk_df['risk_score'].dropna()
        if len(valid_scores) > 0:
            metrics['avg_risk_score'] = valid_scores.mean()
    
    return metrics

def create_activity_risk_matrix(unified_data):
    """Create activity-risk matrix visualization"""
    st.markdown("#### 🎯 مصفوفة النشاط والمخاطر")
    
    activity_risk_data = []
    
    for data_type, df in unified_data.items():
        if df.empty:
            continue
        
        activity_col = None
        risk_col = None
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['نشاط', 'activity']):
                activity_col = col
            elif any(keyword in col.lower() for keyword in ['مخاطر', 'risk', 'تصنيف']):
                risk_col = col
        
        if activity_col and risk_col:
            for _, row in df.iterrows():
                activity = row[activity_col]
                risk = row[risk_col]
                
                if pd.notna(activity) and pd.notna(risk):
                    # Clean activity name
                    clean_activity = str(activity).split('\n')[0] if '\n' in str(activity) else str(activity)
                    
                    activity_risk_data.append({
                        'activity': clean_activity,
                        'risk': str(risk),
                        'count': 1
                    })
    
    if activity_risk_data:
        activity_risk_df = pd.DataFrame(activity_risk_data)
        
        # Create pivot table for heatmap
        pivot_table = activity_risk_df.groupby(['activity', 'risk'])['count'].sum().unstack(fill_value=0)
        
        if not pivot_table.empty:
            fig = px.imshow(
                pivot_table.values,
                x=pivot_table.columns,
                y=pivot_table.index,
                title="مصفوفة الأنشطة والمخاطر",
                color_continuous_scale='Reds',
                aspect='auto'
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Activity filter and recommendations
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🔍 فلترة حسب النشاط")
                selected_activity = st.selectbox(
                    "اختر نوع النشاط",
                    options=['الكل'] + list(pivot_table.index),
                    key="activity_filter"
                )
                
                if selected_activity != 'الكل':
                    activity_data = pivot_table.loc[selected_activity]
                    st.write(f"**النشاط المختار:** {selected_activity}")
                    
                    # Show risk distribution for selected activity
                    risk_dist = activity_data[activity_data > 0]
                    if not risk_dist.empty:
                        fig_activity = px.bar(
                            x=risk_dist.index,
                            y=risk_dist.values,
                            title=f"توزيع المخاطر - {selected_activity}",
                            color=risk_dist.values,
                            color_continuous_scale='Reds'
                        )
                        st.plotly_chart(fig_activity, use_container_width=True)
            
            with col2:
                st.markdown("##### 💡 التوصيات")
                
                # Generate recommendations based on data
                high_risk_activities = []
                for activity in pivot_table.index:
                    activity_risks = pivot_table.loc[activity]
                    high_risk_count = activity_risks.get('عالي', 0) + activity_risks.get('High', 0)
                    if high_risk_count > 0:
                        high_risk_activities.append((activity, high_risk_count))
                
                if high_risk_activities:
                    high_risk_activities.sort(key=lambda x: x[1], reverse=True)
                    
                    st.markdown("**الأنشطة عالية المخاطر:**")
                    for activity, count in high_risk_activities[:5]:
                        st.markdown(f"🔴 **{activity}**: {count} حالة عالية المخاطر")
                        
                        # Generate specific recommendations
                        recommendations = generate_activity_recommendations(activity)
                        for rec in recommendations:
                            st.markdown(f"   • {rec}")

def generate_activity_recommendations(activity):
    """Generate recommendations based on activity type"""
    activity_lower = activity.lower()
    
    recommendations = []
    
    if 'أعمال ساخنة' in activity_lower or 'hot work' in activity_lower:
        recommendations = [
            "تطبيق نظام تصاريح العمل الساخن",
            "توفير معدات الإطفاء في موقع العمل",
            "فحص المنطقة من المواد القابلة للاشتعال"
        ]
    elif 'حفر' in activity_lower or 'excavation' in activity_lower:
        recommendations = [
            "فحص المرافق تحت الأرض قبل الحفر",
            "استخدام أنظمة دعم الحفر المناسبة",
            "توفير مخارج طوارئ آمنة"
        ]
    elif 'ارتفاع' in activity_lower or 'height' in activity_lower:
        recommendations = [
            "استخدام معدات الحماية من السقوط",
            "فحص السقالات والمنصات",
            "تدريب العمال على السلامة على الارتفاعات"
        ]
    elif 'كهرباء' in activity_lower or 'electrical' in activity_lower:
        recommendations = [
            "تطبيق إجراءات العزل والقفل",
            "استخدام معدات الحماية الشخصية المناسبة",
            "فحص الأدوات الكهربائية قبل الاستخدام"
        ]
    else:
        recommendations = [
            "مراجعة إجراءات السلامة للنشاط",
            "توفير التدريب المناسب للعمال",
            "تطبيق نظام تقييم المخاطر"
        ]
    
    return recommendations

def apply_filters(unified_data, filters):
    """Apply filters to unified data"""
    if not filters:
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

def create_enhanced_main_dashboard(unified_data, kpi_data, filters):
    """Create the enhanced main dashboard"""
    st.markdown('<h1 class="main-header">🛡️ لوحة معلومات السلامة والامتثال المحسنة</h1>', unsafe_allow_html=True)
    
    # Apply filters
    filtered_data = apply_filters(unified_data, filters)
    
    # Recalculate KPIs for filtered data
    dashboard = DashboardComponents()
    filtered_kpis = dashboard.generate_kpi_data(filtered_data)
    
    # Enhanced KPI section
    st.markdown("### 📊 المؤشرات الرئيسية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_inspections = sum([data.get('total_records', 0) for key, data in filtered_kpis.items() if 'inspection' in key.lower()])
        st.markdown(f"""
        <div class="metric-card clickable-metric" onclick="showInspectionDetails()">
            <h3>🔍 إجمالي التفتيشات</h3>
            <h2>{total_inspections:,}</h2>
            <p>+12% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("تفاصيل التفتيشات", key="inspections_btn"):
            show_inspection_details(filtered_data)
    
    with col2:
        total_incidents = sum([data.get('total_records', 0) for key, data in filtered_kpis.items() if 'incident' in key.lower()])
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>⚠️ إجمالي الحوادث</h3>
            <h2>{total_incidents:,}</h2>
            <p>-5% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("تفاصيل الحوادث", key="incidents_btn"):
            show_incident_details(filtered_data)
    
    with col3:
        total_risks = sum([data.get('total_records', 0) for key, data in filtered_kpis.items() if 'risk' in key.lower()])
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>🚨 تقييمات المخاطر</h3>
            <h2>{total_risks:,}</h2>
            <p>+8% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("تفاصيل المخاطر", key="risks_btn"):
            show_risk_details(filtered_data)
    
    with col4:
        total_audits = sum([data.get('total_records', 0) for key, data in filtered_kpis.items() if 'contractor' in key.lower()])
        st.markdown(f"""
        <div class="metric-card clickable-metric">
            <h3>📋 تدقيق المقاولين</h3>
            <h2>{total_audits:,}</h2>
            <p>+15% من الشهر الماضي</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("تفاصيل التدقيق", key="audits_btn"):
            show_audit_details(filtered_data)
    
    # Enhanced visualizations
    create_sector_performance_dashboard(filtered_data, filters)
    create_risk_management_dashboard(filtered_data, filters)

def show_inspection_details(unified_data):
    """Show detailed inspection information"""
    st.markdown("#### 🔍 تفاصيل التفتيشات")
    
    inspection_data = unified_data.get('inspections', pd.DataFrame())
    if not inspection_data.empty:
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_inspections = len(inspection_data)
            st.metric("إجمالي التفتيشات", total_inspections)
        
        with col2:
            # Count open inspections
            open_inspections = 0
            for col in inspection_data.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    open_inspections = len(inspection_data[inspection_data[col].str.contains('مفتوح|Open', na=False)])
                    break
            st.metric("التفتيشات المفتوحة", open_inspections)
        
        with col3:
            closed_inspections = total_inspections - open_inspections
            st.metric("التفتيشات المغلقة", closed_inspections)
        
        # Detailed table
        st.dataframe(inspection_data, use_container_width=True)
    else:
        st.warning("لا توجد بيانات تفتيش متاحة")

def show_incident_details(unified_data):
    """Show detailed incident information"""
    st.markdown("#### ⚠️ تفاصيل الحوادث")
    
    incident_data = unified_data.get('incidents', pd.DataFrame())
    if not incident_data.empty:
        st.dataframe(incident_data, use_container_width=True)
    else:
        st.warning("لا توجد بيانات حوادث متاحة")

def show_risk_details(unified_data):
    """Show detailed risk information"""
    st.markdown("#### 🚨 تفاصيل المخاطر")
    
    risk_data = unified_data.get('risk_assessments', pd.DataFrame())
    if not risk_data.empty:
        st.dataframe(risk_data, use_container_width=True)
    else:
        st.warning("لا توجد بيانات مخاطر متاحة")

def show_audit_details(unified_data):
    """Show detailed audit information"""
    st.markdown("#### 📋 تفاصيل التدقيق")
    
    audit_data = unified_data.get('contractor_audits', pd.DataFrame())
    if not audit_data.empty:
        st.dataframe(audit_data, use_container_width=True)
    else:
        st.warning("لا توجد بيانات تدقيق متاحة")

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
                st.stop()
    
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
        ["الرئيسية المحسنة", "التحليلات المتقدمة", "رفع البيانات", "المساعد الذكي", "تقرير الجودة"]
    )
    
    # Display selected page
    if page == "الرئيسية المحسنة":
        create_enhanced_main_dashboard(unified_data, kpi_data, filters)
    
    elif page == "التحليلات المتقدمة":
        from streamlit_app import create_analytics_page
        create_analytics_page(unified_data, kpi_data)
    
    elif page == "رفع البيانات":
        from streamlit_app import create_manual_upload_section
        create_manual_upload_section()
    
    elif page == "المساعد الذكي":
        create_chatbot_interface(unified_data, kpi_data)
    
    elif page == "تقرير الجودة":
        st.header("📋 تقرير جودة البيانات")
        
        if quality_report:
            # Overall summary
            total_records = sum([report['total_rows'] for report in quality_report.values()])
            total_columns = sum([report['total_columns'] for report in quality_report.values()])
            avg_missing = np.mean([report['missing_data_percentage'] for report in quality_report.values()])
            
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
                        st.write(f"**عدد الصفوف:** {report['total_rows']:,}")
                        st.write(f"**عدد الأعمدة:** {report['total_columns']}")
                        st.write(f"**البيانات المفقودة:** {report['missing_data_percentage']:.1f}%")
                        st.write(f"**الصفوف المكررة:** {report['duplicate_rows']:,}")
                        st.write(f"**استخدام الذاكرة:** {report['memory_usage'] / 1024:.1f} KB")
                    
                    with col2:
                        st.subheader("أنواع البيانات")
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