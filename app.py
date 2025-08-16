import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Safety & Compliance Analytics Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #55efc4 0%, #00b894 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class DataProcessor:
    """Advanced data processing and cleaning class"""
    
    def __init__(self):
        self.datasets = {}
        self.cleaned_datasets = {}
        self.master_df = None
        
    def load_all_data(self):
        """Load all CSV files and perform initial processing"""
        csv_files = {
            'identifiers': 'معرفات.csv',
            'site_audits': 'والمواقع.csv',
            'risk_assessment': 'تقييم_المخاطر.csv',
            'contractor_audits': 'العلى_المقاولين.csv',
            'incidents': 'الحوادث.csv',
            'hypotheses': 'الفرضيات.csv',
            'fire_safety': 'أنظمة_السلامة_والإطفاء.csv',
            'inspection_notes': 'التفتيش.csv',
            'scis_audit': 'متطلبات_SCIS.csv'
        }
        
        for key, filename in csv_files.items():
            try:
                df = pd.read_csv(filename, encoding='utf-8-sig')
                self.datasets[key] = df
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
        
        return self.datasets
    
    def clean_column_names(self, df):
        """Clean and standardize column names"""
        # Use first row as headers if it contains meaningful data
        if len(df) > 0:
            first_row = df.iloc[0]
            new_columns = []
            
            for i, (col, val) in enumerate(zip(df.columns, first_row)):
                if pd.notna(val) and str(val).strip() != '' and 'Unnamed' not in str(col):
                    new_columns.append(str(val).strip())
                elif 'Unnamed' not in str(col):
                    new_columns.append(col)
                else:
                    new_columns.append(f'Column_{i}')
            
            df.columns = new_columns
            df = df.drop(df.index[0]).reset_index(drop=True)
        
        return df
    
    def standardize_status(self, status_value):
        """Standardize status values across all datasets"""
        if pd.isna(status_value):
            return None
        
        status_str = str(status_value).strip().lower()
        if any(word in status_str for word in ['open', 'مفتوح', 'pending', 'active']):
            return 'Open'
        elif any(word in status_str for word in ['close', 'مغلق', 'closed', 'completed']):
            return 'Closed'
        elif any(word in status_str for word in ['progress', 'ongoing', 'جاري']):
            return 'In Progress'
        else:
            return status_value
    
    def standardize_classification(self, classification_value):
        """Standardize classification/priority values"""
        if pd.isna(classification_value):
            return None
        
        class_str = str(classification_value).strip().lower()
        if any(word in class_str for word in ['high', 'عالي', 'critical', 'urgent']):
            return 'High'
        elif any(word in class_str for word in ['medium', 'متوسط', 'moderate']):
            return 'Medium'
        elif any(word in class_str for word in ['low', 'منخفض', 'minor']):
            return 'Low'
        else:
            return classification_value
    
    def clean_dates(self, df):
        """Clean and standardize date columns"""
        date_columns = [col for col in df.columns if any(word in col.lower() for word in ['تاريخ', 'date', 'time'])]
        
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def process_all_datasets(self):
        """Process and clean all datasets"""
        for key, df in self.datasets.items():
            if df.empty:
                continue
                
            # Clean column names
            df_clean = self.clean_column_names(df.copy())
            
            # Handle duplicate columns
            df_clean = self._handle_duplicate_columns(df_clean)
            
            # Standardize status columns
            status_cols = [col for col in df_clean.columns if any(word in col.lower() for word in ['حالة', 'status', 'state'])]
            for col in status_cols:
                df_clean[col] = df_clean[col].apply(self.standardize_status)
            
            # Standardize classification columns
            class_cols = [col for col in df_clean.columns if any(word in col.lower() for word in ['تصنيف', 'classification', 'priority', 'severity'])]
            for col in class_cols:
                df_clean[col] = df_clean[col].apply(self.standardize_classification)
            
            # Clean dates
            df_clean = self.clean_dates(df_clean)
            
            # Add metadata
            df_clean['dataset_source'] = key
            df_clean['record_id'] = df_clean.index
            
            self.cleaned_datasets[key] = df_clean
        
        return self.cleaned_datasets
    
    def _handle_duplicate_columns(self, df):
        """Handle duplicate column names"""
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [
                dup + f'_{i}' if i != 0 else dup 
                for i in range(sum(cols == dup))
            ]
        df.columns = cols
        return df
    
    def create_master_dataset(self):
        """Create a unified master dataset for cross-analysis"""
        master_records = []
        
        for key, df in self.cleaned_datasets.items():
            if df.empty:
                continue
            
            # Extract common fields
            for _, row in df.iterrows():
                record = {
                    'dataset_source': key,
                    'record_id': row.get('record_id', ''),
                    'date': self._extract_date(row),
                    'status': self._extract_status(row),
                    'classification': self._extract_classification(row),
                    'department': self._extract_department(row),
                    'activity_type': self._extract_activity_type(row),
                    'unit': self._extract_unit(row),
                    'risk_score': self._extract_risk_score(row),
                    'compliance_score': self._extract_compliance_score(row)
                }
                master_records.append(record)
        
        self.master_df = pd.DataFrame(master_records)
        return self.master_df
    
    def _extract_date(self, row):
        """Extract date from row"""
        date_cols = [col for col in row.index if any(word in col.lower() for word in ['تاريخ', 'date'])]
        for col in date_cols:
            if pd.notna(row[col]):
                return row[col]
        return None
    
    def _extract_status(self, row):
        """Extract status from row"""
        status_cols = [col for col in row.index if any(word in col.lower() for word in ['حالة', 'status'])]
        for col in status_cols:
            if pd.notna(row[col]):
                return row[col]
        return None
    
    def _extract_classification(self, row):
        """Extract classification from row"""
        class_cols = [col for col in row.index if any(word in col.lower() for word in ['تصنيف', 'classification'])]
        for col in class_cols:
            if pd.notna(row[col]):
                return row[col]
        return None
    
    def _extract_department(self, row):
        """Extract department from row"""
        dept_cols = [col for col in row.index if any(word in col.lower() for word in ['إدارة', 'department', 'المسئولة'])]
        for col in dept_cols:
            if pd.notna(row[col]):
                return row[col]
        return None
    
    def _extract_activity_type(self, row):
        """Extract activity type from row"""
        activity_cols = [col for col in row.index if any(word in col.lower() for word in ['نشاط', 'activity', 'تصنيف النشاط'])]
        for col in activity_cols:
            if pd.notna(row[col]):
                return str(row[col]).split('\n')[0]  # Take first part if multi-line
        return None
    
    def _extract_unit(self, row):
        """Extract unit from row"""
        unit_cols = [col for col in row.index if any(word in col.lower() for word in ['وحدة', 'unit'])]
        for col in unit_cols:
            if pd.notna(row[col]):
                return row[col]
        return None
    
    def _extract_risk_score(self, row):
        """Extract risk score from row"""
        risk_cols = [col for col in row.index if any(word in col.lower() for word in ['مخاطر', 'risk', 'نسب'])]
        for col in risk_cols:
            if pd.notna(row[col]) and isinstance(row[col], (int, float)):
                return row[col]
        return None
    
    def _extract_compliance_score(self, row):
        """Extract compliance score from row"""
        compliance_cols = [col for col in row.index if any(word in col.lower() for word in ['compliance', 'امتثال', 'نسبة'])]
        for col in compliance_cols:
            if pd.notna(row[col]) and isinstance(row[col], (int, float)):
                return row[col]
        return None

