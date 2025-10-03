# synthetic_data_kit/ingest/base_parser.py
from abc import ABC, abstractmethod
from typing import List

class BaseParser(ABC):
    """Base class for document parsers (following SDK pattern)"""
    
    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Parse document and return text"""
        pass
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text (SDK approach)"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Remove null bytes and special characters
        text = text.replace('\x00', '')
        text = text.replace('\ufffd', '')  # Replacement character
        return text.strip()