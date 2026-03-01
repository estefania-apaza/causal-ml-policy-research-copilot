import os
import chromadb
from chromadb.config import Settings

class ChromaDBStore:
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "papers_db"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize the Chroma client with persistence
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def add_chunks(self, chunks: list[dict], embeddings: list[list[float]], batch_size: int = 50):
        """
        Add text chunks and their embeddings to the store in batches to avoid SQLite variable limits.
        """
        if not chunks or not embeddings:
            return
            
        ids = [f"{c['metadata'].get('paper_id', 'unknown')}_{c['chunk_id']}" for c in chunks]
        texts = [c['text'] for c in chunks]
        metadatas = [c['metadata'] for c in chunks]
        
        for i in range(0, len(ids), batch_size):
            self.collection.add(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=texts[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

    def search(self, query_embedding: list[float], n_results: int = 5, where: dict | None = None) -> dict:
        """
        Search for the most similar chunks given a query embedding.
        Returns the ChromaDB query results dict.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=['documents', 'metadatas', 'distances']
        )
        return results