class AdvancedAnalytics:
    """Advanced analytics and insights generation"""
    
    def __init__(self, master_df, cleaned_datasets):
        self.master_df = master_df
        self.cleaned_datasets = cleaned_datasets
    
    def calculate_kpis(self):
        """Calculate comprehensive KPIs"""
        kpis = {}
        
        # Basic counts
        kpis['total_records'] = len(self.master_df)
        kpis['total_datasets'] = len(self.cleaned_datasets)
        
        # Status analysis
        status_counts = self.master_df['status'].value_counts()
        kpis['open_items'] = status_counts.get('Open', 0)
        kpis['closed_items'] = status_counts.get('Closed', 0)
        kpis['in_progress_items'] = status_counts.get('In Progress', 0)
        
        total_actionable = kpis['open_items'] + kpis['closed_items'] + kpis['in_progress_items']
        kpis['closure_rate'] = (kpis['closed_items'] / total_actionable * 100) if total_actionable > 0 else 0
        
        # Risk analysis
        risk_data = self.master_df['risk_score'].dropna()
        if not risk_data.empty:
            kpis['avg_risk_score'] = risk_data.mean()
            kpis['high_risk_items'] = len(risk_data[risk_data > 0.7])
            kpis['risk_trend'] = self._calculate_risk_trend()
        else:
            kpis['avg_risk_score'] = 0
            kpis['high_risk_items'] = 0
            kpis['risk_trend'] = 0
        
        # Compliance analysis
        compliance_data = self.master_df['compliance_score'].dropna()
        if not compliance_data.empty:
            kpis['avg_compliance_score'] = compliance_data.mean()
            kpis['compliance_trend'] = self._calculate_compliance_trend()
        else:
            kpis['avg_compliance_score'] = 0
            kpis['compliance_trend'] = 0
        
        # Department performance
        dept_performance = self.master_df.groupby('department').size().sort_values(ascending=False)
        kpis['top_department'] = dept_performance.index[0] if not dept_performance.empty else 'N/A'
        kpis['department_count'] = len(dept_performance)
        
        # Activity analysis
        activity_counts = self.master_df['activity_type'].value_counts()
        kpis['top_activity'] = activity_counts.index[0] if not activity_counts.empty else 'N/A'
        kpis['activity_diversity'] = len(activity_counts)
        
        return kpis
    
    def _calculate_risk_trend(self):
        """Calculate risk trend over time"""
        df_with_dates = self.master_df.dropna(subset=['date', 'risk_score'])
        if len(df_with_dates) < 2:
            return 0
        
        df_with_dates = df_with_dates.sort_values('date')
        recent_risk = df_with_dates.tail(10)['risk_score'].mean()
        older_risk = df_with_dates.head(10)['risk_score'].mean()
        
        return ((recent_risk - older_risk) / older_risk * 100) if older_risk > 0 else 0
    
    def _calculate_compliance_trend(self):
        """Calculate compliance trend over time"""
        df_with_dates = self.master_df.dropna(subset=['date', 'compliance_score'])
        if len(df_with_dates) < 2:
            return 0
        
        df_with_dates = df_with_dates.sort_values('date')
        recent_compliance = df_with_dates.tail(10)['compliance_score'].mean()
        older_compliance = df_with_dates.head(10)['compliance_score'].mean()
        
        return ((recent_compliance - older_compliance) / older_compliance * 100) if older_compliance > 0 else 0
    
    def perform_correlation_analysis(self):
        """Perform correlation analysis between different metrics"""
        numeric_cols = ['risk_score', 'compliance_score']
        correlation_data = self.master_df[numeric_cols].corr()
        return correlation_data
    
    def perform_clustering_analysis(self):
        """Perform clustering analysis on departments/activities"""
        # Prepare data for clustering
        dept_metrics = self.master_df.groupby('department').agg({
            'risk_score': 'mean',
            'compliance_score': 'mean',
            'status': lambda x: (x == 'Closed').sum() / len(x) if len(x) > 0 else 0
        }).fillna(0)
        
        if len(dept_metrics) < 2:
            return None, None
        
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(dept_metrics)
        
        # Perform K-means clustering
        n_clusters = min(3, len(dept_metrics))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        dept_metrics['cluster'] = clusters
        return dept_metrics, clusters
    
    def generate_insights(self, kpis):
        """Generate automated insights based on data analysis"""
        insights = []
        
        # Closure rate insights
        if kpis['closure_rate'] > 80:
            insights.append(("success", f"Excellent closure rate of {kpis['closure_rate']:.1f}% indicates strong follow-through on safety items."))
        elif kpis['closure_rate'] > 60:
            insights.append(("warning", f"Moderate closure rate of {kpis['closure_rate']:.1f}% suggests room for improvement in item resolution."))
        else:
            insights.append(("error", f"Low closure rate of {kpis['closure_rate']:.1f}% requires immediate attention to improve safety compliance."))
        
        # Risk insights
        if kpis['avg_risk_score'] > 0.7:
            insights.append(("error", f"High average risk score of {kpis['avg_risk_score']:.2f} indicates significant safety concerns."))
        elif kpis['avg_risk_score'] > 0.4:
            insights.append(("warning", f"Moderate risk score of {kpis['avg_risk_score']:.2f} requires ongoing monitoring."))
        else:
            insights.append(("success", f"Low risk score of {kpis['avg_risk_score']:.2f} indicates good safety management."))
        
        # High-risk items
        if kpis['high_risk_items'] > 0:
            insights.append(("error", f"{kpis['high_risk_items']} high-risk items require immediate attention."))
        
        # Department diversity
        insights.append(("info", f"Analysis covers {kpis['department_count']} departments with {kpis['activity_diversity']} different activity types."))
        
        return insights

