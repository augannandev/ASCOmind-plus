#!/usr/bin/env python3
# batch_processor_prostate_json.py - Process prostate cancer from scraped JSON

import asyncio
import json
from pathlib import Path
from datetime import datetime
import logging

from agents.metadata_extractor import EnhancedMetadataExtractor
from agents.analyzer import IntelligentAnalyzer
from agents.visualizer import AdvancedVisualizer
from agents.cache_manager import CancerSpecificCacheManager
from models.abstract_metadata import ComprehensiveAbstractMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_prostate_from_json():
    """Process prostate cancer abstracts from scraped JSON files"""
    
    # Initialize components
    extractor = EnhancedMetadataExtractor()
    analyzer = IntelligentAnalyzer()
    visualizer = AdvancedVisualizer()
    cache_manager = CancerSpecificCacheManager()
    
    # Load all scraped JSON files
    json_files = [
        "data/scraped_abstracts_20250618_000545.json",
        "data/scraped_abstracts_20250618_000714.json",
        "data/scraped_abstracts_test_asco_website.json"
    ]
    
    all_abstracts = []
    prostate_abstracts = []
    
    print("🔍 Loading and filtering prostate cancer abstracts...")
    
    for json_file in json_files:
        if Path(json_file).exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
                abstracts = data if isinstance(data, list) else data.get('abstracts', [])
                all_abstracts.extend(abstracts)
    
    # Filter for prostate cancer abstracts
    for abstract in all_abstracts:
        title = abstract.get('title', '').lower()
        text = abstract.get('abstract_text', '').lower()
        
        if 'prostate' in title or 'prostate' in text:
            prostate_abstracts.append(abstract)
    
    print(f"✅ Found {len(prostate_abstracts)} prostate cancer abstracts")
    
    if not prostate_abstracts:
        print("❌ No prostate cancer abstracts found!")
        return
    
    # Process abstracts into ComprehensiveAbstractMetadata
    processed_abstracts = []
    
    print("🔄 Processing abstracts...")
    for i, abstract in enumerate(prostate_abstracts, 1):
        try:
            # Extract metadata
            metadata = await extractor.extract_enhanced_metadata(
                abstract_text=abstract.get('abstract_text', ''),
                title=abstract.get('title', ''),
                authors=abstract.get('authors', []),
                abstract_id=abstract.get('abstract_id', f'PROSTATE_{i}'),
                session_info=abstract.get('session', ''),
                cancer_type='prostate'
            )
            
            # Set source file to indicate year if available
            year = abstract.get('year', 2023)
            metadata.source_file = f"asco_{year}_prostate_{i}.json"
            
            processed_abstracts.append(metadata)
            
            if i % 10 == 0:
                print(f"  Processed {i}/{len(prostate_abstracts)} abstracts...")
                
        except Exception as e:
            logger.error(f"Error processing abstract {i}: {e}")
    
    print(f"✅ Successfully processed {len(processed_abstracts)} abstracts")
    
    # Cache the processed data
    print("💾 Caching processed data...")
    await cache_manager.cache_data('prostate', processed_abstracts)
    
    # Generate and cache analysis
    print("📊 Generating analysis and visualizations...")
    
    # Generate summary
    analysis_results = analyzer.analyze_comprehensive_dataset(processed_abstracts)
    summary = {
        'cancer_type': 'prostate',
        'total_studies': len(processed_abstracts),
        'analysis_results': analysis_results,
        'last_updated': datetime.now().isoformat()
    }
    await cache_manager.cache_summary('prostate', summary)
    await cache_manager.cache_analysis_summary('prostate', summary)
    
    # Generate visualizations
    visualizations = visualizer.create_comprehensive_dashboard(processed_abstracts)
    await cache_manager.cache_visualizations('prostate', visualizations)
    
    print("✅ Cache generation completed!")
    print(f"📁 Cache files created in: data/cache/prostate/")
    
    return {
        'total_processed': len(processed_abstracts),
        'cache_location': 'data/cache/prostate/',
        'summary': summary
    }


if __name__ == "__main__":
    print("🚀 Starting Prostate Cancer Cache Generation from Scraped JSON...")
    print("=" * 60)
    
    try:
        results = asyncio.run(process_prostate_from_json())
        print("\n✅ SUCCESS! Cache generated successfully")
        print(f"📊 Total abstracts processed: {results['total_processed']}")
        print("\n🎉 You can now run the main application!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
