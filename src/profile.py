"""Conservative extraction of facts explicitly stated in a user query."""
import re
from typing import Any, Dict

from src.config import CASTE_CATEGORY_TERMS, INDIAN_STATES


def extract_profile(query: str) -> Dict[str, Any]:
    """Return only profile facts directly expressed in *query*; unknown facts stay None."""
    text = query or ""
    lower = text.lower()
    profile: Dict[str, Any] = {
        "age": None, "gender": None, "state": None, "education": None,
        "occupation": None, "income": None, "caste_category": None, "location": None,
    }
    age = re.search(r"\b(?:i am|i'm|aged?)\s+(?:a |an )?(\d{1,3})\s*(?:years? old|year old|years)?\b", lower)
    if age:
        profile["age"] = int(age.group(1))
    if re.search(r"\b(female|woman|girl)\b", lower):
        profile["gender"] = "female"
    elif re.search(r"\bmale\b", lower):
        profile["gender"] = "male"
    for state in INDIAN_STATES:
        if re.search(r"\b" + re.escape(state) + r"\b", text, re.I):
            profile["state"] = profile["location"] = state
            break
    for term in CASTE_CATEGORY_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", text, re.I):
            profile["caste_category"] = term
            break
    income = re.search(r"\b(?:annual |family )?income\s*(?:is|of|=|:)?\s*(?:rs\.?|inr|₹)?\s*([\d,]+)", lower)
    if income:
        profile["income"] = int(income.group(1).replace(",", ""))
    education_patterns = ("engineering", "student", "school", "college", "university", "phd", "graduate")
    found_education = [p for p in education_patterns if re.search(r"\b" + p + r"\b", lower)]
    if found_education:
        profile["education"] = ", ".join(found_education)
    occupations = ("farmer", "business owner", "entrepreneur", "worker", "fisherman", "artisan")
    for occupation in occupations:
        if re.search(r"\b" + re.escape(occupation) + r"\b", lower):
            profile["occupation"] = occupation
            break
    return profile


def merge_profiles(base_profile: Dict[str, Any] | None, new_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Merge newly extracted facts into a persistent base profile.
    
    If an attribute exists in both, the newly extracted fact (from the current query) 
    overrides the base profile, allowing users to update their state conversationally.
    """
    merged = dict(base_profile or {})
    for key, value in new_profile.items():
        if value is not None:
            # For strings, if it's explicitly stated in the new query, overwrite.
            # But don't overwrite with empty strings if we have valid data.
            if isinstance(value, str) and not value.strip() and merged.get(key):
                continue
            # Basic type conversion for numbers saved as strings in DB
            if key in ("age", "income") and isinstance(merged.get(key), str) and merged[key].isdigit():
                merged[key] = int(merged[key])
            merged[key] = value
    
    # Ensure types are correct for the pipeline logic
    if "age" in merged and isinstance(merged["age"], str) and merged["age"].isdigit():
        merged["age"] = int(merged["age"])
    if "income" in merged and isinstance(merged["income"], str) and merged["income"].isdigit():
        merged["income"] = int(merged["income"])
        
    return merged
