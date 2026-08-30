"""Evidence-based eligibility screening, deliberately separate from similarity."""
from typing import Dict, List, Tuple

ELIGIBLE = "ELIGIBLE"
POTENTIALLY_ELIGIBLE = "POTENTIALLY_ELIGIBLE"
INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
NOT_ELIGIBLE = "NOT_ELIGIBLE"


def analyze_eligibility(scheme: Dict, profile: Dict) -> Dict:
    """Reject only explicit structured conflicts; otherwise retain uncertainty with evidence."""
    evidence: List[str] = []
    missing: List[str] = []
    conflicts: List[str] = []
    if scheme.get("state") not in (None, "", "unknown"):
        if profile.get("state") and scheme["state"] != profile["state"]:
            conflicts.append(f"Scheme text identifies {scheme['state']}; profile states {profile['state']}.")
        elif not profile.get("state"):
            missing.append("state")
        else:
            evidence.append(f"State matches: {profile['state']}.")
    criterion_gender = scheme.get("gender_criteria", "unknown")
    if criterion_gender != "unknown":
        if profile.get("gender") and criterion_gender != profile["gender"]:
            conflicts.append(f"Scheme is marked for {criterion_gender} applicants.")
        elif not profile.get("gender"):
            missing.append("gender")
        else:
            evidence.append(f"Gender criterion matches: {profile['gender']}.")
    if scheme.get("age_min") is not None or scheme.get("age_max") is not None:
        age = profile.get("age")
        if age is None:
            missing.append("age")
        elif (scheme.get("age_min") is not None and age < scheme["age_min"]) or (scheme.get("age_max") is not None and age > scheme["age_max"]):
            conflicts.append("Stated age is outside the extracted scheme age range.")
        else:
            evidence.append("Age is within the extracted scheme age range.")
    ceiling = scheme.get("income_ceiling_inr")
    if ceiling is not None:
        income = profile.get("income")
        if income is None:
            missing.append("income")
        elif income > ceiling:
            conflicts.append(f"Stated income exceeds extracted ceiling of ₹{ceiling:,}.")
        else:
            evidence.append(f"Income is within extracted ceiling of ₹{ceiling:,}.")
    caste_criteria = scheme.get("caste_criteria") or []
    if caste_criteria:
        caste = profile.get("caste_category")
        if caste is None:
            missing.append("caste/category")
        elif caste not in caste_criteria:
            conflicts.append("Stated caste/category does not match the extracted scheme category criterion.")
        else:
            evidence.append(f"Caste/category matches: {caste}.")

    # These requirements are common in free text but do not have a reliable
    # structured CSV column.  Report their absence explicitly instead of
    # letting a high semantic score disguise a prerequisite.
    eligibility_text = (scheme.get("eligibility_text") or "").lower()
    occupation = profile.get("occupation")
    signals = {
        "disability status": ("differently abled", "person with disabilit", "disabled person"),
        "construction-worker status": ("construction worker", "building worker"),
        "fisherworker status": ("fisherman", "fisherfolk", "fisherwoman"),
    }
    for required_field, terms in signals.items():
        if any(term in eligibility_text for term in terms):
            expected_occupation = {
                "construction-worker status": "worker",
                "fisherworker status": "fisherman",
            }.get(required_field)
            if expected_occupation and occupation == expected_occupation:
                evidence.append(f"Profile supplies {required_field}.")
            else:
                missing.append(required_field)
    if conflicts:
        status = NOT_ELIGIBLE
    elif missing:
        status = INSUFFICIENT_INFORMATION
    elif evidence:
        # The dataset's free-text criteria can include conditions that a
        # conservative extractor cannot prove have all been satisfied.
        # Matching extracted fields is useful evidence, but not confirmation.
        status = POTENTIALLY_ELIGIBLE
    else:
        status = POTENTIALLY_ELIGIBLE
        evidence.append("No structured eligibility conflict was extracted; verify the full eligibility text.")
    return {"eligibility_status": status, "eligibility_evidence": evidence, "missing_information": missing, "conflicts": conflicts}
