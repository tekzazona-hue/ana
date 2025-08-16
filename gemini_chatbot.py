"""
Gemini AI Chatbot Integration
Intelligent chatbot for safety and compliance data analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Note: In production, you would use the actual Google Gemini API
# For this demo, we'll create a comprehensive mock implementation

class GeminiChatbot:
    """Intelligent chatbot for safety and compliance data analysis"""
    
    def __init__(self, unified_data, kpi_data):
        self.unified_data = unified_data
        self.kpi_data = kpi_data
        self.conversation_history = []
        
        # Initialize knowledge base
        self.knowledge_base = self._build_knowledge_base()
        
        # Common queries and responses
        self.query_patterns = {
            'total_incidents': ['كم عدد الحوادث', 'إجمالي الحوادث', 'total incidents'],
            'open_cases': ['الحالات المفتوحة', 'المفتوح', 'open cases'],
            'closed_cases': ['الحالات المغلقة', 'المغلق', 'closed cases'],
            'department_performance': ['أداء القطاع', 'القطاعات', 'department performance'],
            'risk_assessment': ['تقييم المخاطر', 'المخاطر', 'risk assessment'],
            'compliance_rate': ['معدل الامتثال', 'الامتثال', 'compliance rate'],
            'trends': ['الاتجاهات', 'التطور', 'trends', 'trend'],
            'statistics': ['إحصائيات', 'statistics', 'stats']
        }
    
    def _build_knowledge_base(self):
        """Build knowledge base from unified data"""
        knowledge = {
            'data_summary': {},
            'key_metrics': {},
            'insights': []
        }
        
        # Build data summary
        for data_type, df in self.unified_data.items():
            if not df.empty:
                knowledge['data_summary'][data_type] = {
                    'total_records': len(df),
                    'columns': list(df.columns),
                    'date_range': self._get_date_range(df),
                    'key_statistics': self._get_key_statistics(df)
                }
        
        # Build key metrics
        knowledge['key_metrics'] = self.kpi_data
        
        # Generate insights
        knowledge['insights'] = self._generate_insights()
        
        return knowledge
    
    def _get_date_range(self, df):
        """Get date range from dataframe"""
        date_columns = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
        if not date_columns:
            return None
        
        all_dates = pd.concat([df[col].dropna() for col in date_columns])
        if len(all_dates) == 0:
            return None
        
        return {
            'start': all_dates.min().strftime('%Y-%m-%d'),
            'end': all_dates.max().strftime('%Y-%m-%d'),
            'days': (all_dates.max() - all_dates.min()).days
        }
    
    def _get_key_statistics(self, df):
        """Get key statistics from dataframe"""
        stats = {}
        
        # Status distribution
        status_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
        if status_cols:
            status_dist = df[status_cols[0]].value_counts().to_dict()
            stats['status_distribution'] = status_dist
        
        # Department distribution
        dept_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department'])]
        if dept_cols:
            dept_dist = df[dept_cols[0]].value_counts().head(5).to_dict()
            stats['top_departments'] = dept_dist
        
        return stats
    
    def _generate_insights(self):
        """Generate automatic insights from data"""
        insights = []
        
        # Total records insight
        total_records = sum([len(df) for df in self.unified_data.values() if not df.empty])
        insights.append(f"يحتوي النظام على إجمالي {total_records:,} سجل عبر جميع أنواع البيانات")
        
        # Compliance insight
        total_open = 0
        total_closed = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            total_open += count
                        elif 'مغلق' in str(status):
                            total_closed += count
        
        if total_open + total_closed > 0:
            compliance_rate = (total_closed / (total_open + total_closed)) * 100
            insights.append(f"معدل الامتثال الإجمالي هو {compliance_rate:.1f}% ({total_closed:,} مغلق من أصل {total_open + total_closed:,})")
        
        # Department insight
        dept_performance = {}
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            dept_col = None
            status_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_col = col
                elif any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_col = col
            
            if dept_col and status_col:
                dept_counts = df[dept_col].value_counts()
                top_dept = dept_counts.index[0] if len(dept_counts) > 0 else None
                if top_dept:
                    insights.append(f"القطاع الأكثر نشاطاً هو {top_dept} بـ {dept_counts.iloc[0]:,} سجل")
                    break
        
        return insights
    
    def process_query(self, user_query):
        """Process user query and generate response"""
        user_query = user_query.strip()
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_query': user_query,
            'response': None
        })
        
        # Determine query type
        query_type = self._classify_query(user_query)
        
        # Generate response based on query type
        response = self._generate_response(query_type, user_query)
        
        # Update conversation history
        self.conversation_history[-1]['response'] = response
        
        return response
    
    def _classify_query(self, query):
        """Classify user query into categories"""
        query_lower = query.lower()
        
        for category, patterns in self.query_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query_lower:
                    return category
        
        # Default classification based on keywords
        if any(word in query_lower for word in ['كم', 'عدد', 'إجمالي', 'how many', 'total']):
            return 'statistics'
        elif any(word in query_lower for word in ['أفضل', 'أسوأ', 'best', 'worst']):
            return 'department_performance'
        elif any(word in query_lower for word in ['متى', 'when', 'تاريخ', 'date']):
            return 'trends'
        else:
            return 'general'
    
    def _generate_response(self, query_type, user_query):
        """Generate response based on query type"""
        try:
            if query_type == 'total_incidents':
                return self._get_incidents_summary()
            elif query_type == 'open_cases':
                return self._get_open_cases_summary()
            elif query_type == 'closed_cases':
                return self._get_closed_cases_summary()
            elif query_type == 'department_performance':
                return self._get_department_performance()
            elif query_type == 'risk_assessment':
                return self._get_risk_assessment_summary()
            elif query_type == 'compliance_rate':
                return self._get_compliance_summary()
            elif query_type == 'trends':
                return self._get_trends_summary()
            elif query_type == 'statistics':
                return self._get_general_statistics()
            else:
                return self._get_general_response(user_query)
        except Exception as e:
            return {
                'text': f"عذراً، حدث خطأ في معالجة استفسارك: {str(e)}",
                'chart': None,
                'data': None
            }
    
    def _get_incidents_summary(self):
        """Get incidents summary"""
        if 'incidents' not in self.unified_data or self.unified_data['incidents'].empty:
            return {
                'text': "لا توجد بيانات حوادث متاحة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        incidents_df = self.unified_data['incidents']
        total_incidents = len(incidents_df)
        
        # Get status distribution
        status_dist = {}
        for col in incidents_df.columns:
            if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                status_dist = incidents_df[col].value_counts().to_dict()
                break
        
        # Create chart
        if status_dist:
            chart_data = pd.DataFrame([
                {'الحالة': status, 'العدد': count}
                for status, count in status_dist.items()
            ])
            
            fig = px.pie(
                chart_data,
                values='العدد',
                names='الحالة',
                title="توزيع حالات الحوادث"
            )
        else:
            fig = None
        
        text = f"إجمالي الحوادث المسجلة: {total_incidents:,} حادث\n"
        if status_dist:
            text += "توزيع الحالات:\n"
            for status, count in status_dist.items():
                text += f"• {status}: {count:,} حادث\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': incidents_df.head(10)
        }
    
    def _get_open_cases_summary(self):
        """Get open cases summary"""
        open_cases = {}
        total_open = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    open_count = len(df[df[col].str.contains('مفتوح', na=False)])
                    if open_count > 0:
                        open_cases[data_type] = open_count
                        total_open += open_count
                    break
        
        if not open_cases:
            return {
                'text': "لا توجد حالات مفتوحة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'الحالات المفتوحة': count}
            for data_type, count in open_cases.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='الحالات المفتوحة',
            title="الحالات المفتوحة حسب نوع البيانات"
        )
        
        text = f"إجمالي الحالات المفتوحة: {total_open:,}\n"
        text += "التوزيع حسب نوع البيانات:\n"
        for data_type, count in open_cases.items():
            text += f"• {data_type}: {count:,} حالة مفتوحة\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_closed_cases_summary(self):
        """Get closed cases summary"""
        closed_cases = {}
        total_closed = 0
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    closed_count = len(df[df[col].str.contains('مغلق', na=False)])
                    if closed_count > 0:
                        closed_cases[data_type] = closed_count
                        total_closed += closed_count
                    break
        
        if not closed_cases:
            return {
                'text': "لا توجد حالات مغلقة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'الحالات المغلقة': count}
            for data_type, count in closed_cases.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='الحالات المغلقة',
            title="الحالات المغلقة حسب نوع البيانات",
            color_discrete_sequence=['#2ca02c']
        )
        
        text = f"إجمالي الحالات المغلقة: {total_closed:,}\n"
        text += "التوزيع حسب نوع البيانات:\n"
        for data_type, count in closed_cases.items():
            text += f"• {data_type}: {count:,} حالة مغلقة\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_department_performance(self):
        """Get department performance analysis"""
        dept_performance = {}
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            dept_col = None
            status_col = None
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_col = col
                elif any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_col = col
            
            if dept_col and status_col:
                dept_status = df.groupby(dept_col)[status_col].value_counts().unstack(fill_value=0)
                for dept in dept_status.index:
                    closed = dept_status.loc[dept].get('مغلق', 0)
                    total = dept_status.loc[dept].sum()
                    compliance_rate = (closed / total * 100) if total > 0 else 0
                    
                    if dept not in dept_performance:
                        dept_performance[dept] = {'total': 0, 'closed': 0, 'rates': []}
                    
                    dept_performance[dept]['total'] += total
                    dept_performance[dept]['closed'] += closed
                    dept_performance[dept]['rates'].append(compliance_rate)
        
        if not dept_performance:
            return {
                'text': "لا توجد بيانات أداء القطاعات متاحة.",
                'chart': None,
                'data': None
            }
        
        # Calculate average performance
        performance_data = []
        for dept, data in dept_performance.items():
            avg_rate = np.mean(data['rates']) if data['rates'] else 0
            performance_data.append({
                'القطاع': dept,
                'معدل الامتثال': avg_rate,
                'إجمالي الحالات': data['total'],
                'الحالات المغلقة': data['closed']
            })
        
        performance_df = pd.DataFrame(performance_data)
        performance_df = performance_df.sort_values('معدل الامتثال', ascending=False)
        
        # Create chart
        fig = px.bar(
            performance_df.head(10),
            x='القطاع',
            y='معدل الامتثال',
            title="أداء القطاعات - معدل الامتثال",
            color='معدل الامتثال',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        # Generate text summary
        best_dept = performance_df.iloc[0]
        worst_dept = performance_df.iloc[-1]
        
        text = f"تحليل أداء القطاعات:\n\n"
        text += f"أفضل قطاع: {best_dept['القطاع']} بمعدل امتثال {best_dept['معدل الامتثال']:.1f}%\n"
        text += f"أضعف قطاع: {worst_dept['القطاع']} بمعدل امتثال {worst_dept['معدل الامتثال']:.1f}%\n\n"
        text += f"متوسط معدل الامتثال العام: {performance_df['معدل الامتثال'].mean():.1f}%"
        
        return {
            'text': text,
            'chart': fig,
            'data': performance_df
        }
    
    def _get_risk_assessment_summary(self):
        """Get risk assessment summary"""
        if 'risk_assessments' not in self.unified_data or self.unified_data['risk_assessments'].empty:
            return {
                'text': "لا توجد بيانات تقييم المخاطر متاحة في النظام حالياً.",
                'chart': None,
                'data': None
            }
        
        risk_df = self.unified_data['risk_assessments']
        total_assessments = len(risk_df)
        
        # Get risk level distribution
        risk_levels = {'عالي': 0, 'متوسط': 0, 'منخفض': 0}
        
        for col in risk_df.columns:
            if any(keyword in col.lower() for keyword in ['تصنيف', 'مخاطر', 'risk']):
                level_counts = risk_df[col].value_counts()
                for level, count in level_counts.items():
                    level_str = str(level).lower()
                    if 'عالي' in level_str or 'high' in level_str:
                        risk_levels['عالي'] += count
                    elif 'متوسط' in level_str or 'medium' in level_str:
                        risk_levels['متوسط'] += count
                    elif 'منخفض' in level_str or 'low' in level_str:
                        risk_levels['منخفض'] += count
                break
        
        # Create chart
        chart_data = pd.DataFrame([
            {'مستوى المخاطر': level, 'العدد': count}
            for level, count in risk_levels.items() if count > 0
        ])
        
        if not chart_data.empty:
            fig = px.pie(
                chart_data,
                values='العدد',
                names='مستوى المخاطر',
                title="توزيع مستويات المخاطر",
                color_discrete_map={
                    'عالي': '#d62728',
                    'متوسط': '#ff7f0e',
                    'منخفض': '#2ca02c'
                }
            )
        else:
            fig = None
        
        text = f"ملخص تقييم المخاطر:\n\n"
        text += f"إجمالي التقييمات: {total_assessments:,}\n"
        if any(risk_levels.values()):
            text += "توزيع مستويات المخاطر:\n"
            for level, count in risk_levels.items():
                if count > 0:
                    percentage = (count / sum(risk_levels.values())) * 100
                    text += f"• {level}: {count:,} ({percentage:.1f}%)\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': risk_df.head(10)
        }
    
    def _get_compliance_summary(self):
        """Get overall compliance summary"""
        total_open = 0
        total_closed = 0
        compliance_by_type = {}
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            type_open = 0
            type_closed = 0
            
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            type_open += count
                            total_open += count
                        elif 'مغلق' in str(status):
                            type_closed += count
                            total_closed += count
                    break
            
            if type_open + type_closed > 0:
                compliance_rate = (type_closed / (type_open + type_closed)) * 100
                compliance_by_type[data_type] = {
                    'rate': compliance_rate,
                    'closed': type_closed,
                    'total': type_open + type_closed
                }
        
        if total_open + total_closed == 0:
            return {
                'text': "لا توجد بيانات كافية لحساب معدل الامتثال.",
                'chart': None,
                'data': None
            }
        
        overall_compliance = (total_closed / (total_open + total_closed)) * 100
        
        # Create chart
        chart_data = pd.DataFrame([
            {'نوع البيانات': data_type, 'معدل الامتثال': data['rate']}
            for data_type, data in compliance_by_type.items()
        ])
        
        fig = px.bar(
            chart_data,
            x='نوع البيانات',
            y='معدل الامتثال',
            title="معدل الامتثال حسب نوع البيانات",
            color='معدل الامتثال',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        text = f"ملخص الامتثال العام:\n\n"
        text += f"معدل الامتثال الإجمالي: {overall_compliance:.1f}%\n"
        text += f"إجمالي الحالات: {total_open + total_closed:,}\n"
        text += f"الحالات المغلقة: {total_closed:,}\n"
        text += f"الحالات المفتوحة: {total_open:,}\n\n"
        text += "معدل الامتثال حسب نوع البيانات:\n"
        
        for data_type, data in compliance_by_type.items():
            text += f"• {data_type}: {data['rate']:.1f}% ({data['closed']}/{data['total']})\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': chart_data
        }
    
    def _get_trends_summary(self):
        """Get trends analysis"""
        trends_data = {}
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            date_col = None
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]':
                    date_col = col
                    break
            
            if date_col:
                monthly_trend = df.groupby(pd.Grouper(key=date_col, freq='M')).size()
                if len(monthly_trend) > 1:
                    trends_data[data_type] = monthly_trend
        
        if not trends_data:
            return {
                'text': "لا توجد بيانات كافية لتحليل الاتجاهات الزمنية.",
                'chart': None,
                'data': None
            }
        
        # Create combined trends chart
        fig = go.Figure()
        
        for data_type, trend in trends_data.items():
            fig.add_trace(go.Scatter(
                x=trend.index,
                y=trend.values,
                mode='lines+markers',
                name=data_type,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="الاتجاهات الزمنية للبيانات",
            xaxis_title="التاريخ",
            yaxis_title="عدد السجلات",
            hovermode='x unified'
        )
        
        text = "تحليل الاتجاهات الزمنية:\n\n"
        
        for data_type, trend in trends_data.items():
            latest_value = trend.iloc[-1]
            previous_value = trend.iloc[-2] if len(trend) > 1 else latest_value
            change = ((latest_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            text += f"• {data_type}:\n"
            text += f"  - القيمة الحالية: {latest_value:,}\n"
            text += f"  - التغيير: {change:+.1f}% من الشهر السابق\n\n"
        
        return {
            'text': text,
            'chart': fig,
            'data': None
        }
    
    def _get_general_statistics(self):
        """Get general statistics"""
        stats = {
            'total_records': 0,
            'data_types': len(self.unified_data),
            'date_ranges': {},
            'top_departments': {},
            'status_summary': {'مفتوح': 0, 'مغلق': 0}
        }
        
        for data_type, df in self.unified_data.items():
            if df.empty:
                continue
            
            stats['total_records'] += len(df)
            
            # Get date range
            date_range = self._get_date_range(df)
            if date_range:
                stats['date_ranges'][data_type] = date_range
            
            # Get department info
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department']):
                    dept_counts = df[col].value_counts().head(3)
                    stats['top_departments'][data_type] = dept_counts.to_dict()
                    break
            
            # Get status info
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['حالة', 'status']):
                    status_counts = df[col].value_counts()
                    for status, count in status_counts.items():
                        if 'مفتوح' in str(status):
                            stats['status_summary']['مفتوح'] += count
                        elif 'مغلق' in str(status):
                            stats['status_summary']['مغلق'] += count
                    break
        
        text = f"الإحصائيات العامة للنظام:\n\n"
        text += f"إجمالي السجلات: {stats['total_records']:,}\n"
        text += f"أنواع البيانات: {stats['data_types']}\n"
        text += f"الحالات المفتوحة: {stats['status_summary']['مفتوح']:,}\n"
        text += f"الحالات المغلقة: {stats['status_summary']['مغلق']:,}\n\n"
        
        if stats['date_ranges']:
            text += "النطاقات الزمنية:\n"
            for data_type, date_range in stats['date_ranges'].items():
                text += f"• {data_type}: من {date_range['start']} إلى {date_range['end']} ({date_range['days']} يوم)\n"
        
        return {
            'text': text,
            'chart': None,
            'data': None
        }
    
    def _get_general_response(self, user_query):
        """Get general response for unclassified queries"""
        # Check if query contains specific keywords
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['مساعدة', 'help']):
            return {
                'text': """يمكنني مساعدتك في الاستفسار عن:

