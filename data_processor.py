"""
Advanced Data Engineering Module
Handles data cleaning, standardization, and unification for the Safety & Compliance Dashboard
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SafetyDataProcessor:
    """Comprehensive data processor for safety and compliance data"""
    
    def __init__(self):
        self.data_sources = {}
        self.unified_data = {}
        self.metadata = {}
        
    def load_excel_data(self, file_path):
        """Load and process Excel data with multiple sheets"""
        try:
            excel_file = pd.ExcelFile(file_path)
            data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                df = self._clean_dataframe(df, sheet_name)
                data[sheet_name] = df
                
            return data
        except Exception as e:
            print(f"Error loading Excel file {file_path}: {str(e)}")
            return {}
    
    def load_csv_data(self, file_path):
        """Load and process CSV data"""
        try:
            df = pd.read_csv(file_path)
            filename = file_path.split('/')[-1].replace('.csv', '')
            df = self._clean_dataframe(df, filename)
            return df
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def _clean_dataframe(self, df, source_name):
        """Clean and standardize dataframe"""
        if df.empty:
            return df
            
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Clean column names
        df.columns = self._clean_column_names(df.columns)
        
        # Handle header rows (first row often contains actual column names)
        if len(df) > 0:
            first_row = df.iloc[0]
            if self._is_header_row(first_row):
                df.columns = [str(col).strip() if pd.notna(col) else f"col_{i}" 
                             for i, col in enumerate(first_row)]
                df = df.iloc[1:].reset_index(drop=True)
                df.columns = self._clean_column_names(df.columns)
        
        # Standardize data types
        df = self._standardize_data_types(df)
        
        # Clean text data
        df = self._clean_text_data(df)
        
        # Standardize status values
        df = self._standardize_status_values(df)
        
        return df
    
    def _clean_column_names(self, columns):
        """Clean and standardize column names"""
        cleaned_columns = []
        for col in columns:
            if pd.isna(col) or str(col).startswith('Unnamed'):
                cleaned_columns.append(f"col_{len(cleaned_columns)}")
            else:
                # Clean the column name
                clean_col = str(col).strip()
                clean_col = re.sub(r'\n+', '_', clean_col)
                clean_col = re.sub(r'\s+', '_', clean_col)
                cleaned_columns.append(clean_col)
        return cleaned_columns
    
    def _is_header_row(self, row):
        """Check if the first row contains header information"""
        non_null_count = row.notna().sum()
        return non_null_count > len(row) * 0.5
    
    def _standardize_data_types(self, df):
        """Standardize data types across the dataframe"""
        for col in df.columns:
            # Try to convert date columns
            if any(keyword in col.lower() for keyword in ['تاريخ', 'date']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Try to convert numeric columns
            elif any(keyword in col.lower() for keyword in ['عدد', 'نسبة', 'رقم', 'number', 'count', 'percentage']):
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def _clean_text_data(self, df):
        """Clean and standardize text data"""
        text_columns = df.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].str.strip()
            df[col] = df[col].replace('nan', np.nan)
            df[col] = df[col].replace('', np.nan)
        
        return df
    
    def _standardize_status_values(self, df):
        """Standardize status values across all datasets"""
        status_mappings = {
            'مفتوح - Open': 'مفتوح',
            'مغلق - Close': 'مغلق',
            'مغلق - Closed': 'مغلق',
            'Closed - Close': 'مغلق',
            'Open': 'مفتوح',
            'Close': 'مغلق',
            'Closed': 'مغلق'
        }
        
        # Apply status standardization to relevant columns
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['حالة', 'status', 'state']):
                df[col] = df[col].map(status_mappings).fillna(df[col])
        
        return df
    
    def create_unified_dataset(self, data_sources):
        """Create unified datasets from multiple sources"""
        unified_data = {}
        
        # Process inspection data
        inspection_data = []
        for source, data in data_sources.items():
            if 'تفتيش' in source or 'inspection' in source.lower():
                if isinstance(data, dict):
                    for sheet_name, df in data.items():
                        if not df.empty:
                            df['source'] = f"{source}_{sheet_name}"
                            inspection_data.append(df)
                else:
                    if not data.empty:
                        data['source'] = source
                        inspection_data.append(data)
        
        if inspection_data:
            unified_data['inspections'] = self._merge_similar_datasets(inspection_data)
        
        # Process incident data
        incident_data = []
        for source, data in data_sources.items():
            if 'حوادث' in source or 'incident' in source.lower():
                if isinstance(data, dict):
                    for sheet_name, df in data.items():
                        if not df.empty:
                            df['source'] = f"{source}_{sheet_name}"
                            incident_data.append(df)
                else:
                    if not data.empty:
                        data['source'] = source
                        incident_data.append(data)
        
        if incident_data:
            unified_data['incidents'] = self._merge_similar_datasets(incident_data)
        
        # Process risk assessment data
        risk_data = []
        for source, data in data_sources.items():
            if 'مخاطر' in source or 'risk' in source.lower():
                if isinstance(data, dict):
                    for sheet_name, df in data.items():
                        if not df.empty:
                            df['source'] = f"{source}_{sheet_name}"
                            risk_data.append(df)
                else:
                    if not data.empty:
                        data['source'] = source
                        risk_data.append(data)
        
        if risk_data:
            unified_data['risk_assessments'] = self._merge_similar_datasets(risk_data)
        
        # Process contractor audit data
        contractor_data = []
        for source, data in data_sources.items():
            if 'مقاولين' in source or 'contractor' in source.lower():
                if isinstance(data, dict):
                    for sheet_name, df in data.items():
                        if not df.empty:
                            df['source'] = f"{source}_{sheet_name}"
                            contractor_data.append(df)
                else:
                    if not data.empty:
                        data['source'] = source
                        contractor_data.append(data)
        
        if contractor_data:
            unified_data['contractor_audits'] = self._merge_similar_datasets(contractor_data)
        
        return unified_data
    
    def _merge_similar_datasets(self, datasets):
        """Merge datasets with similar structure"""
        if not datasets:
            return pd.DataFrame()
        
        if len(datasets) == 1:
            return datasets[0]
        
        # Find common columns
        common_columns = set(datasets[0].columns)
        for df in datasets[1:]:
            common_columns = common_columns.intersection(set(df.columns))
        
        # Merge datasets using common columns
        merged_data = []
        for df in datasets:
            # Select common columns and add missing ones with NaN
            df_subset = df[list(common_columns)].copy()
            merged_data.append(df_subset)
        
        result = pd.concat(merged_data, ignore_index=True)
        return result
    
    def generate_kpi_data(self, unified_data):
        """Generate KPI data for dashboard"""
        kpis = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
                
            kpis[data_type] = {
                'total_records': len(df),
                'date_range': self._get_date_range(df),
                'status_distribution': self._get_status_distribution(df),
                'department_distribution': self._get_department_distribution(df),
                'activity_distribution': self._get_activity_distribution(df)
            }
        
        return kpis
    
    def _get_date_range(self, df):
        """Get date range from dataframe"""
        date_columns = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
        if not date_columns:
            return None
        
        all_dates = pd.concat([df[col].dropna() for col in date_columns])
        if len(all_dates) == 0:
            return None
        
        return {
            'min_date': all_dates.min(),
            'max_date': all_dates.max()
        }
    
    def _get_status_distribution(self, df):
        """Get status distribution from dataframe"""
        status_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['حالة', 'status'])]
        if not status_columns:
            return {}
        
        status_counts = {}
        for col in status_columns:
            counts = df[col].value_counts().to_dict()
            status_counts.update(counts)
        
        return status_counts
    
    def _get_department_distribution(self, df):
        """Get department distribution from dataframe"""
        dept_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['إدارة', 'قطاع', 'department', 'sector'])]
        if not dept_columns:
            return {}
        
        dept_counts = {}
        for col in dept_columns:
            counts = df[col].value_counts().to_dict()
            dept_counts.update(counts)
        
        return dept_counts
    
    def _get_activity_distribution(self, df):
        """Get activity distribution from dataframe"""
        activity_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['نشاط', 'activity', 'تصنيف'])]
        if not activity_columns:
            return {}
        
        activity_counts = {}
        for col in activity_columns:
            counts = df[col].value_counts().to_dict()
            activity_counts.update(counts)
        
        return activity_counts
    
    def export_cleaned_data(self, unified_data, output_path):
        """Export cleaned and unified data"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in unified_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Cleaned data exported to {output_path}")
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
    
    def get_data_quality_report(self, unified_data):
        """Generate data quality report"""
        report = {}
        
        for data_type, df in unified_data.items():
            if df.empty:
                continue
                
            report[data_type] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_data_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'duplicate_rows': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict(),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
        
        return report

def main():
    """Main function for testing the data processor"""
    processor = SafetyDataProcessor()
    
    # Load sample data
    sample_data = processor.load_excel_data('sample-of-data.xlsx')
    
    # Create unified dataset
    unified_data = processor.create_unified_dataset({'sample_data': sample_data})
    
    # Generate KPIs
    kpis = processor.generate_kpi_data(unified_data)
    
    # Generate quality report
    quality_report = processor.get_data_quality_report(unified_data)
    
    print("Data processing completed successfully!")
    print(f"Unified datasets created: {list(unified_data.keys())}")
    print(f"KPIs generated: {list(kpis.keys())}")
    
    return processor, unified_data, kpis, quality_report

if __name__ == "__main__":
    main()