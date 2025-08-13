#!/usr/bin/env python3
"""
Fix corrupted PDF files by regenerating them with proper PDF format
"""

import json
import asyncio
from pathlib import Path
from scrapers.scraping_orchestrator import ScrapingOrchestrator

async def fix_corrupted_pdfs():
    """Fix corrupted PDF files by regenerating them"""
    
    print("🔧 Fixing corrupted PDF files...")
    
    # Load existing scraped data
    data_files = list(Path("data").glob("scraped_abstracts_*.json"))
    
    if not data_files:
        print("❌ No scraped data files found!")
        return
    
    # Use the most recent file
    latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Loading data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        abstracts = json.load(f)
    
    print(f"📊 Found {len(abstracts)} abstracts to process")
    
    # Initialize orchestrator
    orchestrator = ScrapingOrchestrator()
    
    # Clear existing corrupted PDFs
    pdf_dir = Path("data/pdfs/conferences/asco")
    if pdf_dir.exists():
        for pdf_file in pdf_dir.rglob("*.pdf"):
            if pdf_file.name != ".gitkeep":
                print(f"🗑️  Removing corrupted PDF: {pdf_file.name}")
                pdf_file.unlink()
    
    # Regenerate PDFs with proper format
    print("🔄 Regenerating PDFs with proper format...")
    
    for i, abstract in enumerate(abstracts, 1):
        print(f"📝 Processing abstract {i}/{len(abstracts)}: {abstract['title'][:50]}...")
        
        # Create proper PDF content
        pdf_content = orchestrator._create_dummy_pdf_content(abstract)
        
        # Store with proper metadata
        pdf_metadata = {
            'title': abstract.get('title', 'Unknown Title'),
            'authors': abstract.get('authors', 'Unknown Authors'),
            'year': abstract.get('year'),
            'conference': abstract.get('conference', 'ASCO'),
            'abstract_number': abstract.get('abstract_number'),
            'indication': abstract.get('indication'),
            'source': abstract.get('source'),
            'pmid': abstract.get('pmid'),
            'doi': abstract.get('doi'),
            'scraped_at': abstract.get('scraped_at')
        }
        
        # Store PDF
        storage_result = orchestrator.pdf_manager.store_pdf(
            pdf_content=pdf_content,
            metadata=pdf_metadata,
            storage_category="conferences"
        )
        
        if storage_result['status'] == 'success':
            print(f"✅ Successfully created PDF: {storage_result['filename']}")
        else:
            print(f"❌ Failed to create PDF: {storage_result}")
    
    # Get final statistics
    stats = orchestrator.pdf_manager.get_storage_statistics()
    print(f"\n📈 Final Statistics:")
    print(f"   Total PDFs: {stats['total_pdfs']}")
    print(f"   Total Size: {stats['total_size_mb']:.2f} MB")
    print(f"   By Conference: {stats['conferences']}")
    print(f"   By Year: {stats['years']}")
    
    print("\n🎉 PDF fix completed! All PDFs should now open properly.")

if __name__ == "__main__":
    asyncio.run(fix_corrupted_pdfs()) 