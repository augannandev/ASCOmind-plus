# utils/database.py - DATABASE UTILITIES

import duckdb
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid

from models.abstract_metadata import ComprehensiveAbstractMetadata
from config.settings import settings


class ASCOmindDatabase:
    """Database operations for ASCOmind+ with session isolation"""
    
    def __init__(self, db_path: Optional[str] = None, session_id: Optional[str] = None):
        self.db_path = db_path or str(settings.DATA_DIR / "ascomind.db")
        self.session_id = session_id or self._generate_session_id()
        self._ensure_db_directory()
        self.conn = self._connect()
        self._initialize_schema()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{random_id}"
    
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
        """Initialize database schema with session isolation"""
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS abstracts (
                    id VARCHAR PRIMARY KEY,
                    session_id VARCHAR NOT NULL,
                    title VARCHAR,
                    study_type VARCHAR,
                    total_enrolled INTEGER,
                    extraction_confidence FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """)
            
            # Create index on session_id for performance
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_abstracts_session_id 
                ON abstracts(session_id)
            """)
        except Exception as e:
            pass  # Schema might already exist
    
    def store_abstract(self, abstract: ComprehensiveAbstractMetadata) -> bool:
        """Store abstract with session isolation"""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO abstracts 
                (id, session_id, title, study_type, total_enrolled, extraction_confidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                abstract.abstract_id,
                self.session_id,
                abstract.study_identification.title,
                abstract.study_design.study_type.value,
                abstract.patient_demographics.total_enrolled,
                abstract.extraction_confidence,
                json.dumps(abstract.model_dump())
            ])
            return True
        except Exception as e:
            print(f"Error storing abstract: {e}")
            return False
    
    def get_session_abstracts(self) -> List[ComprehensiveAbstractMetadata]:
        """Get all abstracts for current session"""
        try:
            results = self.conn.execute("""
                SELECT metadata FROM abstracts 
                WHERE session_id = ?
                ORDER BY created_at
            """, [self.session_id]).fetchall()
            
            abstracts = []
            for row in results:
                metadata_dict = json.loads(row[0])
                abstract = ComprehensiveAbstractMetadata(**metadata_dict)
                abstracts.append(abstract)
            
            return abstracts
        except Exception as e:
            print(f"Error retrieving session abstracts: {e}")
            return []
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics for current session"""
        try:
            stats = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_abstracts,
                    AVG(extraction_confidence) as avg_confidence,
                    MIN(created_at) as first_upload,
                    MAX(created_at) as last_upload
                FROM abstracts 
                WHERE session_id = ?
            """, [self.session_id]).fetchone()
            
            return {
                "session_id": self.session_id,
                "total_abstracts": stats[0] if stats else 0,
                "avg_confidence": stats[1] if stats and stats[1] else 0,
                "first_upload": stats[2] if stats else None,
                "last_upload": stats[3] if stats else None
            }
        except Exception as e:
            return {"session_id": self.session_id, "error": str(e)}
    
    def clear_session_data(self) -> bool:
        """Clear all data for current session"""
        try:
            self.conn.execute("""
                DELETE FROM abstracts WHERE session_id = ?
            """, [self.session_id])
            return True
        except Exception as e:
            print(f"Error clearing session data: {e}")
            return False
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_id


def get_database(session_id: Optional[str] = None) -> ASCOmindDatabase:
    """Get database instance with session isolation"""
    return ASCOmindDatabase(session_id=session_id) 