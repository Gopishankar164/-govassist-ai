import time
import json
from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, END, START

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

class AgentResponse(TypedDict):
    agent_name: str
    input: Any
    output: Any
    confidence: float
    latency: float
    reason: str

class AgentState(TypedDict):
    session_id: str
    query: str
    optimized_query: str
    language: str
    user_profile: Dict[str, Any]
    missing_fields: List[str]
    needs_more_info: bool
    retrieved_schemes: List[Dict[str, Any]]
    evaluated_schemes: List[Dict[str, Any]]
    verified_schemes: List[Dict[str, Any]]
    ai_summary: str
    workflow_trace: List[AgentResponse]

def wrap_agent(agent_name: str, reason: str, func):
    def wrapper(state: AgentState) -> AgentState:
        start_time = time.time()
        # Call the underlying function
        result_state = func(state)
        latency = (time.time() - start_time) * 1000 # in ms
        
        # Build the standard AgentResponse
        trace = result_state.get("workflow_trace", [])
        
        # Prevent circular reference by copying state and removing trace
        safe_input = {k: v for k, v in state.items() if k != "workflow_trace"}
        safe_output = {k: v for k, v in result_state.items() if k != "workflow_trace"}

        response: AgentResponse = {
            "agent_name": agent_name,
            "input": safe_input,
            "output": safe_output,
            "confidence": 0.95, # Mock confidence for deterministic agents, will be overridden for LLM agents
            "latency": latency,
            "reason": reason
        }
        trace.append(response)
        result_state["workflow_trace"] = trace
        return result_state
    return wrapper

# 1. Coordinator Node
def raw_coordinator_node(state: AgentState) -> AgentState:
    return state

coordinator_node = wrap_agent("Coordinator Agent", "Orchestrates the workflow and initializes context.", raw_coordinator_node)

# 2. Memory Node
def raw_memory_node(state: AgentState) -> AgentState:
    merged_profile = memory_agent.merge_profile(state["session_id"], state.get("user_profile", {}))
    return {**state, "user_profile": merged_profile}

memory_node = wrap_agent("Memory Agent", "Retrieves conversation history and merges user context.", raw_memory_node)

# 3. Profile Node
def raw_profile_node(state: AgentState) -> AgentState:
    extracted_profile = profile_agent.extract_profile_from_text(state["query"], state.get("user_profile", {}))
    missing = profile_agent.identify_missing_fields(extracted_profile)
    return {
        **state,
        "user_profile": extracted_profile,
        "missing_fields": missing,
        "needs_more_info": len(missing) > 2
    }

profile_node = wrap_agent("Profile Extraction Agent", "Extracts structured demographic data from the natural language query.", raw_profile_node)

# 4. Query Rewrite Node
def raw_query_rewrite_node(state: AgentState) -> AgentState:
    opt_q = query_rewriter_agent.rewrite_query(state["query"], state.get("user_profile", {}))
    return {**state, "optimized_query": opt_q}

query_rewrite_node = wrap_agent("Query Rewriter Agent", "Optimizes the user query for maximum vector retrieval performance.", raw_query_rewrite_node)

# 5. Retrieval Node
def raw_retrieval_node(state: AgentState) -> AgentState:
    # Retrieve top 10 as per requirements
    retrieved = retrieval_agent.execute_retrieval(state["optimized_query"] or state["query"], state.get("user_profile", {}), top_k=10)
    return {**state, "retrieved_schemes": retrieved}

retrieval_node = wrap_agent("Retrieval Agent", "Queries the FAISS vector database using dense embeddings (bge-small-en-v1.5) for top 10 relevant schemes.", raw_retrieval_node)

# 6. Eligibility Node
def raw_eligibility_node(state: AgentState) -> AgentState:
    evaluated = eligibility_agent.evaluate_retrieved_items(state["user_profile"], state.get("retrieved_schemes", []))
    return {**state, "evaluated_schemes": evaluated}

eligibility_node = wrap_agent("Eligibility Agent", "Applies strict deterministic rules to filter ineligible schemes.", raw_eligibility_node)

# 7. Verification Node
def raw_verification_node(state: AgentState) -> AgentState:
    verified = verification_agent.verify_documents(state.get("evaluated_schemes", []))
    return {**state, "verified_schemes": verified}

verification_node = wrap_agent("Verification Agent", "Verifies document requirements and assigns verification badges.", raw_verification_node)