@st.cache_data
def load_and_process_data():
    """Load and process all data with caching"""
    processor = DataProcessor()
    datasets = processor.load_all_data()
    cleaned_datasets = processor.process_all_datasets()
    master_df = processor.create_master_dataset()
    
    analytics = AdvancedAnalytics(master_df, cleaned_datasets)
    kpis = analytics.calculate_kpis()
    insights = analytics.generate_insights(kpis)
    
    return datasets, cleaned_datasets, master_df, analytics, kpis, insights

def create_advanced_charts(master_df, cleaned_datasets):
    """Create advanced interactive charts"""
    charts = {}
    
    # 1. Timeline Analysis
    if 'date' in master_df.columns and master_df['date'].notna().any():
        timeline_data = master_df.dropna(subset=['date']).copy()
        timeline_data['month'] = timeline_data['date'].dt.to_period('M')
        monthly_counts = timeline_data.groupby(['month', 'status']).size().reset_index(name='count')
        monthly_counts['month'] = monthly_counts['month'].astype(str)
        
        fig_timeline = px.line(
            monthly_counts, 
            x='month', 
            y='count', 
            color='status',
            title='Timeline Analysis: Items by Status Over Time',
            markers=True
        )
        fig_timeline.update_layout(height=400, xaxis_tickangle=45)
        charts['timeline'] = fig_timeline
    
    # 2. Department Performance Heatmap
    dept_status = master_df.groupby(['department', 'status']).size().unstack(fill_value=0)
    if not dept_status.empty:
        fig_heatmap = px.imshow(
            dept_status.values,
            x=dept_status.columns,
            y=dept_status.index,
            title='Department Performance Heatmap',
            color_continuous_scale='RdYlBu_r',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=500)
        charts['dept_heatmap'] = fig_heatmap
    
    # 3. Risk vs Compliance Scatter Plot
    risk_compliance = master_df.dropna(subset=['risk_score', 'compliance_score'])
    if not risk_compliance.empty:
        fig_scatter = px.scatter(
            risk_compliance,
            x='compliance_score',
            y='risk_score',
            color='status',
            size='risk_score',
            hover_data=['department', 'activity_type'],
            title='Risk vs Compliance Analysis',
            labels={'compliance_score': 'Compliance Score', 'risk_score': 'Risk Score'}
        )
        fig_scatter.update_layout(height=500)
        charts['risk_compliance'] = fig_scatter
    
    # 4. Activity Type Distribution (Sunburst)
    activity_dept = master_df.dropna(subset=['activity_type', 'department'])
    if not activity_dept.empty:
        fig_sunburst = px.sunburst(
            activity_dept,
            path=['department', 'activity_type'],
            title='Activity Distribution by Department'
        )
        fig_sunburst.update_layout(height=500)
        charts['activity_sunburst'] = fig_sunburst
    
    # 5. Status Distribution by Unit (Stacked Bar)
    unit_status = master_df.groupby(['unit', 'status']).size().reset_index(name='count')
    if not unit_status.empty:
        fig_stacked = px.bar(
            unit_status,
            x='unit',
            y='count',
            color='status',
            title='Status Distribution by Business Unit',
            barmode='stack'
        )
        fig_stacked.update_layout(height=400)
        charts['unit_status'] = fig_stacked
    
    return charts

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🛡️ Safety & Compliance Analytics Platform</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('🔄 Loading and processing comprehensive data...'):
        datasets, cleaned_datasets, master_df, analytics, kpis, insights = load_and_process_data()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["🏠 Executive Dashboard", "📊 Advanced Analytics", "📈 Comprehensive Reports", "🔍 Data Explorer", "🤖 AI Insights"]
    )
    
    # Sidebar filters
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Global Filters")
    
    # Date filter
    if 'date' in master_df.columns and master_df['date'].notna().any():
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(master_df['date'].min().date(), master_df['date'].max().date()),
            min_value=master_df['date'].min().date(),
            max_value=master_df['date'].max().date()
        )
    
    # Department filter
    departments = master_df['department'].dropna().unique()
    selected_departments = st.sidebar.multiselect(
        "Departments",
        departments,
        default=departments[:5] if len(departments) > 5 else departments
    )
    
    # Status filter
    statuses = master_df['status'].dropna().unique()
    selected_statuses = st.sidebar.multiselect(
        "Status",
        statuses,
        default=statuses
    )
    
    # Activity filter
    activities = master_df['activity_type'].dropna().unique()
    selected_activities = st.sidebar.multiselect(
        "Activity Types",
        activities,
        default=activities[:10] if len(activities) > 10 else activities
    )
    
    # Apply filters
    filtered_df = master_df.copy()
    if selected_departments:
        filtered_df = filtered_df[filtered_df['department'].isin(selected_departments)]
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
    if selected_activities:
        filtered_df = filtered_df[filtered_df['activity_type'].isin(selected_activities)]
    
    # Page routing
    if page == "🏠 Executive Dashboard":
        show_executive_dashboard(filtered_df, kpis, insights)
    elif page == "📊 Advanced Analytics":
        show_advanced_analytics(filtered_df, analytics, cleaned_datasets)
    elif page == "📈 Comprehensive Reports":
        show_comprehensive_reports(filtered_df, cleaned_datasets)
    elif page == "🔍 Data Explorer":
        show_data_explorer(cleaned_datasets, filtered_df)
    elif page == "🤖 AI Insights":
        show_ai_insights(filtered_df, analytics)

