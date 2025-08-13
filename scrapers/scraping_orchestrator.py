# scrapers/scraping_orchestrator.py - Complete Scraping & Storage System

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .asco_scraper import ASCOAbstractScraper
from .pdf_manager import PDFStorageManager
from agents.metadata_extractor import EnhancedMetadataExtractor
from agents.vector_store import IntelligentVectorStore

class ScrapingOrchestrator:
    """Orchestrates the complete scraping, storage, and processing pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pdf_manager = PDFStorageManager()
        self.metadata_extractor = EnhancedMetadataExtractor()
        
        # Global session for scraped data
        self.global_session_id = "scraped_portal_data"
        self.vector_store = IntelligentVectorStore(session_id=self.global_session_id)
        
        # Processing statistics
        self.processing_stats = {
            'total_scraped': 0,
            'total_processed': 0,
            'pdfs_downloaded': 0,
            'pdfs_stored': 0,
            'vectors_created': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def run_full_scraping_pipeline(self, 
                                       years: List[int] = None,
                                       indications: List[str] = None,
                                       max_abstracts_per_year: int = 20,
                                       download_pdfs: bool = True,
                                       process_abstracts: bool = True) -> Dict[str, Any]:
        """Run the complete scraping and processing pipeline"""
        
        self.processing_stats['start_time'] = datetime.now()
        self.logger.info("🚀 Starting full ASCO scraping pipeline...")
        
        try:
            # Step 1: Scrape abstracts
            self.logger.info("📥 Step 1: Scraping ASCO abstracts...")
            scraped_abstracts = await self._scrape_abstracts(years, indications, max_abstracts_per_year)
            self.processing_stats['total_scraped'] = len(scraped_abstracts)
            
            if not scraped_abstracts:
                self.logger.warning("No abstracts were scraped. Ending pipeline.")
                return self._generate_final_report()
            
            # Step 2: Download and store PDFs
            if download_pdfs:
                self.logger.info("📄 Step 2: Downloading and storing PDFs...")
                await self._download_and_store_pdfs(scraped_abstracts)
            
            # Step 3: Process abstracts with LLM
            if process_abstracts:
                self.logger.info("🧠 Step 3: Processing abstracts with LLM...")
                await self._process_abstracts_with_llm(scraped_abstracts)
            
            # Step 4: Generate summary
            self.processing_stats['end_time'] = datetime.now()
            final_report = self._generate_final_report()
            
            self.logger.info("✅ Scraping pipeline completed successfully!")
            return final_report
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            self.processing_stats['errors'] += 1
            self.processing_stats['end_time'] = datetime.now()
            return self._generate_final_report()
    
    async def _scrape_abstracts(self, 
                              years: List[int],
                              indications: List[str],
                              max_abstracts_per_year: int) -> List[Dict[str, Any]]:
        """Scrape abstracts using the ASCO scraper"""
        
        if not years:
            years = [2024, 2023, 2022]
        
        if not indications:
            indications = ["multiple_myeloma", "breast_cancer", "lung_cancer"]
        
        try:
            async with ASCOAbstractScraper() as scraper:
                abstracts = await scraper.scrape_asco_abstracts(
                    years=years,
                    indications=indications,
                    max_abstracts=max_abstracts_per_year * len(years)
                )
                
                # Save raw scraped data
                scraper.save_abstracts_to_json(abstracts)
                
                # Get scraping statistics
                scraping_stats = scraper.get_scraping_statistics(abstracts)
                self.logger.info(f"📊 Scraping stats: {scraping_stats}")
                
                return abstracts
                
        except Exception as e:
            self.logger.error(f"Error in scraping phase: {e}")
            return []
    
    async def _download_and_store_pdfs(self, abstracts: List[Dict[str, Any]]):
        """Download PDFs and store them locally"""
        
        pdf_download_tasks = []
        
        for abstract in abstracts:
            if abstract.get('pdf_url'):
                task = self._download_and_store_single_pdf(abstract)
                pdf_download_tasks.append(task)
        
        if pdf_download_tasks:
            self.logger.info(f"📥 Downloading {len(pdf_download_tasks)} PDFs...")
            results = await asyncio.gather(*pdf_download_tasks, return_exceptions=True)
            
            # Count successful downloads
            successful_downloads = sum(1 for result in results if not isinstance(result, Exception))
            self.processing_stats['pdfs_downloaded'] = successful_downloads
            
            self.logger.info(f"✅ Successfully downloaded {successful_downloads}/{len(pdf_download_tasks)} PDFs")
    
    async def _download_and_store_single_pdf(self, abstract: Dict[str, Any]) -> bool:
        """Download and store a single PDF"""
        try:
            pdf_url = abstract.get('pdf_url')
            if not pdf_url:
                return False
            
            # Note: For demo purposes, we'll create a dummy PDF
            # In real implementation, this would download from the actual URL
            dummy_pdf_content = self._create_dummy_pdf_content(abstract)
            
            # Prepare metadata for storage
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
            storage_result = self.pdf_manager.store_pdf(
                pdf_content=dummy_pdf_content,
                metadata=pdf_metadata,
                storage_category="conferences"
            )
            
            if storage_result['status'] == 'success':
                self.processing_stats['pdfs_stored'] += 1
                # Update abstract with storage info
                abstract['pdf_storage'] = storage_result
                return True
            else:
                self.logger.warning(f"Failed to store PDF: {storage_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading/storing PDF: {e}")
            self.processing_stats['errors'] += 1
            return False
    
    def _create_dummy_pdf_content(self, abstract: Dict[str, Any]) -> bytes:
        """Create proper PDF content for demonstration"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import darkblue, black
            from io import BytesIO
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
            
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=darkblue
            )
            
            story = []
            
            # Header
            story.append(Paragraph(f"ASCO Abstract - {abstract.get('year', 'Unknown Year')}", styles['Title']))
            story.append(Spacer(1, 20))
            
            # Main title
            title = abstract.get('title', 'Unknown Title')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Authors
            authors = abstract.get('authors', 'Unknown Authors')
            story.append(Paragraph(f"<b>Authors:</b> {authors}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Abstract number
            abs_num = abstract.get('abstract_number', 'Unknown')
            story.append(Paragraph(f"<b>Abstract Number:</b> {abs_num}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Abstract text
            story.append(Paragraph("<b>Abstract:</b>", styles['Heading2']))
            abstract_text = abstract.get('abstract_text', 'No abstract text available')
            story.append(Paragraph(abstract_text, styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Metadata
            story.append(Paragraph(f"<b>Source:</b> {abstract.get('source', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"<b>Indication:</b> {abstract.get('indication', 'Unknown')}", styles['Normal']))
            story.append(Paragraph(f"<b>Scraped:</b> {abstract.get('scraped_at', 'Unknown')}", styles['Normal']))
            
            if abstract.get('pmid'):
                story.append(Paragraph(f"<b>PMID:</b> {abstract['pmid']}", styles['Normal']))
            
            if abstract.get('doi'):
                story.append(Paragraph(f"<b>DOI:</b> {abstract['doi']}", styles['Normal']))
            
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except ImportError:
            # Fallback to text content if reportlab not available
            self.logger.warning("reportlab not available, creating text-based content")
            content = f"""
ASCO Abstract - {abstract.get('year', 'Unknown Year')}

Title: {abstract.get('title', 'Unknown Title')}

Authors: {abstract.get('authors', 'Unknown Authors')}

Abstract Number: {abstract.get('abstract_number', 'Unknown')}

Abstract Text:
{abstract.get('abstract_text', 'No abstract text available')}

Source: {abstract.get('source', 'Unknown')}
Indication: {abstract.get('indication', 'Unknown')}
Scraped: {abstract.get('scraped_at', 'Unknown')}
            """.strip().encode('utf-8')
            
            return content
    
    async def _process_abstracts_with_llm(self, abstracts: List[Dict[str, Any]]):
        """Process abstracts using LLM for metadata extraction and vectorization"""
        
        processing_tasks = []
        
        for abstract in abstracts:
            task = self._process_single_abstract(abstract)
            processing_tasks.append(task)
        
        if processing_tasks:
            self.logger.info(f"🧠 Processing {len(processing_tasks)} abstracts with LLM...")
            results = await asyncio.gather(*processing_tasks, return_exceptions=True)
            
            # Count successful processing
            successful_processing = sum(1 for result in results if not isinstance(result, Exception))
            self.processing_stats['total_processed'] = successful_processing
            
            self.logger.info(f"✅ Successfully processed {successful_processing}/{len(processing_tasks)} abstracts")
    
    async def _process_single_abstract(self, abstract: Dict[str, Any]) -> bool:
        """Process a single abstract with LLM extraction and vectorization"""
        try:
            # Prepare abstract text for processing
            abstract_text = f"{abstract.get('title', '')}\n\n{abstract.get('abstract_text', '')}"
            
            if not abstract_text.strip():
                self.logger.warning("Empty abstract text, skipping...")
                return False
            
            # Extract comprehensive metadata using LLM
            extracted_metadata = await self.metadata_extractor.extract_comprehensive_metadata(
                abstract_text,
                source_info={
                    'conference': abstract.get('conference', 'ASCO'),
                    'year': abstract.get('year'),
                    'abstract_number': abstract.get('abstract_number'),
                    'authors': abstract.get('authors'),
                    'pmid': abstract.get('pmid'),
                    'doi': abstract.get('doi'),
                    'indication': abstract.get('indication')
                }
            )
            
            # Set source information
            extracted_metadata.source_text = abstract_text
            extracted_metadata.source_file = f"scraped_abstract_{abstract.get('abstract_number', 'unknown')}"
            
            # Create vector embeddings
            embedding_result = await self.vector_store.embed_abstract(extracted_metadata)
            
            if embedding_result['status'] == 'success':
                self.processing_stats['vectors_created'] += 1
                # Store processing results in abstract
                abstract['llm_processing'] = {
                    'metadata': extracted_metadata.model_dump(),
                    'embedding_result': embedding_result
                }
                return True
            else:
                self.logger.warning(f"Failed to create embeddings: {embedding_result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing abstract: {e}")
            self.processing_stats['errors'] += 1
            return False
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        processing_time = None
        if self.processing_stats['start_time'] and self.processing_stats['end_time']:
            processing_time = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
        
        # Get storage statistics
        storage_stats = self.pdf_manager.get_storage_statistics()
        
        # Get vector store statistics
        vector_stats = self.vector_store.get_statistics()
        
        report = {
            'pipeline_summary': {
                'status': 'completed' if self.processing_stats['errors'] == 0 else 'completed_with_errors',
                'processing_time_seconds': processing_time,
                'start_time': self.processing_stats['start_time'].isoformat() if self.processing_stats['start_time'] else None,
                'end_time': self.processing_stats['end_time'].isoformat() if self.processing_stats['end_time'] else None
            },
            'scraping_results': {
                'total_abstracts_scraped': self.processing_stats['total_scraped'],
                'total_abstracts_processed': self.processing_stats['total_processed'],
                'success_rate': (
                    self.processing_stats['total_processed'] / self.processing_stats['total_scraped']
                    if self.processing_stats['total_scraped'] > 0 else 0
                )
            },
            'pdf_storage': {
                'pdfs_downloaded': self.processing_stats['pdfs_downloaded'],
                'pdfs_stored': self.processing_stats['pdfs_stored'],
                'storage_statistics': storage_stats
            },
            'vector_store': {
                'vectors_created': self.processing_stats['vectors_created'],
                'vector_statistics': vector_stats
            },
            'errors': {
                'total_errors': self.processing_stats['errors']
            },
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on processing results"""
        recommendations = []
        
        if self.processing_stats['total_scraped'] == 0:
            recommendations.append("No abstracts were scraped. Check scraping configuration and network connectivity.")
        
        if self.processing_stats['pdfs_downloaded'] < self.processing_stats['total_scraped']:
            recommendations.append("Some PDFs failed to download. Consider implementing retry logic for failed downloads.")
        
        if self.processing_stats['total_processed'] < self.processing_stats['total_scraped']:
            recommendations.append("Some abstracts failed LLM processing. Check API keys and rate limits.")
        
        if self.processing_stats['errors'] > 0:
            recommendations.append(f"Pipeline encountered {self.processing_stats['errors']} errors. Review logs for details.")
        
        if self.processing_stats['vectors_created'] > 0:
            recommendations.append("Vectorization successful! You can now use the AI assistant to query the scraped data.")
        
        return recommendations
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            'stats': self.processing_stats.copy(),
            'storage_stats': self.pdf_manager.get_storage_statistics(),
            'vector_stats': self.vector_store.get_statistics()
        } 