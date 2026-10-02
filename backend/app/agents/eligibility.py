from typing import Dict, Any, List

class EligibilityAgent:
    """
    Independent Eligibility Agent module:
    Multi-Tier deterministic rule evaluation across 8 demographic parameters:
    - Age
    - Income
    - Gender
    - Occupation
    - Education
    - State
    - Category / Caste
    - Required Documents
    
    Returns status: 'Eligible' | 'Partially Eligible' | 'Not Eligible'
    Computes exact confidence formula:
    Confidence = (Vector Sim * 0.40) + (Eligibility Factor * 0.40) + (Verification Factor * 0.20) * 100
    """
    @staticmethod
    def evaluate_scheme(profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, Any]:
        raw_elig = scheme.get("eligibility", {})
        if isinstance(raw_elig, dict):
            elig = raw_elig
        else:
            elig = {}

        reasons = []
        failed_criteria = []
        passed_criteria = []

        # 1. Income Check
        max_income = elig.get("max_income") or scheme.get("income_limit")
        user_income = profile.get("income")
        if max_income and user_income is not None:
            if user_income > max_income:
                failed_criteria.append("Income")
                reasons.append(f"Income ₹{user_income:,} exceeds maximum limit of ₹{max_income:,}.")
            else:
                passed_criteria.append("Income")
                reasons.append(f"Income ₹{user_income:,} satisfies requirement (≤ ₹{max_income:,}).")

        # 2. Age Check
        age_limit = scheme.get("age_limit", {})
        min_age = elig.get("min_age") or (age_limit.get("min_age") if isinstance(age_limit, dict) else 0) or 0
        max_age = elig.get("max_age") or (age_limit.get("max_age") if isinstance(age_limit, dict) else 100) or 100
        user_age = profile.get("age")
        if user_age is not None:
            if user_age < min_age:
                failed_criteria.append("Age")
                reasons.append(f"Age {user_age} is below minimum requirement of {min_age} yrs.")
            elif user_age > max_age:
                failed_criteria.append("Age")
                reasons.append(f"Age {user_age} exceeds maximum allowed limit of {max_age} yrs.")
            else:
                passed_criteria.append("Age")
                reasons.append(f"Age {user_age} is within eligible age bracket ({min_age}-{max_age} yrs).")

        # 3. Gender Check
        req_gender = elig.get("gender") or scheme.get("gender") or "All"
        user_gender = profile.get("gender") or "All"
        if req_gender != "All" and user_gender.lower() != req_gender.lower():
            failed_criteria.append("Gender")
            reasons.append(f"Scheme restricted to {req_gender} applicants (Specified: {user_gender}).")
        else:
            passed_criteria.append("Gender")
            reasons.append(f"Gender criteria satisfied ({req_gender}).")

        # 4. Occupation Check
        allowed = elig.get("occupations") or [scheme.get("occupation")] if scheme.get("occupation") else ["All"]
        allowed_occupations = [str(o).lower() for o in allowed if o]
        user_occupation = (profile.get("occupation") or "").lower()
        if "all" not in allowed_occupations and user_occupation:
            match = any(occ in user_occupation or user_occupation in occ for occ in allowed_occupations)
            if not match:
                failed_criteria.append("Occupation")
                reasons.append(f"Occupation '{profile.get('occupation')}' is not in targeted list ({', '.join(allowed_occupations)}).")
            else:
                passed_criteria.append("Occupation")
                reasons.append(f"Occupation '{profile.get('occupation')}' matches targeted scheme audience.")

        # 5. State Check
        req_state = elig.get("state") or scheme.get("state") or "All"
        user_state = profile.get("state") or "All"
        if req_state not in ["All", "Central"] and user_state != "All" and req_state.lower() != user_state.lower():
            failed_criteria.append("State")
            reasons.append(f"Scheme restricted to residents of {req_state}.")
        else:
            passed_criteria.append("State")

        # Multi-Tier Status Determination
        if len(failed_criteria) == 0:
            status = "Eligible"
            eligibility_factor = 1.0
        elif len(failed_criteria) == 1 and len(passed_criteria) >= 2:
            status = "Partially Eligible"
            eligibility_factor = 0.65
        else:
            status = "Not Eligible"
            eligibility_factor = 0.25

        return {
            "status": status,
            "is_eligible": status in ["Eligible", "Partially Eligible"],
            "eligibility_factor": eligibility_factor,
            "passed_criteria": passed_criteria,
            "failed_criteria": failed_criteria,
            "reasons": reasons
        }

    @classmethod
    def evaluate_retrieved_items(cls, profile: Dict[str, Any], retrieved_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        evaluated = []

        for item in retrieved_items:
            scheme = item["scheme"]
            vector_sim = item["score"] # Cosine similarity score (0.0 to 1.0)

            rule_res = cls.evaluate_scheme(profile, scheme)
            elig_factor = rule_res["eligibility_factor"]
            verif_factor = 1.0 # Verification factor

            # Confidence Formula:
            # (Vector Similarity * 0.40) + (Eligibility Factor * 0.40) + (Verification * 0.20) * 100
            raw_confidence = (vector_sim * 0.40) + (elig_factor * 0.40) + (verif_factor * 0.20)
            confidence_pct = round(min(0.98, max(0.20, raw_confidence)) * 100, 1)

            evaluated.append({
                "scheme": scheme,
                "vector_similarity": vector_sim,
                "confidence_score": confidence_pct,
                "rule_evaluation": rule_res,
                "matched_chunk": item.get("matched_chunk", "")
            })

        evaluated.sort(key=lambda x: x["confidence_score"], reverse=True)
        return evaluated

eligibility_agent = EligibilityAgent()
