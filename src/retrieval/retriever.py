class Retriever:
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, paper_id: str = None) -> list[dict]:
        """
        Retrieves top_k most relevant chunks for the given query.
        Optionally filter by paper_id.
        """
        query_embedding = self.embedder.embed_text(query)
        
        where = None
        if paper_id:
            where = {"paper_id": paper_id}
            
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where
        )
        
        # Format results into a cleaner list of dictionaries
        formatted_results = []
        if isinstance(results, dict) and results.get('documents') and results['documents'][0]:
            docs = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            for doc, meta, dist in zip(docs, metadatas, distances):
                formatted_results.append({
                    "text": doc,
                    "metadata": meta,
                    "distance": dist
                })
                
        return formatted_results

    def format_context(self, retrieved_chunks: list[dict]) -> str:
        """
        Formats retrieved chunks into a single context string for the LLM.
        """
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            meta = chunk['metadata']
            paper_id = meta.get('paper_id', 'Unknown')
            authors_str = meta.get('authors', 'Unknown Authors')
            year = meta.get('year', 'Unknown Year')
            
            # APA et al. logic
            authors = [a.strip() for a in authors_str.split(",") if a.strip()]
            if not authors:
                citation = f"({year})"
            elif len(authors) == 1:
                citation = f"({authors[0]}, {year})"
            elif len(authors) == 2:
                citation = f"({authors[0]} & {authors[1]}, {year})"
            else:
                citation = f"({authors[0]} et al., {year})"
            
            context_parts.append(f"--- [Source: {paper_id}] {citation} ---\n{chunk['text']}")
            
        return "\n\n".join(context_parts)
