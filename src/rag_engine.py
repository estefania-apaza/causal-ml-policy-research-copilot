import os
import json
from dotenv import load_dotenv

# Load env vars from project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.text_cleaner import clean_extracted_text
from src.chunking.chunker import TokenChunker
from src.embedding.embedder import OpenAIEmbedder
from src.vectorstore.chroma_store import ChromaDBStore
from src.retrieval.retriever import Retriever
from src.generation.generator import Generator

class RAGPipeline:
    __version__ = "2.0.0"
    def __init__(self, project_root: str = None, chunk_size: int = 512):
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.project_root = project_root
        db_path = os.path.join(project_root, "chroma_db")
        self.prompts_dir = os.path.join(project_root, "prompts")
        
        self.chunker = TokenChunker(chunk_size=chunk_size, chunk_overlap=50)
        self.embedder = OpenAIEmbedder(model_name="text-embedding-3-small")
        self.vector_store = ChromaDBStore(persist_directory=db_path)
        self.retriever = Retriever(embedder=self.embedder, vector_store=self.vector_store)
        self.generator = Generator(model_name="gpt-4-turbo-preview")

    def format_apa_citation(self, title: str, authors_str: str, year: str) -> str:
        """Formats authors according to APA rules: First Author et al. for 3+ authors."""
        authors = [a.strip() for a in authors_str.split(",") if a.strip()]
        if not authors:
            return f"Unknown ({year})"
        
        if len(authors) == 1:
            ref = authors[0]
        elif len(authors) == 2:
            ref = f"{authors[0]} & {authors[1]}"
        else:
            ref = f"{authors[0]} et al."
            
        return f"{ref} ({year})"
        
    def add_paper(self, pdf_path: str, paper_metadata: dict) -> int:
        """
        Process a PDF and add its chunks to the vector store.
        Returns number of chunks added.
        """
        paper_id = paper_metadata.get('id', 'unknown')
        
        # 1. Extract
        ext_result = extract_text_from_pdf(pdf_path)
        
        # 2. Clean
        cleaned_text = clean_extracted_text(ext_result.get('text', ''))
        
        if not cleaned_text or len(cleaned_text.strip()) < 50:
            return 0  # Skip documents with almost no extractable text
        
        # 3. Chunk  — All metadata values MUST be strings for ChromaDB
        metadata = {
            "paper_id": paper_id,
            "title": str(paper_metadata.get('title', 'Unknown Title')),
            "authors": ", ".join(paper_metadata.get('authors', [])),
            "year": str(paper_metadata.get('year', '')),
            "doi": str(paper_metadata.get('doi', '')),
        }
        chunks = self.chunker.chunk_text(cleaned_text, metadata=metadata)
        
        if not chunks:
            return 0
        
        # 4. Embed
        texts = [c['text'] for c in chunks]
        embeddings = self.embedder.embed_batch(texts)
        
        # 5. Store in batches
        self.vector_store.add_chunks(chunks, embeddings)
        return len(chunks)
        
    def answer_question(self, question: str, strategy: str = "v1_delimiters", paper_id: str | None = None, history: list = None) -> str:
        """
        Answers a user question based on the selected prompt strategy and optional chat history.
        """
        # 1. Retrieve
        retrieved = self.retriever.retrieve(question, top_k=5, paper_id=paper_id)
        if not retrieved:
            return "No relevant context found in the ingested papers. Please make sure PDFs have been ingested on the Papers page."
            
        context = self.retriever.format_context(retrieved)
        
        # 2. Load Prompt (using absolute path)
        prompt_path = os.path.join(self.prompts_dir, f"{strategy}.txt")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template not found: {prompt_path}")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
            
        # 3. Generate
        if strategy == "v2_json_output":
            ans_dict = self.generator.generate_json_answer(system_prompt, context, question, history=history)
            return json.dumps(ans_dict, indent=2)
        else:
            return self.generator.generate_answer(system_prompt, context, question, history=history)
