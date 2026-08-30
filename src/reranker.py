"""Transparent structured reranking after semantic retrieval and eligibility checks."""
import re
from typing import Dict, List, Set

from src.config import DOMAIN_LABELS, QUERY_DOMAIN_KEYWORDS, SCHEME_DOMAIN_CATEGORIES, SCHEME_DOMAIN_TERMS

_STATUS_WEIGHT = {"ELIGIBLE": 0.10, "POTENTIALLY_ELIGIBLE": 0.04, "INSUFFICIENT_INFORMATION": 0.0, "NOT_ELIGIBLE": -1.0}


def classify_query_domain(query: str, profile: Dict | None = None) -> str:
    """Classify the likely topic of a user query without inferring missing personal facts."""
    if not query or not query.strip():
        return "other"

    text = re.sub(r"[^a-z0-9\s]", " ", query.lower())
    text = " ".join(text.split())
    if not text:
        return "other"

    score_by_domain = {domain: 0 for domain in DOMAIN_LABELS}
    for domain, keywords in QUERY_DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                score_by_domain[domain] += 1

    occupation = (profile or {}).get("occupation")
    if occupation == "student":
        score_by_domain["education"] += 2
    elif occupation == "farmer":
        score_by_domain["agriculture"] += 2
    elif occupation == "entrepreneur":
        score_by_domain["business"] += 2
    elif occupation in {"worker", "fisherman", "artisan"}:
        score_by_domain["employment"] += 1

    winner = max(score_by_domain, key=score_by_domain.get)
    return winner if score_by_domain[winner] > 0 else "other"


def _candidate_domains(candidate: Dict) -> Set[str]:
    """Use category and descriptive metadata as a conservative relevance signal."""
    scheme = candidate.get("scheme", {})
    category = (scheme.get("category") or "").lower()
    text = " ".join(str(scheme.get(field) or "") for field in (
        "scheme_name", "description", "benefits", "eligibility_text", "application_process", "tags",
    )).lower()
    domains = set()
    for domain, categories in SCHEME_DOMAIN_CATEGORIES.items():
        if any(value.lower() in category for value in categories) or any(term in text for term in SCHEME_DOMAIN_TERMS[domain]):
            domains.add(domain)
    return domains


def _query_domains(query: str, profile: Dict | None) -> Set[str]:
    """Infer only clearly stated high-level intent domains."""
    domain = classify_query_domain(query, profile)
    return {domain} if domain != "other" else set()


def rerank(candidates: List[Dict], limit: int = 3, query: str = "", profile: Dict | None = None, use_domain_intent: bool = False) -> List[Dict]:
    """Rank FAISS candidates with eligibility and conservative stated-intent signals."""
    requested_domains = _query_domains(query, profile)
    ranked = []
    for candidate in candidates:
        result = dict(candidate)
        candidate_domains = _candidate_domains(result)
        matching_domains = requested_domains & candidate_domains
        if use_domain_intent:
            intent = classify_query_domain(query, profile)
            result["domain_intent"] = intent
            result["domain_match"] = sorted(matching_domains)
            if intent != "other":
                if matching_domains:
                    domain_adjustment = 0.08
                elif intent in candidate_domains:
                    domain_adjustment = 0.03
                else:
                    domain_adjustment = -0.06
            else:
                domain_adjustment = 0.0
        else:
            result["domain_intent"] = classify_query_domain(query, profile)
            result["domain_match"] = sorted(matching_domains)
            domain_adjustment = 0.06 if matching_domains else (-0.05 if requested_domains else 0.0)

        result["domain_rank_adjustment"] = domain_adjustment
        result["final_rank_score"] = result["similarity_score"] + _STATUS_WEIGHT[result["eligibility_status"]] + domain_adjustment
        ranked.append(result)
    ranked.sort(key=lambda item: item["final_rank_score"], reverse=True)
    return [item for item in ranked if item["eligibility_status"] != "NOT_ELIGIBLE"][:limit]
