from typing import List, Dict, Any
from backend.app.rag.pipeline import rag_pipeline
from backend.app.config import logger

class LLMGroundedAgent:
    """
    Independent LLM Grounded Agent module:
    Enforces strict prompt grounding over retrieved context blocks.
    Prevents hallucination by requiring retrieved context for answer generation.
    """
    @staticmethod
    def generate_grounded_response(query: str, profile: Dict[str, Any], verified_items: List[Dict[str, Any]]) -> str:
        eligible_items = [it for it in verified_items if it["rule_evaluation"]["is_eligible"]]

        if not verified_items:
            return "No matching official government scheme documents were retrieved from the knowledge base for your query."

        # Format retrieved context
        context_str = rag_pipeline.format_grounded_context(verified_items)

        if not eligible_items:
            summary = (
                f"### 🔍 Database Retrieval Results\n\n"
                f"We retrieved **{len(verified_items)} schemes** matching query '{query}', but based on your demographic profile "
                f"(Age: {profile.get('age', 'N/A')}, Income: ₹{profile.get('income', 0):,}, Occupation: {profile.get('occupation', 'N/A')}), "
                f"none fully met mandatory criteria.\n\n"
                f"**Retrieved Context Summary:**\n{context_str[:400]}..."
            )
            return summary

        top = eligible_items[0]
        top_scheme = top["scheme"]
        top_name = top_scheme.get("name") or top_scheme.get("scheme_name") or "Government Scheme"
        url = top_scheme.get("application_url") or top_scheme.get("official_application_url") or "#"
        docs = ", ".join(top_scheme.get("documents_required") or top_scheme.get("required_documents") or [])

        summary = f"### 🌟 Recommended Scheme: {top_name} ({top['confidence_score']}% Match)\n\n"
        summary += f"**Eligibility Status:** ✅ {top['rule_evaluation']['status']} (Cosine Sim: {top['vector_similarity']:.4f})\n\n"
        summary += f"**Why Eligible?**\n"
        for reason in top["rule_evaluation"]["reasons"]:
            summary += f"• {reason}\n"

        summary += f"\n**Key Benefits:**\n{top_scheme.get('benefits', '')}\n\n"
        summary += f"**Required Documents:**\n📄 {docs}\n\n"
        summary += f"**Official Application Portal:**\n🔗 [{url}]({url})\n"

        if len(eligible_items) > 1:
            other_names = [it['scheme'].get('name') or it['scheme'].get('scheme_name') for it in eligible_items[1:]]
            summary += f"\n---\n*Additional Eligible Options:* " + ", ".join(f"**{name}**" for name in other_names)

        return summary

llm_grounded_agent = LLMGroundedAgent()
