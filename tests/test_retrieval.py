import pytest
from unittest.mock import MagicMock
from src.retrieval.retriever import Retriever

def test_retriever_formatting():
    # Mock embedder and vector store
    mock_embed = MagicMock()
    mock_store = MagicMock()
    
    retriever = Retriever(embedder=mock_embed, vector_store=mock_store)
    
    # Mock retrieved chunks
    sample_docs = [
        {"text": "Context piece 1", "metadata": {"title": "Title 1", "paper_id": "P1"}},
        {"text": "Context piece 2", "metadata": {"title": "Title 2", "paper_id": "P2"}}
    ]
    
    formatted = retriever.format_context(sample_docs)
    
    assert "Context piece 1" in formatted
    assert "Context piece 2" in formatted
    assert "[Source: P1]" in formatted or "P1" in formatted

def test_retrieval_logic_call():
    mock_embed = MagicMock()
    mock_embed.embed_text.return_value = [0.1, 0.2]
    
    mock_store = MagicMock()
    # Mock ChromaDB-style dict response: { 'documents': [ [...] ], 'metadatas': [ [...] ], 'distances': [ [...] ] }
    mock_store.search.return_value = {
        "documents": [["result"]],
        "metadatas": [[{"paper_id": "P1"}]],
        "distances": [[0.1]]
    }
    
    retriever = Retriever(embedder=mock_embed, vector_store=mock_store)
    results = retriever.retrieve("query", top_k=2)
    
    assert len(results) == 1
    assert results[0]['text'] == "result"
    mock_embed.embed_text.assert_called_once()
    mock_store.search.assert_called_once()
