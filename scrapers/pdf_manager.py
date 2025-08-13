# scrapers/pdf_manager.py - Local PDF Storage Manager

import os
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import shutil

class PDFStorageManager:
    """Local PDF storage management for scraped abstracts"""
    
    def __init__(self, base_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Local storage configuration
        self.base_path = Path(base_path) if base_path else Path("data/pdfs")
        self.setup_local_directories()
        
        # PDF metadata tracking
        self.metadata_file = self.base_path / "pdf_registry.json"
        self.pdf_registry = self.load_pdf_registry()
    
    def setup_local_directories(self):
        """Create organized directory structure for PDFs"""
        directories = [
            # Conference-based organization
            "conferences/asco/2024",
            "conferences/asco/2023", 
            "conferences/asco/2022",
            "conferences/asco/2021",
            "conferences/ash/2024",
            "conferences/ash/2023",
            "conferences/esmo/2024",
            
            # Indication-based organization
            "indications/multiple_myeloma",
            "indications/breast_cancer",
            "indications/lung_cancer",
            "indications/lymphoma",
            "indications/leukemia",
            "indications/colorectal",
            "indications/melanoma",
            "indications/prostate",
            "indications/pancreatic",
            "indications/ovarian",
            
            # Source-based organization
            "journals/blood",
            "journals/nejm",
            "journals/jco",
            "journals/lancet_oncology",
            
            # User uploads
            "uploads/user_submissions",
            "uploads/batch_imports",
            
            # Generated documents
            "generated/reports",
            "generated/protocols",
            "generated/summaries",
            
            # Temporary processing
            "temp/processing",
            "temp/extraction",
            
            # Archive
            "archive/old_versions",
            "archive/duplicates"
        ]
        
        for directory in directories:
            full_path = self.base_path / directory
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep files
            gitkeep = full_path / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.write_text("# PDF storage directory\n")
        
        self.logger.info(f"PDF storage directories created at: {self.base_path}")
    
    def store_pdf(self, 
                  pdf_content: bytes, 
                  metadata: Dict[str, Any],
                  storage_category: str = "conferences") -> Dict[str, Any]:
        """Store PDF with organized naming and metadata"""
        try:
            # Generate file info
            file_hash = hashlib.sha256(pdf_content).hexdigest()[:16]
            
            # Check for duplicates
            if file_hash in self.pdf_registry:
                existing_record = self.pdf_registry[file_hash]
                self.logger.info(f"PDF already exists: {existing_record['filename']}")
                return {
                    "status": "duplicate",
                    "file_hash": file_hash,
                    "existing_path": existing_record['local_path'],
                    "filename": existing_record['filename']
                }
            
            # Create filename based on metadata
            filename = self._generate_filename(metadata, file_hash)
            
            # Determine storage path
            storage_path = self._determine_storage_path(metadata, storage_category)
            local_path = self.base_path / storage_path / filename
            
            # Store locally
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with local_path.open('wb') as f:
                f.write(pdf_content)
            
            # Update registry
            pdf_record = {
                "file_hash": file_hash,
                "filename": filename,
                "local_path": str(local_path),
                "storage_category": storage_category,
                "file_size": len(pdf_content),
                "metadata": metadata,
                "stored_at": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": None
            }
            
            self.pdf_registry[file_hash] = pdf_record
            self.save_pdf_registry()
            
            self.logger.info(f"PDF stored successfully: {filename}")
            
            return {
                "status": "success",
                "file_hash": file_hash,
                "local_path": str(local_path),
                "filename": filename,
                "storage_info": pdf_record
            }
            
        except Exception as e:
            self.logger.error(f"Error storing PDF: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_filename(self, metadata: Dict[str, Any], file_hash: str) -> str:
        """Generate organized filename"""
        parts = []
        
        # Conference/source prefix
        if 'conference' in metadata:
            parts.append(metadata['conference'].upper())
        elif 'journal' in metadata:
            parts.append(metadata['journal'].replace(' ', '_'))
        
        # Year
        if 'year' in metadata:
            parts.append(str(metadata['year']))
        
        # Abstract/study identifier
        if 'abstract_number' in metadata:
            parts.append(f"ABS_{metadata['abstract_number']}")
        elif 'nct_number' in metadata:
            parts.append(metadata['nct_number'])
        elif 'pmid' in metadata:
            parts.append(f"PMID_{metadata['pmid']}")
        
        # Study title (truncated and cleaned)
        if 'title' in metadata:
            title_clean = "".join(c for c in metadata['title'][:50] if c.isalnum() or c in ' -_')
            title_clean = title_clean.replace(' ', '_')
            parts.append(title_clean)
        
        # File hash for uniqueness
        parts.append(file_hash)
        
        filename = "_".join(filter(None, parts)) + ".pdf"
        
        # Ensure filename isn't too long (max 200 chars)
        if len(filename) > 200:
            filename = "_".join(parts[:3]) + "_" + file_hash + ".pdf"
        
        return filename
    
    def _determine_storage_path(self, metadata: Dict[str, Any], category: str) -> Path:
        """Determine appropriate storage subdirectory"""
        if category == "conferences":
            conference = metadata.get('conference', 'unknown').lower()
            year = metadata.get('year', datetime.now().year)
            return Path(f"conferences/{conference}/{year}")
        
        elif category == "indications":
            indication = metadata.get('indication', 'unknown').lower()
            return Path(f"indications/{indication}")
        
        elif category == "journals":
            journal = metadata.get('journal', 'unknown').lower().replace(' ', '_')
            return Path(f"journals/{journal}")
        
        elif category == "uploads":
            upload_type = metadata.get('upload_type', 'user_submissions')
            return Path(f"uploads/{upload_type}")
        
        elif category == "generated":
            doc_type = metadata.get('document_type', 'reports')
            return Path(f"generated/{doc_type}")
        
        else:
            return Path("misc")
    
    def retrieve_pdf(self, file_hash: str) -> Optional[bytes]:
        """Retrieve PDF by file hash"""
        try:
            if file_hash not in self.pdf_registry:
                self.logger.error(f"PDF not found: {file_hash}")
                return None
            
            record = self.pdf_registry[file_hash]
            
            # Update access tracking
            record['access_count'] += 1
            record['last_accessed'] = datetime.now().isoformat()
            
            # Read from local storage
            local_path = Path(record['local_path'])
            if local_path.exists():
                self.save_pdf_registry()
                return local_path.read_bytes()
            else:
                self.logger.error(f"Local PDF file not found: {local_path}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving PDF: {e}")
            return None
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        try:
            stats = {
                "total_pdfs": len(self.pdf_registry),
                "total_size_bytes": sum(record['file_size'] for record in self.pdf_registry.values()),
                "categories": {},
                "conferences": {},
                "indications": {},
                "years": {},
                "last_updated": datetime.now().isoformat()
            }
            
            # Category breakdown
            for record in self.pdf_registry.values():
                category = record['storage_category']
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
                
                # Conference breakdown
                if 'conference' in record['metadata']:
                    conf = record['metadata']['conference']
                    stats['conferences'][conf] = stats['conferences'].get(conf, 0) + 1
                
                # Indication breakdown  
                if 'indication' in record['metadata']:
                    indication = record['metadata']['indication']
                    stats['indications'][indication] = stats['indications'].get(indication, 0) + 1
                
                # Year breakdown
                if 'year' in record['metadata']:
                    year = str(record['metadata']['year'])
                    stats['years'][year] = stats['years'].get(year, 0) + 1
            
            # Convert bytes to human readable
            stats['total_size_mb'] = stats['total_size_bytes'] / (1024 * 1024)
            stats['total_size_gb'] = stats['total_size_mb'] / 1024
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting storage statistics: {e}")
            return {}
    
    def load_pdf_registry(self) -> Dict[str, Any]:
        """Load PDF registry from disk"""
        try:
            if self.metadata_file.exists():
                with self.metadata_file.open('r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading PDF registry: {e}")
            return {}
    
    def save_pdf_registry(self):
        """Save PDF registry to disk"""
        try:
            with self.metadata_file.open('w') as f:
                json.dump(self.pdf_registry, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving PDF registry: {e}")
    
    def list_pdfs_by_criteria(self, **criteria) -> List[Dict[str, Any]]:
        """List PDFs matching specific criteria"""
        results = []
        
        for file_hash, record in self.pdf_registry.items():
            match = True
            
            for key, value in criteria.items():
                if key in record['metadata']:
                    if str(record['metadata'][key]).lower() != str(value).lower():
                        match = False
                        break
                elif key in record:
                    if str(record[key]).lower() != str(value).lower():
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                results.append(record)
        
        return results 