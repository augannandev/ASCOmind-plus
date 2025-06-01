# config/settings.py - COMPREHENSIVE CONFIGURATION

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional, Any
import streamlit as st

class Settings(BaseSettings):
    """Comprehensive system configuration"""
    
    # Application settings
    APP_NAME: str = "ASCOmind+"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # API Keys and Authentication (Optional - use Streamlit secrets instead)
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    
    # Database settings
    DATABASE_URL: str = "duckdb:///data/ascomind_plus.db"
    VECTOR_DB_PATH: str = "data/vector_store"
    
    # LLM Configuration
    PRIMARY_LLM: str = "claude-3-sonnet"
    FALLBACK_LLM: str = "gpt-4o"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.1
    
    # Processing settings
    BATCH_SIZE: int = 10
    MAX_CONCURRENT_REQUESTS: int = 5
    RETRY_ATTEMPTS: int = 3
    REQUEST_TIMEOUT: int = 120
    
    # Extraction settings
    MIN_CONFIDENCE_THRESHOLD: float = 0.7
    VALIDATION_ENABLED: bool = True
    AUTO_CORRECTION_ENABLED: bool = True
    
    # Visualization settings
    CHART_THEME: str = "plotly_white"
    COLOR_PALETTE: List[str] = [
        "#667eea", "#764ba2", "#f093fb", "#f5576c", 
        "#4facfe", "#00f2fe", "#43e97b", "#38f9d7"
    ]
    
    # File processing
    UPLOAD_MAX_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".csv", ".xlsx"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models" 
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    
    # Medical domain configuration
    MEDICAL_ENTITIES: Dict[str, List[str]] = {
        "drug_classes": [
            "proteasome_inhibitor", "immunomodulatory_drug", "monoclonal_antibody",
            "alkylating_agent", "corticosteroid", "histone_deacetylase_inhibitor",
            "selective_inhibitor_nuclear_export", "bcl2_inhibitor", "car_t_therapy"
        ],
        "response_criteria": [
            "complete_response", "very_good_partial_response", "partial_response",
            "stable_disease", "progressive_disease", "stringent_complete_response"
        ],
        "survival_endpoints": [
            "overall_survival", "progression_free_survival", "event_free_survival",
            "time_to_next_treatment", "duration_of_response", "time_to_progression"
        ]
    }
    
    # Confidence scoring weights
    CONFIDENCE_WEIGHTS: Dict[str, float] = {
        "exact_match": 1.0,
        "high_certainty": 0.9,
        "moderate_certainty": 0.7,
        "low_certainty": 0.5,
        "inference": 0.3
    }
    
    # Database
    DATABASE_TYPE: str = "duckdb"
    DATABASE_PATH: str = "ascomind_data.db"
    
    # Pinecone Configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "ascomind-abstracts"
    
    # Vector Store Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSION: int = 3072
    MAX_SEARCH_RESULTS: int = 10
    
    # LLM Provider Configuration
    DEFAULT_LLM_PROVIDER: str = "claude"  # Options: "claude", "openai", "gemini"
    AVAILABLE_LLM_PROVIDERS: List[str] = ["claude", "openai", "gemini"]
    
    # Model specifications for each provider
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Developer mode settings
    DEVELOPER_MODE: bool = False
    SHOW_PROCESSING_OPTIONS: bool = False
    SHOW_LLM_SELECTION: bool = False
    
    # Pinecone Configuration
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to load from environment or secrets"""
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment or Streamlit secrets"""
        try:
            # Load API keys from environment or Streamlit secrets
            self.ANTHROPIC_API_KEY = (
                os.getenv("ANTHROPIC_API_KEY") or 
                self._get_streamlit_secret("ANTHROPIC_API_KEY") or
                self._get_streamlit_secret("api_keys", "ANTHROPIC_API_KEY") or
                self._get_streamlit_secret("api_keys", "claude")
            )
            
            self.OPENAI_API_KEY = (
                os.getenv("OPENAI_API_KEY") or 
                self._get_streamlit_secret("OPENAI_API_KEY") or
                self._get_streamlit_secret("api_keys", "OPENAI_API_KEY") or
                self._get_streamlit_secret("api_keys", "openai")
            )
            
            self.GEMINI_API_KEY = (
                os.getenv("GEMINI_API_KEY") or 
                self._get_streamlit_secret("GEMINI_API_KEY") or
                self._get_streamlit_secret("api_keys", "GEMINI_API_KEY") or
                self._get_streamlit_secret("api_keys", "gemini")
            )
            
            # Load Pinecone configuration
            self.PINECONE_API_KEY = (
                os.getenv("PINECONE_API_KEY") or 
                self._get_streamlit_secret("PINECONE_API_KEY") or
                self._get_streamlit_secret("api_keys", "PINECONE_API_KEY") or
                self._get_streamlit_secret("api_keys", "pinecone")
            )
            
            self.PINECONE_INDEX_NAME = (
                os.getenv("PINECONE_INDEX_NAME") or 
                self._get_streamlit_secret("PINECONE_INDEX_NAME") or
                self._get_streamlit_secret("api_keys", "PINECONE_INDEX_NAME") or
                self._get_streamlit_secret("api_keys", "index_name") or
                "ascomind-abstracts"
            )
            
            # LLM Provider preferences
            self.DEFAULT_LLM_PROVIDER = (
                os.getenv("DEFAULT_LLM_PROVIDER") or 
                self._get_streamlit_secret("DEFAULT_LLM_PROVIDER") or
                self._get_streamlit_secret("api_keys", "DEFAULT_LLM_PROVIDER") or
                "claude"
            )
            
            self.CLAUDE_MODEL = (
                os.getenv("CLAUDE_MODEL") or 
                self._get_streamlit_secret("CLAUDE_MODEL") or
                self._get_streamlit_secret("api_keys", "CLAUDE_MODEL") or
                "claude-3-5-sonnet-20241022"
            )
            
            self.OPENAI_MODEL = (
                os.getenv("OPENAI_MODEL") or 
                self._get_streamlit_secret("OPENAI_MODEL") or
                self._get_streamlit_secret("api_keys", "OPENAI_MODEL") or
                "gpt-4o"
            )
            
            self.GEMINI_MODEL = (
                os.getenv("GEMINI_MODEL") or 
                self._get_streamlit_secret("GEMINI_MODEL") or
                self._get_streamlit_secret("api_keys", "GEMINI_MODEL") or
                "gemini-1.5-pro"
            )
            
            self.PINECONE_ENVIRONMENT = (
                os.getenv("PINECONE_ENVIRONMENT") or 
                self._get_streamlit_secret("PINECONE_ENVIRONMENT") or
                self._get_streamlit_secret("api_keys", "PINECONE_ENVIRONMENT") or
                "gcp-starter"
            )
        except Exception:
            # Fallback if Streamlit secrets aren't available yet
            pass
    
    def _get_streamlit_secret(self, *keys) -> Optional[str]:
        """Safely get a Streamlit secret, supporting nested access"""
        try:
            if hasattr(st, 'secrets'):
                current = st.secrets
                for key in keys:
                    if key in current:
                        current = current[key]
                    else:
                        return None
                return str(current) if current is not None else None
        except Exception:
            pass
        return None
    
    def refresh_from_secrets(self):
        """Refresh settings from Streamlit secrets (call this after secrets are loaded)"""
        self._load_api_keys()
    
    def has_required_keys(self) -> bool:
        """Check if all required API keys are available"""
        return all([
            self.ANTHROPIC_API_KEY,
            self.OPENAI_API_KEY,
            self.GEMINI_API_KEY,
            self.PINECONE_API_KEY
        ])

    def get_available_providers(self) -> Dict[str, bool]:
        """Get available LLM providers based on API key availability"""
        return {
            "claude": bool(self.ANTHROPIC_API_KEY),
            "openai": bool(self.OPENAI_API_KEY),
            "gemini": bool(self.GEMINI_API_KEY)
        }
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific LLM provider"""
        configs = {
            "claude": {
                "api_key": self.ANTHROPIC_API_KEY,
                "model": self.CLAUDE_MODEL,
                "name": "Claude 3.5 Sonnet",
                "icon": "🤖"
            },
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "name": "GPT-4o",
                "icon": "🧠"
            },
            "gemini": {
                "api_key": self.GEMINI_API_KEY,
                "model": self.GEMINI_MODEL,
                "name": "Gemini 1.5 Pro",
                "icon": "✨"
            }
        }
        return configs.get(provider, {})

    def is_configuration_valid(self) -> bool:
        """Check if basic configuration is valid"""
        return bool(any([
            self.ANTHROPIC_API_KEY,
            self.OPENAI_API_KEY,
            self.GEMINI_API_KEY,
            self.PINECONE_API_KEY
        ]))

# Global settings instance
settings = Settings()

# Ensure directories exist
for directory in [settings.DATA_DIR, settings.UPLOADS_DIR, settings.OUTPUTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Auto-refresh from Streamlit secrets on import
settings.refresh_from_secrets() 