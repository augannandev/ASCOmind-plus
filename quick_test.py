#!/usr/bin/env python3
# quick_test.py - Quick test of the scraping system

import asyncio
import logging
from scrapers.scraping_orchestrator import ScrapingOrchestrator

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    print("🚀 Quick ASCO Scraper Test")
    print("=" * 40)
    
    orchestrator = ScrapingOrchestrator()
    
    # Run a small test scrape
    results = await orchestrator.run_full_scraping_pipeline(
        years=[2023],
        indications=["multiple_myeloma"],
        max_abstracts_per_year=3,
        download_pdfs=True,
        process_abstracts=False  # Skip LLM processing for speed
    )
    
    print("\n📊 RESULTS:")
    print(f"Status: {results['pipeline_summary']['status']}")
    print(f"Processing Time: {results['pipeline_summary']['processing_time_seconds']:.2f} seconds")
    print(f"Abstracts Scraped: {results['scraping_results']['total_abstracts_scraped']}")
    print(f"PDFs Downloaded: {results['pdf_storage']['pdfs_downloaded']}")
    print(f"PDFs Stored: {results['pdf_storage']['pdfs_stored']}")
    
    if results['recommendations']:
        print("\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    print("\n✅ Scraper test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 