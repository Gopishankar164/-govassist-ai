import time
from typing import Dict, Any, List
from backend.app.agents.memory import memory_agent
from backend.app.agents.profile import profile_agent
from backend.app.agents.query_rewriter import query_rewriter_agent
from backend.app.agents.retrieval import retrieval_agent
from backend.app.agents.eligibility import eligibility_agent
from backend.app.agents.verification import verification_agent
from backend.app.agents.llm_grounding import llm_grounded_agent
from backend.app.agents.explanation import explanation_agent
from backend.app.agents.translation import translation_agent
from backend.app.config import logger

class CoordinatorAgent:
    """
    Independent Coordinator Agent module:
    - Receives incoming user request
    - Manages workflow trace lifecycle
    - Coordinates downstream agent execution
    - Merges and returns structured agent state payload
    """
    def execute_workflow(self, session_id: str, query: str, profile: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        trace = []

        # 1. Memory Agent
        trace.append({"step": "Checking Memory", "status": "COMPLETED", "agent": "Memory Agent", "timestamp": time.time()})
        merged_profile = memory_agent.merge_profile(session_id, profile)

        # 2. Profile Extraction Agent
        trace.append({"step": "Extracting Profile", "status": "COMPLETED", "agent": "Profile Agent", "timestamp": time.time()})
        extracted_profile = profile_agent.extract_profile_from_text(query, merged_profile)
        missing_fields = profile_agent.identify_missing_fields(extracted_profile)

        # 3. Query Rewriting Agent
        trace.append({"step": "Rewriting Query", "status": "COMPLETED", "agent": "Query Rewriting Agent", "timestamp": time.time()})
        optimized_query = query_rewriter_agent.rewrite_query(query, extracted_profile)

        # 4. Retrieval Agent (Embedding Model + FAISS Top-K)
        trace.append({"step": "Searching FAISS Database", "status": "COMPLETED", "agent": "Retrieval Agent", "timestamp": time.time()})
        retrieved_items = retrieval_agent.execute_retrieval(query, extracted_profile, top_k=6)

        # 5. Eligibility Agent (Multi-tier rule evaluation & confidence scoring)
        trace.append({"step": "Checking Eligibility Rules", "status": "COMPLETED", "agent": "Eligibility Agent", "timestamp": time.time()})
        evaluated_items = eligibility_agent.evaluate_retrieved_items(extracted_profile, retrieved_items)

        # 6. Verification Agent (Grounding & anti-hallucination check)
        trace.append({"step": "Verifying Documents", "status": "COMPLETED", "agent": "Verification Agent", "timestamp": time.time()})
        verified_items = verification_agent.verify_documents(evaluated_items)

        # 7. LLM Grounded Prompt Synthesis Agent
        trace.append({"step": "Synthesizing Grounded LLM Response", "status": "COMPLETED", "agent": "LLM Grounded Agent", "timestamp": time.time()})
        grounded_summary = llm_grounded_agent.generate_grounded_response(query, extracted_profile, verified_items)

        # 8. Explanation Agent
        trace.append({"step": "Formulating Explanation", "status": "COMPLETED", "agent": "Explanation Agent", "timestamp": time.time()})
        explained_summary = explanation_agent.format_explanation(grounded_summary, verified_items)

        # 9. Translation Agent
        trace.append({"step": "Translating Summary", "status": "COMPLETED", "agent": "Translation Agent", "timestamp": time.time()})
        final_summary = translation_agent.translate(explained_summary, language)

        # Save turn to conversation memory
        memory_agent.record_turn(session_id, query, extracted_profile, final_summary)

        # Partition into eligible vs ineligible for UI render
        eligible_schemes = [it for it in verified_items if it["rule_evaluation"]["is_eligible"]]
        ineligible_schemes = [it for it in verified_items if not it["rule_evaluation"]["is_eligible"]]

        return {
            "session_id": session_id,
            "query": query,
            "optimized_query": optimized_query,
            "language": language,
            "workflow_trace": trace,
            "user_profile": extracted_profile,
            "missing_fields": missing_fields,
            "needs_more_info": len(missing_fields) > 2,
            "ai_summary": final_summary,
            "eligible_schemes": eligible_schemes,
            "ineligible_schemes": ineligible_schemes
        }

coordinator_agent = CoordinatorAgent()
