#!/usr/bin/env python3
# batch_processor_prostate.py - PROSTATE CANCER TXT FILES BATCH PROCESSOR

"""
Process your year-organized prostate cancer TXT files through the enhanced agentic framework.
This will create a complete prostate cancer intelligence database.
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProstateDataProcessor:
    """Process prostate cancer TXT files through enhanced agentic framework"""
    
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)
        self.cancer_type = "prostate"
        
        # Initialize enhanced agents
        self.batch_extractor = BatchExtractor()
        self.batch_categorizer = BatchCategorizer()
        self.analyzer = IntelligentAnalyzer()
        self.visualizer = AdvancedVisualizer()
        self.cache_manager = CancerSpecificCacheManager()
        
        # Initialize prostate-specific vector store
        self.vector_store = IntelligentVectorStore(
            session_id=f"cancer_prostate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        logger.info(f"Prostate processor initialized for: {self.data_directory}")
    
    async def process_all_years(self) -> Dict[str, Any]:
        """Process all year directories and create complete prostate intelligence"""
        logger.info("🚀 Starting complete prostate cancer processing pipeline")
        
        results = {
            "total_abstracts": 0,
            "by_year": {},
            "processing_summary": {},
            "cache_status": {},
            "vector_store_status": {}
        }
        
        # Step 1: Discover and load all TXT files by year
        abstracts_by_year = await self._load_abstracts_by_year()
        
        if not abstracts_by_year:
            logger.warning("No TXT files found in the specified directory structure")
            return results
        
        # Step 2: Process each year through the agentic pipeline
        all_processed_abstracts = []
        
        for year, abstracts in abstracts_by_year.items():
            logger.info(f"📅 Processing ASCO {year}: {len(abstracts)} abstracts")
            
            year_results = await self._process_year_batch(year, abstracts)
            results["by_year"][year] = year_results
            
            # Collect all processed abstracts
            all_processed_abstracts.extend(year_results["processed_abstracts"])
            results["total_abstracts"] += len(abstracts)
        
        # Step 3: Generate comprehensive analysis across all years
        logger.info("📊 Generating comprehensive prostate cancer analysis")
        comprehensive_analysis = self.analyzer.analyze_comprehensive_dataset(all_processed_abstracts)
        
        # Step 4: Create visualizations
        logger.info("📈 Creating comprehensive visualizations")
        visualizations = self.visualizer.create_comprehensive_dashboard(all_processed_abstracts)
        
        # Step 5: Cache everything for the new cancer-first UI
        logger.info("💾 Caching for cancer-first UI")
        cache_results = await self._cache_for_ui(all_processed_abstracts, comprehensive_analysis, visualizations)
        
        # Step 6: Vector store embedding
        logger.info("🔍 Creating vector embeddings for AI assistant")
        vector_results = await self.vector_store.batch_embed_abstracts(all_processed_abstracts)
        
        results["processing_summary"] = {
            "total_processed": len(all_processed_abstracts),
            "analysis_generated": bool(comprehensive_analysis),
            "visualizations_created": len(visualizations),
            "comprehensive_analysis": comprehensive_analysis
        }
        
        results["cache_status"] = cache_results
        results["vector_store_status"] = vector_results
        
        logger.info("✅ Complete prostate cancer processing pipeline finished!")
        return results
    
    async def _load_abstracts_by_year(self) -> Dict[str, List[str]]:
        """Load TXT files organized by year directories"""
        abstracts_by_year = {}
        
        # Look for year directories (2020, 2021, 2022, 2023, 2024)
        for year in [2020, 2021, 2022, 2023, 2024]:
            year_dir = self.data_directory / str(year)
            
            if year_dir.exists() and year_dir.is_dir():
                logger.info(f"📁 Found year directory: {year_dir}")
                
                # Find all TXT files in this year
                txt_files = list(year_dir.glob("*.txt"))
                
                if txt_files:
                    year_abstracts = []
                    
                    for txt_file in txt_files:
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                content = f.read().strip()
                            
                            if content:  # Only include non-empty files
                                year_abstracts.append(content)
                                logger.debug(f"Loaded: {txt_file.name}")
                        
                        except Exception as e:
                            logger.error(f"Error loading {txt_file}: {e}")
                    
                    if year_abstracts:
                        abstracts_by_year[year] = year_abstracts
                        logger.info(f"📅 Year {year}: {len(year_abstracts)} abstracts loaded")
                else:
                    logger.warning(f"No TXT files found in {year_dir}")
            else:
                logger.info(f"Year directory not found: {year_dir}")
        
        total_abstracts = sum(len(abstracts) for abstracts in abstracts_by_year.values())
        logger.info(f"📊 Total abstracts loaded: {total_abstracts} across {len(abstracts_by_year)} years")
        
        return abstracts_by_year
    
    async def _process_year_batch(self, year: int, abstracts: List[str]) -> Dict[str, Any]:
        """Process a single year's abstracts through the agentic pipeline"""
        logger.info(f"🔬 Processing {len(abstracts)} abstracts for {year}")
        
        # Step 1: Extract comprehensive metadata
        logger.info(f"📝 Extracting metadata for {year}")
        processed_abstracts = await self.batch_extractor.process_batch(abstracts)
        
        # Step 2: Add year information to each abstract
        for abstract in processed_abstracts:
            abstract.study_identification.publication_year = year
            abstract.study_identification.conference_name = "ASCO"
        
        # Step 3: Categorize studies
        logger.info(f"🏷️ Categorizing studies for {year}")
        study_data = [
            {"abstract_text": abstract.source_text, "metadata": abstract}
            for abstract in processed_abstracts
        ]
        categorizations = await self.batch_categorizer.categorize_batch(study_data)
        
        # Step 4: Generate year-specific analysis
        logger.info(f"📊 Analyzing {year} data")
        year_analysis = self.analyzer.analyze_comprehensive_dataset(processed_abstracts)
        
        return {
            "year": year,
            "abstract_count": len(abstracts),
            "processed_abstracts": processed_abstracts,
            "categorizations": categorizations,
            "analysis": year_analysis,
            "success_rate": len(processed_abstracts) / len(abstracts) if abstracts else 0
        }
    
    async def _cache_for_ui(self, 
                          all_abstracts: List[ComprehensiveAbstractMetadata],
                          analysis: Dict[str, Any],
                          visualizations: Dict[str, Any]) -> Dict[str, Any]:
        """Cache everything for the new cancer-first UI"""
        
        # Cache the raw data
        await self.cache_manager.cache_data(self.cancer_type, all_abstracts)
        
        # Cache the analysis/summary
        summary = {
            'cancer_type': self.cancer_type,
            'total_studies': len(all_abstracts),
            'analysis_results': analysis,
            'last_updated': datetime.now().isoformat(),
            'config': get_cancer_type_config(CancerType.PROSTATE).dict()
        }
        await self.cache_manager.cache_summary(self.cancer_type, summary)
        
        # Cache the visualizations
        await self.cache_manager.cache_visualizations(self.cancer_type, visualizations)
        
        return {
            "data_cached": True,
            "summary_cached": True,
            "visualizations_cached": True,
            "cache_directory": str(self.cache_manager.cache_dir / self.cancer_type)
        }
    
    def generate_processing_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable processing report"""
        
        report = f"""
