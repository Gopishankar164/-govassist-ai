import os
import json
from typing import List, Dict, Any
from backend.app.rag.vector_store import FAISSVectorStore, vector_store
from backend.app.database import db
from backend.app.config import settings, logger

class TextSplitter:
    """Recursive character text splitter for chunking raw PDF text or documents."""
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start += (self.chunk_size - self.chunk_overlap)
        return [c for c in chunks if c]

class RAGPipeline:
    """
    Production-grade RAG Pipeline leveraging:
    - BGE-small-en-v1.5 Dense Embeddings
    - FAISS Cosine Similarity Vector Index
    - Grounded Context Prompt Construction
    """
    SYSTEM_PROMPT = """You are GovAssist AI, an intelligent research assistant for Indian Government Schemes.

CRITICAL GROUNDEDNESS RULES:
1. Answer ONLY using information retrieved from official government documents provided in the context.
2. NEVER invent schemes, benefits, or eligibility rules not present in the context.
3. Always explain the exact reasons for eligibility matching or restriction.
4. List all required documents clearly.
5. Provide official application portal links.
"""

    def __init__(self):
        self.vector_store = vector_store
        self.splitter = TextSplitter(chunk_size=500, chunk_overlap=50)

    def reload_index(self):
        self.vector_store.reload_index()

    def search_schemes(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vector_store.search(query, top_k=top_k)

    def format_grounded_context(self, retrieved_items: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, item in enumerate(retrieved_items, 1):
            s = item["scheme"]
            name = s.get("name") or s.get("scheme_name") or "Scheme"
            elig = s.get("eligibility", {})
            if isinstance(elig, dict):
                min_age = elig.get("min_age", 0)
                max_age = elig.get("max_age", 100)
                max_income = elig.get("max_income", "N/A")
            else:
                min_age = 0
                max_age = 100
                max_income = "N/A"

            docs = ", ".join(s.get("documents_required") or s.get("required_documents") or [])
            url = s.get("application_url") or s.get("official_application_url") or "#"
            score_val = item.get("score") if item.get("score") is not None else item.get("vector_similarity", 0.0)
            
            block = (
                f"--- DOCUMENT {idx}: {name} (Cosine Sim Score: {score_val:.4f}) ---\n"
                f"Category: {s.get('category', 'General')}\n"
                f"Target Audience: {s.get('target_audience', 'Citizens')}\n"
                f"Description: {s.get('description', '')}\n"
                f"Benefits: {s.get('benefits', '')}\n"
                f"Eligibility Limits: Max Income ₹{max_income}, Age {min_age}-{max_age}\n"
                f"Required Documents: {docs}\n"
                f"Official Portal: {url}\n"
            )
            context_blocks.append(block)
        return "\n".join(context_blocks)

rag_pipeline = RAGPipeline()
