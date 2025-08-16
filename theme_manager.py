"""
Theme Manager for Safety & Compliance Dashboard
Handles dark/light theme switching and UI customization
"""

import streamlit as st
import json
from datetime import datetime

class ThemeManager:
    """Advanced theme management system"""
    
    def __init__(self):
        self.themes = {
            'light': {
                'name': 'Light Theme',
                'icon': '☀️',
                'primary_color': '#1f77b4',
                'secondary_color': '#ff7f0e',
                'success_color': '#2ca02c',
                'warning_color': '#d62728',
                'info_color': '#9467bd',
                'background_color': '#ffffff',
                'surface_color': '#f8f9fa',
                'text_color': '#212529',
                'text_secondary': '#6c757d',
                'border_color': '#dee2e6',
                'shadow': '0 4px 6px rgba(0,0,0,0.1)',
                'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'gradient_success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'card_bg': 'linear-gradient(135deg, #f0f2f6 0%, #e8ecf0 100%)',
                'sidebar_bg': '#f8f9fa'
            },
            'dark': {
                'name': 'Dark Theme',
                'icon': '🌙',
                'primary_color': '#4dabf7',
                'secondary_color': '#ffa726',
                'success_color': '#66bb6a',
                'warning_color': '#ef5350',
                'info_color': '#ab47bc',
                'background_color': '#121212',
                'surface_color': '#1e1e1e',
                'text_color': '#ffffff',
                'text_secondary': '#b0b0b0',
                'border_color': '#333333',
                'shadow': '0 4px 6px rgba(0,0,0,0.3)',
                'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'gradient_success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'card_bg': 'linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)',
                'sidebar_bg': '#1a1a1a'
            },
            'blue': {
                'name': 'Ocean Blue',
                'icon': '🌊',
                'primary_color': '#0077be',
                'secondary_color': '#00a8cc',
                'success_color': '#00c851',
                'warning_color': '#ff8800',
                'info_color': '#33b5e5',
                'background_color': '#f0f8ff',
                'surface_color': '#e6f3ff',
                'text_color': '#1a1a1a',
                'text_secondary': '#4a4a4a',
                'border_color': '#b3d9ff',
                'shadow': '0 4px 6px rgba(0,119,190,0.2)',
                'gradient_primary': 'linear-gradient(135deg, #0077be 0%, #00a8cc 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #33b5e5 0%, #0077be 100%)',
                'gradient_success': 'linear-gradient(135deg, #00c851 0%, #00a8cc 100%)',
                'card_bg': 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)',
                'sidebar_bg': '#e6f3ff'
            },
            'green': {
                'name': 'Nature Green',
                'icon': '🌿',
                'primary_color': '#2e7d32',
                'secondary_color': '#66bb6a',
                'success_color': '#4caf50',
                'warning_color': '#ff9800',
                'info_color': '#00bcd4',
                'background_color': '#f1f8e9',
                'surface_color': '#e8f5e8',
                'text_color': '#1b5e20',
                'text_secondary': '#388e3c',
                'border_color': '#c8e6c9',
                'shadow': '0 4px 6px rgba(46,125,50,0.2)',
                'gradient_primary': 'linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%)',
                'gradient_secondary': 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
                'gradient_success': 'linear-gradient(135deg, #66bb6a 0%, #4caf50 100%)',
                'card_bg': 'linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%)',
                'sidebar_bg': '#e8f5e8'
            }
        }
        
        # Initialize theme in session state
        if 'current_theme' not in st.session_state:
            st.session_state.current_theme = 'light'
    
    def get_current_theme(self):
        """Get current theme configuration"""
        return self.themes[st.session_state.current_theme]
    
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name in self.themes:
            st.session_state.current_theme = theme_name
            st.rerun()
    
    def create_theme_selector(self):
        """Create theme selector widget"""
        st.sidebar.markdown("### 🎨 اختيار المظهر")
        
        current_theme = st.session_state.current_theme
        theme_options = {name: f"{config['icon']} {config['name']}" 
                        for name, config in self.themes.items()}
        
        selected_theme = st.sidebar.selectbox(
            "اختر المظهر",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=list(theme_options.keys()).index(current_theme),
            key="theme_selector"
        )
        
        if selected_theme != current_theme:
            self.set_theme(selected_theme)
        
        # Theme preview
        theme_config = self.get_current_theme()
        st.sidebar.markdown(f"""
        <div style="
            background: {theme_config['card_bg']};
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid {theme_config['border_color']};
            margin: 1rem 0;
        ">
            <h4 style="color: {theme_config['primary_color']}; margin: 0;">
                {theme_config['icon']} {theme_config['name']}
            </h4>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
                <div style="width: 20px; height: 20px; background: {theme_config['primary_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['secondary_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['success_color']}; border-radius: 50%;"></div>
                <div style="width: 20px; height: 20px; background: {theme_config['warning_color']}; border-radius: 50%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def apply_theme_css(self):
        """Apply current theme CSS"""
        theme = self.get_current_theme()
        
        css = f"""
        <style>
            /* Global Theme Variables */
            :root {{
                --primary-color: {theme['primary_color']};
                --secondary-color: {theme['secondary_color']};
                --success-color: {theme['success_color']};
                --warning-color: {theme['warning_color']};
                --info-color: {theme['info_color']};
                --background-color: {theme['background_color']};
                --surface-color: {theme['surface_color']};
                --text-color: {theme['text_color']};
                --text-secondary: {theme['text_secondary']};
                --border-color: {theme['border_color']};
                --shadow: {theme['shadow']};
                --gradient-primary: {theme['gradient_primary']};
                --gradient-secondary: {theme['gradient_secondary']};
                --gradient-success: {theme['gradient_success']};
                --card-bg: {theme['card_bg']};
                --sidebar-bg: {theme['sidebar_bg']};
            }}
            
            /* Main App Background */
            .stApp {{
                background-color: var(--background-color);
                color: var(--text-color);
            }}
            
            /* Sidebar Styling */
            .css-1d391kg {{
                background-color: var(--sidebar-bg);
            }}
            
            /* Main Header */
            .main-header {{
                font-size: 3rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 2rem;
                background: var(--gradient-primary);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                animation: headerGlow 3s ease-in-out infinite alternate;
            }}
            
            @keyframes headerGlow {{
                from {{ filter: brightness(1); }}
                to {{ filter: brightness(1.2); }}
            }}
            
            /* Enhanced Metric Cards */
            .metric-card {{
                background: var(--card-bg);
                padding: 2rem;
                border-radius: 1rem;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .metric-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: var(--gradient-primary);
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px) scale(1.02);
                box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            }}
            
            .metric-card h2 {{
                color: var(--primary-color);
                font-size: 2.5rem;
                font-weight: bold;
                margin: 0.5rem 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }}
            
            .metric-card h3 {{
                color: var(--text-color);
                font-size: 1.2rem;
                margin: 0;
                opacity: 0.8;
            }}
            
            .metric-card p {{
                color: var(--text-secondary);
                font-size: 0.9rem;
                margin: 0.5rem 0 0 0;
            }}
            
            /* Sector Cards */
            .sector-card {{
                background: var(--gradient-primary);
                color: white;
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: var(--shadow);
                position: relative;
                overflow: hidden;
            }}
            
            .sector-card::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
                transform: rotate(45deg);
                transition: all 0.5s;
                opacity: 0;
            }}
            
            .sector-card:hover::before {{
                animation: shimmer 1s ease-in-out;
                opacity: 1;
            }}
            
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
                100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
            }}
            
            .sector-card:hover {{
                transform: scale(1.05) rotateY(5deg);
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            
            /* Risk Level Styling */
            .risk-high {{
                background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                color: #c62828;
                border-left: 4px solid #d32f2f;
            }}
            
            .risk-medium {{
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                color: #ef6c00;
                border-left: 4px solid #f57c00;
            }}
            
            .risk-low {{
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                color: #2e7d32;
                border-left: 4px solid #388e3c;
            }}
            
            /* Status Styling */
            .status-open {{
                background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                color: #c62828;
                padding: 0.5rem 1rem;
                border-radius: 2rem;
                font-weight: bold;
                display: inline-block;
                margin: 0.2rem;
            }}
            
            .status-closed {{
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
                color: #2e7d32;
                padding: 0.5rem 1rem;
                border-radius: 2rem;
                font-weight: bold;
                display: inline-block;
                margin: 0.2rem;
            }}
            
            /* Activity Badges */
            .activity-badge {{
                background: var(--gradient-secondary);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 2rem;
                font-size: 0.8rem;
                margin: 0.2rem;
                display: inline-block;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                transition: all 0.2s ease;
            }}
            
            .activity-badge:hover {{
                transform: scale(1.1);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }}
            
            /* Filter Section */
            .filter-section {{
                background: var(--surface-color);
                padding: 2rem;
                border-radius: 1rem;
                border: 1px solid var(--border-color);
                margin-bottom: 2rem;
                box-shadow: var(--shadow);
            }}
            
            /* Enhanced Buttons */
            .stButton > button {{
                background: var(--gradient-primary);
                color: white;
                border: none;
                border-radius: 2rem;
                padding: 0.75rem 2rem;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: var(--shadow);
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                filter: brightness(1.1);
            }}
            
            /* Enhanced Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 5px;
                background: var(--surface-color);
                padding: 0.5rem;
                border-radius: 1rem;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .stTabs [data-baseweb="tab"] {{
                height: 60px;
                padding: 0 2rem;
                background: transparent;
                border-radius: 0.8rem;
                font-weight: bold;
                transition: all 0.3s ease;
                color: var(--text-secondary);
            }}
            
            .stTabs [aria-selected="true"] {{
                background: var(--gradient-primary);
                color: white;
                box-shadow: var(--shadow);
                transform: translateY(-2px);
            }}
            
            /* Enhanced Selectbox */
            .stSelectbox > div > div {{
                background: var(--surface-color);
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                color: var(--text-color);
            }}
            
            /* Enhanced Multiselect */
            .stMultiSelect > div > div {{
                background: var(--surface-color);
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                color: var(--text-color);
            }}
            
            /* Enhanced Dataframe */
            .stDataFrame {{
                border-radius: 1rem;
                overflow: hidden;
                box-shadow: var(--shadow);
            }}
            
            /* Loading Spinner */
            .stSpinner > div {{
                border-top-color: var(--primary-color) !important;
            }}
            
            /* Success/Warning/Error Messages */
            .stSuccess {{
                background: var(--gradient-success);
                color: white;
                border-radius: 0.5rem;
                padding: 1rem;
                box-shadow: var(--shadow);
            }}
            
            .stWarning {{
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                color: #ef6c00;
                border-radius: 0.5rem;
                padding: 1rem;
                box-shadow: var(--shadow);
            }}
            
            .stError {{
                background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
                color: #c62828;
                border-radius: 0.5rem;
                padding: 1rem;
                box-shadow: var(--shadow);
            }}
            
            /* Animated Elements */
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .fade-in-up {{
                animation: fadeInUp 0.6s ease-out;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
            
            .pulse {{
                animation: pulse 2s infinite;
            }}
            
            /* Responsive Design */
            @media (max-width: 768px) {{
                .main-header {{
                    font-size: 2rem;
                }}
                
                .metric-card {{
                    padding: 1rem;
                }}
                
                .sector-card {{
                    padding: 1rem;
                }}
            }}
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar {{
                width: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: var(--surface-color);
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: var(--primary-color);
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: var(--secondary-color);
            }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def create_theme_info(self):
        """Create theme information display"""
        theme = self.get_current_theme()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎨 معلومات المظهر")
        st.sidebar.markdown(f"""
        **المظهر الحالي:** {theme['icon']} {theme['name']}
        
        **الألوان:**
        - 🔵 الأساسي: `{theme['primary_color']}`
        - 🟠 الثانوي: `{theme['secondary_color']}`
        - 🟢 النجاح: `{theme['success_color']}`
        - 🔴 التحذير: `{theme['warning_color']}`
        """)
    
    def save_theme_preferences(self, user_id=None):
        """Save theme preferences to local storage"""
        preferences = {
            'theme': st.session_state.current_theme,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id or 'default'
        }
        
        # In a real application, you would save this to a database
        # For now, we'll use session state
        st.session_state.theme_preferences = preferences
    
    def load_theme_preferences(self, user_id=None):
        """Load theme preferences from local storage"""
        if 'theme_preferences' in st.session_state:
            preferences = st.session_state.theme_preferences
            if preferences.get('user_id') == (user_id or 'default'):
                self.set_theme(preferences.get('theme', 'light'))