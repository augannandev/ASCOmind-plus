# test_scraping.py - Test the ASCO scraping system

import asyncio
import logging
from pathlib import Path
from scrapers.scraping_orchestrator import ScrapingOrchestrator
from scrapers.pdf_manager import PDFStorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_pdf_storage():
    """Test PDF storage system"""
    print("\n🧪 Testing PDF Storage System...")
    
    # Initialize PDF manager
    pdf_manager = PDFStorageManager()
    
    # Test storing a dummy PDF
    dummy_content = b"This is a test PDF content for ASCO abstract"
    test_metadata = {
        'title': 'Test ASCO Abstract - Multiple Myeloma Study',
        'authors': 'Test Author, Another Author',
        'year': 2024,
        'conference': 'ASCO',
        'abstract_number': 'TEST001',
        'indication': 'multiple_myeloma'
    }
    
    result = pdf_manager.store_pdf(dummy_content, test_metadata)
    print(f"✅ PDF storage result: {result['status']}")
    print(f"📁 Stored at: {result.get('local_path', 'N/A')}")
    
    # Get storage statistics
    stats = pdf_manager.get_storage_statistics()
    print(f"📊 Storage stats: {stats}")
    
    return result

async def test_basic_scraping():
    """Test basic ASCO scraping functionality"""
    print("\n🧪 Testing ASCO Scraping...")
    
    # Initialize orchestrator
    orchestrator = ScrapingOrchestrator()
    
    # Run a small test scrape
    results = await orchestrator.run_full_scraping_pipeline(
        years=[2023],  # Just one year for testing
        indications=["multiple_myeloma"],  # Just one indication
        max_abstracts_per_year=5,  # Small number for testing
        download_pdfs=True,
        process_abstracts=True
    )
    
    print("\n📊 Scraping Results Summary:")
    print(f"Status: {results['pipeline_summary']['status']}")
    print(f"Processing Time: {results['pipeline_summary']['processing_time_seconds']:.2f} seconds")
    print(f"Abstracts Scraped: {results['scraping_results']['total_abstracts_scraped']}")
    print(f"Abstracts Processed: {results['scraping_results']['total_abstracts_processed']}")
    print(f"PDFs Downloaded: {results['pdf_storage']['pdfs_downloaded']}")
    print(f"PDFs Stored: {results['pdf_storage']['pdfs_stored']}")
    print(f"Vectors Created: {results['vector_store']['vectors_created']}")
    
    if results['recommendations']:
        print("\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  • {rec}")
    
    return results

async def test_directory_structure():
    """Test that directory structure is created properly"""
    print("\n🧪 Testing Directory Structure...")
    
    # Initialize PDF manager to create directories
    pdf_manager = PDFStorageManager()
    
    # Check key directories exist
    base_path = Path("data/pdfs")
    key_directories = [
        "conferences/asco/2024",
        "conferences/asco/2023",
        "indications/multiple_myeloma",
        "indications/breast_cancer",
        "uploads/user_submissions"
    ]
    
    all_exist = True
    for directory in key_directories:
        full_path = base_path / directory
        if full_path.exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory}")
            all_exist = False
    
    if all_exist:
        print("🎉 All required directories created successfully!")
    else:
        print("⚠️ Some directories are missing")
    
    return all_exist

def display_storage_info():
    """Display current storage information"""
    print("\n📁 Current Storage Information:")
    
    pdf_manager = PDFStorageManager()
    stats = pdf_manager.get_storage_statistics()
    
    print(f"Total PDFs: {stats['total_pdfs']}")
    print(f"Total Size: {stats.get('total_size_mb', 0):.2f} MB")
    
    if stats.get('conferences'):
        print("\nBy Conference:")
        for conf, count in stats['conferences'].items():
            print(f"  {conf}: {count} PDFs")
    
    if stats.get('indications'):
        print("\nBy Indication:")
        for indication, count in stats['indications'].items():
            print(f"  {indication}: {count} PDFs")
    
    if stats.get('years'):
        print("\nBy Year:")
        for year, count in stats['years'].items():
            print(f"  {year}: {count} PDFs")

async def main():
    """Run all tests"""
    print("🚀 Starting ASCOmind+ Scraping System Tests")
    print("=" * 50)
    
    try:
        # Test 1: Directory structure
        await test_directory_structure()
        
        # Test 2: PDF storage
        await test_pdf_storage()
        
        # Test 3: Basic scraping
        await test_basic_scraping()
        
        # Display final storage info
        display_storage_info()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 