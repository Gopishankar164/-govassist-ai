"""Grounded presentation layer: builds deterministic, conversational responses without LLMs."""
from typing import Any, Dict, List


def _format_known_facts(profile: Dict[str, Any]) -> str:
    """Format known profile facts into a natural string."""
    facts = []
    
    # Core identity
    identity = []
    if profile.get("gender"):
        identity.append(profile["gender"])
    if profile.get("education"):
        identity.append(profile["education"])
    if profile.get("occupation"):
        if profile["occupation"] not in ("student", profile.get("education", "")):
            identity.append(profile["occupation"])
    
    if identity:
        # e.g., "a female engineering student" or "a farmer"
        vowel = identity[0][0].lower() in "aeiou" if identity[0] else False
        article = "an" if vowel else "a"
        facts.append(f"{article} {' '.join(identity)}")
        
    if profile.get("state"):
        if facts:
            facts.append(f"from {profile['state']}")
        else:
            facts.append(f"a resident of {profile['state']}")
            
    if profile.get("age"):
        facts.append(f"({profile['age']} years old)")
        
    if profile.get("caste_category"):
        facts.append(f"belonging to the {profile['caste_category']} category")
        
    if profile.get("income") is not None:
        facts.append(f"with an annual family income of ₹{profile['income']:,}")
        
    if not facts:
        return ""
        
    return "you are " + " ".join(facts)


def build_grounded_answer(recommendations: List[Dict], profile: Dict[str, Any], query_domain: str) -> str:
    """Generate a conversational preamble based on extracted facts and retrieval evidence."""
    if not recommendations:
        return "I could not find any compatible schemes in the knowledge base that match your current profile and request. If you applied highly specific constraints, try broadening your search."

    preamble_parts = []
    
    # 1. Acknowledge what we found
    domain_text = f"{query_domain}-related" if query_domain != "other" else "government"
    preamble_parts.append(f"Based on what you've shared, I found several {domain_text} schemes that may be relevant to you.")
    
    # 2. Acknowledge what we know
    known_text = _format_known_facts(profile)
    
    # 3. Identify missing information across top recommendations
    all_missing = set()
    for item in recommendations:
        if item.get("missing_information"):
            for m in item["missing_information"]:
                all_missing.add(m)
                
    # 4. Construct the contextual sentence
    if known_text and all_missing:
        missing_list = list(all_missing)[:4] # limit to top 4 for readability
        missing_str = ", ".join(missing_list[:-1]) + (" and " if len(missing_list) > 1 else "") + missing_list[-1]
        preamble_parts.append(
            f"I can confirm that {known_text}, but I still need some information such as your {missing_str} before determining whether you meet every eligibility requirement."
        )
    elif known_text:
        preamble_parts.append(f"I've tailored these results because I know {known_text}.")
    elif all_missing:
        missing_list = list(all_missing)[:4]
        missing_str = ", ".join(missing_list[:-1]) + (" and " if len(missing_list) > 1 else "") + missing_list[-1]
        preamble_parts.append(
            f"I found these matches, but you haven't provided much profile information. Please share your {missing_str} so I can check your eligibility more accurately."
        )

    # Note: We NO LONGER append raw scheme text here. The structured cards will handle that.
    # The 'answer' field is now exclusively for the conversational assistant preamble.
    return "\n\n".join(preamble_parts)
