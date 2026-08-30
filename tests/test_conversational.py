import pytest
from src.pipeline import GovAssistPipeline
from src.profile import extract_profile, merge_profiles

def test_student_scholarship_query_extraction():
    query = "I am a female engineering student from Tamil Nadu looking for scholarships"
    profile = extract_profile(query)
    assert profile["gender"] == "female"
    assert "engineering" in profile["education"]
    assert "student" in profile["education"]
    assert profile["state"] == "Tamil Nadu"

def test_farmer_query_extraction():
    query = "I am a farmer from Maharashtra with an annual income of Rs 50000"
    profile = extract_profile(query)
    assert profile["occupation"] == "farmer"
    assert profile["state"] == "Maharashtra"
    assert profile["income"] == 50000

def test_housing_query_extraction():
    query = "I am looking for housing assistance in Karnataka"
    profile = extract_profile(query)
    assert profile["state"] == "Karnataka"
    assert profile["occupation"] is None

def test_employment_query_extraction():
    query = "I am an artisan looking for skill development"
    profile = extract_profile(query)
    assert profile["occupation"] == "artisan"

def test_missing_profile_information_merging():
    base = {"state": "Kerala", "income": None, "caste_category": None}
    new_query = "My income is 150000"
    extracted = extract_profile(new_query)
    merged = merge_profiles(base, extracted)
    
    assert merged["state"] == "Kerala" # Preserved from base
    assert merged["income"] == 150000  # Updated from new query
    assert merged["caste_category"] is None

def test_follow_up_profile_information_override():
    base = {"state": "Goa", "occupation": "student"}
    new_query = "Actually I am a business owner now"
    extracted = extract_profile(new_query)
    merged = merge_profiles(base, extracted)
    
    assert merged["state"] == "Goa" # Preserved
    assert merged["occupation"] == "business owner" # Overridden!

def test_irrelevant_query_domain():
    from src.reranker import classify_query_domain
    domain = classify_query_domain("What is the weather today?")
    assert domain == "other"

def test_empty_query():
    profile = extract_profile("")
    assert all(v is None for v in profile.values())

def test_malformed_request_merging():
    base = {"age": 25}
    extracted = extract_profile("I am !!! years old")
    merged = merge_profiles(base, extracted)
    assert merged["age"] == 25 # Did not extract invalid age, base is preserved

def test_no_hallucinated_eligibility():
    pipeline = GovAssistPipeline()
    # A query with no profile info should not be marked as ELIGIBLE
    result = pipeline.recommend("I need financial support")
    for rec in result["recommendations"]:
        assert rec["eligibility_status"] != "ELIGIBLE" # It lacks strict evidence
        
def test_grounded_benefits_and_application():
    pipeline = GovAssistPipeline()
    result = pipeline.recommend("student scholarships")
    assert len(result["recommendations"]) > 0
    assert "answer" in result
    # We no longer test for literal "Benefits:" in answer, since answer is just the conversational preamble.
    # The actual benefits are passed as structured data for the frontend to render!
    for rec in result["recommendations"]:
        scheme = rec["scheme"]
        assert "benefits" in scheme
        assert "application_process" in scheme
