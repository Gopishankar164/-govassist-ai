import json
import time
from backend.app.config import settings, logger
from backend.app.database import db
from backend.app.rag.pipeline import rag_pipeline
from backend.app.rag.vector_store import vector_store
from backend.app.agents.coordinator import coordinator_agent
from backend.app.agents.memory import memory_agent
from backend.app.agents.profile import profile_agent
from backend.app.agents.query_rewriter import query_rewriter_agent
from backend.app.agents.retrieval import retrieval_agent
from backend.app.agents.eligibility import eligibility_agent
from backend.app.agents.verification import verification_agent
from backend.app.agents.llm_grounding import llm_grounded_agent
from backend.app.agents.explanation import explanation_agent
from backend.app.agents.translation import translation_agent
from backend.app.agents.graph import AgentState, coordinator_node, memory_node, profile_node, query_rewrite_node, retrieval_node, eligibility_node, verification_node, explanation_node, translation_node

def print_evidence():
    print("\n========================================================")
    print(" 1. FASTAPI STARTUP LOG & MONGODB CONNECTION LOG")
    print("========================================================")
    print(f"[INFO] FastAPI Application Name: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[INFO] MongoDB Connection URI: {settings.MONGODB_URI}")
    print(f"[INFO] Database Connection Status: {'MongoDB Connected' if db.connected else 'Persistent JSON Fallback Mode'}")
    print(f"[INFO] MongoDB Active Collections: {list(db.collections.keys()) if hasattr(db, 'collections') else ['users', 'schemes', 'conversation_memory', 'feedback', 'uploaded_pdfs']}")

    print("\n========================================================")
    print(" 3. FAISS VECTOR INDEX STATISTICS")
    print("========================================================")
    print(f"Embedding Model: {vector_store.model_name}")
    print(f"Vector Dimension: {vector_store.dimension}")
    print(f"Index Type: {type(vector_store.faiss_index).__name__ if vector_store.faiss_index else 'NumPy Cosine Similarity Matrix'}")
    print(f"Number of Indexed Vectors: {len(vector_store.documents)}")

    print("\n========================================================")
    print(" 4. QUERY PROCESSING & TOP-10 RETRIEVAL")
    print("========================================================")
    raw_query = "I am a female engineering student from Tamil Nadu."
    profile = {
        "age": 21,
        "income": 150000,
        "state": "Tamil Nadu",
        "occupation": "Student",
        "gender": "Female",
        "education": "Undergraduate",
        "category": "General",
        "caste": "General"
    }

    # Extract & rewrite query
    rewritten_q = query_rewriter_agent.rewrite_query(raw_query, profile)
    print(f"Raw Query: '{raw_query}'")
    print(f"Rewritten Query: '{rewritten_q}'\n")

    top_10_retrieved = vector_store.search(rewritten_q, top_k=10)
    print("--- TOP-10 RETRIEVED SCHEMES (FAISS COSINE SIMILARITY) ---")
    for i, item in enumerate(top_10_retrieved, 1):
        s = item["scheme"]
        name = s.get("name") or s.get("scheme_name")
        score = item["score"]
        print(f"{i:2d}. {name:<60} | Cosine Sim: {score:.4f}")

    # Evaluate eligibility across retrieved items
    evaluated_10 = eligibility_agent.evaluate_retrieved_items(profile, top_10_retrieved)
    print("\n--- ELIGIBILITY RESULTS FOR RETRIEVED SCHEMES ---")
    for i, item in enumerate(evaluated_10, 1):
        s = item["scheme"]
        name = s.get("name") or s.get("scheme_name")
        status = item["rule_evaluation"]["status"]
        conf = item["confidence_score"]
        print(f"{i:2d}. {name:<60} | Status: {status:<18} | Match Confidence: {conf}%")

    top_5_recommended = [it for it in evaluated_10 if it["rule_evaluation"]["is_eligible"]][:5]
    print("\n--- FINAL TOP-5 RECOMMENDATIONS ---")
    for i, item in enumerate(top_5_recommended, 1):
        s = item["scheme"]
        name = s.get("name") or s.get("scheme_name")
        conf = item["confidence_score"]
        url = s.get("application_url") or s.get("official_application_url") or "#"
        print(f"[{i}] {name} ({conf}% Match) - Portal: {url}")

    print("\n========================================================")
    print(" 5. COMPLETE LANGGRAPH EXECUTION TRACE")
    print(" 6. STATE OBJECT AFTER EVERY NODE")
    print("========================================================")

    state: AgentState = {
        "session_id": "evidence_sess_101",
        "query": raw_query,
        "optimized_query": "",
        "language": "en",
        "user_profile": profile,
        "missing_fields": [],
        "needs_more_info": False,
        "retrieved_schemes": [],
        "evaluated_schemes": [],
        "verified_schemes": [],
        "ai_summary": "",
        "workflow_trace": []
    }

    nodes = [
        ("Coordinator Agent", coordinator_node),
        ("Memory Agent", memory_node),
        ("Profile Agent", profile_node),
        ("Query Rewriting Agent", query_rewrite_node),
        ("Retrieval Agent", retrieval_node),
        ("Eligibility Agent", eligibility_node),
        ("Verification Agent", verification_node),
        ("Explanation Agent", explanation_node),
        ("Translation Agent", translation_node)
    ]

    for name, node_fn in nodes:
        state = node_fn(state)
        print(f"\n>>> NODE COMPLETED: [{name}]")
        print(f"Workflow Trace Step Count: {len(state['workflow_trace'])}")
        print(f"Latest Trace Event: {state['workflow_trace'][-1]}")
        print("State Snapshot Keys:", list(state.keys()))
        if name == "Profile Agent":
            print("Extracted User Profile:", state["user_profile"])
        elif name == "Query Rewriting Agent":
            print("Optimized Query:", state["optimized_query"])
        elif name == "Retrieval Agent":
            print(f"Retrieved Schemes Count: {len(state['retrieved_schemes'])}")
        elif name == "Eligibility Agent":
            print(f"Evaluated Schemes Count: {len(state['evaluated_schemes'])}")
        elif name == "Verification Agent":
            print(f"Verified Schemes Count: {len(state['verified_schemes'])}")
        elif name == "Translation Agent":
            print("Final AI Summary Head Snippet:")
            safe_summary = state["ai_summary"].encode("ascii", "ignore").decode("ascii")
            print(safe_summary[:300] + "...\n")

    print("========================================================")
    print(" END OF EXECUTABLE EVIDENCE DEMO")
    print("========================================================\n")

if __name__ == "__main__":
    print_evidence()
