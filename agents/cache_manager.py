# agents/cache_manager.py - CANCER-SPECIFIC CACHING SYSTEM

import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pickle
from loguru import logger

from config.cancer_types import CancerType, get_cancer_type_config
from agents.visualizer import AdvancedVisualizer
from agents.analyzer import IntelligentAnalyzer
from models.abstract_metadata import ComprehensiveAbstractMetadata


class CacheEntry:
    """Represents a cached item with metadata"""
    def __init__(self, data: Any, cancer_type: str, cache_type: str):
        self.data = data
        self.cancer_type = cancer_type
        self.cache_type = cache_type
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.access_count = 0
        self.data_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute hash of the cached data"""
        if isinstance(self.data, dict):
            content = json.dumps(self.data, sort_keys=True, default=str)
        else:
            content = str(self.data)
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - self.created_at > timedelta(hours=max_age_hours)
    
    def access(self):
        """Mark cache entry as accessed"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class CancerSpecificCacheManager:
    """Manages pre-generated visualizations and summaries by cancer type"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._memory_cache: Dict[str, CacheEntry] = {}
        
        # Cache settings
        self.max_memory_entries = 100
        self.cache_expiry_hours = 24 * 30  # 30 days instead of 24 hours
        self.auto_refresh_threshold = 0.8  # Refresh when 80% of expiry time passed
        
        logger.info(f"Cache manager initialized with directory: {self.cache_dir}")
    
    def _get_cache_key(self, cancer_type: str, cache_type: str, identifier: str = "", year: Optional[int] = None) -> str:
        """Generate cache key with optional year filtering"""
        base_key = f"{cancer_type}_{cache_type}"
        if year:
            base_key += f"_{year}"
        if identifier:
            base_key += f"_{identifier}"
        return base_key
    
    def _get_file_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        cancer_type = cache_key.split('_')[0]
        cache_subdir = self.cache_dir / cancer_type
        cache_subdir.mkdir(exist_ok=True)
        return cache_subdir / f"{cache_key}.pkl"
    
    async def get_cached_visualizations(self, cancer_type: str) -> Optional[Dict[str, Any]]:
        """Get cached visualizations for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "visualizations")
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired(self.cache_expiry_hours):
                entry.access()
                logger.info(f"Retrieved visualizations from memory cache for {cancer_type}")
                return entry.data
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
        
        # Check file cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if not entry.is_expired(self.cache_expiry_hours):
                    entry.access()
                    self._memory_cache[cache_key] = entry
                    logger.info(f"Retrieved visualizations from file cache for {cancer_type}")
                    return entry.data
                else:
                    # Remove expired file
                    file_path.unlink()
            except Exception as e:
                logger.error(f"Error loading cached visualizations: {e}")
        
        return None
    
    async def cache_visualizations(self, cancer_type: str, visualizations: Dict[str, Any]):
        """Cache visualizations for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "visualizations")
        entry = CacheEntry(visualizations, cancer_type, "visualizations")
        
        # Store in memory
        self._memory_cache[cache_key] = entry
        
        # Store in file
        file_path = self._get_file_path(cache_key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            logger.info(f"Cached visualizations for {cancer_type}")
        except Exception as e:
            logger.error(f"Error caching visualizations to file: {e}")
        
        # Clean up memory if needed
        await self._cleanup_memory_cache()
    
    async def get_cached_summary(self, cancer_type: str) -> Optional[Dict[str, Any]]:
        """Get cached summary for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "summary")
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired(self.cache_expiry_hours):
                entry.access()
                logger.info(f"Retrieved summary from memory cache for {cancer_type}")
                return entry.data
            else:
                del self._memory_cache[cache_key]
        
        # Check file cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if not entry.is_expired(self.cache_expiry_hours):
                    entry.access()
                    self._memory_cache[cache_key] = entry
                    logger.info(f"Retrieved summary from file cache for {cancer_type}")
                    return entry.data
                else:
                    file_path.unlink()
            except Exception as e:
                logger.error(f"Error loading cached summary: {e}")
        
        return None
    
    async def cache_summary(self, cancer_type: str, summary: Dict[str, Any]):
        """Cache summary for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "summary")
        entry = CacheEntry(summary, cancer_type, "summary")
        
        # Store in memory
        self._memory_cache[cache_key] = entry
        
        # Store in file
        file_path = self._get_file_path(cache_key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            logger.info(f"Cached summary for {cancer_type}")
        except Exception as e:
            logger.error(f"Error caching summary to file: {e}")
        
        await self._cleanup_memory_cache()
    
    async def get_cached_data(self, cancer_type: str) -> Optional[List[ComprehensiveAbstractMetadata]]:
        """Get cached abstract data for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "abstracts")
        
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired(self.cache_expiry_hours):
                entry.access()
                return entry.data
            else:
                del self._memory_cache[cache_key]
        
        # Check file cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if not entry.is_expired(self.cache_expiry_hours):
                    entry.access()
                    self._memory_cache[cache_key] = entry
                    return entry.data
                else:
                    file_path.unlink()
            except Exception as e:
                logger.error(f"Error loading cached data: {e}")
        
        return None
    
    async def cache_data(self, cancer_type: str, data: List[ComprehensiveAbstractMetadata]):
        """Cache abstract data for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "abstracts")
        entry = CacheEntry(data, cancer_type, "abstracts")
        
        self._memory_cache[cache_key] = entry
        
        file_path = self._get_file_path(cache_key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            logger.info(f"Cached {len(data)} abstracts for {cancer_type}")
        except Exception as e:
            logger.error(f"Error caching data to file: {e}")
        
        await self._cleanup_memory_cache()
    
    async def cache_analysis_summary(self, cancer_type: str, analysis_data: Dict[str, Any]):
        """Cache analysis summary for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "analysis")
        entry = CacheEntry(analysis_data, cancer_type, "analysis")
        
        self._memory_cache[cache_key] = entry
        
        file_path = self._get_file_path(cache_key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            logger.info(f"Cached analysis summary for {cancer_type}")
        except Exception as e:
            logger.error(f"Error caching analysis summary to file: {e}")
        
        await self._cleanup_memory_cache()
    
    async def get_cached_analysis_summary(self, cancer_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis summary for a cancer type"""
        cache_key = self._get_cache_key(cancer_type, "analysis")
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]
            if not entry.is_expired(self.cache_expiry_hours):
                entry.access()
                logger.info(f"Retrieved analysis summary from memory cache for {cancer_type}")
                return entry.data
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
        
        # Try file cache
        file_path = self._get_file_path(cache_key)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if not entry.is_expired(self.cache_expiry_hours):
                    # Add back to memory cache
                    self._memory_cache[cache_key] = entry
                    entry.access()
                    logger.info(f"Retrieved analysis summary from file cache for {cancer_type}")
                    return entry.data
                else:
                    # Remove expired file
                    file_path.unlink()
                    
            except Exception as e:
                logger.error(f"Error loading cached analysis summary: {e}")
        
        return None
    
    async def invalidate_cache(self, cancer_type: str, cache_type: Optional[str] = None):
        """Invalidate cache for a cancer type"""
        if cache_type:
            # Invalidate specific cache type
            cache_key = self._get_cache_key(cancer_type, cache_type)
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
            
            file_path = self._get_file_path(cache_key)
            if file_path.exists():
                file_path.unlink()
            
            logger.info(f"Invalidated {cache_type} cache for {cancer_type}")
        else:
            # Invalidate all cache for cancer type
            keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(f"{cancer_type}_")]
            for key in keys_to_remove:
                del self._memory_cache[key]
            
            # Remove files
            cancer_cache_dir = self.cache_dir / cancer_type
            if cancer_cache_dir.exists():
                for file_path in cancer_cache_dir.glob("*.pkl"):
                    file_path.unlink()
            
            logger.info(f"Invalidated all cache for {cancer_type}")
    
    async def _cleanup_memory_cache(self):
        """Clean up memory cache if it exceeds limits"""
        if len(self._memory_cache) <= self.max_memory_entries:
            return
        
        # Sort by last accessed time and remove oldest entries
        sorted_entries = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        entries_to_remove = len(self._memory_cache) - self.max_memory_entries
        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del self._memory_cache[key]
        
        logger.info(f"Cleaned up {entries_to_remove} entries from memory cache")
    
    async def pregenerate_all_cancer_caches(self, 
                                          visualizer: AdvancedVisualizer,
                                          analyzer: IntelligentAnalyzer,
                                          data_by_cancer_type: Dict[str, List[ComprehensiveAbstractMetadata]]):
        """Pre-generate all caches for all cancer types"""
        logger.info("Starting pre-generation of all cancer type caches")
        
        tasks = []
        for cancer_type, abstracts in data_by_cancer_type.items():
            if abstracts:  # Only generate if we have data
                task = self._pregenerate_single_cancer_cache(
                    cancer_type, abstracts, visualizer, analyzer
                )
                tasks.append(task)
        
        # Run all pre-generation tasks concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("Completed pre-generation of all cancer type caches")
    
    async def _pregenerate_single_cancer_cache(self,
                                             cancer_type: str,
                                             abstracts: List[ComprehensiveAbstractMetadata],
                                             visualizer: AdvancedVisualizer,
                                             analyzer: IntelligentAnalyzer):
        """Pre-generate cache for a single cancer type"""
        try:
            logger.info(f"Pre-generating cache for {cancer_type} with {len(abstracts)} abstracts")
            
            # Cache the raw data
            await self.cache_data(cancer_type, abstracts)
            
            # Generate and cache visualizations
            visualizations = visualizer.create_comprehensive_dashboard(abstracts)
            await self.cache_visualizations(cancer_type, visualizations)
            
            # Generate and cache summary
            analysis_results = analyzer.analyze_comprehensive_dataset(abstracts)
            summary = {
                'cancer_type': cancer_type,
                'total_studies': len(abstracts),
                'analysis_results': analysis_results,
                'last_updated': datetime.now().isoformat(),
                'config': get_cancer_type_config(CancerType(cancer_type)).dict()
            }
            await self.cache_summary(cancer_type, summary)
            
            logger.info(f"Successfully pre-generated cache for {cancer_type}")
            
        except Exception as e:
            logger.error(f"Error pre-generating cache for {cancer_type}: {e}")
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all caches"""
        status = {
            'memory_cache_size': len(self._memory_cache),
            'cache_directory': str(self.cache_dir),
            'cancer_types': {}
        }
        
        for cancer_type in CancerType:
            cancer_status = {
                'visualizations_cached': False,
                'summary_cached': False,
                'data_cached': False
            }
            
            # Check each cache type
            for cache_type in ['visualizations', 'summary', 'abstracts']:
                cache_key = self._get_cache_key(cancer_type.value, cache_type)
                
                # Check memory cache
                if cache_key in self._memory_cache:
                    entry = self._memory_cache[cache_key]
                    if not entry.is_expired(self.cache_expiry_hours):
                        if cache_type == 'abstracts':
                            cancer_status['data_cached'] = True
                        else:
                            cancer_status[f'{cache_type}_cached'] = True
                
                # Check file cache if not in memory
                else:
                    file_path = self._get_file_path(cache_key)
                    if file_path.exists():
                        if cache_type == 'abstracts':
                            cancer_status['data_cached'] = True
                        else:
                            cancer_status[f'{cache_type}_cached'] = True
            
            status['cancer_types'][cancer_type.value] = cancer_status
        
        return status
