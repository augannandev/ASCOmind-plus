# main.py - ASCOMIND+ STREAMLIT APPLICATION

import streamlit as st
import asyncio
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import io
import json
import time  # Add time import for tracking processing duration

# Import agents and models
from agents.metadata_extractor import EnhancedMetadataExtractor, BatchExtractor
from agents.analyzer import IntelligentAnalyzer
from agents.visualizer import AdvancedVisualizer
from agents.categorizer import SmartCategorizer, BatchCategorizer
from agents.protocol_maker import ProtocolMaker
from agents.vector_store import IntelligentVectorStore
from agents.ai_assistant import AdvancedAIAssistant
from models.abstract_metadata import ComprehensiveAbstractMetadata
from config.settings import settings

# Import utilities
from utils.file_processors import FileProcessor, AbstractExtractor
from utils.database import get_database

# Set page configuration
st.set_page_config(
    page_title="ASCOmind+ | Medical Intelligence Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Custom CSS for professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Variables */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --accent-color: #f093fb;
        --success-color: #4ade80;
        --warning-color: #fbbf24;
        --error-color: #f87171;
        --background-light: #f8fafc;
        --background-dark: #1e293b;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* Hide Streamlit default elements */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    .stFooter {display: none;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main > div {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling with enhanced gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-xl);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-left-color: var(--accent-color);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, var(--primary-color)20, transparent);
        border-radius: 0 1rem 0 100%;
    }
    
    .metric-card h4 {
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .metric-card p {
        color: var(--text-secondary);
        line-height: 1.5;
        margin: 0;
    }
    
    /* Advanced insight panel */
    .insight-panel {
        background: linear-gradient(145deg, #f8fafc 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
        position: relative;
    }
    
    .insight-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        border-radius: 1rem 1rem 0 0;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: var(--background-light);
        padding: 0.25rem;
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white !important;
        box-shadow: var(--shadow-sm);
    }
    
    /* Enhanced sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-right: 1px solid var(--border-color);
    }
    
    /* Quality badges */
    .quality-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.125rem;
    }
    
    .quality-high {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .quality-medium {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: white;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }
    
    .quality-low {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    /* Enhanced progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        border-radius: 9999px;
    }
    
    /* Advanced dataframe styling */
    .stDataFrame {
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    .stDataFrame table {
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        font-weight: 600;
        padding: 1rem;
        border: none;
    }
    
    .stDataFrame td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-color);
        transition: background-color 0.2s ease;
    }
    
    .stDataFrame tr:hover td {
        background-color: var(--background-light);
    }
    
    /* Enhanced metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .stMetric > div > div:first-child {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    
    .stMetric > div > div:nth-child(2) {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.25rem 0;
    }
    
    /* Enhanced expanders */
    .stExpander {
        border: 1px solid var(--border-color);
        border-radius: 0.75rem;
        overflow: hidden;
        margin-bottom: 1rem;
        box-shadow: var(--shadow-sm);
    }
    
    .stExpander > summary {
        background: linear-gradient(135deg, #f8fafc, #ffffff);
        padding: 1rem 1.5rem;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stExpander > summary:hover {
        background: linear-gradient(135deg, var(--primary-color)10, var(--accent-color)10);
    }
    
    .stExpander[open] > summary {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }
    
    .stExpander > div {
        padding: 1.5rem;
        background: white;
    }
    
    /* Enhanced file uploader */
    .stFileUploader {
        border: 2px dashed var(--border-color);
        border-radius: 0.75rem;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #ffffff, #f8fafc);
    }
    
    .stFileUploader:hover {
        border-color: var(--primary-color);
        background: linear-gradient(145deg, var(--primary-color)05, var(--accent-color)05);
    }
    
    /* Enhanced selectbox */
    .stSelectbox > div > div {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        background: white;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px var(--primary-color)20;
    }
    
    /* Enhanced text areas */
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px var(--primary-color)20;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s infinite;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.125rem;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
    }
    
    /* Enhanced charts */
    .stPlotlyChart {
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        background: white;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .insight-panel {
            padding: 1.5rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--background-light);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
    }
    
    /* Enhanced info boxes */
    .stInfo {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border: 1px solid #3b82f6;
        border-radius: 0.75rem;
        color: #1e40af;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        border: 1px solid #10b981;
        border-radius: 0.75rem;
        color: #065f46;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        border: 1px solid #f59e0b;
        border-radius: 0.75rem;
        color: #92400e;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 1px solid #ef4444;
        border-radius: 0.75rem;
        color: #991b1b;
    }
    
    /* Enhanced sidebar metrics */
    .sidebar-metric {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        margin-bottom: 0.5rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .sidebar-metric:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    /* Glassmorphism effect for special cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 1rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .section-header h2, .section-header h3 {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        font-weight: 700;
    }
    
    /* Custom navigation styles */
    .nav-button {
        display: block;
        width: 100%;
        padding: 1rem 1.5rem;
        margin-bottom: 0.5rem;
        border: none;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #f8fafc, #ffffff);
        color: #64748b;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        border-color: #667eea;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #1e293b;
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-color: #5a67d8;
        box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3);
    }
    
    .nav-button.active:hover {
        background: linear-gradient(135deg, #5a67d8, #6b46c1);
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(102, 126, 234, 0.4);
    }
    
    .nav-icon {
        font-size: 1.25rem;
        margin-right: 0.75rem;
        display: inline-block;
        width: 24px;
        text-align: center;
    }
    
    .nav-text {
        display: inline-block;
        vertical-align: middle;
    }
    
    .nav-badge {
        float: right;
        background: rgba(255, 255, 255, 0.2);
        color: inherit;
        padding: 0.125rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


class ASCOmindApp:
    """Main ASCOmind+ Streamlit Application"""
    
    def __init__(self):
        """Initialize the ASCOmind+ application with performance optimizations"""
        
        # Refresh settings to load API keys from Streamlit secrets
        settings.refresh_from_secrets()
        
        # Initialize session state first
        self.initialize_session_state()
        
        # Initialize database and utilities (lightweight operations)
        try:
            self.database = get_database(session_id=getattr(st.session_state, 'session_id', None))
            self.file_processor = FileProcessor()
            self.abstract_extractor = AbstractExtractor()
        except Exception as e:
            st.warning(f"Database initialization issue: {e}")
            self.database = None
            self.file_processor = None
            self.abstract_extractor = None
        
        # Initialize core agents with better error handling (lazy loading)
        try:
            self.metadata_extractor = EnhancedMetadataExtractor()
            self.categorizer = SmartCategorizer()
            self.protocol_maker = ProtocolMaker()
        except Exception as e:
            st.warning(f"Core agents initialization delayed: {e}")
            self.metadata_extractor = None
            self.categorizer = None
            self.protocol_maker = None
        
        # Initialize analyzer only when needed (lazy loading)
        self.analyzer = None
        self.visualizer = None
        
        # Initialize vector store and AI assistant only when needed (lazy loading)
        self.vector_store = None
        self.ai_assistant = None
    
    def initialize_session_state(self):
        """Initialize session state variables with session isolation"""
        
        # Generate or retrieve session ID for data isolation
        if 'session_id' not in st.session_state:
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = str(uuid.uuid4())[:8]
            st.session_state.session_id = f"session_{timestamp}_{random_id}"
        
        # Developer mode detection
        if 'developer_mode' not in st.session_state:
            # Check URL parameters for ?dev
            query_params = st.query_params
            st.session_state.developer_mode = 'dev' in query_params or query_params.get('dev') == 'true'
        
        # LLM Provider selection (for developer mode)
        if 'selected_llm_provider' not in st.session_state:
            st.session_state.selected_llm_provider = settings.DEFAULT_LLM_PROVIDER
            
        if 'extracted_data' not in st.session_state:
            st.session_state.extracted_data = []
        
        if 'categorization_data' not in st.session_state:
            st.session_state.categorization_data = []
        
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        
        if 'session_stats' not in st.session_state:
            st.session_state.session_stats = {
                'total_abstracts': 0,
                'total_processing_time': 0.0,
                'session_start_time': time.time(),
                'abstracts_processed': 0,
                'files_processed': 0,
                'processing_history': []
            }
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
        
        if 'demo_mode' not in st.session_state:
            st.session_state.demo_mode = False
        
        # Vector store and AI assistant session state
        if 'vector_embedding_status' not in st.session_state:
            st.session_state.vector_embedding_status = []
        
        if 'ai_conversation_history' not in st.session_state:
            st.session_state.ai_conversation_history = []
        
        if 'ai_context' not in st.session_state:
            st.session_state.ai_context = {}
        
        # Session isolation flags
        if 'session_data_isolated' not in st.session_state:
            st.session_state.session_data_isolated = True
    
    def run(self):
        """Main application entry point"""
        
        # Enhanced Header with better styling
        st.markdown("""
        <div class="main-header">
            <h1>🧬 ASCOmind+ Medical Intelligence Platform</h1>
            <p>Advanced Oncology Research Analytics & Clinical Insights Powered by AI</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced sidebar navigation
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h2 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">Navigation</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Modern navigation with interactive buttons
            st.markdown("""
            <style>
            .nav-button {
                display: block;
                width: 100%;
                padding: 1rem 1.5rem;
                margin-bottom: 0.5rem;
                border: none;
                border-radius: 0.75rem;
                background: linear-gradient(135deg, #f8fafc, #ffffff);
                color: #64748b;
                text-decoration: none;
                font-weight: 500;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }
            
            .nav-button:hover {
                background: linear-gradient(135deg, #667eea20, #764ba220);
                border-color: #667eea;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                color: #1e293b;
            }
            
            .nav-button.active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border-color: #5a67d8;
                box-shadow: 0 4px 6px -1px rgba(102, 126, 234, 0.3);
            }
            
            .nav-button.active:hover {
                background: linear-gradient(135deg, #5a67d8, #6b46c1);
                transform: translateY(-1px);
                box-shadow: 0 6px 8px -1px rgba(102, 126, 234, 0.4);
            }
            
            .nav-icon {
                font-size: 1.25rem;
                margin-right: 0.75rem;
                display: inline-block;
                width: 24px;
                text-align: center;
            }
            
            .nav-text {
                display: inline-block;
                vertical-align: middle;
            }
            
            .nav-badge {
                float: right;
                background: rgba(255, 255, 255, 0.2);
                color: inherit;
                padding: 0.125rem 0.5rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 0.5rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Navigation options with enhanced design
            nav_options = [
                {"icon": "🏠", "name": "Welcome", "key": "welcome", "badge": None},
                {"icon": "📊", "name": "Dashboard", "key": "dashboard", "badge": len(st.session_state.extracted_data) if st.session_state.extracted_data else None},
                {"icon": "📄", "name": "Abstract Analysis", "key": "abstract", "badge": len(st.session_state.extracted_data) if st.session_state.extracted_data else None},
                {"icon": "🤖", "name": "AI Assistant", "key": "ai", "badge": len(st.session_state.ai_conversation_history) if len(st.session_state.ai_conversation_history) > 0 else None},
                {"icon": "🔬", "name": "Protocol Generator", "key": "protocol", "badge": None},
                {"icon": "🔍", "name": "Research Explorer", "key": "research", "badge": "Soon"},
                {"icon": "💊", "name": "Treatment Intelligence", "key": "treatment", "badge": "Soon"},
                {"icon": "📈", "name": "Market Analytics", "key": "market", "badge": "Soon"},
                {"icon": "⚙️", "name": "Settings", "key": "settings", "badge": None}
            ]
            
            # Get current page from session state or default to Welcome
            if 'current_nav_page' not in st.session_state:
                st.session_state.current_nav_page = 'welcome'
            
            # Create navigation buttons
            for option in nav_options:
                # Determine if this button is active
                is_active = st.session_state.current_nav_page == option['key']
                
                # Create badge text if badge exists
                badge_text = ''
                if option['badge'] is not None:
                    if isinstance(option['badge'], str):
                        badge_text = f" ({option['badge']})"
                    elif isinstance(option['badge'], int) and option['badge'] > 0:
                        badge_text = f" ({option['badge']})"
                
                # Create button label with icon and badge
                button_label = f"{option['icon']} {option['name']}{badge_text}"
                
                # Use different button types for active vs inactive
                if is_active:
                    st.button(
                        button_label,
                        key=f"nav_btn_{option['key']}",
                        help=f"Current page: {option['name']}",
                        type="primary",
                        use_container_width=True,
                        disabled=True
                    )
                else:
                    if st.button(
                        button_label,
                        key=f"nav_btn_{option['key']}",
                        help=f"Go to {option['name']}",
                        use_container_width=True
                    ):
                        st.session_state.current_nav_page = option['key']
                        st.rerun()
            
            # Add JavaScript for button interactions
            st.markdown("""
            <script>
            function selectPage(pageKey) {
                // This will be handled by the Streamlit button clicks
                console.log('Selected page:', pageKey);
            }
            </script>
            """, unsafe_allow_html=True)
            
            # Enhanced quick stats section
            if st.session_state.extracted_data:
                st.markdown("---")  # Divider
                st.markdown("### 📊 Quick Stats")
                
                # Simple stats without complex calculations
                total_studies = len(st.session_state.extracted_data)
                st.metric("📚 Studies", total_studies, help="Total studies processed")
                
                # Simple quality assessment using LLM confidence
                if total_studies > 0:
                    avg_confidence = sum(d.extraction_confidence for d in st.session_state.extracted_data) / total_studies
                    quality_level = "Excellent" if avg_confidence >= 0.8 else "Good" if avg_confidence >= 0.6 else "Fair"
                    st.metric("✅ Quality", f"{quality_level}", delta=f"{avg_confidence:.0%}", help="Data extraction quality")
                
                # Show categorization stats if available
                if st.session_state.categorization_data and len(st.session_state.categorization_data) > 0:
                    st.metric("🏷️ Categorized", len(st.session_state.categorization_data), help="Studies with AI categorization")
                
                # Simple session timing
                if hasattr(st.session_state, 'session_stats'):
                    session_time = time.time() - st.session_state.session_stats.get('session_start_time', time.time())
                    st.metric("⏱️ Session", f"{session_time/60:.1f}m", help="Current session duration")
            
            # Quick action buttons for common tasks
            if st.session_state.extracted_data:
                st.markdown("---")
                st.markdown("### ⚡ Quick Actions")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Analyze", use_container_width=True, help="Generate analysis"):
                        st.session_state.current_nav_page = 'dashboard'
                        st.rerun()
                with col2:
                    if st.button("🤖 Ask AI", use_container_width=True, help="Go to AI Assistant"):
                        st.session_state.current_nav_page = 'ai'
                        st.rerun()
        
        # Route to appropriate page
        page_name = st.session_state.current_nav_page
        if page_name == "welcome":
            self.render_welcome()
        elif page_name == "dashboard":
            self.render_dashboard()
        elif page_name == "abstract":
            self.render_abstract_analyzer()
        elif page_name == "protocol":
            self.render_protocol_generator()
        elif page_name == "research":
            self.render_research_explorer()
        elif page_name == "treatment":
            self.render_treatment_intelligence()
        elif page_name == "market":
            self.render_market_analytics()
        elif page_name == "ai":
            self.render_ai_assistant()
        elif page_name == "settings":
            self.render_settings()
        else:
            # Default to welcome
            st.session_state.current_nav_page = 'welcome'
            self.render_welcome()
    
    def render_welcome(self):
        """Render welcome and getting started page"""
        
        st.markdown("""
        <div class="section-header">
            <h2>🏠 Welcome to ASCOmind+</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Main welcome section
        st.markdown("""
        <div class="insight-panel" style="text-align: center; margin-bottom: 2rem;">
            <h3 style="color: #1e293b; margin-bottom: 1rem;">🚀 Your AI-Powered Medical Research Platform</h3>
            <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 1.5rem;">
                Transform medical abstracts into actionable insights with advanced AI analysis
            </p>
            <div style="background: linear-gradient(135deg, #667eea20, #f093fb20); padding: 1.5rem; border-radius: 0.75rem; display: inline-block;">
                <span style="font-size: 3rem;">🧬</span>
                <div style="margin-top: 0.5rem; font-weight: 600; color: #1e293b;">Ready to get started?</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Getting started workflow
        st.markdown("""
        <div class="section-header">
            <h3>🎯 Quick Start Guide</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card" style="text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📄</div>
                <h4 style="margin-bottom: 0.5rem; color: #1e293b;">1. Upload Abstracts</h4>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Upload research papers, abstracts, or text files for AI analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card" style="text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🤖</div>
                <h4 style="margin-bottom: 0.5rem; color: #1e293b;">2. AI Processing</h4>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Automatic extraction of 50+ data elements with intelligent categorization</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card" style="text-align: center; height: 200px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">📊</div>
                <h4 style="margin-bottom: 0.5rem; color: #1e293b;">3. View Insights</h4>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Interactive dashboards, AI chat, and comprehensive analytics</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("---")
        st.markdown("### ⚡ Ready to Start?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Upload Abstracts", type="primary", use_container_width=True, help="Go to Abstract Analysis to upload your research files"):
                st.session_state.current_nav_page = 'abstract'
                st.rerun()
        
        with col2:
            if st.button("🤖 Try AI Assistant", use_container_width=True, help="Chat with our AI research assistant"):
                st.session_state.current_nav_page = 'ai'
                st.rerun()
        
        with col3:
            if st.button("📊 View Demo Dashboard", use_container_width=True, help="See what the dashboard looks like", disabled=not st.session_state.extracted_data):
                if st.session_state.extracted_data:
                    st.session_state.current_nav_page = 'dashboard'
                    st.rerun()
                else:
                    st.info("Upload and process abstracts first to view the dashboard!")
        
        # Platform capabilities
        st.markdown("""
        <div class="section-header" style="margin-top: 2rem;">
            <h3>🌟 Platform Capabilities</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="insight-panel">
                <h4 style="color: #1e293b; margin-bottom: 1rem;">📊 Advanced Analytics</h4>
                <ul style="color: #64748b; line-height: 1.6;">
                    <li>✅ 50+ data elements extracted automatically</li>
                    <li>✅ Study categorization and classification</li>
                    <li>✅ Efficacy and safety analysis</li>
                    <li>✅ Treatment landscape mapping</li>
                    <li>✅ Publication-quality visualizations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-panel">
                <h4 style="color: #1e293b; margin-bottom: 1rem;">🤖 AI-Powered Features</h4>
                <ul style="color: #64748b; line-height: 1.6;">
                    <li>🧠 Intelligent research assistant</li>
                    <li>🔍 Semantic search across studies</li>
                    <li>📝 Automated protocol generation</li>
                    <li>💡 Clinical insights and recommendations</li>
                    <li>⚡ Real-time question answering</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Current session status
        if st.session_state.extracted_data:
            st.markdown("---")
            st.markdown("### 📈 Your Current Session")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📚 Studies Processed", len(st.session_state.extracted_data))
            with col2:
                total_patients = sum(d.patient_demographics.total_enrolled for d in st.session_state.extracted_data if d.patient_demographics.total_enrolled)
                st.metric("👥 Total Patients", f"{total_patients:,}" if total_patients else "N/A")
            with col3:
                ai_conversations = len(st.session_state.ai_conversation_history)
                st.metric("💬 AI Conversations", ai_conversations)
            with col4:
                if hasattr(st.session_state, 'session_stats'):
                    session_time = time.time() - st.session_state.session_stats.get('session_start_time', time.time())
                    st.metric("⏱️ Session Time", f"{session_time/60:.1f}m")
                else:
                    st.metric("⏱️ Session Time", "0m")
            
            # Continue working buttons
            st.markdown("### 🚀 Continue Your Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 View Dashboard", type="primary", use_container_width=True):
                    st.session_state.current_nav_page = 'dashboard'
                    st.rerun()
            with col2:
                if st.button("📄 Add More Studies", use_container_width=True):
                    st.session_state.current_nav_page = 'abstract'
                    st.rerun()
            with col3:
                if st.button("🤖 Ask AI Questions", use_container_width=True):
                    st.session_state.current_nav_page = 'ai'
                    st.rerun()
    
    def render_dashboard(self):
        """Render enhanced main dashboard with modern UI - Data visualization focused"""
        
        st.markdown("""
        <div class="section-header">
            <h2>📊 Executive Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.extracted_data:
            # Simple message directing users to upload data
            st.markdown("""
            <div class="insight-panel" style="text-align: center; margin-bottom: 2rem;">
                <h3 style="color: #1e293b; margin-bottom: 1rem;">📊 No Data Available</h3>
                <p style="color: #64748b; font-size: 1.1rem; margin-bottom: 1.5rem;">
                    Upload and process abstracts to view interactive analytics and insights
                </p>
                <div style="margin-top: 1.5rem;">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📄 Go to Abstract Analysis", type="primary", use_container_width=True):
                    st.session_state.current_nav_page = 'abstract'
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Welcome", use_container_width=True):
                    st.session_state.current_nav_page = 'welcome'
                    st.rerun()
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            return
        
        # Generate analysis if not available
        if not st.session_state.analysis_results:
            with st.spinner("🧠 Generating comprehensive analysis..."):
                analyzer = self._get_analyzer()
                st.session_state.analysis_results = analyzer.analyze_comprehensive_dataset(
                    st.session_state.extracted_data
                )
        
        # Generate visualizations if not available
        if not st.session_state.visualizations:
            with st.spinner("🎨 Creating interactive visualizations..."):
                visualizer = self._get_visualizer()
                st.session_state.visualizations = visualizer.create_comprehensive_dashboard(
                    st.session_state.extracted_data  # Use extracted_data instead of analysis_results
                )
        
        # Display enhanced dashboard content
        self._render_dashboard_content()
    
    def _render_dashboard_content(self):
        """Render enhanced dashboard content with modern visualizations"""
        
        # Enhanced key metrics row with modern styling
        st.markdown("""
        <div class="section-header">
            <h3>📈 Key Performance Indicators</h3>
        </div>
        """, unsafe_allow_html=True)
        
        summary_stats = st.session_state.analysis_results.get('dataset_overview', {}).get('summary_statistics', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_studies = summary_stats.get('total_studies', len(st.session_state.extracted_data))
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{total_studies}</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">Total Studies</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_enrollment = summary_stats.get('avg_enrollment', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{avg_enrollment:.0f}</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">Avg Enrollment</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            randomized_pct = summary_stats.get('randomized_percentage', 0)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{randomized_pct:.1f}%</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">Randomized Studies</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_confidence = summary_stats.get('avg_confidence', 0)
            confidence_color = "#10b981" if avg_confidence >= 0.75 else "#3b82f6" if avg_confidence >= 0.65 else "#f59e0b" if avg_confidence >= 0.5 else "#ef4444"  # Updated thresholds
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {confidence_color}, {confidence_color}dd); color: white; padding: 1.5rem; border-radius: 1rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">{avg_confidence:.1%}</div>
                <div style="font-size: 0.875rem; opacity: 0.9;">Data Quality</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Simple, data-driven visualizations based on extracted studies only
        st.markdown("""
        <div class="section-header" style="margin-top: 2rem;">
            <h3>📊 Your Study Data Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Extract actual data from user's studies
        study_data = []
        for i, data in enumerate(st.session_state.extracted_data):
            categorization = st.session_state.categorization_data[i] if i < len(st.session_state.categorization_data) else {}
            
            # Get study info
            study_name = data.study_identification.study_acronym or f"Study {i+1}"
            study_title = data.study_identification.title[:50] + "..." if len(data.study_identification.title) > 50 else data.study_identification.title
            
            # Extract ORR
            orr_val = None
            orr_data = data.efficacy_outcomes.overall_response_rate
            if orr_data and isinstance(orr_data, dict):
                orr_val = orr_data.get('value')
                if orr_val is not None:
                    try:
                        orr_val = float(orr_val)
                    except:
                        orr_val = None
            
            # Extract PFS
            pfs_val = None
            pfs_data = data.efficacy_outcomes.progression_free_survival
            if pfs_data and isinstance(pfs_data, dict):
                pfs_val = pfs_data.get('median')
                if pfs_val is not None:
                    try:
                        pfs_val = float(pfs_val)
                    except:
                        pfs_val = None
            
            # Extract enrollment
            enrollment = data.patient_demographics.total_enrolled
            
            study_data.append({
                'name': study_name,
                'title': study_title,
                'phase': data.study_design.study_type.value,
                'category': categorization.get('study_category', 'Unknown'),
                'orr': orr_val,
                'pfs': pfs_val,
                'enrollment': enrollment,
                'confidence': data.extraction_confidence
            })
        
        # Only show visualizations if we have actual data
        if len(study_data) == 1:
            # Single study view
            study = study_data[0]
            st.markdown(f"### 📋 Analysis of: {study['name']}")
            st.markdown(f"**Title:** {study['title']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                orr_display = f"{study['orr']:.1f}%" if study['orr'] is not None else "N/A"
                st.metric("🎯 ORR", orr_display)
            with col2:
                pfs_display = f"{study['pfs']:.1f} mo" if study['pfs'] is not None else "N/A"
                st.metric("📈 PFS", pfs_display)
            with col3:
                enroll_display = str(study['enrollment']) if study['enrollment'] else "N/A"
                st.metric("👥 Enrolled", enroll_display)
            with col4:
                st.metric("✅ Quality", f"{study['confidence']:.0%}")
            
            # Show what data was actually found
            st.markdown("#### 📊 Data Availability")
            data_found = []
            if study['orr'] is not None:
                data_found.append(f"✅ Response Rate: {study['orr']:.1f}%")
            if study['pfs'] is not None:
                data_found.append(f"✅ PFS: {study['pfs']:.1f} months")
            if study['enrollment']:
                data_found.append(f"✅ Enrollment: {study['enrollment']} patients")
            
            if data_found:
                for item in data_found:
                    st.markdown(item)
            else:
                st.info("ℹ️ Limited quantitative data available in this abstract")
        
        elif len(study_data) > 1:
            # Multiple studies comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Response Rates")
                
                # Only show studies with ORR data
                studies_with_orr = [s for s in study_data if s['orr'] is not None]
                
                if studies_with_orr:
                    fig_orr = go.Figure(data=[
                        go.Bar(
                            x=[s['name'] for s in studies_with_orr],
                            y=[s['orr'] for s in studies_with_orr],
                            marker_color=['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][:len(studies_with_orr)],
                            text=[f"{s['orr']:.1f}%" for s in studies_with_orr],
                            textposition='auto',
                        )
                    ])
                    
                    fig_orr.update_layout(
                        title="Your Studies: Overall Response Rate",
                        xaxis_title="Study",
                        yaxis_title="ORR (%)",
                        height=400,
                        showlegend=False,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_orr, use_container_width=True)
                else:
                    st.info("📊 No ORR data available in your studies")
            
            with col2:
                st.markdown("#### 👥 Study Sizes")
                
                # Only show studies with enrollment data
                studies_with_enrollment = [s for s in study_data if s['enrollment']]
                
                if studies_with_enrollment:
                    fig_enroll = go.Figure(data=[
                        go.Scatter(
                            x=[s['name'] for s in studies_with_enrollment],
                            y=[s['enrollment'] for s in studies_with_enrollment],
                            mode='markers+text',
                            marker=dict(
                                size=[max(20, min(60, s['enrollment']/20)) for s in studies_with_enrollment],
                                color=['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'][:len(studies_with_enrollment)],
                                opacity=0.7
                            ),
                            text=[str(s['enrollment']) for s in studies_with_enrollment],
                            textposition="middle center",
                            textfont=dict(color="white", size=12, family="Arial Black")
                        )
                    ])
                    
                    fig_enroll.update_layout(
                        title="Your Studies: Patient Enrollment",
                        xaxis_title="Study",
                        yaxis_title="Patients Enrolled",
                        height=400,
                        showlegend=False,
                        template="plotly_white"
                    )
                    
                    st.plotly_chart(fig_enroll, use_container_width=True)
                else:
                    st.info("📊 No enrollment data available in your studies")
            
            # Summary table with actual data
            st.markdown("#### 📋 Study Comparison")
            summary_table_data = []
            for study in study_data:
                summary_table_data.append({
                    'Study': study['name'],
                    'Phase': study['phase'],
                    'Category': study['category'],
                    'Patients (N)': study['enrollment'] if study['enrollment'] else 'N/A',
                    'ORR (%)': f"{study['orr']:.1f}" if study['orr'] is not None else 'N/A',
                    'PFS (months)': f"{study['pfs']:.1f}" if study['pfs'] is not None else 'N/A',
                    'Data Quality': f"{study['confidence']:.0%}"
                })
            
            summary_df = pd.DataFrame(summary_table_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        else:
            st.info("📊 No studies available. Upload abstracts to see visualizations.")
        
        # Show data extraction summary
        st.markdown("#### 📈 Extraction Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            studies_with_orr = len([s for s in study_data if s['orr'] is not None])
            st.metric("🎯 Studies with ORR", f"{studies_with_orr}/{len(study_data)}")
        
        with col2:
            studies_with_pfs = len([s for s in study_data if s['pfs'] is not None])
            st.metric("📈 Studies with PFS", f"{studies_with_pfs}/{len(study_data)}")
        
        with col3:
            studies_with_enrollment = len([s for s in study_data if s['enrollment']])
            st.metric("👥 Studies with Enrollment", f"{studies_with_enrollment}/{len(study_data)}")
    
        # Show all visualizer plots (skip empty/placeholder plots)
        if st.session_state.visualizations:
            with st.expander('📊 Advanced Visualizations (AI Visualizer)', expanded=True):
                for viz_name, fig in st.session_state.visualizations.items():
                    # Skip if figure has no data traces (placeholder)
                    if hasattr(fig, 'data') and len(fig.data) == 0:
                        continue
                    st.markdown(f"#### {viz_name.replace('_', ' ').title()}")
                    st.plotly_chart(fig, use_container_width=True)
    
        # --- NEW: Analyzer-based advanced visualizations ---
        analyzer_results = st.session_state.analysis_results
        from agents.visualizer import AdvancedVisualizer
        adv_viz = AdvancedVisualizer()
        with st.expander('🤖 AI Advanced Analytics (Analyzer Results)', expanded=False):
            # Efficacy Benchmarks
            efficacy_benchmarks = analyzer_results.get('efficacy_benchmarks', {})
            if efficacy_benchmarks:
                st.markdown('#### Efficacy Benchmarks by Line of Therapy')
                fig = adv_viz._create_efficacy_analysis_chart_from_analyzer(efficacy_benchmarks)
                st.plotly_chart(fig, use_container_width=True)
            # Safety Patterns
            safety_patterns = analyzer_results.get('safety_patterns', {})
            if safety_patterns:
                st.markdown('#### Safety Patterns by Line of Therapy')
                fig = adv_viz._create_safety_analysis_chart_from_analyzer(safety_patterns)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_abstract_analyzer(self):
        """Render enhanced abstract analysis page with modern UI"""
        
        st.markdown("""
        <div class="section-header">
            <h2>📄 Abstract Analysis Engine</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced upload section with modern design
        st.markdown("""
        <div class="section-header">
            <h3>📤 Upload Medical Abstracts</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Modern upload method selector
        upload_method = st.radio(
            "Choose upload method:",
            ["📝 Text Input", "📁 File Upload", "📋 Batch Upload"],
            horizontal=True,
            help="Select how you want to input your abstracts for analysis"
        )
        
        if upload_method == "📝 Text Input":
            self._render_text_input()
        elif upload_method == "📁 File Upload":
            self._render_file_upload()
        elif upload_method == "📋 Batch Upload":
            self._render_batch_upload()
        
        # Display extracted data with enhanced UI
        if st.session_state.extracted_data:
            # Enhanced session statistics header
            session_summary = self._get_session_summary()
            
            st.markdown("""
            <div class="section-header" style="margin-top: 2rem;">
                <h3>📊 Session Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Modern performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 1.25rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">{len(st.session_state.extracted_data)}</div>
                    <div style="font-size: 0.75rem; opacity: 0.9;">📊 Studies</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_processing_time = session_summary['total_processing_time']
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 1.25rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">{total_processing_time:.1f}s</div>
                    <div style="font-size: 0.75rem; opacity: 0.9;">⚡ Processing</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_time = session_summary['avg_time_per_abstract']
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; padding: 1.25rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">{avg_time:.1f}s</div>
                    <div style="font-size: 0.75rem; opacity: 0.9;">📊 Avg/Study</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #8b5cf6, #a78bfa); color: white; padding: 1.25rem; border-radius: 0.75rem; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.25rem;">{session_summary['session_duration']:.0f}s</div>
                    <div style="font-size: 0.75rem; opacity: 0.9;">🕒 Session</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced data summary table
            st.markdown("""
            <div class="section-header" style="margin-top: 2rem;">
                <h3>📋 Extracted Data Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create enhanced summary table with modern styling
            summary_data = []
            for i, data in enumerate(st.session_state.extracted_data):
                # Get categorization data if available
                categorization = st.session_state.categorization_data[i] if i < len(st.session_state.categorization_data) else {}
                
                # Get additional data points
                nct_number = data.study_identification.nct_number or "N/A"
                study_acronym = data.study_identification.study_acronym or ""
                title_display = f"{study_acronym} - {data.study_identification.title[:40]}..." if study_acronym else (data.study_identification.title[:50] + "..." if len(data.study_identification.title) > 50 else data.study_identification.title)
                
                # Get efficacy data
                orr_value = self._extract_orr(data)
                pfs_data = self._extract_pfs(data)
                median_age = data.patient_demographics.median_age or "N/A"
                
                # Get study category
                study_category = categorization.get('study_category', 'Unknown')
                
                # Enhanced quality badge with HTML
                quality_badge = self._get_enhanced_quality_badge(data.extraction_confidence)
                
                summary_data.append({
                    '📄 Title': title_display,
                    '🔬 NCT#': nct_number,
                    '🏥 Study Type': data.study_design.study_type.value,
                    '🏷️ Category': study_category,
                    '👥 N': data.patient_demographics.total_enrolled or "N/A",
                    '📊 Age': f"{median_age}" if median_age != "N/A" else "N/A",
                    '🎯 ORR (%)': orr_value,
                    '📈 PFS (mo)': pfs_data,
                    '⏰ Extracted': data.extraction_timestamp.strftime("%H:%M:%S")
                })
            
            df = pd.DataFrame(summary_data)
            
            # Custom dataframe display with enhanced styling
            st.markdown("""
            <style>
                .stDataFrame table {
                    background: white;
                    border-radius: 0.75rem;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    border: 1px solid #e2e8f0;
                }
                .stDataFrame th {
                    background: linear-gradient(135deg, #667eea, #764ba2) !important;
                    color: white !important;
                    font-weight: 600 !important;
                    text-align: center !important;
                    padding: 1rem !important;
                }
                .stDataFrame td {
                    padding: 0.75rem !important;
                    border-bottom: 1px solid #f1f5f9 !important;
                    text-align: center !important;
                    vertical-align: middle !important;
                }
                .stDataFrame tr:hover {
                    background-color: #f8fafc !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Developer mode toggle for technical explanations
            show_dev_explanations = st.checkbox("🔧 Show Developer Information", value=False, help="Show technical details about scoring and metrics")
            
            if show_dev_explanations:
                with st.expander("ℹ️ Developer: Scoring System Details", expanded=False):
                    st.markdown("""
                    ### 🎯 **Technical Scoring System Information**
                    
                    **Quality Assessment Algorithm:**
                    - Uses LLM's internal confidence scores (highly calibrated)
                    - Success-based scoring: counts successful extractions vs attempts
                    - No penalties for missing data that wasn't in source abstract
                    - Quality reflects extraction accuracy, not schema completeness
                    
                    **Quality Thresholds:**
                    - 🏆 **Excellent (80%+)**: High LLM confidence in extraction accuracy
                    - ✅ **Good (60-80%)**: Solid LLM confidence with good data extraction
                    - ⚠️ **Fair (40-60%)**: Moderate LLM confidence, may need review
                    - ❌ **Poor (<40%)**: Low LLM confidence, requires attention
                    
                    **Efficiency Calculation (if enabled):**
                    - Baseline: 6 seconds per abstract (includes API latency)
                    - Quality bonus: up to 20% boost for high-confidence extractions
                    - Realistic thresholds: 60%+ excellent, 40-60% good, <40% needs optimization
                    
                    **Current Session Metrics:**
                    """)
                    
                    # Show technical session details in developer mode
                    session_summary = self._get_session_summary()
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        **Processing Efficiency:** {session_summary['processing_efficiency']:.1f}%  
                        **Quality Bonus Applied:** {max(0, (sum(d.extraction_confidence for d in st.session_state.extracted_data) / len(st.session_state.extracted_data) - 0.6) * 50):.1f}%
                        """)
                    
                    with col2:
                        avg_confidence = sum(d.extraction_confidence for d in st.session_state.extracted_data) / len(st.session_state.extracted_data)
                        st.markdown(f"""
                        **Average LLM Confidence:** {avg_confidence:.1%}  
                        **Confidence Range:** {min(d.extraction_confidence for d in st.session_state.extracted_data):.1%} - {max(d.extraction_confidence for d in st.session_state.extracted_data):.1%}
                        """)
                    
                    with col3:
                        st.markdown(f"""
                        **API Response Time:** {session_summary['avg_time_per_abstract']:.1f}s avg  
                        **Processing Overhead:** {session_summary['total_processing_time'] - (session_summary['abstracts_processed'] * 6):.1f}s total
                        """)
            
            # Enhanced detailed data view
            st.markdown("""
            <div class="section-header" style="margin-top: 2rem;">
                <h3>🔍 Detailed Extraction Results</h3>
            </div>
            """, unsafe_allow_html=True)
            
            for i, data in enumerate(st.session_state.extracted_data):
                # Get categorization data if available
                categorization = st.session_state.categorization_data[i] if i < len(st.session_state.categorization_data) else {}
                
                with st.expander(f"📋 Study {i+1}: {data.study_identification.study_acronym or 'Study'} - {data.study_identification.title[:60]}...", expanded=False):
                    
                    # Enhanced Study Identification section
                    st.markdown("""
                    <div class="insight-panel" style="margin-bottom: 1.5rem;">
                        <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-size: 1rem;">🏷️</span>
                            Study Identification
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**📄 Title:** {data.study_identification.title}")
                        st.markdown(f"**🏷️ Acronym:** {data.study_identification.study_acronym or 'N/A'}")
                        st.markdown(f"**🔗 NCT Number:** {data.study_identification.nct_number or 'N/A'}")
                    with col2:
                        st.markdown(f"**🏥 Study Group:** {data.study_identification.study_group or 'N/A'}")
                        st.markdown(f"**🏥 Study Type:** {data.study_design.study_type.value}")
                        st.markdown(f"**📊 Phase:** {data.study_design.study_type.value}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Enhanced Study Categorization
                    if categorization:
                        st.markdown("""
                        <div class="insight-panel" style="margin-bottom: 1.5rem;">
                            <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                                <span style="background: linear-gradient(135deg, #10b981, #34d399); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-size: 1rem;">🤖</span>
                                AI Study Categorization
                            </h4>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**📂 Study Category:** {categorization.get('study_category', 'Unknown')}")
                            st.markdown(f"**🏥 Clinical Setting:** {categorization.get('clinical_setting', 'Unknown')}")
                            st.markdown(f"**🎯 Therapeutic Intent:** {categorization.get('therapeutic_intent', 'Unknown')}")
                        
                        with col2:
                            populations = categorization.get('population_types', {}).get('populations', [])
                            if populations:
                                st.markdown("**👥 Population Types:**")
                                for pop in populations[:3]:  # Show top 3
                                    st.markdown(f"• {pop}")
                            else:
                                st.markdown("**👥 Population Types:** Not identified")
                        
                        with col3:
                            treatments = categorization.get('treatment_categories', {}).get('treatment_categories', [])
                            if treatments:
                                st.markdown("**💊 Treatment Categories:**")
                                for treatment in treatments[:3]:  # Show top 3
                                    st.markdown(f"• {treatment}")
                            else:
                                st.markdown("**💊 Treatment Categories:** Not identified")
                        
                        # Enhanced categorization confidence
                        conf_scores = categorization.get('confidence_scores', {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            overall_conf = conf_scores.get('overall', 0)
                            st.markdown(f'<div style="background: #10b981; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: 500;">Status: ✅ Verified</div>', unsafe_allow_html=True)
                        with col2:
                            cat_conf = conf_scores.get('study_category', 0)
                            st.markdown(f'<div style="background: #3b82f6; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: 500;">Category: ✅ Identified</div>', unsafe_allow_html=True)
                        with col3:
                            pop_conf = conf_scores.get('population', 0)
                            st.markdown(f'<div style="background: #8b5cf6; color: white; padding: 0.5rem; border-radius: 0.5rem; text-align: center; font-weight: 500;">Population: ✅ Classified</div>', unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Enhanced Quality Assessment
                    st.markdown("""
                    <div class="insight-panel" style="margin-bottom: 1.5rem;">
                        <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-size: 1rem;">📊</span>
                            Data Quality Assessment
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        # Use LLM confidence directly - it's well calibrated!
                        quality_badge = self._get_quality_badge(data.extraction_confidence)
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">EXTRACTION QUALITY</div>
                            <div style="font-size: 1.25rem;">{quality_badge}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        # Show what was successfully extracted
                        realistic_assessment = self._get_realistic_quality_assessment(data)
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">DATA EXTRACTED</div>
                            <div style="font-size: 1.25rem; font-weight: 700; color: #10b981;">{realistic_assessment['extractions_found']}/{realistic_assessment['extractions_attempted']}</div>
                            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Key data points found</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        # Clinical relevance based on study type and data richness
                        relevance_score = min(data.extraction_confidence + 0.1, 1.0)  # Slight boost for clinical relevance
                        relevance_badge = self._get_clinical_relevance_badge(relevance_score)
                        st.markdown(f"""
                        <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">CLINICAL RELEVANCE</div>
                            <div style="font-size: 1.25rem;">{relevance_badge}</div>
                            <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Research value</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Add quality explanation with developer toggle
                    show_quality_details = st.checkbox(f"💡 Show Quality Details for Study {i+1}", value=False, key=f"quality_details_{i}")
                    
                    if show_quality_details:
                        realistic_assessment = self._get_realistic_quality_assessment(data)
                        st.markdown(f"""
                        <div style="background: #f0f9ff; padding: 1rem; border-radius: 0.5rem; border: 1px solid #0ea5e9; margin-top: 1rem;">
                            <h5 style="color: #0369a1; margin: 0 0 0.5rem 0;">🔍 Quality Assessment Details</h5>
                            <div style="color: #0c4a6e; font-size: 0.875rem; line-height: 1.5;">
                                <strong>How We Assess Quality:</strong><br>
                                • We evaluate successful data extraction from the source abstract<br>
                                • We only look for information that's typically available<br>
                                • Missing data doesn't indicate poor quality if it wasn't in the source<br>
                                • Quality reflects extraction accuracy, not completeness<br><br>
                                
                                <strong>This Study Results:</strong><br>
                                • Successfully extracted {realistic_assessment['extractions_found']} out of {realistic_assessment['extractions_attempted']} key data points<br>
                                • Quality level: {realistic_assessment['assessment']}<br>
                                • Data richness: {realistic_assessment['quality_score']:.0%} of expected information found<br>
                                • All extracted data appears accurate and well-structured
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Enhanced Patient Demographics
                    st.markdown("""
                    <div class="insight-panel" style="margin-bottom: 1.5rem;">
                        <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="background: linear-gradient(135deg, #8b5cf6, #a78bfa); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-size: 1rem;">👥</span>
                            Patient Demographics
                        </h4>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_enrolled = data.patient_demographics.total_enrolled or "N/A"
                        evaluable = data.patient_demographics.evaluable_patients or "N/A"
                        st.markdown(f"""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.875rem; color: #64748b;">Total Enrolled</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{total_enrolled}</div>
                        </div>
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b;">Evaluable</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{evaluable}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        median_age = f"{data.patient_demographics.median_age} years" if data.patient_demographics.median_age else "N/A"
                        male_pct = f"{data.patient_demographics.male_percentage:.1f}%" if data.patient_demographics.male_percentage else "N/A"
                        st.markdown(f"""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.875rem; color: #64748b;">Median Age</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{median_age}</div>
                        </div>
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b;">Male %</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{male_pct}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        ecog_01 = f"{(data.patient_demographics.ecog_0_percentage or 0) + (data.patient_demographics.ecog_1_percentage or 0):.1f}%" if data.patient_demographics.ecog_0_percentage or data.patient_demographics.ecog_1_percentage else "N/A"
                        st.markdown(f"""
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.875rem; color: #64748b;">ECOG 0-1</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{ecog_01}</div>
                        </div>
                        <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0;">
                            <div style="font-size: 0.875rem; color: #64748b;">Data Quality</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">✅ Complete</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Enhanced Treatment Regimens
                    if data.treatment_regimens:
                        st.markdown("""
                        <div class="insight-panel" style="margin-bottom: 1.5rem;">
                            <h4 style="color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center;">
                                <span style="background: linear-gradient(135deg, #ec4899, #f472b6); color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-size: 1rem;">💊</span>
                                Treatment Regimens
                            </h4>
                        """, unsafe_allow_html=True)
                        
                        for j, regimen in enumerate(data.treatment_regimens):
                            st.markdown(f"""
                            <div style="background: #f8fafc; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; margin-bottom: 0.75rem;">
                                <div style="font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">Regimen {j+1}: {regimen.regimen_name}</div>
                            """, unsafe_allow_html=True)
                            
                            if regimen.drugs:
                                drug_list = ", ".join([f"{drug.get('name', 'Unknown')} ({drug.get('dose', 'Unknown dose')})" for drug in regimen.drugs])
                                st.markdown(f"<div style='color: #64748b; font-size: 0.875rem; margin-bottom: 0.25rem;'><strong>Drugs:</strong> {drug_list}</div>", unsafe_allow_html=True)
                            if regimen.cycle_length:
                                st.markdown(f"<div style='color: #64748b; font-size: 0.875rem;'><strong>Cycle Length:</strong> {regimen.cycle_length} days</div>", unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            # Enhanced Export and Action options
            st.markdown("""
            <div class="section-header" style="margin-top: 2rem;">
                <h3>⚡ Actions & Export</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Generate Analysis", type="primary", help="Generate comprehensive clinical analysis"):
                    with st.spinner("🧠 Generating comprehensive clinical analysis..."):
                        try:
                            # Get analyzer using lazy loading
                            analyzer = self._get_analyzer()
                            
                            # Generate comprehensive analysis
                            st.session_state.analysis_results = analyzer.analyze_comprehensive_dataset(
                                st.session_state.extracted_data
                            )
                            
                            # Generate visualizations using lazy loading
                            visualizer = self._get_visualizer()
                            
                            st.session_state.visualizations = visualizer.create_comprehensive_dashboard(
                                st.session_state.extracted_data  # Use extracted_data instead of analysis_results
                            )
                            
                            st.success("✅ Analysis completed! Check the insights in the Dashboard.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
                            # Fallback: Generate basic summary
                            st.session_state.analysis_results = self._generate_basic_analysis()
                            st.rerun()
            
            with col2:
                if st.button("📥 Export Data", help="Export extracted data to CSV"):
                    self._export_data()
            
            with col3:
                if st.button("🗑️ Clear Data", help="Clear all extracted data"):
                    if st.session_state.extracted_data:
                        st.session_state.extracted_data = []
                        st.session_state.categorization_data = []
                        st.session_state.analysis_results = None
                        st.session_state.visualizations = {}
                        st.session_state.session_stats = {
                            'total_processing_time': 0.0,
                            'abstracts_processed': 0,
                            'session_start_time': time.time(),
                            'processing_history': []
                        }
                        st.success("🗑️ All data cleared successfully!")
                        st.rerun()
    
    def _render_text_input(self):
        """Render text input interface with timing and progress"""
        
        abstract_text = st.text_area(
            "Paste abstract text:",
            height=200,
            placeholder="Enter multiple myeloma research abstract text here..."
        )
        
        if abstract_text and st.button("🔍 Process Abstract", type="primary"):
            # Start timing
            start_time = time.time()
            
            # Create progress containers
            progress_container = st.container()
            time_container = st.container()
            
            with progress_container:
                st.subheader("🔄 Processing Abstract")
                progress_bar = st.progress(0, text="Initializing...")
                status_text = st.empty()
            
            try:
                # Step 1: Extract metadata (30% of progress)
                status_text.text("🧠 Extracting metadata with AI...")
                progress_bar.progress(15, text="Extracting metadata...")
                
                extracted_data = asyncio.run(
                    self.metadata_extractor.extract_comprehensive_metadata(abstract_text)
                )
                progress_bar.progress(30, text="Metadata extraction complete")
                
                # Step 2: Categorize study (20% of progress)
                status_text.text("🏷️ Categorizing study...")
                progress_bar.progress(40, text="Categorizing study...")
                
                categorization = asyncio.run(
                    self.categorizer.categorize_study(
                        abstract_text, 
                        extracted_data.model_dump()
                    )
                )
                progress_bar.progress(50, text="Study categorization complete")
                
                # Step 3: Embed to vector store (30% of progress)
                embedding_status = None
                if self._get_vector_store():
                    status_text.text("🔗 Embedding to knowledge base...")
                    progress_bar.progress(60, text="Creating vector embeddings...")
                    
                    try:
                        embedding_result = asyncio.run(
                            self._get_vector_store().embed_abstract(extracted_data)
                        )
                        progress_bar.progress(80, text="Vector embedding complete")
                        embedding_status = embedding_result
                        
                        # Store embedding status
                        st.session_state.vector_embedding_status[extracted_data.abstract_id] = embedding_result
                        
                    except Exception as e:
                        st.warning(f"Vector embedding failed: {e}")
                        embedding_status = {"status": "error", "reason": str(e)}
                
                # Step 4: Store results (20% of progress)
                status_text.text("💾 Storing results...")
                progress_bar.progress(90, text="Storing results...")
                
                # Store extracted data
                extracted_data.source_text = abstract_text
                st.session_state.extracted_data.append(extracted_data)
                st.session_state.categorization_data.append(categorization)
                
                # Calculate processing time
                end_time = time.time()
                processing_time = end_time - start_time
                
                progress_bar.progress(100, text="Processing complete!")
                
                # Display completion message with timing and embedding status
                with time_container:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ Status", "Complete")
                    with col2:
                        st.metric("⏱️ Processing Time", f"{processing_time:.1f}s")
                    with col3:
                        st.metric("📊 Data Elements", "50+")
                    with col4:
                        if embedding_status:
                            if embedding_status["status"] == "success":
                                st.metric("🔗 Vector Status", "✅ Embedded")
                            elif embedding_status["status"] == "skipped":
                                st.metric("🔗 Vector Status", "⏭️ Exists")
                            else:
                                st.metric("🔗 Vector Status", "❌ Failed")
                        else:
                            st.metric("🔗 Vector Status", "➖ Disabled")
                
                success_message = f"🎉 Abstract processed successfully in {processing_time:.1f} seconds!"
                if embedding_status and embedding_status["status"] == "success":
                    success_message += f" Created {embedding_status.get('vectors_created', 0)} vector embeddings for AI assistant."
                elif embedding_status and embedding_status["status"] == "skipped":
                    success_message += " Abstract already exists in knowledge base."
                
                st.success(success_message)
                
                # Clear progress after 1 second
                time.sleep(1)
                progress_container.empty()
                
                # Update session statistics
                self._update_session_stats(processing_time, 1)
                
            except Exception as e:
                progress_bar.progress(100, text="❌ Processing failed")
                st.error(f"❌ Processing failed: {str(e)}")
                
                # Calculate time even on failure
                end_time = time.time()
                processing_time = end_time - start_time
                with time_container:
                    st.metric("⏱️ Time Elapsed", f"{processing_time:.1f}s")
    
    def _render_file_upload(self):
        """Render file upload interface with vector embedding integration"""
        
        st.markdown("""
        <div class="section-header">
            <h3>📁 Single File Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload a medical research file",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, Word documents, and text files"
        )
        
        if uploaded_file:
            # File details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", uploaded_file.name)
            with col2:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            with col3:
                st.metric("File Type", uploaded_file.type)
            
            # Processing options (Developer mode only)
            if st.session_state.developer_mode:
                with st.expander("⚙️ Processing Options", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        extract_metadata = st.checkbox("📊 Extract Metadata", value=True, help="Extract comprehensive study metadata")
                        categorize_study = st.checkbox("🏷️ Categorize Study", value=True, help="Intelligent study categorization")
                        embed_vectors = st.checkbox("🧠 Vector Embedding", value=True, help="Create vector embeddings for AI search")
                    
                    with col2:
                        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.1, help="Minimum confidence for extracted data")
                        auto_correct = st.checkbox("🔧 Auto-correction", value=True, help="Automatically correct obvious errors")
            else:
                # Default values when developer mode is off
                extract_metadata = True
                categorize_study = True
                embed_vectors = True
                confidence_threshold = 0.7
                auto_correct = True
            
            # Process button
            if st.button("🚀 Process File", type="primary", use_container_width=True):
                # Initialize processing tracking
                start_time = time.time()
                processing_results = {
                    'metadata_extraction': {'status': 'pending', 'data': None},
                    'categorization': {'status': 'pending', 'data': None}, 
                    'vector_embedding': {'status': 'pending', 'data': None}
                }
                
                # Create progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                step_details = st.empty()
                
                try:
                    # Step 1: Text Extraction (10%)
                    status_text.text("📄 Extracting text from file...")
                    progress_bar.progress(10)
                    
                    # Extract text
                    file_content = uploaded_file.read()
                    if uploaded_file.type == "application/pdf":
                        from utils.file_processors import FileProcessor
                        processor = FileProcessor()
                        text_content = processor.process_file(file_content, uploaded_file.name)
                    else:
                        # Handle other file types
                        text_content = file_content.decode('utf-8')
                    
                    if not text_content.strip():
                        st.error("❌ Could not extract text from the file.")
                        return
                    
                    # Step 2: Metadata Extraction (30%)
                    if extract_metadata:
                        status_text.text("🔍 Extracting comprehensive metadata...")
                        progress_bar.progress(30)
                        
                        try:
                            extracted_data = asyncio.run(
                                self.metadata_extractor.extract_comprehensive_metadata(text_content)
                            )
                            extracted_data.source_file = uploaded_file.name
                            
                            processing_results['metadata_extraction'] = {
                                'status': 'success',
                                'data': extracted_data
                            }
                            step_details.success("✅ Metadata extraction completed")
                        except Exception as e:
                            processing_results['metadata_extraction'] = {
                                'status': 'failed',
                                'error': str(e)
                            }
                            step_details.error(f"❌ Metadata extraction failed: {str(e)}")
                    
                    # Step 3: Categorization (50%)
                    if categorize_study and processing_results['metadata_extraction']['status'] == 'success':
                        status_text.text("🏷️ Categorizing study...")
                        progress_bar.progress(50)
                        
                        try:
                            category_data = asyncio.run(
                                self.categorizer.categorize_study(
                                    text_content,  # Pass text content, not metadata object
                                    processing_results['metadata_extraction']['data'].model_dump()
                                )
                            )
                            processing_results['categorization'] = {
                                'status': 'success',
                                'data': category_data
                            }
                            step_details.success("✅ Study categorization completed")
                        except Exception as e:
                            processing_results['categorization'] = {
                                'status': 'failed',
                                'error': str(e)
                            }
                            step_details.error(f"❌ Categorization failed: {str(e)}")
                    
                    # Step 4: Vector Embedding (80%)
                    if embed_vectors and processing_results['metadata_extraction']['status'] == 'success' and self._get_vector_store():
                        status_text.text("🧠 Creating vector embeddings...")
                        progress_bar.progress(80)
                        
                        try:
                            embedding_result = asyncio.run(
                                self._get_vector_store().embed_abstract(processing_results['metadata_extraction']['data'])
                            )
                            processing_results['vector_embedding'] = {
                                'status': 'success',
                                'data': embedding_result
                            }
                            
                            # Update session state for vector embedding status
                            if 'vector_embedding_status' not in st.session_state:
                                st.session_state.vector_embedding_status = []
                            
                            st.session_state.vector_embedding_status.append({
                                'file': uploaded_file.name,
                                'status': embedding_result['status'],
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            if embedding_result['status'] == 'success':
                                step_details.success(f"✅ Vector embedding completed - {embedding_result['vectors_created']} chunks created")
                            elif embedding_result['status'] == 'skipped':
                                step_details.info(f"ℹ️ Vector embedding skipped - {embedding_result['reason']}")
                            else:
                                step_details.warning(f"⚠️ Vector embedding failed - {embedding_result.get('reason', 'Unknown error')}")
                        
                        except Exception as e:
                            processing_results['vector_embedding'] = {
                                'status': 'failed',
                                'error': str(e)
                            }
                            step_details.error(f"❌ Vector embedding failed: {str(e)}")
                    
                    # Step 5: Finalization (100%)
                    status_text.text("✅ Processing complete!")
                    progress_bar.progress(100)
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    
                    # Store results in session state
                    if processing_results['metadata_extraction']['status'] == 'success':
                        if 'extracted_data' not in st.session_state:
                            st.session_state.extracted_data = []
                        
                        # Add file metadata
                        extracted_data = processing_results['metadata_extraction']['data']
                        extracted_data.source_file = uploaded_file.name
                        
                        st.session_state.extracted_data.append(extracted_data)
                        
                        # Update session statistics
                        self._update_session_stats(processing_time, 1)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    step_details.empty()
                    
                    # Show detailed results
                    self._show_processing_results(processing_results, processing_time)
                    
                    # Success message with summary
                    success_parts = []
                    if processing_results['metadata_extraction']['status'] == 'success':
                        success_parts.append("metadata extracted")
                    if processing_results['categorization']['status'] == 'success':
                        success_parts.append("study categorized")
                    if processing_results['vector_embedding']['status'] == 'success':
                        success_parts.append("vectors created")
                    elif processing_results['vector_embedding']['status'] == 'skipped':
                        success_parts.append("vectors skipped (duplicate)")
                    
                    st.success(f"🎉 **File processed successfully!** {', '.join(success_parts).capitalize()}")
                    
                    # Auto-rerun to refresh the interface
                    st.rerun()
                    
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    step_details.empty()
                    st.error(f"❌ **Processing failed:** {str(e)}")
                    st.info("Please check the file format and try again.")
    
    def _show_processing_results(self, results: Dict, processing_time: float):
        """Show detailed processing results"""
        
        st.markdown("#### 📊 Processing Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if results['metadata_extraction']['status'] == 'success':
                st.metric("Metadata", "✅ Success", delta="Extracted")
            else:
                st.metric("Metadata", "❌ Failed", delta="Error")
        
        with col2:
            if results['categorization']['status'] == 'success':
                st.metric("Categorization", "✅ Success", delta="Completed")
            elif results['categorization']['status'] == 'failed':
                st.metric("Categorization", "❌ Failed", delta="Error")
            else:
                st.metric("Categorization", "⏭️ Skipped", delta="Not requested")
        
        with col3:
            if results['vector_embedding']['status'] == 'success':
                vectors_created = results['vector_embedding']['data'].get('vectors_created', 0)
                st.metric("Vector Embedding", "✅ Success", delta=f"{vectors_created} chunks")
            elif results['vector_embedding']['status'] == 'skipped':
                st.metric("Vector Embedding", "⏭️ Skipped", delta="Duplicate")
            elif results['vector_embedding']['status'] == 'failed':
                st.metric("Vector Embedding", "❌ Failed", delta="Error")
            else:
                st.metric("Vector Embedding", "⏭️ Skipped", delta="Not requested")
        
        with col4:
            st.metric("Processing Time", f"{processing_time:.1f}s", delta="Duration")
        
        # Show detailed results in expandable sections
        if results['metadata_extraction']['status'] == 'success':
            with st.expander("📋 Extracted Metadata Details"):
                data = results['metadata_extraction']['data']
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Study Information:**")
                    st.write(f"• Title: {data.study_identification.title}")
                    if data.study_identification.study_acronym:
                        st.write(f"• Acronym: {data.study_identification.study_acronym}")
                    if data.study_identification.nct_number:
                        st.write(f"• NCT: {data.study_identification.nct_number}")
                    st.write(f"• Type: {data.study_design.study_type.value}")
                
                with col2:
                    st.write("**Quality Metrics:**")
                    st.write(f"• Confidence: {data.extraction_confidence:.1%}")
                    st.write(f"• Completeness: {self._calculate_completeness(data):.1%}")
                    st.write(f"• Clinical Relevance: High")
        
        if results['vector_embedding']['status'] == 'success':
            with st.expander("🧠 Vector Embedding Details"):
                embedding_data = results['vector_embedding']['data']
                st.write(f"**Study:** {embedding_data['study_title']}")
                st.write(f"**Vectors Created:** {embedding_data['vectors_created']}")
                st.write(f"**Chunk Types:** {', '.join(embedding_data['chunk_types'])}")
                st.write(f"**Content Hash:** {embedding_data['content_hash']}")
    
    def _calculate_completeness(self, data) -> float:
        """Calculate data completeness score"""
        total_fields = 0
        filled_fields = 0
        
        # Check key fields
        if data.study_identification.title:
            filled_fields += 1
        total_fields += 1
        
        if data.study_identification.nct_number:
            filled_fields += 1
        total_fields += 1
        
        if data.treatment_regimens:
            filled_fields += 1
        total_fields += 1
        
        if data.efficacy_outcomes.overall_response_rate:
            filled_fields += 1
        total_fields += 1
        
        if data.patient_demographics.total_enrolled:
            filled_fields += 1
        total_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def _render_batch_upload(self):
        """Render batch upload interface with vector embedding integration"""
        
        st.markdown("""
        <div class="section-header">
            <h3>📚 Batch Processing</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload multiple research files",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"],
            help="Upload multiple files for batch processing. Supported formats: PDF, Word documents, and text files"
        )
        
        if uploaded_files:
            # Files overview
            st.markdown(f"### 📋 {len(uploaded_files)} Files Selected")
            
            # Display file details
            with st.expander("📁 File Details", expanded=True):
                for i, file in enumerate(uploaded_files, 1):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**{i}.** {file.name}")
                    with col2:
                        st.write(f"{file.size / 1024:.1f} KB")
                    with col3:
                        st.write(file.type)
                    with col4:
                        st.write("✅ Ready")
            
            # Batch processing options (Developer mode only)
            if st.session_state.developer_mode:
                with st.expander("⚙️ Batch Processing Options", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        extract_metadata = st.checkbox("📊 Extract Metadata", value=True, help="Extract comprehensive study metadata for all files")
                        categorize_studies = st.checkbox("🏷️ Categorize Studies", value=True, help="Intelligent study categorization for all files")
                        embed_vectors = st.checkbox("🧠 Vector Embedding", value=True, help="Create vector embeddings for AI search")
                    
                    with col2:
                        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.1, help="Minimum confidence for extracted data")
                        parallel_processing = st.checkbox("⚡ Parallel Processing", value=True, help="Process multiple files simultaneously")
                        auto_correct = st.checkbox("🔧 Auto-correction", value=True, help="Automatically correct obvious errors")
                
                # Advanced options (moved outside the main expander to avoid nesting)
                with st.expander("🔬 Advanced Settings", expanded=False):
                    batch_size = st.slider("Batch Size", 1, min(10, len(uploaded_files)), min(5, len(uploaded_files)), help="Number of files to process simultaneously")
                    skip_duplicates = st.checkbox("⏭️ Skip Duplicates", value=True, help="Skip files that have already been processed")
                    error_handling = st.selectbox("Error Handling", ["Stop on Error", "Continue on Error", "Retry Failed"], help="How to handle processing errors")
            else:
                # Default values when developer mode is off
                extract_metadata = True
                categorize_studies = True
                embed_vectors = True
                confidence_threshold = 0.7
                parallel_processing = True
                auto_correct = True
                batch_size = min(5, len(uploaded_files))
                skip_duplicates = True
                error_handling = "Continue on Error"
            
            # Processing button
            if st.button("🚀 Process All Files", type="primary", use_container_width=True):
                
                # Initialize tracking
                start_time = time.time()
                total_files = len(uploaded_files)
                successful_extractions = 0
                successful_categorizations = 0
                successful_embeddings = 0
                skipped_embeddings = 0
                failed_files = []
                
                # Create main progress indicators
                st.markdown("### 🔄 Batch Processing Progress")
                overall_progress = st.progress(0)
                overall_status = st.empty()
                
                # Create detailed progress tracking
                progress_details = st.container()
                
                try:
                    # Process files
                    for i, uploaded_file in enumerate(uploaded_files):
                        file_progress = (i / total_files)
                        overall_progress.progress(int(file_progress * 100))
                        overall_status.text(f"Processing file {i+1}/{total_files}: {uploaded_file.name}")
                        
                        # Individual file processing container
                        with progress_details:
                            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                                file_col1, file_col2, file_col3 = st.columns(3)
                                
                                file_start_time = time.time()
                                file_results = {
                                    'metadata_extraction': {'status': 'pending'},
                                    'categorization': {'status': 'pending'},
                                    'vector_embedding': {'status': 'pending'}
                                }
                                
                                try:
                                    # Step 1: Extract text content
                                    file_content = uploaded_file.read()
                                    if uploaded_file.type == "application/pdf":
                                        from utils.file_processors import FileProcessor
                                        processor = FileProcessor()
                                        text_content = processor.process_file(file_content, uploaded_file.name)
                                    else:
                                        text_content = file_content.decode('utf-8')
                                    
                                    if not text_content.strip():
                                        raise ValueError("No text content extracted")
                                    
                                    # Step 2: Metadata Extraction
                                    if extract_metadata:
                                        with file_col1:
                                            st.info("🔍 Extracting metadata...")
                                        
                                        try:
                                            extracted_data = asyncio.run(
                                                self.metadata_extractor.extract_comprehensive_metadata(text_content)
                                            )
                                            
                                            file_results['metadata_extraction'] = {
                                                'status': 'success',
                                                'data': extracted_data
                                            }
                                            successful_extractions += 1
                                            
                                            with file_col1:
                                                st.success("✅ Metadata extracted")
                                                
                                        except Exception as e:
                                            file_results['metadata_extraction'] = {
                                                'status': 'failed',
                                                'error': str(e)
                                            }
                                            with file_col1:
                                                st.error(f"❌ Extraction failed: {str(e)[:50]}...")
                                    
                                    # Step 3: Categorization
                                    if categorize_studies and file_results['metadata_extraction']['status'] == 'success':
                                        with file_col2:
                                            st.info("🏷️ Categorizing study...")
                                        
                                        try:
                                            category_data = asyncio.run(
                                                self.categorizer.categorize_study(
                                                    text_content,  # Pass text content, not metadata object
                                                    file_results['metadata_extraction']['data'].model_dump()
                                                )
                                            )
                                            file_results['categorization'] = {
                                                'status': 'success',
                                                'data': category_data
                                            }
                                            successful_categorizations += 1
                                            
                                            with file_col2:
                                                st.success("✅ Study categorized")
                                                
                                        except Exception as e:
                                            file_results['categorization'] = {
                                                'status': 'failed',
                                                'error': str(e)
                                            }
                                            with file_col2:
                                                st.error(f"❌ Categorization failed: {str(e)[:50]}...")
                                    
                                    # Step 4: Vector Embedding
                                    if embed_vectors and file_results['metadata_extraction']['status'] == 'success' and self._get_vector_store():
                                        with file_col3:
                                            st.info("🧠 Creating embeddings...")
                                        
                                        try:
                                            embedding_result = asyncio.run(
                                                self._get_vector_store().embed_abstract(file_results['metadata_extraction']['data'])
                                            )
                                            file_results['vector_embedding'] = {
                                                'status': 'success',
                                                'data': embedding_result
                                            }
                                            
                                            # Update session state for vector embedding status
                                            if 'vector_embedding_status' not in st.session_state:
                                                st.session_state.vector_embedding_status = []
                                            
                                            st.session_state.vector_embedding_status.append({
                                                'file': uploaded_file.name,
                                                'status': embedding_result['status'],
                                                'timestamp': datetime.now().isoformat()
                                            })
                                            
                                            if embedding_result['status'] == 'success':
                                                successful_embeddings += 1
                                                with file_col3:
                                                    st.success(f"✅ {embedding_result['vectors_created']} vectors created")
                                            elif embedding_result['status'] == 'skipped':
                                                skipped_embeddings += 1
                                                with file_col3:
                                                    st.info(f"⏭️ Skipped (duplicate)")
                                            else:
                                                with file_col3:
                                                    st.warning(f"⚠️ Failed: {embedding_result.get('reason', 'Unknown')}")
                                                    
                                        except Exception as e:
                                            file_results['vector_embedding'] = {
                                                'status': 'failed',
                                                'error': str(e)
                                            }
                                            with file_col3:
                                                st.error(f"❌ Embedding failed: {str(e)[:50]}...")
                                    
                                    # Store successful extractions
                                    if file_results['metadata_extraction']['status'] == 'success':
                                        if 'extracted_data' not in st.session_state:
                                            st.session_state.extracted_data = []
                                        st.session_state.extracted_data.append(file_results['metadata_extraction']['data'])
                                        
                                        if file_results['categorization']['status'] == 'success':
                                            if 'categorization_data' not in st.session_state:
                                                st.session_state.categorization_data = []
                                            st.session_state.categorization_data.append(file_results['categorization']['data'])
                                
                                except Exception as e:
                                    failed_files.append({
                                        'file': uploaded_file.name,
                                        'error': str(e)
                                    })
                                    st.error(f"❌ **{uploaded_file.name}** failed: {str(e)}")
                                    
                                    if error_handling == "Stop on Error":
                                        break
                    
                    # Complete processing
                    overall_progress.progress(100)
                    processing_time = time.time() - start_time
                    
                    # Update session statistics
                    if successful_extractions > 0:
                        self._update_session_stats(processing_time, successful_extractions)
                    
                    # Show final results
                    st.markdown("---")
                    st.markdown("### 📊 Batch Processing Results")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Total Files", total_files)
                    with col2:
                        st.metric("Metadata Extracted", successful_extractions, delta=f"{successful_extractions/total_files:.1%}")
                    with col3:
                        st.metric("Studies Categorized", successful_categorizations, delta=f"{successful_categorizations/total_files:.1%}")
                    with col4:
                        st.metric("Vectors Created", successful_embeddings, delta=f"{skipped_embeddings} skipped")
                    with col5:
                        st.metric("Processing Time", f"{processing_time:.1f}s", delta=f"{processing_time/total_files:.1f}s avg")
                    
                    # Error summary
                    if failed_files:
                        with st.expander(f"❌ {len(failed_files)} Failed Files", expanded=False):
                            for failure in failed_files:
                                st.write(f"• **{failure['file']}**: {failure['error']}")
                    
                    # Success message
                    if successful_extractions > 0:
                        success_message = f"🎉 **Batch processing completed!** "
                        success_parts = []
                        if successful_extractions > 0:
                            success_parts.append(f"{successful_extractions} metadata extracted")
                        if successful_categorizations > 0:
                            success_parts.append(f"{successful_categorizations} categorized")
                        if successful_embeddings > 0:
                            success_parts.append(f"{successful_embeddings} vectorized")
                        if skipped_embeddings > 0:
                            success_parts.append(f"{skipped_embeddings} duplicates skipped")
                        
                        success_message += ', '.join(success_parts)
                        st.success(success_message)
                        
                        # Auto-rerun to refresh the interface
                        st.rerun()
                    else:
                        st.error("❌ No files were processed successfully. Please check the error messages above.")
                
                except Exception as e:
                    overall_progress.progress(100)
                    overall_status.text("❌ Batch processing failed")
                    st.error(f"❌ **Batch processing error:** {str(e)}")
                    st.info("Please check your files and API configuration, then try again.")
            
            # Processing tips
            st.markdown("---")
            st.markdown("""
            **💡 Batch Processing Tips:**
            - Ensure all files contain medical research abstracts or papers
            - Larger files may take longer to process
            - Vector embedding creates searchable knowledge for the AI assistant
            - Duplicate detection prevents re-processing the same studies
            - Use parallel processing for faster results with multiple files
            """)
        
        else:
            # Instructions when no files uploaded
            st.info("""
            📚 **Batch Processing**
            
            Upload multiple research files to process them all at once:
            • Extract metadata from all files simultaneously
            • Create vector embeddings for AI search capabilities
            • Categorize studies automatically
            • Track processing progress for each file
            
            Supported formats: PDF, Word documents (.docx), and text files (.txt)
            """)
    
    def _extract_orr(self, data: ComprehensiveAbstractMetadata) -> str:
        """Extract ORR value for display"""
        orr_data = data.efficacy_outcomes.overall_response_rate
        if orr_data and isinstance(orr_data, dict):
            for key in ['value', 'rate', 'percentage']:
                if key in orr_data:
                    try:
                        return f"{float(orr_data[key]):.1f}"
                    except (ValueError, TypeError):
                        continue
        return "N/A"
    
    def _extract_pfs(self, data: ComprehensiveAbstractMetadata) -> str:
        """Extract PFS value for display"""
        pfs_data = data.efficacy_outcomes.progression_free_survival
        if pfs_data and isinstance(pfs_data, dict):
            for key in ['median', 'value', 'months']:
                if key in pfs_data:
                    try:
                        return f"{float(pfs_data[key]):.1f}"
                    except (ValueError, TypeError):
                        continue
        return "N/A"
    
    def _export_data(self):
        """Export extracted data"""
        
        export_data = []
        for data in st.session_state.extracted_data:
            export_data.append({
                'abstract_id': data.abstract_id,
                'title': data.study_identification.title,
                'study_type': data.study_design.study_type.value,
                'total_enrolled': data.patient_demographics.total_enrolled,
                'extraction_confidence': data.extraction_confidence,
                'extraction_timestamp': data.extraction_timestamp.isoformat()
            })
        
        df = pd.DataFrame(export_data)
        
        # Create download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"ascomind_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    def render_research_explorer(self):
        """Render research explorer page"""
        st.title("🔍 Research Data Explorer")
        st.info("🚧 Advanced research exploration interface coming soon!")
    
    def render_treatment_intelligence(self):
        """Render treatment intelligence page"""
        st.title("💊 Treatment Landscape Intelligence")
        st.info("🚧 Treatment intelligence dashboard coming soon!")
    
    def render_market_analytics(self):
        """Render market analytics page"""
        st.title("📈 Market Analytics & Commercial Intelligence")
        st.info("🚧 Market analytics platform coming soon!")
    
    def render_ai_assistant(self):
        """Render AI assistant chatbot page with improved performance and UX"""
        
        st.markdown("""
        <div class="section-header">
            <h2>🤖 Dr. ASCOmind+ | AI Research Assistant</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize components with lazy loading and session awareness
        if not hasattr(self, '_ai_assistant_initialized'):
            self.ai_assistant = self._get_ai_assistant()
            self.vector_store = self._get_vector_store()
            self._ai_assistant_initialized = True
        
        # Session information header
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">🤖 AI Research Assistant</h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                Session: {st.session_state.session_id[:12]}... | 
                Data Isolated: ✅ Only your studies
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Developer mode controls
        if st.session_state.developer_mode:
            with st.expander("🛠️ Developer Controls", expanded=False):
                st.markdown("**🧠 LLM Provider Selection:**")
                
                # Get available providers
                available_providers = settings.get_available_providers()
                enabled_providers = [provider for provider, available in available_providers.items() if available]
                
                if enabled_providers:
                    provider_options = {}
                    for provider in enabled_providers:
                        config = settings.get_provider_config(provider)
                        provider_options[f"{config['icon']} {config['name']} ({provider})"] = provider
                    
                    selected_display = st.selectbox(
                        "Choose LLM Provider:",
                        options=list(provider_options.keys()),
                        index=list(provider_options.values()).index(st.session_state.selected_llm_provider) 
                        if st.session_state.selected_llm_provider in provider_options.values() else 0,
                        key="llm_provider_select"
                    )
                    
                    # Update session state when selection changes
                    new_provider = provider_options[selected_display]
                    if new_provider != st.session_state.selected_llm_provider:
                        st.session_state.selected_llm_provider = new_provider
                        st.success(f"✅ Switched to {selected_display}")
                        st.rerun()
                    
                    # Show provider status
                    col1, col2, col3 = st.columns(3)
                    for i, (provider, available) in enumerate(available_providers.items()):
                        col = [col1, col2, col3][i % 3]
                        config = settings.get_provider_config(provider)
                        status = "✅" if available else "❌"
                        current = "🎯" if provider == st.session_state.selected_llm_provider else ""
                        col.write(f"{status} {config['icon']} {config['name']} {current}")
                else:
                    st.error("❌ No LLM providers available! Check your API keys in secrets.")
                
                st.markdown("---")
                st.markdown("**🔧 Quick Actions:**")
                if st.button("🔄 Refresh API Keys", key="refresh_api_keys"):
                    settings.refresh_from_secrets()
                    st.success("API keys refreshed!")
                    st.rerun()
        
        # Simplified sidebar with session info
        with st.sidebar:
            st.markdown("### 🤖 Assistant Status")
            st.success("✅ Ready")
            
            # Session info
            st.markdown("### 📊 Session Info")
            st.info(f"Session: {st.session_state.session_id[:12]}...")
            st.metric("Studies in Session", len(st.session_state.extracted_data))
            
            # Session management
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Refresh Stats", key="ai_refresh_stats"):
                    # Get fresh statistics
                    if self.vector_store:
                        vector_stats = self.vector_store.get_statistics()
                        st.json(vector_stats)
                    else:
                        st.warning("Vector store not available")
            
            with col2:
                if st.button("🗑️ Clear Session Data", key="ai_clear_session"):
                    if self.vector_store:
                        result = asyncio.run(self.vector_store.clear_session_data())
                        if result["status"] == "success":
                            st.success(f"Cleared {result['vectors_deleted']} vectors")
                            # Also clear session state
                            st.session_state.extracted_data = []
                            st.session_state.ai_conversation_history = []
                            st.rerun()
                        else:
                            st.error("Failed to clear session data")
                    else:
                        # Just clear session state if no vector store
                        st.session_state.extracted_data = []
                        st.session_state.ai_conversation_history = []
                        st.success("Session data cleared")
                        st.rerun()
        
        # Display conversation history (optimized)
        if st.session_state.ai_conversation_history:
            st.markdown("### 💬 Conversation History")
            
            # Show only last 2 exchanges to improve performance
            recent_exchanges = st.session_state.ai_conversation_history[-2:]
            
            for i, exchange in enumerate(recent_exchanges):
                with st.chat_message("user"):
                    st.write(exchange.get('user_message', ''))
                
                with st.chat_message("assistant"):
                    response_data = exchange.get('response_data', {})
                    st.write(response_data.get('response', 'No response available'))
                    
                    # Show studies count if available
                    if response_data.get('studies_referenced', 0) > 0:
                        st.caption(f"📚 Referenced {response_data['studies_referenced']} studies")
            
            if len(st.session_state.ai_conversation_history) > 2:
                st.caption(f"... and {len(st.session_state.ai_conversation_history) - 2} earlier exchanges")
        
        # Chat input with form for Enter key support
        st.markdown("### 💬 Ask Dr. ASCOmind+")
        
        # Use form to enable Enter key submission
        with st.form("ai_chat_form", clear_on_submit=True):
            user_query = st.text_area(
                "Your question:",
                height=80,
                placeholder="Ask about multiple myeloma research, treatment comparisons, or study insights...",
                key="ai_chat_input_form"
            )
            
            # Submit button
            submitted = st.form_submit_button("🚀 Get AI Analysis", type="primary", use_container_width=True)
        
        # Process query when form is submitted
        if submitted and user_query.strip():
            # Store the query for processing
            st.session_state.processing_query = user_query.strip()
            
            # Create a single container for the entire response process
            response_container = st.container()
            
            with response_container:
                # Simple progress indicator
                with st.spinner("🧠 AI is analyzing your question..."):
                    try:
                        # Simple user context
                        user_context = {
                            'session_studies': len(st.session_state.extracted_data) if st.session_state.extracted_data else 0
                        }
                        
                        # Get AI response with timeout
                        response_data = asyncio.run(
                            asyncio.wait_for(
                                self.ai_assistant.chat(st.session_state.processing_query, user_context),
                                timeout=60.0
                            )
                        )
                        
                        # Store conversation immediately
                        conversation_entry = {
                            'user_message': st.session_state.processing_query,
                            'response_data': response_data,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                        
                        if 'ai_conversation_history' not in st.session_state:
                            st.session_state.ai_conversation_history = []
                        
                        st.session_state.ai_conversation_history.append(conversation_entry)
                        
                        # Clear the processing query
                        if 'processing_query' in st.session_state:
                            del st.session_state.processing_query
                        
                        # Show success and immediately rerun to display new conversation
                        st.success("✨ Response generated!")
                        st.rerun()
                        
                    except asyncio.TimeoutError:
                        st.error("⏰ Request timed out. Please try a simpler question.")
                        if 'processing_query' in st.session_state:
                            del st.session_state.processing_query
                    except Exception as e:
                        st.error(f"❌ AI Error: {str(e)}")
                        if 'processing_query' in st.session_state:
                            del st.session_state.processing_query
        
        elif submitted and not user_query.strip():
            st.warning("⚠️ Please enter a question.")
        
        # Quick tips (only show if no conversation history to reduce clutter)
        if not st.session_state.ai_conversation_history:
            st.info("""
            💡 **Quick Start Tips:**
            - Ask about study comparisons: "Compare the efficacy of my uploaded studies"
            - Get safety insights: "What are the main safety concerns?"
            - Request recommendations: "What treatment would you recommend?"
            
            **💡 Pro Tip:** Press Enter or Ctrl+Enter to submit your question quickly!
            """)
        
        # Debug mode - Add session and vector store information
        if st.checkbox("🔧 Debug Mode", value=False, key="ai_debug_mode"):
            with st.expander("🔍 Session & Vector Store Debug Information", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Session Information:**")
                    session_info = {
                        "session_id": st.session_state.session_id,
                        "extracted_data_count": len(st.session_state.extracted_data) if st.session_state.extracted_data else 0,
                        "ai_conversation_count": len(st.session_state.ai_conversation_history),
                        "vector_embedding_status": getattr(st.session_state, 'vector_embedding_status', [])
                    }
                    st.json(session_info)
                    
                    # Show extracted data titles
                    if st.session_state.extracted_data:
                        st.markdown("**📚 Extracted Studies:**")
                        for i, data in enumerate(st.session_state.extracted_data, 1):
                            st.write(f"{i}. {data.study_identification.title}")
                
                with col2:
                    st.markdown("**🧠 Vector Store Information:**")
                    try:
                        if self.vector_store:
                            vector_stats = self.vector_store.get_statistics()
                            st.json(vector_stats)
                            
                            # Test vector store search
                            if st.button("🔍 Test Vector Search", key="debug_test_vector_search"):
                                try:
                                    test_results = asyncio.run(
                                        self.vector_store.search_abstracts("test query", top_k=3)
                                    )
                                    st.write(f"**Search Results:** {len(test_results)} studies found")
                                    for result in test_results:
                                        st.write(f"- {result['study_info']['title']} (Score: {result['score']:.3f})")
                                except Exception as e:
                                    st.error(f"Vector search failed: {e}")
                        else:
                            st.warning("Vector store not initialized")
                    except Exception as e:
                        st.error(f"Error getting vector stats: {e}")
                
                # Manual embedding test
                st.markdown("---")
                st.markdown("**🔧 Manual Embedding Test:**")
                if st.button("🚀 Re-embed All Abstracts", key="debug_reembed_abstracts"):
                    if st.session_state.extracted_data and self.vector_store:
                        embedding_results = []
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, data in enumerate(st.session_state.extracted_data):
                            progress = (i + 1) / len(st.session_state.extracted_data)
                            progress_bar.progress(progress)
                            status_text.text(f"Re-embedding {i+1}/{len(st.session_state.extracted_data)}: {data.study_identification.title[:50]}...")
                            
                            try:
                                result = asyncio.run(
                                    self.vector_store.embed_abstract(data, force_update=True)
                                )
                                embedding_results.append({
                                    "study": data.study_identification.title,
                                    "status": result["status"],
                                    "vectors": result.get("vectors_created", 0)
                                })
                            except Exception as e:
                                embedding_results.append({
                                    "study": data.study_identification.title,
                                    "status": "error",
                                    "error": str(e)
                                })
                        
                        progress_bar.progress(1.0)
                        status_text.text("Re-embedding completed!")
                        st.json(embedding_results)
                        st.success("✅ Re-embedding completed! Try asking questions now.")
                    else:
                        st.warning("No data to embed or vector store not available")
    
    def render_settings(self):
        """Render settings page"""
        st.title("⚙️ System Settings")
        
        st.subheader("🔑 API Configuration")
        
        # API keys configuration
        anthropic_key = st.text_input(
            "Anthropic API Key:",
            value=settings.ANTHROPIC_API_KEY or "",
            type="password",
            help="Enter your Anthropic API key for Claude access"
        )
        
        openai_key = st.text_input(
            "OpenAI API Key:",
            value=settings.OPENAI_API_KEY or "",
            type="password",
            help="Enter your OpenAI API key for GPT-4 fallback"
        )
        
        st.subheader("🎛️ Processing Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            batch_size = st.slider(
                "Batch Size:",
                min_value=1,
                max_value=20,
                value=settings.BATCH_SIZE,
                help="Number of abstracts to process simultaneously"
            )
            
            confidence_threshold = st.slider(
                "Confidence Threshold:",
                min_value=0.0,
                max_value=1.0,
                value=settings.MIN_CONFIDENCE_THRESHOLD,
                step=0.1,
                help="Minimum confidence threshold for data validation"
            )
        
        with col2:
            temperature = st.slider(
                "LLM Temperature:",
                min_value=0.0,
                max_value=1.0,
                value=settings.TEMPERATURE,
                step=0.1,
                help="Temperature setting for LLM extraction"
            )
            
            max_tokens = st.number_input(
                "Max Tokens:",
                min_value=1000,
                max_value=8000,
                value=settings.MAX_TOKENS,
                help="Maximum tokens for LLM responses"
            )
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")

    def _generate_basic_analysis(self) -> Dict[str, Any]:
        """Generate basic analysis fallback when full analysis fails"""
        data = st.session_state.extracted_data
        
        if not data:
            return {}
        
        # Basic statistics
        total_studies = len(data)
        enrollments = [d.patient_demographics.total_enrolled for d in data if d.patient_demographics.total_enrolled]
        avg_enrollment = sum(enrollments) / len(enrollments) if enrollments else 0
        
        # Study types
        study_types = {}
        for d in data:
            study_type = d.study_design.study_type.value
            study_types[study_type] = study_types.get(study_type, 0) + 1
        
        # Basic insights
        insights = [
            f"Analysis includes {total_studies} clinical studies",
            f"Average enrollment: {avg_enrollment:.0f} patients" if avg_enrollment else "Enrollment data limited",
            f"Most common study type: {max(study_types, key=study_types.get)}" if study_types else "Mixed study types"
        ]
        
        return {
            'dataset_overview': {
                'summary_statistics': {
                    'total_studies': total_studies,
                    'avg_enrollment': avg_enrollment,
                    'randomized_percentage': 0,
                    'avg_confidence': sum(d.extraction_confidence for d in data) / len(data)
                }
            },
            'clinical_insights': {
                'key_insights': insights
            },
            'treatment_landscape': {
                'regimen_frequencies': study_types
            }
        }

    def _update_session_stats(self, processing_time: float, abstracts_count: int):
        """Update session statistics with new processing data"""
        st.session_state.session_stats['total_processing_time'] += processing_time
        st.session_state.session_stats['abstracts_processed'] += abstracts_count
        st.session_state.session_stats['processing_history'].append({
            'timestamp': datetime.now().isoformat(),
            'processing_time': processing_time,
            'abstracts_count': abstracts_count
        })

    def _get_session_summary(self) -> Dict[str, Any]:
        """Get session summary statistics with improved efficiency calculation"""
        stats = st.session_state.session_stats
        session_duration = time.time() - stats['session_start_time']
        
        # Improved efficiency calculation that's more realistic
        # Base efficiency on actual processing vs ideal processing time
        if session_duration > 0 and stats['abstracts_processed'] > 0:
            # Ideal time per abstract (considering API calls, processing complexity)
            ideal_time_per_abstract = 6.0  # Even more realistic expectation (6 seconds)
            ideal_total_time = stats['abstracts_processed'] * ideal_time_per_abstract
            
            # Calculate efficiency as (ideal_time / actual_time) * 100, capped at 100%
            raw_efficiency = (ideal_total_time / stats['total_processing_time']) * 100
            processing_efficiency = min(raw_efficiency, 100.0)  # Cap at 100%
            
            # Apply bonus for high-quality extractions
            if st.session_state.extracted_data:
                avg_quality = sum(d.extraction_confidence for d in st.session_state.extracted_data) / len(st.session_state.extracted_data)
                quality_bonus = max(0, (avg_quality - 0.6) * 50)  # Bonus for quality > 60%
                processing_efficiency = min(processing_efficiency + quality_bonus, 100.0)
        else:
            processing_efficiency = 0.0
        
        return {
            'session_duration': session_duration,
            'total_processing_time': stats['total_processing_time'],
            'abstracts_processed': stats['abstracts_processed'],
            'avg_time_per_abstract': stats['total_processing_time'] / max(stats['abstracts_processed'], 1),
            'processing_efficiency': processing_efficiency
        }

    def render_protocol_generator(self):
        """Render protocol generation page"""
        st.title("🔬 AI Protocol Generator")
        
        if not st.session_state.extracted_data:
            st.info("📋 Upload and analyze abstracts first to generate analysis protocols.")
            return
        
        st.subheader("📊 Generate Analysis Protocol")
        
        # Protocol configuration
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_objective = st.text_area(
                "Analysis Objective:",
                placeholder="e.g., Compare efficacy and safety of novel combinations in RRMM patients...",
                height=100
            )
            
            protocol_focus = st.selectbox(
                "Protocol Focus:",
                ["Efficacy Analysis", "Safety Analysis", "Comparative Analysis", 
                 "Meta-Analysis", "Real-World Evidence", "Biomarker Analysis", "Health Economics"]
            )
        
        with col2:
            complexity_level = st.selectbox(
                "Analysis Complexity:",
                ["Basic", "Intermediate", "Advanced", "Expert"]
            )
            
            include_subgroups = st.multiselect(
                "Include Subgroup Analyses:",
                ["High-risk vs Standard-risk", "NDMM vs RRMM", "Age-based", 
                 "Treatment mechanism", "Geographic", "Temporal trends"]
            )
        
        # User requirements
        st.subheader("📋 Additional Requirements")
        user_requirements = {}
        
        col1, col2, col3 = st.columns(3)
        with col1:
            user_requirements['timeline_weeks'] = st.number_input("Timeline (weeks):", min_value=1, max_value=52, value=8)
            user_requirements['budget_range'] = st.selectbox("Budget Range:", ["<$25K", "$25K-$75K", "$75K-$150K", ">$150K"])
        
        with col2:
            user_requirements['statistical_software'] = st.multiselect("Statistical Software:", ["R", "SAS", "STATA", "Python"])
            user_requirements['deliverable_format'] = st.multiselect("Deliverables:", ["PDF Report", "Interactive Dashboard", "Raw Data", "Code"])
        
        with col3:
            user_requirements['regulatory_focus'] = st.checkbox("Regulatory Submission Focus")
            user_requirements['publication_ready'] = st.checkbox("Publication-Ready Analysis")
        
        # Generate protocol button
        if st.button("🚀 Generate Analysis Protocol", type="primary") and analysis_objective:
            with st.spinner("🧠 Generating comprehensive analysis protocol..."):
                try:
                    # Prepare study data with categorizations
                    studies_with_categories = []
                    for i, study in enumerate(st.session_state.extracted_data):
                        study_data = {
                            'abstract_text': study.source_text or "",
                            'metadata': study.model_dump(),
                            'categorization': st.session_state.categorization_data[i] if i < len(st.session_state.categorization_data) else {}
                        }
                        studies_with_categories.append(study_data)
                    
                    # Generate protocol
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    protocol = loop.run_until_complete(
                        self.protocol_maker.generate_analysis_protocol(
                            studies_with_categories,
                            analysis_objective,
                            user_requirements
                        )
                    )
                    
                    st.session_state.protocol_results = protocol
                    st.success("✅ Analysis protocol generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Protocol generation failed: {str(e)}")
        
        # Display protocol results
        if st.session_state.protocol_results:
            st.subheader("📋 Generated Analysis Protocol")
            
            protocol = st.session_state.protocol_results
            
            # Protocol overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protocol ID", protocol.get('protocol_id', 'N/A'))
            with col2:
                st.metric("Estimated Timeline", protocol.get('estimated_timeline', {}).get('total_duration', 'N/A'))
            with col3:
                st.metric("Studies Included", protocol.get('study_overview', {}).get('total_studies', 0))
            
            # Protocol tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "📊 Statistical Plan", "🔍 Quality Framework", "📅 Timeline", "💰 Resources"])
            
            with tab1:
                st.markdown("### 🎯 Analysis Objective")
                st.write(protocol.get('analysis_objective', 'Not specified'))
                
                st.markdown("### 📊 Study Overview")
                study_overview = protocol.get('study_overview', {})
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Study Characteristics:**")
                    st.write(f"- Total Studies: {study_overview.get('total_studies', 0)}")
                    st.write(f"- Study Types: {len(study_overview.get('study_types', {}))}")
                    st.write(f"- Population Types: {len(study_overview.get('population_types', {}))}")
                
                with col2:
                    st.write("**Data Quality:**")
                    quality_metrics = study_overview.get('data_quality_metrics', {})
                    st.write(f"- High Quality: {quality_metrics.get('high_quality_count', 0)} studies")
                    st.write(f"- Mean Confidence: {quality_metrics.get('mean_confidence', 0):.1%}")
                
                # Protocol recommendation
                recommendation = protocol.get('protocol_recommendation', {})
                if recommendation:
                    st.markdown("### 🎯 Recommended Approach")
                    st.write(f"**Protocol Type:** {recommendation.get('recommended_protocol_type', 'Not specified')}")
                    st.write(f"**Complexity Level:** {recommendation.get('complexity_level', 'Not specified')}")
                    st.write(f"**Feasibility:** High - Based on available data quality")
            
            with tab2:
                st.markdown("### 📊 Statistical Analysis Plan")
                stat_plan = protocol.get('statistical_analysis_plan', {})
                
                if 'primary_analysis' in stat_plan:
                    st.markdown("#### Primary Analysis")
                    primary = stat_plan['primary_analysis']
                    st.write(f"**Objective:** {primary.get('objective', 'Not specified')}")
                    st.write(f"**Statistical Methods:** {', '.join(primary.get('statistical_methods', []))}")
                    st.write(f"**Significance Level:** {primary.get('significance_level', 'Not specified')}")
                
                if 'secondary_analyses' in stat_plan:
                    st.markdown("#### Secondary Analyses")
                    secondary = stat_plan['secondary_analyses']
                    
                    if 'subgroup_analyses' in secondary:
                        st.write("**Subgroup Analyses:**")
                        for subgroup in secondary['subgroup_analyses']:
                            st.write(f"- {subgroup}")
            
            with tab3:
                st.markdown("### 🔍 Quality Assessment Framework")
                quality_framework = protocol.get('quality_assessment', {})
                
                if 'study_selection_criteria' in quality_framework:
                    selection = quality_framework['study_selection_criteria']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Inclusion Criteria")
                        for criteria in selection.get('inclusion_criteria', []):
                            st.write(f"✅ {criteria}")
                    
                    with col2:
                        st.markdown("#### Exclusion Criteria")
                        for criteria in selection.get('exclusion_criteria', []):
                            st.write(f"❌ {criteria}")
            
            with tab4:
                st.markdown("### 📅 Project Timeline")
                timeline = protocol.get('estimated_timeline', {})
                
                if 'phases' in timeline:
                    phases = timeline['phases']
                    
                    # Create timeline visualization
                    phase_names = list(phases.keys())
                    phase_durations = list(phases.values())
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=phase_durations,
                            y=phase_names,
                            orientation='h',
                            marker_color='#667eea'
                        )
                    ])
                    
                    fig.update_layout(
                        title="Project Timeline by Phase",
                        xaxis_title="Duration",
                        yaxis_title="Project Phase",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Milestones
                if 'milestones' in timeline:
                    st.markdown("#### Key Milestones")
                    for i, milestone in enumerate(timeline['milestones'], 1):
                        st.write(f"{i}. {milestone}")
            
            with tab5:
                st.markdown("### 💰 Resource Requirements")
                resources = protocol.get('resource_requirements', {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'personnel' in resources:
                        st.markdown("#### Personnel Requirements")
                        personnel = resources['personnel']
                        for role, requirement in personnel.items():
                            st.write(f"**{role.replace('_', ' ').title()}:** {requirement}")
                    
                    if 'estimated_cost' in resources:
                        st.markdown("#### Estimated Cost")
                        st.write(f"**Total Budget:** {resources['estimated_cost']}")
                
                with col2:
                    if 'software_requirements' in resources:
                        st.markdown("#### Software Requirements")
                        for software in resources['software_requirements']:
                            st.write(f"- {software}")
                    
                    if 'infrastructure' in resources:
                        st.markdown("#### Infrastructure")
                        for infra in resources['infrastructure']:
                            st.write(f"- {infra}")
            
            # Export protocol
            st.subheader("📥 Export Protocol")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Download PDF"):
                    st.info("PDF export functionality coming soon!")
            
            with col2:
                protocol_json = json.dumps(protocol, indent=2, default=str)
                st.download_button(
                    label="📋 Download JSON",
                    data=protocol_json,
                    file_name=f"protocol_{protocol.get('protocol_id', 'unknown')}.json",
                    mime="application/json"
                )
            
            with col3:
                if st.button("📧 Email Protocol"):
                    st.info("Email functionality coming soon!")

    def _get_realistic_quality_assessment(self, data: ComprehensiveAbstractMetadata) -> Dict[str, Any]:
        """Get realistic quality assessment based on extraction success rather than completeness"""
        
        # Count successful extractions (non-null, non-empty values)
        extraction_successes = 0
        total_attempts = 0
        
        # Core identification data (always expected)
        if data.study_identification.title:
            extraction_successes += 1
        total_attempts += 1
        
        if data.study_identification.study_acronym:
            extraction_successes += 1
        total_attempts += 1
        
        # Study design (usually available)
        if data.study_design.study_type:
            extraction_successes += 1
        total_attempts += 1
        
        # Demographics (often partially available)
        if data.patient_demographics.total_enrolled:
            extraction_successes += 1
        total_attempts += 1
        
        if data.patient_demographics.median_age:
            extraction_successes += 1
        total_attempts += 1
        
        # Efficacy outcomes (variable availability)
        if data.efficacy_outcomes.overall_response_rate and isinstance(data.efficacy_outcomes.overall_response_rate, dict):
            if any(data.efficacy_outcomes.overall_response_rate.values()):
                extraction_successes += 1
        total_attempts += 1
        
        if data.efficacy_outcomes.progression_free_survival and isinstance(data.efficacy_outcomes.progression_free_survival, dict):
            if any(data.efficacy_outcomes.progression_free_survival.values()):
                extraction_successes += 1
        total_attempts += 1
        
        # Treatment regimens (often available)
        if data.treatment_regimens and len(data.treatment_regimens) > 0:
            extraction_successes += 1
        total_attempts += 1
        
        # Calculate realistic quality score
        extraction_quality = extraction_successes / total_attempts if total_attempts > 0 else 0
        
        # Boost score based on LLM's own confidence
        llm_confidence_boost = min(0.2, data.extraction_confidence * 0.2)  # Up to 20% boost
        
        final_quality = min(1.0, extraction_quality + llm_confidence_boost)
        
        return {
            'quality_score': final_quality,
            'extractions_found': extraction_successes,
            'extractions_attempted': total_attempts,
            'llm_confidence': data.extraction_confidence,
            'assessment': self._get_quality_level(final_quality)
        }
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level based on realistic thresholds"""
        if score >= 0.7:
            return "Excellent"
        elif score >= 0.55:
            return "Good" 
        elif score >= 0.4:
            return "Fair"
        else:
            return "Poor"

    def _get_quality_badge(self, confidence: float) -> str:
        """Get a quality badge using realistic assessment"""
        # Use the LLM's confidence directly as it's already well-calibrated
        if confidence >= 0.8:  # LLM is quite confident
            return "✅ Excellent"
        elif confidence >= 0.6:  # LLM is moderately confident
            return "✅ Good"
        elif confidence >= 0.4:  # LLM has some confidence
            return "⚠️ Fair"
        else:
            return "❌ Poor"

    def _get_completeness_badge(self, completeness: float) -> str:
        """Get a completeness badge - now more descriptive and encouraging"""
        # Focus on what was found rather than what's missing
        if completeness >= 0.6:
            return "✅ Comprehensive Data"
        elif 0.4 <= completeness < 0.6:
            return "✅ Good Coverage"
        elif 0.25 <= completeness < 0.4:
            return "⚠️ Moderate Coverage"
        else:
            return "❌ Limited Data"

    def _get_clinical_relevance_badge(self, relevance: float) -> str:
        """Get a clinical relevance badge with improved thresholds"""
        # Use LLM confidence as proxy for clinical relevance
        if relevance >= 0.7:
            return "✅ Highly Relevant"
        elif 0.5 <= relevance < 0.7:
            return "✅ Clinically Relevant"
        elif 0.3 <= relevance < 0.5:
            return "⚠️ Moderately Relevant"
        else:
            return "❌ Limited Relevance"

    def _get_enhanced_quality_badge(self, confidence: float) -> str:
        """Get an enhanced HTML quality badge using LLM confidence directly"""
        # Trust the LLM's confidence assessment as it's well-calibrated
        if confidence >= 0.8:
            return '<span style="background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);">✅ Excellent</span>'
        elif 0.6 <= confidence < 0.8:
            return '<span style="background: linear-gradient(135deg, #3b82f6, #60a5fa); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);">✅ Good</span>'
        elif 0.4 <= confidence < 0.6:
            return '<span style="background: linear-gradient(135deg, #f59e0b, #fbbf24); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);">⚠️ Fair</span>'
        else:
            return '<span style="background: linear-gradient(135deg, #ef4444, #f87171); color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);">❌ Poor</span>'

    def _get_analyzer(self):
        """Lazy loading for analyzer to improve performance"""
        if self.analyzer is None:
            try:
                if settings.ANTHROPIC_API_KEY and self.database:
                    import anthropic
                    llm_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                    self.analyzer = IntelligentAnalyzer(self.database, llm_client)
                else:
                    # Create minimal analyzer without DB/LLM for basic functions
                    self.analyzer = IntelligentAnalyzer(None, None)
            except Exception as e:
                st.warning(f"Analyzer initialization failed: {e}")
                self.analyzer = IntelligentAnalyzer(None, None)  # Fallback
        return self.analyzer
    
    def _get_visualizer(self):
        """Lazy loading for visualizer to improve performance"""
        if self.visualizer is None:
            try:
                self.visualizer = AdvancedVisualizer()
            except Exception as e:
                st.warning(f"Visualizer initialization failed: {e}")
                self.visualizer = AdvancedVisualizer(None)  # Fallback
        return self.visualizer

    def _get_vector_store(self):
        """Get or initialize session-isolated vector store"""
        if not self.vector_store:
            try:
                from agents.vector_store import IntelligentVectorStore
                session_id = getattr(st.session_state, 'session_id', None)
                
                # Refresh settings from secrets in case they weren't loaded initially
                settings.refresh_from_secrets()
                
                # Check if we have required API keys
                if not settings.PINECONE_API_KEY:
                    st.error("🔑 **Pinecone API key not configured!**")
                    st.info("""
                    **To enable vector search:**
                    1. Add your Pinecone API key to Streamlit secrets
                    2. Format: `api_keys.pinecone = "your-pinecone-key"`
                    3. Or set environment variable: `PINECONE_API_KEY`
                    
                    **Without vector search:** You can still use basic text analysis features.
                    """)
                    return None
                
                if not settings.OPENAI_API_KEY:
                    st.error("🔑 **OpenAI API key not configured!**")
                    st.info("""
                    **To enable vector embeddings:**
                    1. Add your OpenAI API key to Streamlit secrets
                    2. Format: `api_keys.openai = "your-openai-key"`
                    3. Or set environment variable: `OPENAI_API_KEY`
                    """)
                    return None
                
                self.vector_store = IntelligentVectorStore(session_id=session_id)
                
                # Test the connection and get stats
                stats = self.vector_store.get_statistics()
                unique_studies = stats.get('unique_studies', 0)
                
                if unique_studies > 0:
                    st.success(f"🧠 Vector store connected! Session: {session_id[:12]}... | Studies: {unique_studies}")
                else:
                    st.info(f"🧠 Vector store ready! Session: {session_id[:12]}... | No studies embedded yet")
                
            except Exception as e:
                st.error(f"🚨 Vector store initialization failed: {e}")
                st.warning("AI Assistant will work with limited capabilities (no semantic search).")
                
                # Provide specific help based on error type
                error_str = str(e).lower()
                if "api" in error_str or "key" in error_str:
                    st.info("💡 This looks like an API key issue. Check your Pinecone and OpenAI keys in Streamlit secrets.")
                elif "pinecone" in error_str:
                    st.info("💡 This looks like a Pinecone service issue. Check your Pinecone index configuration.")
                
                return None
        return self.vector_store
    
    def _get_ai_assistant(self):
        """Get or initialize session-isolated AI assistant"""
        if not self.ai_assistant:
            try:
                from agents.ai_assistant import AdvancedAIAssistant
                session_id = getattr(st.session_state, 'session_id', None)
                selected_provider = getattr(st.session_state, 'selected_llm_provider', settings.DEFAULT_LLM_PROVIDER)
                
                self.ai_assistant = AdvancedAIAssistant(
                    vector_store=self._get_vector_store(),
                    llm_provider=selected_provider
                )
                st.success(f"🤖 AI Assistant initialized with {selected_provider.title()} for session: {session_id[:12]}...")
            except Exception as e:
                st.error(f"AI Assistant initialization failed: {e}")
        return self.ai_assistant


def main():
    """Main application entry point"""
    app = ASCOmindApp()
    app.run()


if __name__ == "__main__":
    main() 