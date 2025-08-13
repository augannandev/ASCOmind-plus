#!/usr/bin/env python3
"""
Test ASCO website scraping functionality
"""

import asyncio
import json
from scrapers.asco_scraper import ASCOAbstractScraper

async def test_asco_website_scraping():
    """Test the new ASCO website scraping functionality"""
    
    print("🔬 Testing ASCO Website Scraping...")
    print("=" * 50)
    
    # Initialize scraper
    async with ASCOAbstractScraper() as scraper:
        
        # Test parameters
        test_years = [2023]
        test_indications = ["multiple_myeloma"]
        max_abstracts = 5
        
        print(f"📋 Test Parameters:")
        print(f"   Years: {test_years}")
        print(f"   Indications: {test_indications}")
        print(f"   Max abstracts: {max_abstracts}")
        print()
        
        # Run scraping
        print("🕸️  Starting ASCO website scraping...")
        abstracts = await scraper.scrape_asco_abstracts(
            years=test_years,
            indications=test_indications,
            max_abstracts=max_abstracts
        )
        
        print(f"✅ Scraping completed!")
        print(f"📊 Total abstracts found: {len(abstracts)}")
        print()
        
        # Analyze results by source
        sources = {}
        for abstract in abstracts:
            source = abstract.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print("📈 Results by Source:")
        for source, count in sources.items():
            print(f"   {source}: {count} abstracts")
        print()
        
        # Show sample abstracts
        print("📝 Sample Abstracts:")
        print("-" * 40)
        
        for i, abstract in enumerate(abstracts[:3], 1):
            print(f"\n{i}. {abstract['title'][:80]}...")
            print(f"   Authors: {abstract['authors'][:60]}...")
            print(f"   Source: {abstract['source']}")
            print(f"   Year: {abstract['year']}")
            if abstract.get('abstract_number'):
                print(f"   Abstract #: {abstract['abstract_number']}")
            if abstract.get('pdf_url'):
                print(f"   PDF URL: {abstract['pdf_url']}")
        
        # Save results
        timestamp = "test_asco_website"
        filename = f"data/scraped_abstracts_{timestamp}.json"
        scraper.save_abstracts_to_json(abstracts, filename)
        
        # Get statistics
        stats = scraper.get_scraping_statistics(abstracts)
        
        print(f"\n📊 Scraping Statistics:")
        print(f"   Total abstracts: {stats['total_abstracts']}")
        print(f"   By year: {stats['by_year']}")
        print(f"   By indication: {stats['by_indication']}")
        print(f"   By source: {stats['by_source']}")
        print(f"   With PDFs: {stats['with_pdfs']}")
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Test specific ASCO methods
        print(f"\n🔍 Testing Direct ASCO Methods:")
        print("-" * 40)
        
        # Test meeting library search
        print("Testing ASCO Meeting Library...")
        meeting_results = await scraper._search_asco_meeting_library(2023, "multiple_myeloma", 3)
        print(f"Meeting library results: {len(meeting_results)}")
        
        # Test alternative search
        print("Testing ASCO Alternative Search...")
        alt_results = await scraper._search_asco_alternative(2023, "multiple_myeloma", 3)
        print(f"Alternative search results: {len(alt_results)}")
        
        print(f"\n🎯 ASCO Website Testing Complete!")
        
        return abstracts

if __name__ == "__main__":
    results = asyncio.run(test_asco_website_scraping()) 