• إجمالي الحوادث والملاحظات
• الحالات المفتوحة والمغلقة
• أداء القطاعات المختلفة
• تقييمات المخاطر
• معدلات الامتثال
• الاتجاهات الزمنية
• الإحصائيات العامة

مثال على الأسئلة:
- "كم عدد الحوادث المفتوحة؟"
- "ما هو أداء قطاع المشاريع؟"
- "أظهر لي اتجاه الملاحظات"
- "ما هو معدل الامتثال؟"
""",
                'chart': None,
                'data': None
            }
        
        # Provide insights from knowledge base
        insights_text = "إليك بعض الرؤى من البيانات:\n\n"
        for insight in self.knowledge_base['insights'][:3]:
            insights_text += f"• {insight}\n"
        
        insights_text += "\nيمكنك طرح أسئلة أكثر تحديداً للحصول على تحليل مفصل."
        
        return {
            'text': insights_text,
            'chart': None,
            'data': None
        }
    
    def get_conversation_history(self):
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def export_conversation(self):
        """Export conversation history"""
        if not self.conversation_history:
            return None
        
        conversation_data = []
        for entry in self.conversation_history:
            conversation_data.append({
                'timestamp': entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'user_query': entry['user_query'],
                'response_text': entry['response']['text'] if entry['response'] else None
            })
        
        return pd.DataFrame(conversation_data)

def create_chatbot_interface(unified_data, kpi_data):
    """Create chatbot interface in Streamlit"""
    st.subheader("🤖 مساعد الذكاء الاصطناعي")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = GeminiChatbot(unified_data, kpi_data)
    
    # Chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("chart"):
                st.plotly_chart(message["chart"], use_container_width=True)
            if message.get("data") is not None:
                st.dataframe(message["data"], use_container_width=True)
    
    # Chat input
    if prompt := st.chat_input("اطرح سؤالك حول بيانات السلامة والامتثال..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("جاري التحليل..."):
                response = st.session_state.chatbot.process_query(prompt)
            
            st.markdown(response['text'])
            
            if response['chart']:
                st.plotly_chart(response['chart'], use_container_width=True)
            
            if response['data'] is not None:
                st.dataframe(response['data'], use_container_width=True)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response['text'],
                "chart": response['chart'],
                "data": response['data']
            })
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("إعدادات المحادثة")
        
        if st.button("مسح المحادثة"):
            st.session_state.messages = []
            st.session_state.chatbot.clear_conversation()
            st.rerun()
        
        if st.button("تصدير المحادثة"):
            conversation_df = st.session_state.chatbot.export_conversation()
            if conversation_df is not None:
                csv = conversation_df.to_csv(index=False)
                st.download_button(
                    label="تحميل سجل المحادثة",
                    data=csv,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("لا توجد محادثة لتصديرها")
        
        # Quick questions
        st.subheader("أسئلة سريعة")
        quick_questions = [
            "كم عدد الحوادث الإجمالي؟",
            "ما هي الحالات المفتوحة؟",
            "أظهر أداء القطاعات",
            "ما هو معدل الامتثال؟",
            "أظهر الاتجاهات الزمنية"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}"):
                # Simulate clicking the question
                st.session_state.messages.append({"role": "user", "content": question})
                
                with st.spinner("جاري التحليل..."):
                    response = st.session_state.chatbot.process_query(question)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response['text'],
                    "chart": response['chart'],
                    "data": response['data']
                })
                st.rerun()