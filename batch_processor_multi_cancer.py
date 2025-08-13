#!/usr/bin/env python3
# batch_processor_multi_cancer.py - MULTI-CANCER BATCH PROCESSOR

"""
Process multiple cancer types (Multiple Myeloma + Prostate) through the enhanced agentic framework.
This will create comprehensive cancer intelligence databases with proper isolation.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

# Import the enhanced agentic framework
from agents.metadata_extractor import BatchExtractor
from agents.analyzer import IntelligentAnalyzer
from agents.visualizer import AdvancedVisualizer
from agents.categorizer import BatchCategorizer
from agents.vector_store import IntelligentVectorStore
from agents.cache_manager import CancerSpecificCacheManager
from config.cancer_types import CancerType, get_cancer_type_config
from models.abstract_metadata import ComprehensiveAbstractMetadata
from utils.file_processors import FileProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiCancerDataProcessor:
    """Process multiple cancer types through enhanced agentic framework"""
    
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        
        # Initialize enhanced agents (shared across cancer types)
        self.batch_extractor = BatchExtractor()
        self.batch_categorizer = BatchCategorizer()
        self.analyzer = IntelligentAnalyzer(None, None)
        self.visualizer = AdvancedVisualizer()
        self.cache_manager = CancerSpecificCacheManager()
        self.file_processor = FileProcessor()
        
        # Cancer type configurations
        self.cancer_configs = {
            "multiple_myeloma": get_cancer_type_config(CancerType.MULTIPLE_MYELOMA),
            "prostate": get_cancer_type_config(CancerType.PROSTATE)
        }
        
        logger.info(f"Multi-cancer processor initialized for: {self.data_directory}")
    
    def discover_cancer_data(self) -> Dict[str, Dict[int, List[str]]]:
        """Discover TXT files organized by cancer type and year"""
        cancer_data = {}
        
        for cancer_type in ["multiple_myeloma", "prostate-curated-15"]:
            # Use curated prostate data
            if cancer_type == "prostate-curated-15":
                cancer_path = self.data_directory / cancer_type
                display_name = "prostate"  # For caching purposes
            else:
                cancer_path = self.data_directory / cancer_type
                display_name = cancer_type
            
            if not cancer_path.exists():
                logger.warning(f"Cancer directory not found: {cancer_path}")
                continue
            
            cancer_data[display_name] = {}
            
            # Scan year directories
            for year_dir in cancer_path.iterdir():
                if year_dir.is_dir() and year_dir.name.isdigit():
                    year = int(year_dir.name)
                    
                    # Find all TXT files in year directory
                    txt_files = []
                    for txt_file in year_dir.glob("*.txt"):
                        if txt_file.is_file():
                            txt_files.append(str(txt_file))
                    
                    if txt_files:
                        # Limit to max 10 abstracts per year
                        limited_files = txt_files[:10]
                        cancer_data[display_name][year] = limited_files
                        status_msg = f"📅 {display_name.upper()} {year}: {len(limited_files)} abstracts"
                        if len(txt_files) > 10:
                            status_msg += f" (limited from {len(txt_files)})"
                        logger.info(status_msg)
        
        return cancer_data
    
    async def load_abstracts_for_cancer_year(self, cancer_type: str, year: int, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Load abstracts for a specific cancer type and year"""
        abstracts = []
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                # Read the TXT file
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                content = self.file_processor._process_txt(file_content)
                
                if content and content.strip():
                    # Create abstract metadata
                    abstract_id = f"{cancer_type}_{year}_{i:03d}"
                    
                    abstract_data = {
                        'abstract_id': abstract_id,
                        'abstract_text': content.strip(),
                        'source_file': str(file_path),  # Ensure it's a string
                        'cancer_type': cancer_type,
                        'publication_year': year,
                        'file_index': i
                    }
                    
                    abstracts.append(abstract_data)
                else:
                    logger.warning(f"Empty or invalid file: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        return abstracts
    
    async def process_cancer_type(self, cancer_type: str, year_data: Dict[int, List[str]]) -> Dict[str, Any]:
        """Process all data for a specific cancer type"""
        logger.info(f"🔬 Starting {cancer_type.upper()} processing...")
        
        # Create cancer-specific vector store with unique session
        vector_store = IntelligentVectorStore(
            session_id=f"cancer_{cancer_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        cancer_results = {
            'cancer_type': cancer_type,
            'total_abstracts': 0,
            'years_processed': [],
            'processing_results': [],
            'vector_store_session': vector_store.get_session_id(),
            'analytics_summary': {},
            'visualizations': {}
        }
        
        all_abstracts_metadata = []
        
        # Process each year
        total_years = len(year_data.keys())
        for year_idx, year in enumerate(sorted(year_data.keys()), 1):
            file_paths = year_data[year]
            logger.info(f"📅 Processing {cancer_type.upper()} {year}: {len(file_paths)} abstracts [{year_idx}/{total_years}]")
            
            # Load abstracts for this year
            abstracts = await self.load_abstracts_for_cancer_year(cancer_type, year, file_paths)
            cancer_results['total_abstracts'] += len(abstracts)
            cancer_results['years_processed'].append(year)
            
            if not abstracts:
                logger.warning(f"No valid abstracts found for {cancer_type} {year}")
                continue
            
            # Phase 1: Metadata Extraction
            logger.info(f"🔬 Extracting metadata for {len(abstracts)} {cancer_type} {year} abstracts...")
            print(f"   📊 Progress: Processing {len(abstracts)} abstracts for {cancer_type} {year}")
            
            # Extract just the text strings for the batch extractor
            abstract_texts = [abstract['abstract_text'] for abstract in abstracts]
            
            # Process abstracts with robust error handling
            successful_results = []
            failed_count = 0
            
            try:
                batch_results = await self.batch_extractor.process_batch(abstract_texts, batch_size=3)  # Reduce batch size for stability
                
                # Add the source information back to the results and filter out failed ones
                for i, result in enumerate(batch_results):
                    if result is not None and i < len(abstracts):
                        try:
                            result.source_file = abstracts[i]['source_file']
                            result.abstract_id = abstracts[i]['abstract_id']
                            successful_results.append(result)
                        except Exception as e:
                            logger.warning(f"Error adding metadata to result {i}: {e}")
                            failed_count += 1
                    else:
                        failed_count += 1
                        
                batch_results = successful_results
                
                if failed_count > 0:
                    logger.info(f"⚠️ Skipped {failed_count} problematic abstracts, continuing with {len(successful_results)} successful ones")
                    
            except Exception as e:
                logger.error(f"Batch processing failed for {cancer_type} {year}: {e}")
                batch_results = []
            
            # Phase 2: AI Categorization (with error handling)
            logger.info(f"🏷️ Categorizing {cancer_type} {year} studies...")
            
            categorizations = []
            if batch_results:  # Only proceed if we have successful results
                try:
                    categorization_input = []
                    for result in batch_results:
                        try:
                            if hasattr(result, 'source_text') and result.source_text:
                                categorization_input.append({
                                    'abstract_text': result.source_text,
                                    'metadata': {
                                        'cancer_type': cancer_type,
                                        'year': year,
                                        'title': getattr(result.study_identification, 'title', 'Unknown') if hasattr(result, 'study_identification') else 'Unknown'
                                    }
                                })
                        except Exception as e:
                            logger.warning(f"Error preparing categorization input: {e}")
                            continue
                    
                    if categorization_input:
                        categorizations = await self.batch_categorizer.categorize_batch(categorization_input)
                        logger.info(f"✅ Successfully categorized {len(categorizations)} abstracts")
                    
                except Exception as e:
                    logger.warning(f"Categorization failed for {cancer_type} {year}, continuing without categorization: {e}")
                    categorizations = []
            
            # Combine metadata with categorizations
            for i, metadata in enumerate(batch_results):
                if i < len(categorizations):
                    # Add categorization to metadata (this would need to be implemented in your metadata model)
                    pass
                all_abstracts_metadata.append(metadata)
            
            # Phase 3: Vector Store Embedding
            logger.info(f"💾 Embedding {cancer_type} {year} abstracts in vector store...")
            print(f"   🔍 Progress: Creating vectors for {len(batch_results)} processed abstracts")
            embedding_results = await vector_store.batch_embed_abstracts(batch_results)
            
            year_result = {
                'year': year,
                'abstracts_processed': len(abstracts),
                'extraction_success': len(batch_results),
                'categorization_success': len(categorizations),
                'embedding_results': embedding_results
            }
            cancer_results['processing_results'].append(year_result)
            
            print(f"   ✅ {cancer_type.upper()} {year} completed: {len(batch_results)} processed, {embedding_results.get('success', 0)} embedded")
            logger.info(f"✅ {cancer_type.upper()} {year} completed: {len(batch_results)} processed")
        
        # Phase 4: Comprehensive Analysis
        if all_abstracts_metadata:
            logger.info(f"📊 Generating {cancer_type.upper()} analytics...")
            analytics = self.analyzer.analyze_comprehensive_dataset(all_abstracts_metadata)
            cancer_results['analytics_summary'] = analytics
            
            # Phase 5: Advanced Visualizations
            logger.info(f"🎨 Creating {cancer_type.upper()} visualizations...")
            visualizations = self.visualizer.create_comprehensive_dashboard(
                all_abstracts_metadata
            )
            cancer_results['visualizations'] = visualizations
        
        # Phase 6: Cancer-Specific Caching
        logger.info(f"💾 Caching {cancer_type.upper()} results...")
        
        # Cache the abstract data
        await self.cache_manager.cache_data(cancer_type, all_abstracts_metadata)
        
        # Cache analytics if available
        if cancer_results.get('analytics_summary'):
            await self.cache_manager.cache_analysis_summary(cancer_type, cancer_results['analytics_summary'])
        
        # Cache visualizations if available  
        if cancer_results.get('visualizations'):
            await self.cache_manager.cache_visualizations(cancer_type, cancer_results['visualizations'])
        
        cache_results = {
            'status': 'success',
            'abstracts_cached': len(all_abstracts_metadata),
            'analytics_cached': bool(cancer_results.get('analytics_summary')),
            'visualizations_cached': bool(cancer_results.get('visualizations'))
        }
        
        cancer_results['cache_status'] = cache_results
        
        logger.info(f"🎉 {cancer_type.upper()} processing completed!")
        logger.info(f"   📊 Total abstracts: {cancer_results['total_abstracts']}")
        logger.info(f"   📅 Years: {cancer_results['years_processed']}")
        logger.info(f"   🔍 Vector store: {cancer_results['vector_store_session']}")
        
        return cancer_results
    
    async def process_all_cancers(self) -> Dict[str, Any]:
        """Process all discovered cancer types"""
        logger.info("🚀 Starting multi-cancer processing pipeline...")
        
        # Discover all cancer data
        cancer_data = self.discover_cancer_data()
        
        if not cancer_data:
            logger.error("❌ No cancer data discovered!")
            return {"status": "error", "message": "No data found"}
        
        # Process each cancer type
        results = {
            'start_time': datetime.now().isoformat(),
            'cancer_results': {},
            'summary': {},
            'status': 'success'
        }
        
        for cancer_type, year_data in cancer_data.items():
            try:
                cancer_result = await self.process_cancer_type(cancer_type, year_data)
                results['cancer_results'][cancer_type] = cancer_result
                
            except Exception as e:
                logger.error(f"❌ Error processing {cancer_type}: {e}")
                results['cancer_results'][cancer_type] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Generate overall summary
        total_abstracts = sum(
            result.get('total_abstracts', 0) 
            for result in results['cancer_results'].values()
            if isinstance(result, dict)
        )
        
        successful_cancers = [
            cancer for cancer, result in results['cancer_results'].items()
            if isinstance(result, dict) and result.get('total_abstracts', 0) > 0
        ]
        
        results['summary'] = {
            'total_cancer_types': len(cancer_data),
            'successful_cancer_types': len(successful_cancers),
            'total_abstracts_processed': total_abstracts,
            'cancer_types_processed': successful_cancers,
            'end_time': datetime.now().isoformat()
        }
        
        logger.info("🎉 Multi-cancer processing completed!")
        logger.info(f"   🎯 Cancer types: {successful_cancers}")
        logger.info(f"   📊 Total abstracts: {total_abstracts}")
        
        return results


async def main():
    """Main execution function"""
    
    # Configure data directory path
    # UPDATE THIS PATH to point to your cancer-abstracts-data directory
    data_directory = "/Users/ansberthafreiku/dev/ASCOMind+/cancer-abstracts-data"
    
    # Initialize processor
    processor = MultiCancerDataProcessor(data_directory)
    
    # Process all cancer types
    results = await processor.process_all_cancers()
    
    # Save processing results
    results_file = f"multi_cancer_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n🎉 Processing completed! Results saved to: {results_file}")
    print(f"📊 Summary:")
    for cancer_type, result in results['cancer_results'].items():
        if isinstance(result, dict) and 'total_abstracts' in result:
            print(f"   {cancer_type.upper()}: {result['total_abstracts']} abstracts, Session: {result['vector_store_session']}")


if __name__ == "__main__":
    asyncio.run(main())
