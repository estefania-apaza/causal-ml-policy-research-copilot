import os
import time
from openai import OpenAI

# Initialize the OpenAI client (expects OPENAI_API_KEY in environment)
client = OpenAI()

class OpenAIEmbedder:
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single string of text.
        """
        response = client.embeddings.create(
            input=text,
            model=self.model_name
        )
        return response.data[0].embedding

    def embed_batch(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        """
        Generate embeddings for a batch of strings safely without exceeding API limits.
        """
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = client.embeddings.create(input=batch, model=self.model_name)
                all_embeddings.extend([data.embedding for data in response.data])
            except Exception as e:
                print(f"API Limit or Error hit: {e}. Retrying in 5 seconds...")
                time.sleep(5)
                response = client.embeddings.create(input=batch, model=self.model_name)
                all_embeddings.extend([data.embedding for data in response.data])
                
        return all_embeddings