def show_executive_dashboard(filtered_df, kpis, insights):
    """Executive dashboard page"""
    st.markdown('<h2 class="sub-header">🏠 Executive Dashboard</h2>', unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Closure Rate</h3>
            <h2>{kpis['closure_rate']:.1f}%</h2>
            <p>{kpis['closed_items']} of {kpis['closed_items'] + kpis['open_items']} items closed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️ Risk Score</h3>
            <h2>{kpis['avg_risk_score']:.2f}</h2>
            <p>{kpis['high_risk_items']} high-risk items</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ Compliance</h3>
            <h2>{kpis['avg_compliance_score']:.1f}%</h2>
            <p>Average compliance score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 Total Items</h3>
            <h2>{kpis['total_records']}</h2>
            <p>Across {kpis['total_datasets']} datasets</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Insights section
    st.markdown('<h3 class="sub-header">💡 Key Insights</h3>', unsafe_allow_html=True)
    
    for insight_type, message in insights:
        if insight_type == "success":
            st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)
        elif insight_type == "warning":
            st.markdown(f'<div class="warning-box">⚠️ {message}</div>', unsafe_allow_html=True)
        elif insight_type == "error":
            st.markdown(f'<div class="warning-box">🚨 {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box">ℹ️ {message}</div>', unsafe_allow_html=True)
    
    # Main charts
    charts = create_advanced_charts(filtered_df, {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'timeline' in charts:
            st.plotly_chart(charts['timeline'], use_container_width=True)
        
        # Department performance
        dept_counts = filtered_df['department'].value_counts().head(10)
        if not dept_counts.empty:
            fig_dept = px.bar(
                x=dept_counts.values,
                y=dept_counts.index,
                orientation='h',
                title='Top 10 Departments by Activity Volume',
                color=dept_counts.values,
                color_continuous_scale='Blues'
            )
            fig_dept.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_dept, use_container_width=True)
    
    with col2:
        # Status distribution
        status_counts = filtered_df['status'].value_counts()
        if not status_counts.empty:
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title='Status Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)
        
        # Risk distribution
        risk_data = filtered_df['risk_score'].dropna()
        if not risk_data.empty:
            risk_categories = pd.cut(risk_data, bins=[0, 0.3, 0.7, 1.0], labels=['Low', 'Medium', 'High'])
            risk_counts = risk_categories.value_counts()
            
            fig_risk = px.bar(
                x=risk_counts.index,
                y=risk_counts.values,
                title='Risk Level Distribution',
                color=risk_counts.values,
                color_continuous_scale='Reds'
            )
            fig_risk.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_risk, use_container_width=True)

