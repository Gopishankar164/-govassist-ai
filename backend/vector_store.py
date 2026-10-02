"""
Bridge layer ensuring backward compatibility for legacy imports.
Points directly to backend/app/rag/vector_store.py (FAISSVectorStore).
"""
from backend.app.rag.vector_store import FAISSVectorStore as EmbeddingVectorStore, vector_store

__all__ = ["EmbeddingVectorStore", "vector_store"]
