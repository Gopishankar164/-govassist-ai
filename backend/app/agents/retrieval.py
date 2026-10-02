from typing import List, Dict, Any
from backend.app.rag.pipeline import rag_pipeline
from backend.app.agents.query_rewriter import query_rewriter_agent

class RetrievalAgent:
    """
    Independent Retrieval Agent module:
    - Invokes Query Rewriting Agent for search optimization
    - Generates BGE embeddings & queries FAISS vector store
    - Retrieves Top 5–10 schemes with Cosine Similarity scores
    """
    @staticmethod
    def execute_retrieval(raw_query: str, profile: Dict[str, Any], top_k: int = 6) -> List[Dict[str, Any]]:
        optimized_query = query_rewriter_agent.rewrite_query(raw_query, profile)
        retrieved_items = rag_pipeline.search_schemes(optimized_query, top_k=top_k)
        return retrieved_items

retrieval_agent = RetrievalAgent()
