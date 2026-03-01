import tiktoken  # type: ignore[import-untyped]
from typing import Optional

class TokenChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, model: str = "gpt-4"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.encoding_for_model(model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> list:  # type: ignore[type-arg]
        """
        Split text into overlapping chunks.
        Returns: List of chunk dictionaries with text and metadata
        """
        tokens = self.encoder.encode(text)
        chunks = []
        start = 0
        chunk_id = 0
        base_meta = metadata if metadata is not None else {}

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text_str = self.encoder.decode(chunk_tokens)
            
            # Build chunk metadata with chunk_id included
            chunk_meta = {}  # type: ignore[var-annotated]
            chunk_meta.update(base_meta)  # type: ignore[arg-type]
            chunk_meta["chunk_id"] = chunk_id
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text_str,
                "token_count": len(chunk_tokens),
                "start_token": start,
                "end_token": end,
                "metadata": chunk_meta,
            })
            
            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1

        return chunks
