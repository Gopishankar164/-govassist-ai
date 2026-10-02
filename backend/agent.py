from typing import Dict, Any, List
from backend.vector_store import EmbeddingVectorStore
from backend.rule_engine import RuleEngine

class SchemeRecommendationAgent:
    """
    Agentic RAG Pipeline:
    Step 1: Extract User Demographics & Information
    Step 2: Vector Search in Scheme Database (FAISS/Embedding store)
    Step 3: Deterministic Rule Verification
    Step 4: LLM Structured Response Generation
    """
    def __init__(self, vector_store: EmbeddingVectorStore):
        self.vector_store = vector_store

    def extract_info_from_query(self, user_query: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agentic Information Extraction from user conversation.
        Updates user profile attributes like occupation, age, or income mentioned in plain text.
        """
        updated_profile = dict(current_profile)
        q_lower = user_query.lower()

        # Extract occupation hints
        if "student" in q_lower or "engineering" in q_lower or "college" in q_lower:
            updated_profile["occupation"] = "Student"
        elif "farmer" in q_lower or "agriculture" in q_lower:
            updated_profile["occupation"] = "Farmer"
        elif "business" in q_lower or "shop" in q_lower or "startup" in q_lower:
            updated_profile["occupation"] = "Entrepreneur"
        elif "unemployed" in q_lower or "job" in q_lower or "work" in q_lower:
            if not updated_profile.get("occupation"):
                updated_profile["occupation"] = "Job Seeker"

        # Gender hints
        if "girl" in q_lower or "female" in q_lower or "woman" in q_lower or "women" in q_lower:
            updated_profile["gender"] = "Female"

        return updated_profile

    def process_recommendations(self, user_query: str, profile: Dict[str, Any]) -> Dict[str, Any]:
        # Step 1: Agentic Info Extraction
        extracted_profile = self.extract_info_from_query(user_query, profile)

        # Step 2: Vector Search
        search_results = self.vector_store.search(user_query, top_k=6)
        retrieved_schemes = [res["scheme"] for res in search_results]

        # Step 3: Apply Rule Engine
        evaluated_schemes = RuleEngine.filter_schemes(extracted_profile, retrieved_schemes)

        # Separate eligible and conditionally eligible schemes
        eligible_schemes = []
        ineligible_schemes = []

        for item in evaluated_schemes:
            if item["rule_evaluation"]["is_eligible"]:
                eligible_schemes.append(item)
            else:
                ineligible_schemes.append(item)

        # Step 4: Generate LLM Response synthesis
        ai_summary = self._generate_ai_summary(user_query, extracted_profile, eligible_schemes, ineligible_schemes)

        # Check missing profile info to prompt user agentically
        missing_fields = []
        if not extracted_profile.get("age"): missing_fields.append("Age")
        if not extracted_profile.get("income"): missing_fields.append("Annual Family Income")
        if not extracted_profile.get("occupation"): missing_fields.append("Occupation")

        return {
            "query": user_query,
            "user_profile": extracted_profile,
            "missing_fields_prompt": missing_fields,
            "ai_summary": ai_summary,
            "eligible_schemes": eligible_schemes,
            "ineligible_schemes": ineligible_schemes
        }

    def _generate_ai_summary(self, query: str, profile: Dict[str, Any], eligible: List[Dict[str, Any]], ineligible: List[Dict[str, Any]]) -> str:
        occ = profile.get("occupation", "citizen")
        inc = f"₹{profile.get('income'):,}" if profile.get("income") is not None else "Not specified"
        age = profile.get("age", "Not specified")

        if eligible:
            top_scheme = eligible[0]
            summary = f"Based on your profile ({occ.title()}, Age: {age}, Income: {inc}), we identified **{len(eligible)} high-matching government schemes** for you!\n\n"
            summary += f"🌟 **Top Recommendation: {top_scheme['name']}**\n"
            summary += f"• **Key Benefit:** {top_scheme['benefits']}\n"
            summary += f"• **Eligibility Status:** ✅ Fully Verified by Rule Engine\n"
            summary += f"• **Required Documents:** {', '.join(top_scheme['documents_required'])}\n\n"
            if len(eligible) > 1:
                summary += f"Explore additional eligible schemes below such as **{eligible[1]['name']}**."
        else:
            summary = f"We searched our database for '{query}'. While some schemes exist in this domain, your current income or demographic settings didn't match the strict eligibility criteria. Try updating your profile details to see tailored options!"

        return summary