def show_advanced_analytics(filtered_df, analytics, cleaned_datasets):
    """Advanced analytics page"""
    st.markdown('<h2 class="sub-header">📊 Advanced Analytics</h2>', unsafe_allow_html=True)
    
    # Correlation analysis
    st.markdown('<h3 class="sub-header">🔗 Correlation Analysis</h3>', unsafe_allow_html=True)
    
    correlation_data = analytics.perform_correlation_analysis()
    if not correlation_data.empty:
        fig_corr = px.imshow(
            correlation_data,
            title='Correlation Matrix: Risk vs Compliance Metrics',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        fig_corr.update_layout(height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Clustering analysis
    st.markdown('<h3 class="sub-header">🎯 Department Clustering Analysis</h3>', unsafe_allow_html=True)
    
    dept_metrics, clusters = analytics.perform_clustering_analysis()
    if dept_metrics is not None:
        fig_cluster = px.scatter_3d(
            dept_metrics.reset_index(),
            x='risk_score',
            y='compliance_score',
            z='status',
            color='cluster',
            hover_name='department',
            title='Department Performance Clusters',
            labels={
                'risk_score': 'Average Risk Score',
                'compliance_score': 'Average Compliance Score',
                'status': 'Closure Rate'
            }
        )
        fig_cluster.update_layout(height=600)
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        # Cluster interpretation
        st.markdown("**Cluster Interpretation:**")
        for i in range(len(dept_metrics['cluster'].unique())):
            cluster_depts = dept_metrics[dept_metrics['cluster'] == i].index.tolist()
            st.write(f"**Cluster {i}:** {', '.join(cluster_depts)}")
    
    # Advanced charts
    charts = create_advanced_charts(filtered_df, cleaned_datasets)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'dept_heatmap' in charts:
            st.plotly_chart(charts['dept_heatmap'], use_container_width=True)
        
        if 'risk_compliance' in charts:
            st.plotly_chart(charts['risk_compliance'], use_container_width=True)
    
    with col2:
        if 'activity_sunburst' in charts:
            st.plotly_chart(charts['activity_sunburst'], use_container_width=True)
        
        if 'unit_status' in charts:
            st.plotly_chart(charts['unit_status'], use_container_width=True)

def show_comprehensive_reports(filtered_df, cleaned_datasets):
    """Comprehensive reports page"""
    st.markdown('<h2 class="sub-header">📈 Comprehensive Reports</h2>', unsafe_allow_html=True)
    
    # Create tabs for different report sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary", 
        "🔍 Detailed Analysis", 
        "📈 Trend Analysis", 
        "🎯 Performance Metrics",
        "📋 Data Quality Report"
    ])
    
    with tab1:
        st.markdown("### Executive Summary Report")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(filtered_df))
            st.metric("Unique Departments", filtered_df['department'].nunique())
            st.metric("Unique Activities", filtered_df['activity_type'].nunique())
        
        with col2:
            open_rate = (filtered_df['status'] == 'Open').sum() / len(filtered_df) * 100
            st.metric("Open Items Rate", f"{open_rate:.1f}%")
            
            if 'risk_score' in filtered_df.columns:
                avg_risk = filtered_df['risk_score'].mean()
                st.metric("Average Risk Score", f"{avg_risk:.2f}")
        
        with col3:
            if 'compliance_score' in filtered_df.columns:
                avg_compliance = filtered_df['compliance_score'].mean()
                st.metric("Average Compliance", f"{avg_compliance:.1f}%")
        
        # Top performers and areas of concern
        st.markdown("#### 🏆 Top Performing Departments")
        dept_performance = filtered_df.groupby('department').agg({
            'status': lambda x: (x == 'Closed').sum() / len(x) * 100
        }).round(1).sort_values('status', ascending=False)
        st.dataframe(dept_performance.head(5), use_container_width=True)
        
        st.markdown("#### ⚠️ Areas Requiring Attention")
        concern_areas = dept_performance.tail(5)
        st.dataframe(concern_areas, use_container_width=True)
    
    with tab2:
        st.markdown("### Detailed Analysis")
        
        # Department deep dive
        selected_dept = st.selectbox(
            "Select Department for Deep Dive",
            filtered_df['department'].dropna().unique()
        )
        
        if selected_dept:
            dept_data = filtered_df[filtered_df['department'] == selected_dept]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Activity breakdown for selected department
                activity_counts = dept_data['activity_type'].value_counts()
                fig_activities = px.bar(
                    x=activity_counts.values,
                    y=activity_counts.index,
                    orientation='h',
                    title=f'Activities in {selected_dept}',
                    color=activity_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig_activities.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_activities, use_container_width=True)
            
            with col2:
                # Status breakdown for selected department
                status_counts = dept_data['status'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title=f'Status Distribution - {selected_dept}'
                )
                fig_status.update_layout(height=400)
                st.plotly_chart(fig_status, use_container_width=True)
    
    with tab3:
        st.markdown("### Trend Analysis")
        
        if 'date' in filtered_df.columns and filtered_df['date'].notna().any():
            # Monthly trends
            trend_data = filtered_df.dropna(subset=['date']).copy()
            trend_data['month'] = trend_data['date'].dt.to_period('M')
            
            # Overall trend
            monthly_counts = trend_data.groupby('month').size()
            monthly_counts.index = monthly_counts.index.astype(str)
            
            fig_trend = px.line(
                x=monthly_counts.index,
                y=monthly_counts.values,
                title='Monthly Activity Trend',
                markers=True
            )
            fig_trend.update_layout(height=400, xaxis_tickangle=45)
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Trend by status
            status_trend = trend_data.groupby(['month', 'status']).size().unstack(fill_value=0)
            status_trend.index = status_trend.index.astype(str)
            
            fig_status_trend = go.Figure()
            for status in status_trend.columns:
                fig_status_trend.add_trace(go.Scatter(
                    x=status_trend.index,
                    y=status_trend[status],
                    mode='lines+markers',
                    name=status
                ))
            
            fig_status_trend.update_layout(
                title='Status Trends Over Time',
                height=400,
                xaxis_tickangle=45
            )
            st.plotly_chart(fig_status_trend, use_container_width=True)
        else:
            st.info("No date information available for trend analysis")
    
    with tab4:
        st.markdown("### Performance Metrics")
        
        # Performance matrix
        performance_metrics = []
        
        for dept in filtered_df['department'].dropna().unique():
            dept_data = filtered_df[filtered_df['department'] == dept]
            
            metrics = {
                'Department': dept,
                'Total Items': len(dept_data),
                'Closure Rate (%)': (dept_data['status'] == 'Closed').sum() / len(dept_data) * 100,
                'Avg Risk Score': dept_data['risk_score'].mean() if 'risk_score' in dept_data.columns else 0,
                'Avg Compliance (%)': dept_data['compliance_score'].mean() if 'compliance_score' in dept_data.columns else 0
            }
            performance_metrics.append(metrics)
        
        performance_df = pd.DataFrame(performance_metrics).round(2)
        st.dataframe(performance_df, use_container_width=True)
        
        # Performance visualization
        if not performance_df.empty:
            fig_performance = px.scatter(
                performance_df,
                x='Closure Rate (%)',
                y='Avg Risk Score',
                size='Total Items',
                hover_name='Department',
                title='Department Performance Matrix',
                color='Avg Compliance (%)',
                color_continuous_scale='RdYlGn'
            )
            fig_performance.update_layout(height=500)
            st.plotly_chart(fig_performance, use_container_width=True)
    
    with tab5:
        st.markdown("### Data Quality Report")
        
        # Data completeness analysis
        completeness_data = []
        
        for dataset_name, df in cleaned_datasets.items():
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            completeness = (total_cells - missing_cells) / total_cells * 100
            
            completeness_data.append({
                'Dataset': dataset_name,
                'Records': df.shape[0],
                'Columns': df.shape[1],
                'Completeness (%)': round(completeness, 2),
                'Missing Values': missing_cells
            })
        
        completeness_df = pd.DataFrame(completeness_data)
        st.dataframe(completeness_df, use_container_width=True)
        
        # Data quality visualization
        fig_quality = px.bar(
            completeness_df,
            x='Dataset',
            y='Completeness (%)',
            title='Data Completeness by Dataset',
            color='Completeness (%)',
            color_continuous_scale='RdYlGn'
        )
        fig_quality.update_layout(height=400, xaxis_tickangle=45)
        st.plotly_chart(fig_quality, use_container_width=True)

