# synthetic_data_kit/utils/chunker.py
from typing import List

def chunk_text(text: str, chunk_size: int = 4000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunk text into overlapping segments (exact SDK approach)
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) == 0:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Get chunk
        chunk = text[start:end]
        
        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk)
        
        # Move start position (with overlap)
        start = end - chunk_overlap
        
        # Break if we've reached the end
        if end >= text_length:
            break
    
    return chunks