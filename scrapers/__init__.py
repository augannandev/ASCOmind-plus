# scrapers/__init__.py - Web scraping package for ASCOmind+

from .asco_scraper import ASCOAbstractScraper
from .pdf_manager import PDFStorageManager

__all__ = ['ASCOAbstractScraper', 'PDFStorageManager'] 