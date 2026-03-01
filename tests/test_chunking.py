import pytest
from src.chunking.chunker import TokenChunker

def test_chunk_size():
    chunker = TokenChunker(chunk_size=100, chunk_overlap=0)
    text = "This is a test. " * 50 # Long enough to create multiple chunks
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk['token_count'] <= 100

def test_overlap():
    chunk_size = 50
    overlap = 10
    chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=overlap)
    text = "Machine learning research is evolving fast. " * 20
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 1
    # Check that chunk tokens are being advanced correctly
    assert chunks[1]['start_token'] == chunk_size - overlap

def test_metadata_persistence():
    chunker = TokenChunker(chunk_size=500, chunk_overlap=0)
    meta = {"paper_id": "P001", "year": "2023"}
    chunks = chunker.chunk_text("Sample text content", metadata=meta)
    
    assert len(chunks) == 1
    assert chunks[0]['metadata']['paper_id'] == "P001"
    assert chunks[0]['metadata']['year'] == "2023"
    assert 'chunk_id' in chunks[0]['metadata']
