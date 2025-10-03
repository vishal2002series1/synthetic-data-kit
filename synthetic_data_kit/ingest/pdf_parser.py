# synthetic_data_kit/ingest/pdf_parser.py
from pdfminer.high_level import extract_text
import os
from .base_parser import BaseParser

class PDFParser(BaseParser):
    """PDF parser using pdfminer.six (exact SDK approach)"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def parse(self, file_path: str) -> str:
        """Extract text from PDF"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File must be a PDF: {file_path}")
        
        try:
            print(f"📄 Parsing PDF: {file_path}")
            text = extract_text(file_path)
            
            if not text or len(text.strip()) == 0:
                raise ValueError(f"No text extracted from PDF: {file_path}")
            
            cleaned_text = self.clean_text(text)
            print(f"✅ Extracted {len(cleaned_text)} characters")
            
            return cleaned_text
            
        except Exception as e:
            print(f"❌ Error parsing PDF {file_path}: {e}")
            raise