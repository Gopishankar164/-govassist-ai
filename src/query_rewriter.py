"""Intent-preserving deterministic query expansion for dense retrieval."""
from typing import Dict

_EXPANSIONS = {
    "scholarship": "higher education student financial assistance scholarship",
    "farmer": "agriculture farmer financial assistance rural livelihood",
    "housing": "housing home construction affordable housing assistance",
    "business": "small business entrepreneur enterprise loan credit financial assistance",
    "loan": "loan credit finance assistance",
}


def rewrite_query(query: str, profile: Dict[str, object]) -> str:
    """Expand stated intent only. Profile facts are never fabricated or inferred."""
    additions = [concepts for term, concepts in _EXPANSIONS.items() if term in query.lower()]
    stated = []
    for key in ("state", "gender", "education", "occupation", "caste_category"):
        if profile.get(key):
            stated.append(f"{key}: {profile[key]}")
    return " ".join(part for part in [query.strip(), *additions, *stated] if part)