def show_data_explorer(cleaned_datasets, filtered_df):
    """Data explorer page"""
    st.markdown('<h2 class="sub-header">🔍 Data Explorer</h2>', unsafe_allow_html=True)
    
    # Dataset selector
    dataset_names = list(cleaned_datasets.keys()) + ['Master Dataset']
    selected_dataset = st.selectbox("Select Dataset", dataset_names)
    
    if selected_dataset == 'Master Dataset':
        df = filtered_df
    else:
        df = cleaned_datasets[selected_dataset]
    
    # Dataset info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isnull().sum().sum())
    with col4:
        st.metric("Completeness", f"{(1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100:.1f}%")
    
    # Column selector
    st.markdown("### Column Selection")
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to display",
        all_columns,
        default=all_columns[:10] if len(all_columns) > 10 else all_columns
    )
    
    if selected_columns:
        # Display data
        st.markdown("### Data Preview")
        st.dataframe(df[selected_columns], use_container_width=True)
        
        # Column statistics
        st.markdown("### Column Statistics")
        
        numeric_cols = df[selected_columns].select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.markdown("#### Numeric Columns")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        categorical_cols = df[selected_columns].select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.markdown("#### Categorical Columns")
            for col in categorical_cols[:5]:  # Show top 5 categorical columns
                st.write(f"**{col}** - Unique values: {df[col].nunique()}")
                value_counts = df[col].value_counts().head(10)
                st.bar_chart(value_counts)
        
        # Download functionality
        csv = df[selected_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download Selected Data as CSV",
            data=csv,
            file_name=f"{selected_dataset}_filtered_data.csv",
            mime="text/csv"
        )

