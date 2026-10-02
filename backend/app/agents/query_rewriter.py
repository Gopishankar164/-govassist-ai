from typing import Dict, Any

class QueryRewritingAgent:
    """
    Independent Query Rewriting Agent module:
    Converts raw natural language queries into optimized retrieval keyword/concept vectors.
    Example:
    "I am a female engineering student"
    └─► "female student engineering Tamil Nadu scholarship degree financial assistance"
    """
    @staticmethod
    def rewrite_query(raw_query: str, profile: Dict[str, Any]) -> str:
        tokens = [raw_query.strip()]

        occ = profile.get("occupation")
        if occ:
            tokens.append(occ)

        gender = profile.get("gender")
        if gender and gender != "All":
            tokens.append(gender)

        state = profile.get("state")
        if state:
            tokens.append(state)

        edu = profile.get("education")
        if edu:
            tokens.append(edu)

        caste = profile.get("caste")
        if caste:
            tokens.append(caste)

        # Domain concept expansion
        q_lower = raw_query.lower()
        if "student" in q_lower or "engineering" in q_lower or "college" in q_lower:
            tokens.extend(["scholarship", "tuition", "education", "stipend"])
        if "farmer" in q_lower or "agriculture" in q_lower:
            tokens.extend(["subsidy", "kisan", "pm-kisan", "crop insurance"])
        if "business" in q_lower or "startup" in q_lower or "shop" in q_lower:
            tokens.extend(["loan", "mudra", "credit", "grant", "subsidy"])

        optimized_query = " ".join(dict.fromkeys(tokens)) # deduplicate keeping order
        return optimized_query

query_rewriter_agent = QueryRewritingAgent()
