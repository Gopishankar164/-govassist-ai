"""End-to-end GovAssist RAG orchestration over the persisted BGE/FAISS index."""
import time
from typing import Dict, Any

from src.config import DEFAULT_TOP_K, FINAL_TOP_N
from src.embeddings import embed_query, load_embedding_model
from src.eligibility import analyze_eligibility
from src.generator import build_grounded_answer
from src.profile import extract_profile, merge_profiles
from src.query_rewriter import rewrite_query
from src.reranker import classify_query_domain, rerank
from src.vector_store import SchemeVectorStore


class GovAssistPipeline:
    def __init__(self):
        self.model = load_embedding_model()
        self.store = SchemeVectorStore.load()

    def recommend(self, query: str, top_k: int = DEFAULT_TOP_K, final_n: int = FINAL_TOP_N, use_domain_intent: bool = False, base_profile: Dict[str, Any] | None = None, state_filter: str | None = None, category_filter: str | None = None) -> Dict:
        if not query or not query.strip():
            raise ValueError("A non-empty user query is required.")
        
        extracted_facts = extract_profile(query)
        profile = merge_profiles(base_profile, extracted_facts)
        
        rewritten_query = rewrite_query(query, profile)
        
        start = time.perf_counter()
        
        # We fetch more candidates from FAISS if filtering is enabled, then apply strict filters
        fetch_k = top_k * 5 if (state_filter or category_filter) else top_k
        
        retrieved = self.store.search(embed_query(rewritten_query, self.model), top_k=fetch_k)
        
        # Apply strict dataset filters
        filtered_retrieved = []
        for r in retrieved:
            scheme = r["scheme"]
            if state_filter and scheme.get("state") and scheme["state"].lower() != state_filter.lower():
                continue
            if category_filter and scheme.get("category") and scheme["category"].lower() != category_filter.lower():
                continue
            filtered_retrieved.append(r)
            
        retrieved = filtered_retrieved[:top_k]
        retrieval_latency_ms = (time.perf_counter() - start) * 1000
        
        analyzed = []
        for result in retrieved:
            result.update(analyze_eligibility(result["scheme"], profile))
            analyzed.append(result)
            
        recommendations = rerank(analyzed, limit=final_n, query=query, profile=profile, use_domain_intent=use_domain_intent)
        
        # Calculate domain intent
        query_domain = classify_query_domain(query, profile)
        
        result = {
            "user_query": query, 
            "profile": profile, # This is the newly enriched profile, which the backend will save
            "rewritten_query": rewritten_query,
            "retrieved_schemes": analyzed, 
            "recommendations": recommendations,
            "retrieval_latency_ms": retrieval_latency_ms,
            "answer": build_grounded_answer(recommendations, profile, query_domain),
            "query_domain": query_domain,
        }
        
        if not use_domain_intent:
            result["query_domain"] = query_domain
            
        return result

    def handle_conversation_turn(self, query: str, profile: Dict[str, Any], context: list[Dict[str, Any]]) -> Dict:
        """Handle a multi-turn conversational query, preserving context and matching follow-ups."""
        lower_query = query.lower()
        
        # Check if it's a follow up
        is_followup = False
        followup_answer = ""
        
        if context:
            top_scheme = context[0]
            scheme_name = top_scheme.get("scheme_name", "the scheme")
            
            if any(k in lower_query for k in ["which", "best"]):
                is_followup = True
                followup_answer = f"Based on your profile, the best option is '{scheme_name}'. It was ranked highest due to your eligibility."
            elif any(k in lower_query for k in ["document", "docs"]):
                is_followup = True
                docs = top_scheme.get("documents") or top_scheme.get("required_documents") or "Not explicitly stated."
                followup_answer = f"For '{scheme_name}', you will need the following documents:\n{docs}"
            elif any(k in lower_query for k in ["eligibility", "requirements", "eligible"]):
                is_followup = True
                elig = top_scheme.get("eligibility") or top_scheme.get("eligibility_text") or "Not explicitly stated."
                followup_answer = f"The eligibility requirements for '{scheme_name}' are:\n{elig}"
            elif any(k in lower_query for k in ["how much", "assistance", "benefit", "money"]):
                is_followup = True
                ben = top_scheme.get("benefits") or "Not explicitly stated."
                followup_answer = f"The financial assistance/benefits for '{scheme_name}' are:\n{ben}"
            elif any(k in lower_query for k in ["link", "url", "apply", "application"]):
                is_followup = True
                url = top_scheme.get("source_url") or top_scheme.get("official_url") or top_scheme.get("application") or "No official link available."
                followup_answer = f"The official application link/process for '{scheme_name}' is:\n{url}"

        if is_followup:
            return {
                "user_query": query,
                "profile": profile,
                "rewritten_query": query,
                "retrieved_schemes": [],
                "recommendations": context, # return the previous recommendations to persist in UI
                "retrieval_latency_ms": 0,
                "answer": followup_answer,
                "query_domain": "followup",
            }
            
        # Not a follow up, do normal retrieval
        return self.recommend(query, base_profile=profile)