🎯 PROSTATE CANCER PROCESSING REPORT
{'='*50}

📊 Processing Summary:
• Total Abstracts Processed: {results['total_abstracts']}
• Years Covered: {', '.join(map(str, results['by_year'].keys()))}
• Success Rate: {results['processing_summary']['total_processed']} / {results['total_abstracts']}

📅 Year Breakdown:
"""
        
        for year, year_data in results['by_year'].items():
            success_rate = year_data['success_rate'] * 100
            report += f"• ASCO {year}: {year_data['abstract_count']} abstracts ({success_rate:.1f}% success)\n"
        
        report += f"""
🧠 AI Processing Results:
• Comprehensive Analysis: {'✅ Generated' if results['processing_summary']['analysis_generated'] else '❌ Failed'}
• Visualizations: {results['processing_summary']['visualizations_created']} charts created
• Vector Embeddings: {results['vector_store_status']['success']} successful, {results['vector_store_status']['errors']} errors

💾 Cache Status:
• Data Cached: {'✅' if results['cache_status']['data_cached'] else '❌'}
• Summary Cached: {'✅' if results['cache_status']['summary_cached'] else '❌'}
• Visualizations Cached: {'✅' if results['cache_status']['visualizations_cached'] else '❌'}

🚀 Ready for Cancer-First UI:
• Select "Prostate Cancer" in left pane
• Filter by years: 2020-2024
• Explore analytics, visualizations, and AI assistant
• All data is pre-loaded and cached for instant access!

📁 Cache Location:
{results['cache_status']['cache_directory']}
"""
        
        return report


async def main():
    """Main processing function"""
    
    # CONFIGURE YOUR DATA DIRECTORY HERE
    data_directory = "cancer-abstracts-data/prostate"
    
    print("🎯 Prostate Cancer Agentic Processing Pipeline")
    print("=" * 50)
    print()
    
    # Check if directory exists
    if not Path(data_directory).exists():
        print("❌ Data directory not found!")
        print(f"Please update 'data_directory' to point to your prostate cancer TXT files")
        print(f"Expected structure:")
        print(f"  {data_directory}/")
        print(f"  ├── 2020/")
        print(f"  │   ├── abstract_001.txt")
        print(f"  │   └── abstract_002.txt")
        print(f"  ├── 2021/")
        print(f"  └── ...")
        return
    
    # Initialize processor
    processor = ProstateDataProcessor(data_directory)
    
    # Process all data
    start_time = datetime.now()
    print(f"🚀 Starting processing at: {start_time}")
    
    try:
        results = await processor.process_all_years()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*50)
        print("✅ PROCESSING COMPLETED!")
        print(f"⏱️ Duration: {duration}")
        print("\n" + processor.generate_processing_report(results))
        
        # Save detailed results
        results_file = f"prostate_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert ComprehensiveAbstractMetadata objects to dicts for JSON serialization
        serializable_results = {
            "total_abstracts": results["total_abstracts"],
            "processing_summary": results["processing_summary"],
            "cache_status": results["cache_status"],
            "vector_store_status": results["vector_store_status"],
            "years_processed": list(results["by_year"].keys()),
            "processing_completed_at": end_time.isoformat(),
            "duration_seconds": duration.total_seconds()
        }
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage:
    print("🎯 To run this processor:")
    print("1. Update the 'data_directory' path in main()")
    print("2. Ensure your TXT files are organized by year directories")
    print("3. Run: python batch_processor_prostate.py")
    print()
    print("This will:")
    print("• Process all your prostate cancer abstracts")
    print("• Extract comprehensive metadata")
    print("• Generate analytics and visualizations")
    print("• Cache everything for the cancer-first UI")
    print("• Create vector embeddings for AI assistant")
    print()
    # Run the processor
    asyncio.run(main())
