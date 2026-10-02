from typing import Dict, Any, List

class RuleEngine:
    """
    Deterministic Rule Engine for strict pre-filtering and post-verifying scheme eligibility.
    Prevents clearly ineligible recommendations (e.g. Income > Limit, Gender mismatch, Occupation mismatch).
    """

    @staticmethod
    def evaluate_scheme(user_profile: Dict[str, Any], scheme: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a user profile against a scheme's hard requirements.
        Returns evaluation result with eligibility flag, score, and reasons.
        """
        eligibility = scheme.get("eligibility", {})
        reasons = []
        is_eligible = True
        
        # 1. Income Check
        max_income = eligibility.get("max_income")
        user_income = user_profile.get("income", 0)
        if max_income and user_income > max_income:
            is_eligible = False
            reasons.append(f"Income ₹{user_income:,} exceeds maximum ceiling of ₹{max_income:,}.")
        else:
            reasons.append(f"Income ₹{user_income:,} meets income criterion (≤ ₹{max_income:,})." if max_income else "No income restriction.")

        # 2. Age Check
        min_age = eligibility.get("min_age", 0)
        max_age = eligibility.get("max_age", 100)
        user_age = user_profile.get("age")
        if user_age is not None:
            if user_age < min_age:
                is_eligible = False
                reasons.append(f"Age {user_age} is below minimum required age of {min_age}.")
            elif user_age > max_age:
                is_eligible = False
                reasons.append(f"Age {user_age} exceeds maximum allowed age of {max_age}.")
            else:
                reasons.append(f"Age {user_age} fits eligibility bracket ({min_age}-{max_age} yrs).")

        # 3. Gender Check
        req_gender = eligibility.get("gender", "All")
        user_gender = user_profile.get("gender", "All")
        if req_gender != "All" and user_gender.lower() != req_gender.lower():
            is_eligible = False
            reasons.append(f"Scheme is restricted to {req_gender} applicants (Specified: {user_gender}).")
        else:
            reasons.append(f"Gender criteria met ({req_gender}).")

        # 4. Occupation Check
        allowed_occupations = [o.lower() for o in eligibility.get("occupations", ["All"])]
        user_occupation = (user_profile.get("occupation") or "").lower()
        
        if "all" not in allowed_occupations and user_occupation:
            match = any(occ in user_occupation or user_occupation in occ for occ in allowed_occupations)
            if not match:
                is_eligible = False
                reasons.append(f"Occupation '{user_profile.get('occupation')}' is not in targeted categories ({', '.join(eligibility.get('occupations', []))}).")
            else:
                reasons.append(f"Occupation '{user_profile.get('occupation')}' matches targeted scheme audience.")

        return {
            "scheme_id": scheme.get("id"),
            "scheme_name": scheme.get("name"),
            "is_eligible": is_eligible,
            "reasons": reasons
        }

    @classmethod
    def filter_schemes(cls, user_profile: Dict[str, Any], schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for scheme in schemes:
            eval_res = cls.evaluate_scheme(user_profile, scheme)
            # Create enriched scheme payload with rule engine diagnostics
            enriched = {**scheme, "rule_evaluation": eval_res}
            results.append(enriched)
        return results
