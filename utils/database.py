# utils/database.py - DATABASE UTILITIES

import duckdb
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from models.abstract_metadata import ComprehensiveAbstractMetadata
from config.settings import settings


class ASCOmindDatabase:
    """Database operations for ASCOmind+"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.DATA_DIR / "ascomind.db")
        self._ensure_db_directory()
        self.conn = self._connect()
        self._initialize_schema()
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _connect(self):
        """Connect to DuckDB database"""
        try:
            return duckdb.connect(self.db_path)
        except Exception as e:
            # Fallback to in-memory database
            return duckdb.connect(':memory:')
    
    def _initialize_schema(self):
        """Initialize database schema"""
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS abstracts (
                    id VARCHAR PRIMARY KEY,
                    title VARCHAR,
                    study_type VARCHAR,
                    total_enrolled INTEGER,
                    extraction_confidence FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """)
        except Exception as e:
            pass  # Schema might already exist
    
    def insert_abstract(self, metadata: ComprehensiveAbstractMetadata) -> bool:
        """Insert abstract metadata into database"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO abstracts 
                (id, title, study_type, total_enrolled, extraction_confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                metadata.abstract_id,
                metadata.study_identification.title,
                metadata.study_design.study_type.value,
                metadata.patient_demographics.total_enrolled,
                metadata.extraction_confidence,
                json.dumps(metadata.dict(), default=str)
            ])
            return True
        except Exception as e:
            return False
    
    def get_abstracts(self, limit: int = 100) -> pd.DataFrame:
        """Get abstracts from database"""
        try:
            return self.conn.execute("""
                SELECT * FROM abstracts 
                ORDER BY created_at DESC 
                LIMIT ?
            """, [limit]).df()
        except:
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def get_database() -> ASCOmindDatabase:
    """Get database instance"""
    return ASCOmindDatabase() 