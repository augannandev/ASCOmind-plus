# agents/vector_store.py - INTELLIGENT VECTOR STORAGE WITH PINECONE

import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
import uuid

import openai
import pinecone
from pinecone import Pinecone, ServerlessSpec
import numpy as np
from pydantic import BaseModel

from models.abstract_metadata import ComprehensiveAbstractMetadata
from config.settings import settings

class VectorMetadata(BaseModel):
    """Structured metadata for vector storage"""
    abstract_id: str
    content_hash: str
    session_id: str  # Add session isolation
    study_title: str
    study_acronym: Optional[str]
    nct_number: Optional[str]
    study_type: str
    mm_subtype: List[str]
    line_of_therapy: Optional[str]
    treatment_regimens: List[str]
    orr_value: Optional[float]
    pfs_median: Optional[float]
    enrollment: Optional[int]
    confidence_score: float
    extraction_timestamp: str
    text_chunk_type: str  # 'full_abstract', 'study_design', 'efficacy', 'safety', etc.

class IntelligentVectorStore:
    """Advanced vector storage with Pinecone for medical abstracts - Session Isolated"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Session management for data isolation
        self.session_id = session_id or self._generate_session_id()
        self.logger.info(f"Initializing vector store for session: {self.session_id}")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.embedding_model = "text-embedding-3-large"
        self.embedding_dimension = 3072  # text-embedding-3-large dimension
        
        # Initialize or connect to index
        self._initialize_index()
        self.index = self.pc.Index(self.index_name)
        
        # Session-specific cache for deduplication
        self._session_content_hashes = set()
        self._load_session_hashes()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        # Use timestamp + random UUID for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{random_id}"
    
    def _initialize_index(self):
        """Initialize Pinecone index if it doesn't exist"""
        try:
            existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                self.logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                self.logger.info(f"Index {self.index_name} created successfully")
            else:
                self.logger.info(f"Using existing Pinecone index: {self.index_name}")
                
        except Exception as e:
            self.logger.error(f"Error initializing Pinecone index: {e}")
            raise
    
    def _load_session_hashes(self):
        """Load existing content hashes for current session only"""
        try:
            # Query only vectors for this session
            query_response = self.index.query(
                vector=[0.0] * self.embedding_dimension,
                top_k=10000,  # Large number to get all session vectors
                include_metadata=True,
                filter={"session_id": self.session_id}
            )
            
            for match in query_response['matches']:
                if 'content_hash' in match['metadata']:
                    self._session_content_hashes.add(match['metadata']['content_hash'])
            
            self.logger.info(f"Loaded {len(self._session_content_hashes)} existing content hashes for session {self.session_id}")
            
        except Exception as e:
            self.logger.warning(f"Could not load session hashes: {e}")
            self._session_content_hashes = set()
    
    def _generate_content_hash(self, abstract_text: str, study_id: str) -> str:
        """Generate unique hash for abstract content (session-scoped)"""
        # Include session ID in hash for session isolation
        content = f"{self.session_id}:{study_id}:{abstract_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _sanitize_metadata_for_pinecone(self, metadata_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values and sanitize metadata for Pinecone compatibility"""
        sanitized = {}
        for key, value in metadata_dict.items():
            if value is not None:
                # Convert values to Pinecone-compatible types
                if isinstance(value, list):
                    # Filter out None values from lists and convert to strings
                    clean_list = [str(item) for item in value if item is not None]
                    if clean_list:  # Only add non-empty lists
                        sanitized[key] = clean_list
                elif isinstance(value, (str, int, float, bool)):
                    sanitized[key] = value
                else:
                    # Convert other types to strings
                    sanitized[key] = str(value)
        return sanitized
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI's large model"""
        try:
            response = await asyncio.to_thread(
                self.openai_client.embeddings.create,
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error getting embedding: {e}")
            raise
    
    def _extract_metadata(self, data: ComprehensiveAbstractMetadata, chunk_type: str = "full_abstract") -> VectorMetadata:
        """Extract structured metadata from abstract data"""
        
        # Extract MM subtypes
        mm_subtypes = []
        if data.disease_characteristics.mm_subtype:
            mm_subtypes = [subtype.value for subtype in data.disease_characteristics.mm_subtype]
        
        # Extract treatment regimens
        treatment_regimens = []
        for regimen in data.treatment_regimens:
            if regimen.regimen_name:
                treatment_regimens.append(regimen.regimen_name)
        
        # Extract efficacy data
        orr_value = None
        if data.efficacy_outcomes.overall_response_rate:
            orr_data = data.efficacy_outcomes.overall_response_rate
            if isinstance(orr_data, dict):
                orr_value = orr_data.get('value')
        
        pfs_median = None
        if data.efficacy_outcomes.progression_free_survival:
            pfs_data = data.efficacy_outcomes.progression_free_survival
            if isinstance(pfs_data, dict):
                pfs_median = pfs_data.get('median')
        
        # Generate unique study identifier
        study_id = data.study_identification.nct_number or data.study_identification.study_acronym or data.abstract_id
        content_hash = self._generate_content_hash(data.source_text or "", study_id)
        
        return VectorMetadata(
            abstract_id=data.abstract_id,
            content_hash=content_hash,
            session_id=self.session_id,
            study_title=data.study_identification.title,
            study_acronym=data.study_identification.study_acronym,
            nct_number=data.study_identification.nct_number,
            study_type=data.study_design.study_type.value,
            mm_subtype=mm_subtypes,
            line_of_therapy=data.treatment_history.line_of_therapy,
            treatment_regimens=treatment_regimens,
            orr_value=orr_value,
            pfs_median=pfs_median,
            enrollment=data.patient_demographics.total_enrolled,
            confidence_score=data.extraction_confidence,
            extraction_timestamp=data.extraction_timestamp.isoformat(),
            text_chunk_type=chunk_type
        )
    
    def _create_text_chunks(self, data: ComprehensiveAbstractMetadata) -> List[Tuple[str, str]]:
        """Create semantic text chunks for better retrieval"""
        chunks = []
        
        # Full abstract (primary chunk)
        if data.source_text:
            chunks.append((data.source_text, "full_abstract"))
        
        # Study design summary
        study_summary = f"""
        Study: {data.study_identification.title}
        Type: {data.study_design.study_type.value}
        Population: {', '.join([s.value for s in data.disease_characteristics.mm_subtype]) if data.disease_characteristics.mm_subtype else 'Multiple Myeloma'}
        Line of Therapy: {data.treatment_history.line_of_therapy or 'Not specified'}
        Enrollment: {data.patient_demographics.total_enrolled or 'Not specified'} patients
        """.strip()
        chunks.append((study_summary, "study_design"))
        
        # Treatment information
        if data.treatment_regimens:
            treatment_text = "Treatment Regimens:\n"
            for i, regimen in enumerate(data.treatment_regimens, 1):
                treatment_text += f"{i}. {regimen.regimen_name}\n"
                if regimen.drugs:
                    drugs = [f"{drug.get('name', 'Unknown')} ({drug.get('dose', 'Unknown dose')})" 
                            for drug in regimen.drugs]
                    treatment_text += f"   Drugs: {', '.join(drugs)}\n"
            chunks.append((treatment_text.strip(), "treatment"))
        
        # Efficacy results
        efficacy_text = f"""
        Efficacy Results for {data.study_identification.title}:
        Overall Response Rate: {data.efficacy_outcomes.overall_response_rate.get('value', 'Not reported') if isinstance(data.efficacy_outcomes.overall_response_rate, dict) else 'Not reported'}%
        Progression-Free Survival: {data.efficacy_outcomes.progression_free_survival.get('median', 'Not reported') if isinstance(data.efficacy_outcomes.progression_free_survival, dict) else 'Not reported'} months
        Complete Response Rate: {data.efficacy_outcomes.complete_response_rate.get('value', 'Not reported') if isinstance(data.efficacy_outcomes.complete_response_rate, dict) else 'Not reported'}%
        """.strip()
        chunks.append((efficacy_text, "efficacy"))
        
        # Safety information
        if data.safety_profile.grade_3_4_aes:
            safety_text = f"Safety Profile for {data.study_identification.title}:\n"
            if isinstance(data.safety_profile.grade_3_4_aes, list):
                for ae in data.safety_profile.grade_3_4_aes:
                    if isinstance(ae, dict):
                        event = ae.get('event', 'Overall')
                        percentage = ae.get('percentage', 'Unknown')
                        safety_text += f"Grade 3-4 {event}: {percentage}%\n"
            chunks.append((safety_text.strip(), "safety"))
        
        return chunks
    
    async def embed_abstract(self, data: ComprehensiveAbstractMetadata, force_update: bool = False) -> Dict[str, Any]:
        """Embed abstract with smart deduplication"""
        try:
            # Extract metadata
            base_metadata = self._extract_metadata(data)
            
            # Check for duplicates
            if not force_update and base_metadata.content_hash in self._session_content_hashes:
                self.logger.info(f"Abstract already embedded: {data.study_identification.title}")
                return {
                    "status": "skipped",
                    "reason": "already_exists",
                    "content_hash": base_metadata.content_hash,
                    "study_title": data.study_identification.title
                }
            
            # Create text chunks for better retrieval
            text_chunks = self._create_text_chunks(data)
            
            # Embed all chunks
            vectors_to_upsert = []
            for i, (text, chunk_type) in enumerate(text_chunks):
                if not text.strip():
                    continue
                
                # Get embedding
                embedding = await self._get_embedding(text)
                
                # Create metadata for this chunk
                chunk_metadata = self._extract_metadata(data, chunk_type)
                metadata_dict = chunk_metadata.model_dump()
                
                # Add chunk-specific info
                metadata_dict['text_content'] = text[:1000]  # Store first 1000 chars for preview
                metadata_dict['chunk_index'] = i
                
                # Create vector ID
                vector_id = f"{base_metadata.content_hash}_{chunk_type}_{i}"
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": self._sanitize_metadata_for_pinecone(metadata_dict)
                })
            
            # Upsert vectors
            if vectors_to_upsert:
                self.index.upsert(vectors=vectors_to_upsert)
                
                # Update cache
                self._session_content_hashes.add(base_metadata.content_hash)
                
                self.logger.info(f"Embedded {len(vectors_to_upsert)} chunks for: {data.study_identification.title}")
                
                return {
                    "status": "success",
                    "vectors_created": len(vectors_to_upsert),
                    "content_hash": base_metadata.content_hash,
                    "study_title": data.study_identification.title,
                    "chunk_types": [chunk[1] for chunk in text_chunks]
                }
            else:
                return {
                    "status": "error",
                    "reason": "no_valid_chunks",
                    "study_title": data.study_identification.title
                }
                
        except Exception as e:
            self.logger.error(f"Error embedding abstract: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "study_title": getattr(data.study_identification, 'title', 'Unknown')
            }
    
    async def search_abstracts(self, query: str, filters: Optional[Dict] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Advanced semantic search with filtering - Session isolated"""
        try:
            # Get query embedding
            query_embedding = await self._get_embedding(query)
            
            # Build metadata filter with session isolation
            metadata_filter = {"session_id": self.session_id}  # Always filter by session
            
            if filters:
                if 'study_type' in filters:
                    metadata_filter['study_type'] = filters['study_type']
                if 'mm_subtype' in filters:
                    metadata_filter['mm_subtype'] = {"$in": filters['mm_subtype']}
                if 'min_confidence' in filters:
                    metadata_filter['confidence_score'] = {"$gte": filters['min_confidence']}
                if 'treatment_type' in filters:
                    # Search in treatment regimens
                    metadata_filter['treatment_regimens'] = {"$in": filters['treatment_type']}
            
            # Search vectors with session filter
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k * 2,  # Get extra results to deduplicate
                include_metadata=True,
                filter=metadata_filter
            )
            
            # Process and deduplicate results
            seen_studies = set()
            results = []
            
            for match in search_results['matches']:
                metadata = match['metadata']
                content_hash = metadata.get('content_hash')
                
                # Skip if we've already seen this study
                if content_hash in seen_studies:
                    continue
                
                seen_studies.add(content_hash)
                
                # Format result
                result = {
                    'score': match['score'],
                    'study_info': {
                        'title': metadata.get('study_title'),
                        'acronym': metadata.get('study_acronym'),
                        'nct_number': metadata.get('nct_number'),
                        'study_type': metadata.get('study_type'),
                        'confidence_score': metadata.get('confidence_score')
                    },
                    'content_preview': metadata.get('text_content', '')[:200] + "...",
                    'chunk_type': metadata.get('text_chunk_type'),
                    'metadata': metadata
                }
                
                results.append(result)
                
                # Break if we have enough unique results
                if len(results) >= top_k:
                    break
            
            self.logger.info(f"Found {len(results)} unique studies for session {self.session_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching abstracts: {e}")
            return []
    
    async def get_study_context(self, study_identifiers: List[str]) -> List[Dict[str, Any]]:
        """Get full context for specific studies - Session isolated"""
        try:
            results = []
            
            for identifier in study_identifiers:
                # Search by NCT number, acronym, or title WITH session filter
                search_filter = {
                    "session_id": self.session_id,  # Always filter by session
                    "$or": [
                        {"nct_number": identifier},
                        {"study_acronym": identifier},
                        {"study_title": {"$regex": identifier}}
                    ]
                }
                
                query_results = self.index.query(
                    vector=[0.0] * self.embedding_dimension,
                    top_k=10,
                    include_metadata=True,
                    filter=search_filter
                )
                
                # Group chunks by study
                study_chunks = {}
                for match in query_results['matches']:
                    metadata = match['metadata']
                    content_hash = metadata.get('content_hash')
                    
                    if content_hash not in study_chunks:
                        study_chunks[content_hash] = {
                            'study_info': {
                                'title': metadata.get('study_title'),
                                'acronym': metadata.get('study_acronym'),
                                'nct_number': metadata.get('nct_number'),
                                'study_type': metadata.get('study_type'),
                                'confidence_score': metadata.get('confidence_score')
                            },
                            'chunks': {}
                        }
                    
                    chunk_type = metadata.get('text_chunk_type')
                    study_chunks[content_hash]['chunks'][chunk_type] = metadata.get('text_content', '')
                
                results.extend(list(study_chunks.values()))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting study context: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics for current session"""
        try:
            # Get session-specific stats
            session_query = self.index.query(
                vector=[0.0] * self.embedding_dimension,
                top_k=10000,
                include_metadata=True,
                filter={"session_id": self.session_id}
            )
            
            session_vectors = len(session_query['matches'])
            unique_studies = len(self._session_content_hashes)
            
            return {
                "total_vectors": session_vectors,
                "unique_studies": unique_studies,
                "session_id": self.session_id,
                "dimension": self.embedding_dimension,
                "session_isolation": True
            }
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {
                "total_vectors": 0,
                "unique_studies": 0,
                "session_id": self.session_id,
                "error": str(e)
            }
    
    async def clear_session_data(self) -> Dict[str, Any]:
        """Clear all data for current session"""
        try:
            # Get all vectors for this session
            session_vectors = self.index.query(
                vector=[0.0] * self.embedding_dimension,
                top_k=10000,
                include_metadata=True,
                filter={"session_id": self.session_id}
            )
            
            # Delete vectors
            if session_vectors['matches']:
                vector_ids = [match['id'] for match in session_vectors['matches']]
                self.index.delete(ids=vector_ids)
                
                # Clear session cache
                self._session_content_hashes.clear()
                
                self.logger.info(f"Cleared {len(vector_ids)} vectors for session {self.session_id}")
                
                return {
                    "status": "success",
                    "vectors_deleted": len(vector_ids),
                    "session_id": self.session_id
                }
            else:
                return {
                    "status": "success",
                    "vectors_deleted": 0,
                    "session_id": self.session_id,
                    "message": "No data to clear"
                }
                
        except Exception as e:
            self.logger.error(f"Error clearing session data: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": self.session_id
            }
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.session_id
    
    async def batch_embed_abstracts(self, abstracts: List[ComprehensiveAbstractMetadata]) -> Dict[str, Any]:
        """Batch embed multiple abstracts efficiently"""
        results = {
            "success": 0,
            "skipped": 0,
            "errors": 0,
            "details": []
        }
        
        for abstract in abstracts:
            try:
                result = await self.embed_abstract(abstract)
                results["details"].append(result)
                
                if result["status"] == "success":
                    results["success"] += 1
                elif result["status"] == "skipped":
                    results["skipped"] += 1
                else:
                    results["errors"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "status": "error",
                    "reason": str(e),
                    "study_title": getattr(abstract.study_identification, 'title', 'Unknown')
                })
        
        return results 