# 8. Grounding & Explanation Node
def raw_explanation_node(state: AgentState) -> AgentState:
    # Get top 3 eligible schemes to return
    verified = state.get("verified_schemes", [])
    eligible = [v for v in verified if v.get("rule_evaluation", {}).get("is_eligible", False)]
    
    # Sort by confidence and take top 3 (or 5)
    eligible.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
    top_3_eligible = eligible[:3]

    # Format AI Summary directly simulating ChatGPT
    if not top_3_eligible:
        ai_summary = "Based on your profile, I could not find any government schemes you are eligible for at this time."
    else:
        ai_summary = f"Based on your profile, I found {len(top_3_eligible)} schemes you are eligible for.\n\n"
        for i, item in enumerate(top_3_eligible, 1):
            scheme = item["scheme"]
            benefits = scheme.get("benefits", "No specific benefits listed.")
            reasons = "\n".join([f"✔ {r}" for r in item.get("rule_evaluation", {}).get("reasons", [])])
            docs = ", ".join(scheme.get("documents_required", scheme.get("required_documents", [])))
            url = scheme.get("official_application_url", scheme.get("application_url", "#"))
            name = scheme.get("scheme_name", scheme.get("name", "Unknown Scheme"))

            ai_summary += f"### {i}. {name}\n\n"
            ai_summary += f"**Eligibility:**\n{reasons}\n\n"
            ai_summary += f"**Benefits:**\n{benefits}\n\n"
            ai_summary += f"**Reason:**\nRecommended because your profile satisfies the eligibility criteria with a {item.get('confidence_score', 0)}% match confidence.\n\n"
            ai_summary += f"**Required Documents:**\n{docs}\n\n"
            ai_summary += f"**Official Portal:**\n[{url}]({url})\n\n---\n\n"
            
    return {**state, "ai_summary": ai_summary}

explanation_node = wrap_agent("Explanation Agent", "Generates the final ChatGPT-like formatted output based strictly on retrieved, eligible documents.", raw_explanation_node)

# 9. Translation Node
def raw_translation_node(state: AgentState) -> AgentState:
    translated = translation_agent.translate(state["ai_summary"], state.get("language", "en"))
    memory_agent.record_turn(state["session_id"], state["query"], state["user_profile"], translated)
    return {**state, "ai_summary": translated}

translation_node = wrap_agent("Translation Agent", "Translates the final explanation to the requested user language.", raw_translation_node)

# 10. Conditional Ask User Node
def raw_ask_user_node(state: AgentState) -> AgentState:
    missing_str = ", ".join(state.get("missing_fields", []))
    msg = f"To provide accurate government scheme recommendations, please specify your {missing_str} in the profile form."
    return {**state, "ai_summary": msg}

ask_user_node = wrap_agent("Ask User Agent", "Interrupts the flow to request mandatory missing information.", raw_ask_user_node)


def check_missing_info_condition(state: AgentState) -> str:
    if state.get("needs_more_info"):
        return "ask_user"
    return "query_rewrite"

# Build and Compile LangGraph StateGraph
builder = StateGraph(AgentState)

builder.add_node("coordinator", coordinator_node)
builder.add_node("memory", memory_node)
builder.add_node("profile", profile_node)
builder.add_node("ask_user", ask_user_node)
builder.add_node("query_rewrite", query_rewrite_node)
builder.add_node("retrieval", retrieval_node)
builder.add_node("eligibility", eligibility_node)
builder.add_node("verification", verification_node)
builder.add_node("explanation", explanation_node)
builder.add_node("translation", translation_node)

builder.add_edge(START, "coordinator")
builder.add_edge("coordinator", "memory")
builder.add_edge("memory", "profile")

builder.add_conditional_edges("profile", check_missing_info_condition, {
    "ask_user": "ask_user",
    "query_rewrite": "query_rewrite"
})

builder.add_edge("ask_user", END)
builder.add_edge("query_rewrite", "retrieval")
builder.add_edge("retrieval", "eligibility")
builder.add_edge("eligibility", "verification")
builder.add_edge("verification", "explanation")
builder.add_edge("explanation", "translation")
builder.add_edge("translation", END)

compiled_graph = builder.compile()

class LangGraphEngine:
    def run(self, session_id: str, query: str, profile: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        initial_state: AgentState = {
            "session_id": session_id,
            "query": query,
            "optimized_query": "",
            "language": language,
            "user_profile": profile,
            "missing_fields": [],
            "needs_more_info": False,
            "retrieved_schemes": [],
            "evaluated_schemes": [],
            "verified_schemes": [],
            "ai_summary": "",
            "workflow_trace": []
        }

        final_state = compiled_graph.invoke(initial_state)

        verified = final_state.get("verified_schemes", [])
        eligible = [it for it in verified if it.get("rule_evaluation", {}).get("is_eligible", False)]
        ineligible = [it for it in verified if not it.get("rule_evaluation", {}).get("is_eligible", True)]

        # Keep top 3 eligible only for the final response, but return others in payload if needed
        eligible.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
        top_3 = eligible[:3]

        return {
            "session_id": final_state["session_id"],
            "query": final_state["query"],
            "optimized_query": final_state.get("optimized_query", ""),
            "language": final_state["language"],
            "workflow_trace": final_state["workflow_trace"],
            "user_profile": final_state["user_profile"],
            "ai_summary": final_state["ai_summary"],
            "eligible_schemes": top_3,
            "ineligible_schemes": ineligible
        }

langgraph_engine = LangGraphEngine()
