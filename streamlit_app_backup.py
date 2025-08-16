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
    page_title="لوحة معلومات السلامة والامتثال",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8ecf0 100%);
        padding: 1.5rem;
        border-radius: 0.8rem;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .kpi-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        gap: 1rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
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
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 0.8rem;
        border: 2px dashed #1f77b4;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
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

def create_manual_upload_section():
    """Create manual data upload section"""
    st.header("📤 رفع البيانات يدوياً")
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
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
                    processor = SafetyDataProcessor()
                    new_data = processor.load_excel_data(f"temp_{uploaded_excel.name}")
                    
                    if new_data:
                        st.success(f"تم رفع الملف بنجاح! تم العثور على {len(new_data)} ورقة عمل")
                        
                        # Show preview
                        for sheet_name, df in new_data.items():
                            with st.expander(f"معاينة: {sheet_name}"):
                                st.dataframe(df.head(), use_container_width=True)
                        
                        # Update session state
                        if 'uploaded_data' not in st.session_state:
                            st.session_state.uploaded_data = {}
                        st.session_state.uploaded_data.update(new_data)
                        
                        if st.button("دمج البيانات الجديدة"):
                            st.session_state.data_updated = True
                            st.success("تم دمج البيانات الجديدة بنجاح!")
                            st.rerun()
                    
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
                    processor = SafetyDataProcessor()
                    new_csv_data = {}
                    
                    for uploaded_csv in uploaded_csvs:
                        # Save temporarily and process
                        with open(f"temp_{uploaded_csv.name}", "wb") as f:
                            f.write(uploaded_csv.getbuffer())
                        
                        df = processor.load_csv_data(f"temp_{uploaded_csv.name}")
                        if not df.empty:
                            new_csv_data[uploaded_csv.name.replace('.csv', '')] = df
                        
                        # Clean up
                        os.remove(f"temp_{uploaded_csv.name}")
                    
                    if new_csv_data:
                        st.success(f"تم رفع {len(new_csv_data)} ملف CSV بنجاح!")
                        
                        # Show preview
                        for file_name, df in new_csv_data.items():
                            with st.expander(f"معاينة: {file_name}"):
                                st.dataframe(df.head(), use_container_width=True)
                        
                        # Update session state
                        if 'uploaded_data' not in st.session_state:
                            st.session_state.uploaded_data = {}
                        st.session_state.uploaded_data.update(new_csv_data)
                        
                        if st.button("دمج ملفات CSV"):
                            st.session_state.data_updated = True
                            st.success("تم دمج ملفات CSV بنجاح!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"خطأ في معالجة ملفات CSV: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data validation section
        st.subheader("🔍 التحقق من جودة البيانات")
        
        if st.button("فحص جودة البيانات"):
            if 'uploaded_data' in st.session_state:
                processor = SafetyDataProcessor()
                quality_report = processor.get_data_quality_report(st.session_state.uploaded_data)
                
                st.subheader("تقرير جودة البيانات")
                
                for data_type, report in quality_report.items():
                    with st.expander(f"تقرير: {data_type}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("عدد الصفوف", f"{report['total_rows']:,}")
                        with col2:
                            st.metric("عدد الأعمدة", report['total_columns'])
                        with col3:
                            st.metric("البيانات المفقودة", f"{report['missing_data_percentage']:.1f}%")
                        
                        if report['duplicate_rows'] > 0:
                            st.warning(f"تم العثور على {report['duplicate_rows']} صف مكرر")
                        else:
                            st.success("لا توجد صفوف مكررة")
            else:
                st.warning("لا توجد بيانات مرفوعة للفحص")

def create_main_dashboard(unified_data, kpi_data):
    """Create the main dashboard"""
    st.markdown('<h1 class="main-header">🛡️ لوحة معلومات السلامة والامتثال</h1>', unsafe_allow_html=True)
    
    # Initialize dashboard components
    dashboard = DashboardComponents()
    
    # Create interactive filters
    filters = dashboard.create_interactive_filters(unified_data)
    
    # Main KPI section
    st.header("📊 المؤشرات الرئيسية")
    dashboard.create_kpi_cards(kpi_data)
    
    # Compliance overview
    dashboard.create_compliance_overview(unified_data)
    
    # Risk management section
    dashboard.create_risk_management_section(unified_data)
    
    # Activity heatmap
    dashboard.create_activity_heatmap(unified_data)
    
    # Time series analysis
    dashboard.create_time_series_analysis(unified_data)
    
    # Detailed tables
    dashboard.create_detailed_tables(unified_data, filters)

def create_analytics_page(unified_data, kpi_data):
    """Create advanced analytics page"""
    st.header("📈 التحليلات المتقدمة")
    
    tab1, tab2, tab3, tab4 = st.tabs(["تحليل الأداء", "تحليل المخاطر", "تحليل الاتجاهات", "التحليل التنبؤي"])
    
    with tab1:
        st.subheader("تحليل الأداء التفصيلي")
        
        # Performance metrics by department
        if unified_data:
            performance_data = []
            for data_type, df in unified_data.items():
                if df.empty:
                    continue
                
                # Calculate performance metrics
                dept_col = None
                status_col = None
                
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                        dept_col = col
                    elif any(keyword in col.lower() for keyword in ['حالة', 'status']):
                        status_col = col
                
                if dept_col and status_col:
                    dept_performance = df.groupby(dept_col)[status_col].value_counts().unstack(fill_value=0)
                    
                    for dept in dept_performance.index:
                        closed = dept_performance.loc[dept].get('مغلق', 0)
                        total = dept_performance.loc[dept].sum()
                        compliance_rate = (closed / total * 100) if total > 0 else 0
                        
                        performance_data.append({
                            'القطاع': dept,
                            'نوع البيانات': data_type,
                            'إجمالي الحالات': total,
                            'الحالات المغلقة': closed,
                            'معدل الامتثال': compliance_rate
                        })
            
            if performance_data:
                performance_df = pd.DataFrame(performance_data)
                
                # Performance comparison chart
                fig = px.sunburst(
                    performance_df,
                    path=['نوع البيانات', 'القطاع'],
                    values='إجمالي الحالات',
                    color='معدل الامتثال',
                    color_continuous_scale='RdYlGn',
                    title="توزيع الأداء حسب القطاع ونوع البيانات"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance table
                st.subheader("جدول الأداء التفصيلي")
                st.dataframe(
                    performance_df.sort_values('معدل الامتثال', ascending=False),
                    use_container_width=True
                )
    
    with tab2:
        st.subheader("تحليل المخاطر المتقدم")
        
        if 'risk_assessments' in unified_data and not unified_data['risk_assessments'].empty:
            risk_df = unified_data['risk_assessments']
            
            # Risk correlation matrix
            numeric_cols = risk_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlation_matrix = risk_df[numeric_cols].corr()
                
                fig = px.imshow(
                    correlation_matrix,
                    title="مصفوفة الارتباط للمخاطر",
                    color_continuous_scale='RdBu',
                    aspect='auto'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Risk distribution by activity
            activity_col = None
            for col in risk_df.columns:
                if any(keyword in col.lower() for keyword in ['نشاط', 'activity']):
                    activity_col = col
                    break
            
            if activity_col:
                risk_by_activity = risk_df[activity_col].value_counts()
                
                fig = px.treemap(
                    values=risk_by_activity.values,
                    names=risk_by_activity.index,
                    title="توزيع المخاطر حسب نوع النشاط"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("لا توجد بيانات تقييم المخاطر متاحة")
    
    with tab3:
        st.subheader("تحليل الاتجاهات الزمنية")
        
        # Combined time series for all data types
        time_series_data = []
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
            
            date_col = None
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    date_col = col
                    break
            
            if date_col:
                monthly_counts = df.groupby(pd.Grouper(key=date_col, freq='M')).size().reset_index()
                monthly_counts['نوع البيانات'] = data_type
                monthly_counts.columns = ['التاريخ', 'العدد', 'نوع البيانات']
                time_series_data.append(monthly_counts)
        
        if time_series_data:
            combined_ts = pd.concat(time_series_data, ignore_index=True)
            
            # Interactive time series chart
            fig = px.line(
                combined_ts,
                x='التاريخ',
                y='العدد',
                color='نوع البيانات',
                title="الاتجاهات الزمنية لجميع أنواع البيانات",
                markers=True
            )
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # Seasonal analysis
            if len(combined_ts) > 12:
                combined_ts['الشهر'] = combined_ts['التاريخ'].dt.month
                seasonal_data = combined_ts.groupby(['الشهر', 'نوع البيانات'])['العدد'].mean().reset_index()
                
                fig = px.bar(
                    seasonal_data,
                    x='الشهر',
                    y='العدد',
                    color='نوع البيانات',
                    title="التحليل الموسمي - متوسط العدد حسب الشهر",
                    barmode='group'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("التحليل التنبؤي")
        
        st.info("هذا القسم يحتوي على نماذج تنبؤية متقدمة لتوقع الاتجاهات المستقبلية")
        
        # Simple trend prediction
        if time_series_data:
            combined_ts = pd.concat(time_series_data, ignore_index=True)
            
            # Group by data type for prediction
            for data_type in combined_ts['نوع البيانات'].unique():
                type_data = combined_ts[combined_ts['نوع البيانات'] == data_type].copy()
                type_data = type_data.sort_values('التاريخ')
                
                if len(type_data) > 3:
                    # Simple linear trend
                    type_data['trend'] = np.arange(len(type_data))
                    correlation = np.corrcoef(type_data['trend'], type_data['العدد'])[0, 1]
                    
                    # Predict next 3 months
                    last_date = type_data['التاريخ'].max()
                    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='M')
                    
                    # Simple linear extrapolation
                    if abs(correlation) > 0.3:  # Only if there's some correlation
                        slope = np.polyfit(type_data['trend'], type_data['العدد'], 1)[0]
                        last_value = type_data['العدد'].iloc[-1]
                        
                        predictions = []
                        for i, future_date in enumerate(future_dates, 1):
                            predicted_value = max(0, last_value + slope * i)  # Ensure non-negative
                            predictions.append({
                                'التاريخ': future_date,
                                'العدد المتوقع': predicted_value,
                                'نوع البيانات': data_type
                            })
                        
                        if predictions:
                            pred_df = pd.DataFrame(predictions)
                            
                            # Combine historical and predicted data
                            historical = type_data[['التاريخ', 'العدد', 'نوع البيانات']].copy()
                            historical['النوع'] = 'فعلي'
                            historical = historical.rename(columns={'العدد': 'القيمة'})
                            
                            predicted = pred_df[['التاريخ', 'العدد المتوقع', 'نوع البيانات']].copy()
                            predicted['النوع'] = 'متوقع'
                            predicted = predicted.rename(columns={'العدد المتوقع': 'القيمة'})
                            
                            combined_pred = pd.concat([historical, predicted], ignore_index=True)
                            
                            fig = px.line(
                                combined_pred,
                                x='التاريخ',
                                y='القيمة',
                                color='النوع',
                                title=f"التنبؤ للأشهر القادمة - {data_type}",
                                line_dash='النوع'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Show prediction table
                            st.subheader(f"التوقعات لـ {data_type}")
                            st.dataframe(pred_df, use_container_width=True)

def main():
    """Main application function"""
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'data_updated' not in st.session_state:
        st.session_state.data_updated = False
    
    # Load data
    if not st.session_state.data_loaded or st.session_state.data_updated:
        with st.spinner("جاري تحميل ومعالجة البيانات..."):
            try:
                processor, unified_data, kpi_data, quality_report = load_and_process_data()
                
                # Merge with uploaded data if available
                if 'uploaded_data' in st.session_state:
                    additional_unified = processor.create_unified_dataset(st.session_state.uploaded_data)
                    
                    # Merge datasets
                    for key, df in additional_unified.items():
                        if key in unified_data:
                            unified_data[key] = pd.concat([unified_data[key], df], ignore_index=True)
                        else:
                            unified_data[key] = df
                    
                    # Regenerate KPIs
                    kpi_data = processor.generate_kpi_data(unified_data)
                
                st.session_state.processor = processor
                st.session_state.unified_data = unified_data
                st.session_state.kpi_data = kpi_data
                st.session_state.quality_report = quality_report
                st.session_state.data_loaded = True
                st.session_state.data_updated = False
                
            except Exception as e:
                st.error(f"خطأ في تحميل البيانات: {str(e)}")
                st.stop()
    
    # Get data from session state
    unified_data = st.session_state.unified_data
    kpi_data = st.session_state.kpi_data
    quality_report = st.session_state.quality_report
    
    # Sidebar navigation
    st.sidebar.title("🧭 التنقل")
    page = st.sidebar.selectbox(
        "اختر الصفحة",
        ["الرئيسية", "التحليلات المتقدمة", "رفع البيانات", "المساعد الذكي", "تقرير الجودة"]
    )
    
    # Display selected page
    if page == "الرئيسية":
        create_main_dashboard(unified_data, kpi_data)
    
    elif page == "التحليلات المتقدمة":
        create_analytics_page(unified_data, kpi_data)
    
    elif page == "رفع البيانات":
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
            <p>🛡️ لوحة معلومات السلامة والامتثال | تم التطوير بواسطة الذكاء الاصطناعي</p>
            <p>آخر تحديث: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
        """Clean column names and handle multi-level headers"""
        if len(df) > 0:
            first_row = df.iloc[0]
            new_columns = []
            
            for i, (col, val) in enumerate(zip(df.columns, first_row)):
                if pd.notna(val) and str(val).strip() != '':
                    new_columns.append(str(val).strip())
                elif col != f'Unnamed: {i}':
                    new_columns.append(col)
                else:
                    new_columns.append(f'Column_{i}')
            
            df.columns = new_columns
            df = df.drop(df.index[0]).reset_index(drop=True)
        
        return df

    def standardize_status(status_value):
        """Standardize status values"""
        if pd.isna(status_value):
            return None
        
        status_str = str(status_value).strip().lower()
        if 'open' in status_str or 'مفتوح' in status_str:
            return 'Open'
        elif 'close' in status_str or 'مغلق' in status_str:
            return 'Closed'
        else:
            return status_value

    def standardize_classification(classification_value):
        """Standardize classification values"""
        if pd.isna(classification_value):
            return None
        
        class_str = str(classification_value).strip().lower()
        if 'high' in class_str or 'عالي' in class_str:
            return 'High'
        elif 'medium' in class_str or 'متوسط' in class_str:
            return 'Medium'
        elif 'low' in class_str or 'منخفض' in class_str:
            return 'Low'
        else:
            return classification_value

    def clean_date_column_safe(date_series):
        """Clean and standardize date columns safely"""
        try:
            return pd.to_datetime(date_series, errors='coerce')
        except:
            return date_series

    def clean_duplicate_columns(df):
        """Handle duplicate column names"""
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols
        return df

    # Load and clean all datasets
    cleaned_datasets = {}
    
    # Sheet mapping
    sheets_info = {
        'site_audits': 'تقارير تدقيق وفحص المواقع',
        'risk_assessment': 'توصيات تقييم المخاطر',
        'contractor_audits': 'توصيات التدقيق على المقاولين',
        'incidents': 'توصيات الحوادث',
        'hypotheses': 'توصيات الفرضيات',
        'fire_safety': 'فحص أنظمة السلامة والإطفاء',
        'inspection_notes': 'ملاحظات التفتيش',
        'scis_audit': 'تدقيق متطلبات SCIS'
    }
    
    for key, sheet_name in sheets_info.items():
        try:
            df = pd.read_excel('sample-of-data.xlsx', sheet_name=sheet_name)
            df_clean = clean_column_names(df, sheet_name)
            df_clean = clean_duplicate_columns(df_clean)
            
            # Standardize status columns
            status_cols = [col for col in df_clean.columns if 'حالة' in col]
            for col in status_cols:
                df_clean[col] = df_clean[col].apply(standardize_status)
            
            # Standardize classification columns
            class_cols = [col for col in df_clean.columns if 'التصنيف' in col]
            for col in class_cols:
                df_clean[col] = df_clean[col].apply(standardize_classification)
            
            # Clean date columns
            date_columns = [col for col in df_clean.columns if 'تاريخ' in col]
            for col in date_columns:
                df_clean[col] = clean_date_column_safe(df_clean[col])
            
            cleaned_datasets[key] = df_clean
            
        except Exception as e:
            st.error(f"Error loading {sheet_name}: {str(e)}")
    
    return cleaned_datasets

@st.cache_data
def calculate_kpis(datasets):
    """Calculate key performance indicators"""
    
    # Collect all status data
    all_statuses = []
    for key, df in datasets.items():
        status_cols = [col for col in df.columns if 'حالة' in col and 'Status' not in col]
        for col in status_cols:
            statuses = df[col].dropna().tolist()
            all_statuses.extend([(status, key) for status in statuses])
    
    status_df = pd.DataFrame(all_statuses, columns=['Status', 'Dataset'])
    
    # Calculate closing compliance
    total_open = status_df[status_df['Status'].isin(['Open', 'مفتوح - Open'])].shape[0]
    total_closed = status_df[status_df['Status'].isin(['Closed', 'مغلق - Close'])].shape[0]
    total_items = total_open + total_closed
    
    closing_compliance_rate = (total_closed / total_items) * 100 if total_items > 0 else 0
    
    # Risk management metrics
    risk_data = datasets.get('risk_assessment', pd.DataFrame())
    avg_risk = 0
    high_risk_count = 0
    
    if not risk_data.empty and 'نسب المخاطرة' in risk_data.columns:
        avg_risk = risk_data['نسب المخاطرة'].mean()
        high_risk_count = risk_data[risk_data['نسب المخاطرة'] > 0.7].shape[0]
    
    # Total records
    total_records = sum([df.shape[0] for df in datasets.values()])
    
    return {
        'closing_compliance_rate': closing_compliance_rate,
        'total_open': total_open,
        'total_closed': total_closed,
        'total_items': total_items,
        'avg_risk': avg_risk,
        'high_risk_count': high_risk_count,
        'total_records': total_records,
        'status_df': status_df
    }

def create_sector_performance_chart(datasets):
    """Create sector performance chart"""
    sector_data = []
    
    for key, df in datasets.items():
        dept_cols = [col for col in df.columns if 'الإدارة' in col and 'المسئولة' in col]
        for col in dept_cols:
            depts = df[col].dropna().tolist()
            for dept in depts:
                sector_data.append({'Sector': dept, 'Dataset': key, 'Count': 1})
    
    if sector_data:
        sector_df = pd.DataFrame(sector_data)
        sector_summary = sector_df.groupby('Sector')['Count'].sum().reset_index()
        sector_summary = sector_summary.sort_values('Count', ascending=True)
        
        fig = px.bar(
            sector_summary, 
            x='Count', 
            y='Sector',
            orientation='h',
            title='Sector Performance (Total Items)',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, showlegend=False)
        return fig
    
    return None

def create_activity_distribution_chart(datasets):
    """Create activity type distribution chart"""
    activity_data = []
    
    for key, df in datasets.items():
        activity_cols = [col for col in df.columns if 'تصنيف النشاط' in col]
        for col in activity_cols:
            activities = df[col].dropna().tolist()
            for activity in activities:
                # Clean activity names
                clean_activity = activity.split('\n')[0] if '\n' in activity else activity
                activity_data.append({'Activity': clean_activity, 'Dataset': key, 'Count': 1})
    
    if activity_data:
        activity_df = pd.DataFrame(activity_data)
        activity_summary = activity_df.groupby('Activity')['Count'].sum().reset_index()
        activity_summary = activity_summary.sort_values('Count', ascending=False).head(10)
        
        fig = px.bar(
            activity_summary,
            x='Activity',
            y='Count',
            title='Top 10 Activity Types',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(height=400, showlegend=False)
        return fig
    
    return None

def create_status_pie_chart(kpis):
    """Create status distribution pie chart"""
    status_counts = kpis['status_df']['Status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title='Status Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(height=400)
    return fig

def create_risk_distribution_chart(datasets):
    """Create risk level distribution chart"""
    risk_data = datasets.get('risk_assessment', pd.DataFrame())
    
    if not risk_data.empty and 'نسب المخاطرة' in risk_data.columns:
        # Create risk level categories
        risk_data_copy = risk_data.copy()
        risk_data_copy['Risk_Category'] = pd.cut(
            risk_data_copy['نسب المخاطرة'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk']
        )
        
        risk_counts = risk_data_copy['Risk_Category'].value_counts()
        
        fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            title='Risk Level Distribution',
            color=risk_counts.values,
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        return fig
    
    return None

def create_unit_performance_chart(datasets):
    """Create unit performance comparison chart"""
    unit_data = []
    
    for key, df in datasets.items():
        unit_cols = [col for col in df.columns if 'الوحدة' in col]
        for col in unit_cols:
            units = df[col].dropna().tolist()
            for unit in units:
                unit_data.append({'Unit': unit, 'Dataset': key, 'Count': 1})
    
    if unit_data:
        unit_df = pd.DataFrame(unit_data)
        unit_summary = unit_df.groupby(['Unit', 'Dataset'])['Count'].sum().reset_index()
        
        fig = px.bar(
            unit_summary,
            x='Unit',
            y='Count',
            color='Dataset',
            title='Unit Performance by Dataset',
            barmode='stack'
        )
        fig.update_layout(height=400)
        return fig
    
    return None

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🛡️ Safety & Compliance Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading and processing data...'):
        datasets = load_and_clean_data()
        kpis = calculate_kpis(datasets)
    
    # Sidebar filters
    st.sidebar.header("📊 Filters")
    
    # Dataset filter
    available_datasets = list(datasets.keys())
    selected_datasets = st.sidebar.multiselect(
        "Select Datasets",
        available_datasets,
        default=available_datasets
    )
    
    # Filter datasets based on selection
    filtered_datasets = {k: v for k, v in datasets.items() if k in selected_datasets}
    
    # Recalculate KPIs for filtered data
    filtered_kpis = calculate_kpis(filtered_datasets)
    
    # Main dashboard
    st.header("📈 Key Performance Indicators")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Closing Compliance Rate",
            value=f"{filtered_kpis['closing_compliance_rate']:.1f}%",
            delta=f"{filtered_kpis['total_closed']} closed"
        )
    
    with col2:
        st.metric(
            label="Total Items",
            value=filtered_kpis['total_items'],
            delta=f"{filtered_kpis['total_open']} open"
        )
    
    with col3:
        st.metric(
            label="Average Risk Level",
            value=f"{filtered_kpis['avg_risk']:.2f}",
            delta=f"{filtered_kpis['high_risk_count']} high risk"
        )
    
    with col4:
        st.metric(
            label="Total Records",
            value=filtered_kpis['total_records'],
            delta=f"{len(filtered_datasets)} datasets"
        )
    
    # Charts section
    st.header("📊 Analytics Dashboard")
    
    # Row 1: Sector Performance and Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        sector_chart = create_sector_performance_chart(filtered_datasets)
        if sector_chart:
            st.plotly_chart(sector_chart, use_container_width=True)
        else:
            st.info("No sector data available for selected datasets")
    
    with col2:
        status_chart = create_status_pie_chart(filtered_kpis)
        st.plotly_chart(status_chart, use_container_width=True)
    
    # Row 2: Activity Distribution and Risk Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        activity_chart = create_activity_distribution_chart(filtered_datasets)
        if activity_chart:
            st.plotly_chart(activity_chart, use_container_width=True)
        else:
            st.info("No activity data available for selected datasets")
    
    with col2:
        risk_chart = create_risk_distribution_chart(filtered_datasets)
        if risk_chart:
            st.plotly_chart(risk_chart, use_container_width=True)
        else:
            st.info("No risk data available for selected datasets")
    
    # Row 3: Unit Performance
    st.subheader("Unit Performance Analysis")
    unit_chart = create_unit_performance_chart(filtered_datasets)
    if unit_chart:
        st.plotly_chart(unit_chart, use_container_width=True)
    else:
        st.info("No unit data available for selected datasets")
    
    # Reports Section
    st.header("📋 Comprehensive Reports")
    
    # Create tabs for different report sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "🔍 Detailed Analysis", "📈 Trends", "📋 Raw Data"])
    
    with tab1:
        st.subheader("Data Overview")
        
        # Dataset summary table
        summary_data = []
        for key, df in filtered_datasets.items():
            summary_data.append({
                'Dataset': key.replace('_', ' ').title(),
                'Records': df.shape[0],
                'Columns': df.shape[1],
                'Date Range': f"{df.select_dtypes(include=['datetime64']).min().min():%Y-%m-%d} to {df.select_dtypes(include=['datetime64']).max().max():%Y-%m-%d}" if not df.select_dtypes(include=['datetime64']).empty else "N/A"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        # Key insights
        st.subheader("Key Insights")
        st.write(f"• **Total compliance rate**: {filtered_kpis['closing_compliance_rate']:.1f}% of items are closed")
        st.write(f"• **Risk management**: Average risk level is {filtered_kpis['avg_risk']:.2f} with {filtered_kpis['high_risk_count']} high-risk items")
        st.write(f"• **Data coverage**: {filtered_kpis['total_records']} total records across {len(filtered_datasets)} datasets")
    
    with tab2:
        st.subheader("Detailed Analysis")
        
        # Compliance by sector
        st.write("**Compliance Analysis by Sector**")
        sector_compliance = []
        
        for key, df in filtered_datasets.items():
            status_cols = [col for col in df.columns if 'حالة' in col and 'Status' not in col]
            dept_cols = [col for col in df.columns if 'الإدارة' in col and 'المسئولة' in col]
            
            if status_cols and dept_cols:
                for _, row in df.iterrows():
                    status = row[status_cols[0]] if status_cols else None
                    dept = row[dept_cols[0]] if dept_cols else None
                    
                    if pd.notna(status) and pd.notna(dept):
                        sector_compliance.append({
                            'Sector': dept,
                            'Status': status,
                            'Dataset': key
                        })
        
        if sector_compliance:
            compliance_df = pd.DataFrame(sector_compliance)
            compliance_summary = compliance_df.groupby(['Sector', 'Status']).size().unstack(fill_value=0)
            
            if 'Closed' in compliance_summary.columns and 'Open' in compliance_summary.columns:
                compliance_summary['Compliance_Rate'] = (compliance_summary['Closed'] / (compliance_summary['Closed'] + compliance_summary['Open']) * 100).round(1)
                st.dataframe(compliance_summary, use_container_width=True)
            else:
                st.dataframe(compliance_summary, use_container_width=True)
        
        # Top issues analysis
        st.write("**Top Issues by Activity Type**")
        if 'activity_data' in locals():
            activity_issues = pd.DataFrame(activity_data)
            top_issues = activity_issues.groupby('Activity')['Count'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_issues)
    
    with tab3:
        st.subheader("Trend Analysis")
        
        # Monthly trend analysis
        monthly_data = []
        for key, df in filtered_datasets.items():
            date_cols = [col for col in df.columns if 'تاريخ' in col]
            if date_cols:
                for _, row in df.iterrows():
                    date_val = row[date_cols[0]]
                    if pd.notna(date_val):
                        monthly_data.append({
                            'Date': date_val,
                            'Dataset': key,
                            'Count': 1
                        })
        
        if monthly_data:
            trend_df = pd.DataFrame(monthly_data)
            trend_df['Month'] = pd.to_datetime(trend_df['Date']).dt.to_period('M')
            monthly_summary = trend_df.groupby(['Month', 'Dataset'])['Count'].sum().reset_index()
            monthly_summary['Month'] = monthly_summary['Month'].astype(str)
            
            fig = px.line(
                monthly_summary,
                x='Month',
                y='Count',
                color='Dataset',
                title='Monthly Trend Analysis',
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date data available for trend analysis")
    
    with tab4:
        st.subheader("Raw Data Explorer")
        
        # Dataset selector for raw data
        selected_dataset = st.selectbox(
            "Select dataset to view:",
            options=list(filtered_datasets.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_dataset:
            df = filtered_datasets[selected_dataset]
            
            # Display basic info
            st.write(f"**Dataset**: {selected_dataset.replace('_', ' ').title()}")
            st.write(f"**Shape**: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Column selector
            selected_columns = st.multiselect(
                "Select columns to display:",
                options=df.columns.tolist(),
                default=df.columns.tolist()[:10] if len(df.columns) > 10 else df.columns.tolist()
            )
            
            if selected_columns:
                # Display filtered data
                st.dataframe(df[selected_columns], use_container_width=True)
                
                # Download button
                csv = df[selected_columns].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_dataset}_data.csv",
                    mime="text/csv"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("**Safety & Compliance Dashboard** | Built with Streamlit | Data updated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == "__main__":
    main()