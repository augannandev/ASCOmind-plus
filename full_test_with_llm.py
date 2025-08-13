#!/usr/bin/env python3
# full_test_with_llm.py - Full test including LLM processing

import asyncio
import logging
from scrapers.scraping_orchestrator import ScrapingOrchestrator

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    print("🚀 Full ASCO Scraper Test (with LLM)")
    print("=" * 50)
    print("⚠️  This will use your LLM APIs and take longer!")
    print()
    
    orchestrator = ScrapingOrchestrator()
    
    # Run full pipeline with LLM processing
    results = await orchestrator.run_full_scraping_pipeline(
        years=[2023],
        indications=["multiple_myeloma"],
        max_abstracts_per_year=2,  # Keep small for testing
        download_pdfs=True,
        process_abstracts=True  # 🧠 ENABLE LLM PROCESSING
    )
    
    print("\n📊 FULL PIPELINE RESULTS:")
    print(f"Status: {results['pipeline_summary']['status']}")
    print(f"Processing Time: {results['pipeline_summary']['processing_time_seconds']:.2f} seconds")
    print(f"Abstracts Scraped: {results['scraping_results']['total_abstracts_scraped']}")
    print(f"Abstracts Processed with LLM: {results['scraping_results']['total_abstracts_processed']}")
    print(f"PDFs Downloaded: {results['pdf_storage']['pdfs_downloaded']}")
    print(f"PDFs Stored: {results['pdf_storage']['pdfs_stored']}")
    print(f"Vector Embeddings Created: {results['vector_store']['vectors_created']}")
    
    if results['recommendations']:
        print("\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    # Show processing details
    if results['scraping_results']['total_abstracts_processed'] > 0:
        print("\n🧠 LLM Processing was successful!")
        print("   - Abstracts were processed with metadata extraction")
        print("   - Vector embeddings were created for semantic search")
        print("   - Data is now ready for AI assistant queries")
    
    print("\n✅ Full pipeline test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 