def show_ai_insights(filtered_df, analytics):
    """AI insights page"""
    st.markdown('<h2 class="sub-header">🤖 AI-Powered Insights</h2>', unsafe_allow_html=True)
    
    # Predictive analytics section
    st.markdown("### 🔮 Predictive Analytics")
    
    # Risk prediction
    if 'risk_score' in filtered_df.columns and filtered_df['risk_score'].notna().any():
        risk_data = filtered_df['risk_score'].dropna()
        
        # Simple trend prediction
        if len(risk_data) > 5:
            recent_trend = risk_data.tail(10).mean() - risk_data.head(10).mean()
            
            if recent_trend > 0.1:
                st.markdown('<div class="warning-box">📈 Risk scores are trending upward. Consider implementing additional safety measures.</div>', unsafe_allow_html=True)
            elif recent_trend < -0.1:
                st.markdown('<div class="success-box">📉 Risk scores are improving. Current safety initiatives appear effective.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="insight-box">➡️ Risk scores are stable. Continue monitoring current trends.</div>', unsafe_allow_html=True)
    
    # Anomaly detection
    st.markdown("### 🚨 Anomaly Detection")
    
    # Detect departments with unusual patterns
    dept_stats = filtered_df.groupby('department').agg({
        'status': lambda x: (x == 'Open').sum() / len(x),
        'risk_score': 'mean'
    }).fillna(0)
    
    if not dept_stats.empty:
        # Find outliers using IQR method
        Q1 = dept_stats['status'].quantile(0.25)
        Q3 = dept_stats['status'].quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = dept_stats[
            (dept_stats['status'] < (Q1 - 1.5 * IQR)) | 
            (dept_stats['status'] > (Q3 + 1.5 * IQR))
        ]
        
        if not outliers.empty:
            st.markdown("**Departments with unusual open item rates:**")
            for dept in outliers.index:
                rate = outliers.loc[dept, 'status'] * 100
                st.write(f"• **{dept}**: {rate:.1f}% open rate (unusual pattern detected)")
        else:
            st.success("No significant anomalies detected in department performance.")
    
    # Recommendations engine
    st.markdown("### 💡 Smart Recommendations")
    
    recommendations = []
    
    # Based on closure rates
    dept_closure = filtered_df.groupby('department')['status'].apply(lambda x: (x == 'Closed').sum() / len(x) * 100)
    low_closure_depts = dept_closure[dept_closure < 50].index.tolist()
    
    if low_closure_depts:
        recommendations.append(f"🎯 Focus on improving closure rates in: {', '.join(low_closure_depts[:3])}")
    
    # Based on risk scores
    if 'risk_score' in filtered_df.columns:
        high_risk_activities = filtered_df[filtered_df['risk_score'] > 0.7]['activity_type'].value_counts().head(3)
        if not high_risk_activities.empty:
            recommendations.append(f"⚠️ Prioritize safety measures for: {', '.join(high_risk_activities.index)}")
    
    # Based on activity volume
    high_volume_activities = filtered_df['activity_type'].value_counts().head(3)
    if not high_volume_activities.empty:
        recommendations.append(f"📊 Consider automation for high-volume activities: {', '.join(high_volume_activities.index)}")
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"**{i}.** {rec}")
    
    # Machine learning insights
    st.markdown("### 🧠 Machine Learning Insights")
    
    # Clustering results interpretation
    dept_metrics, clusters = analytics.perform_clustering_analysis()
    if dept_metrics is not None:
        st.markdown("**Department Performance Clusters:**")
        
        for cluster_id in sorted(dept_metrics['cluster'].unique()):
            cluster_depts = dept_metrics[dept_metrics['cluster'] == cluster_id]
            avg_risk = cluster_depts['risk_score'].mean()
            avg_compliance = cluster_depts['compliance_score'].mean()
            avg_closure = cluster_depts['status'].mean()
            
            if avg_risk > 0.6:
                cluster_type = "High Risk"
                color_class = "warning-box"
            elif avg_compliance > 0.8:
                cluster_type = "High Performance"
                color_class = "success-box"
            else:
                cluster_type = "Standard Performance"
                color_class = "insight-box"
            
            st.markdown(f"""
            <div class="{color_class}">
                <strong>Cluster {cluster_id} - {cluster_type}</strong><br>
                Departments: {', '.join(cluster_depts.index)}<br>
                Avg Risk: {avg_risk:.2f} | Avg Compliance: {avg_compliance:.1f}% | Closure Rate: {avg_closure:.1f}%
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()