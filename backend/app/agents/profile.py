import re
from typing import Dict, Any, List
from backend.app.agents.llm_client import ollama_client

class ProfileAgent:
    """
    Independent Profile Extraction Agent module:
    Extracts and normalizes demographic parameters using Ollama Llama 3.2,
    falling back to regex if the model is unavailable.
    """
    @staticmethod
    def extract_profile_from_text(query: str, existing_profile: Dict[str, Any]) -> Dict[str, Any]:
        profile = dict(existing_profile)
        q = query.lower()
        
        # Try LLM extraction first
        system_prompt = """You are an intelligent profile extraction agent.
Given a user query and their existing profile, extract any new or updated profile fields (age, gender, income, occupation, state, education, caste, category).
Respond ONLY with a valid JSON object containing the extracted fields. Do not invent information. If a field is not mentioned, do not include it. Ensure income is an integer."""
        
        prompt = f"Query: {query}\nExisting Profile: {existing_profile}"
        
        try:
            llm_extracted = ollama_client.generate_json(prompt, system_prompt)
            if llm_extracted:
                for k, v in llm_extracted.items():
                    if v is not None and v != "":
                        profile[k] = v
                return profile
        except Exception as e:
            pass # Fallback to regex

        # Occupation hints
        if any(term in q for term in ["student", "engineering", "college", "university", "school", "degree", "diploma"]):
            profile["occupation"] = "Student"
        elif any(term in q for term in ["farmer", "agriculture", "kisan", "cultivator", "crop"]):
            profile["occupation"] = "Farmer"
        elif any(term in q for term in ["business", "entrepreneur", "startup", "shop", "vendor", "store"]):
            profile["occupation"] = "Entrepreneur"
        elif any(term in q for term in ["unemployed", "job seeker", "career", "employment", "job"]):
            if not profile.get("occupation"):
                profile["occupation"] = "Job Seeker"
        elif any(term in q for term in ["worker", "labour", "artisan", "weaver"]):
            if not profile.get("occupation"):
                profile["occupation"] = "Worker"

        # Gender hints
        if any(term in q for term in ["female", "woman", "women", "girl", "mother", "daughter", "widow"]):
            profile["gender"] = "Female"
        elif any(term in q for term in ["male", "man", "men", "boy", "father", "son"]):
            if not profile.get("gender"):
                profile["gender"] = "Male"

        # Education hints
        if any(term in q for term in ["post graduate", "masters", "phd"]):
            profile["education"] = "Post Graduate"
        elif any(term in q for term in ["undergraduate", "engineering", "btech", "bsc", "bcom", "degree"]):
            profile["education"] = "Undergraduate"
        elif any(term in q for term in ["12th", "higher secondary", "hsc"]):
            profile["education"] = "Higher Secondary"
        elif any(term in q for term in ["10th", "sslc", "schooling"]):
            profile["education"] = "10th Pass"

        # State hints
        states = ["Tamil Nadu", "Kerala", "Karnataka", "Maharashtra", "Delhi", "Uttar Pradesh", "Bihar", "West Bengal", "Gujarat"]
        for s in states:
            if s.lower() in q:
                profile["state"] = s
                break

        # Caste / Category hints
        if "sc" in q or "scheduled caste" in q:
            profile["caste"] = "SC"
            profile["category"] = "SC/ST"
        elif "st" in q or "scheduled tribe" in q:
            profile["caste"] = "ST"
            profile["category"] = "SC/ST"
        elif "obc" in q or "bc" in q or "mbc" in q:
            profile["caste"] = "OBC"
            profile["category"] = "OBC"

        # Age parsing regex: e.g. "21 years old", "age 22"
        age_match = re.search(r'\b(age\s*[:\=]?\s*(\d{1,2})|(\d{1,2})\s*years?\s*old)\b', q)
        if age_match:
            try:
                age_val = int(age_match.group(2) or age_match.group(3))
                if 1 <= age_val <= 100:
                    profile["age"] = age_val
            except ValueError:
                pass

        # Income parsing regex: e.g. "income 150000", "1.5 lakh"
        if "lakh" in q or "lac" in q:
            lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)', q)
            if lakh_match:
                profile["income"] = int(float(lakh_match.group(1)) * 100000)
        else:
            inc_match = re.search(r'\b(?:income|rs|₹)\s*[:\=]?\s*(\d{5,7})\b', q)
            if inc_match:
                profile["income"] = int(inc_match.group(1))

        return profile

    @staticmethod
    def identify_missing_fields(profile: Dict[str, Any]) -> List[str]:
        missing = []
        if profile.get("age") is None:
            missing.append("Age")
        if profile.get("income") is None:
            missing.append("Annual Family Income")
        if not profile.get("occupation"):
            missing.append("Occupation")
        return missing

profile_agent = ProfileAgent()
