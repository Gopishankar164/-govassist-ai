from src.eligibility import INSUFFICIENT_INFORMATION, NOT_ELIGIBLE, analyze_eligibility
from src.profile import extract_profile
from src.query_rewriter import rewrite_query
from src.reranker import classify_query_domain, rerank


def test_profile_extracts_only_stated_facts():
    profile = extract_profile("I am a 21 year old female engineering student from Tamil Nadu.")
    assert profile["age"] == 21 and profile["gender"] == "female" and profile["state"] == "Tamil Nadu"
    assert profile["income"] is None and profile["caste_category"] is None


def test_rewriter_preserves_query_and_does_not_invent_income():
    rewritten = rewrite_query("I need a scholarship", {"income": None, "state": None, "gender": None, "education": None, "occupation": None, "caste_category": None})
    assert "I need a scholarship" in rewritten and "income:" not in rewritten


def test_explicit_state_conflict_is_not_eligible():
    result = analyze_eligibility({"state": "Tamil Nadu", "gender_criteria": "unknown"}, {"state": "Kerala"})
    assert result["eligibility_status"] == NOT_ELIGIBLE


def test_missing_required_criterion_is_reported():
    result = analyze_eligibility({"state": "Tamil Nadu", "gender_criteria": "unknown"}, {"state": None})
    assert result["eligibility_status"] == INSUFFICIENT_INFORMATION


def test_unstated_disability_requirement_is_reported():
    result = analyze_eligibility(
        {"state": "unknown", "gender_criteria": "unknown", "eligibility_text": "The beneficiary must be a differently abled person."},
        {"state": None, "occupation": None},
    )
    assert result["eligibility_status"] == INSUFFICIENT_INFORMATION
    assert "disability status" in result["missing_information"]


def test_reranker_does_not_return_not_eligible_candidate():
    candidates = [{"similarity_score": 0.9, "eligibility_status": NOT_ELIGIBLE}, {"similarity_score": 0.7, "eligibility_status": "POTENTIALLY_ELIGIBLE"}]
    assert rerank(candidates)[0]["eligibility_status"] == "POTENTIALLY_ELIGIBLE"


def test_reranker_demotes_clear_business_mismatch_for_scholarship_query():
    candidates = [
        {"similarity_score": 0.80, "eligibility_status": "POTENTIALLY_ELIGIBLE", "scheme": {"category": "Business & Entrepreneurship", "scheme_name": "Payroll Subsidy"}},
        {"similarity_score": 0.75, "eligibility_status": "INSUFFICIENT_INFORMATION", "scheme": {"category": "Education & Learning", "scheme_name": "Engineering Scholarship"}},
    ]
    ranked = rerank(candidates, query="I am an engineering student looking for scholarships.", profile={"occupation": "student"})
    assert ranked[0]["scheme"]["scheme_name"] == "Engineering Scholarship"
    assert ranked[0]["domain_match"] == ["education"]


def test_reranker_keeps_payroll_scheme_for_explicit_epf_enterprise_query():
    candidates = [
        {"similarity_score": 0.80, "eligibility_status": "POTENTIALLY_ELIGIBLE", "scheme": {"category": "Business & Entrepreneurship", "scheme_name": "Payroll Subsidy"}},
        {"similarity_score": 0.79, "eligibility_status": "POTENTIALLY_ELIGIBLE", "scheme": {"category": "Education & Learning", "scheme_name": "Student Scholarship"}},
    ]
    ranked = rerank(candidates, query="I run a micro enterprise and need help with EPF costs.", profile={"occupation": "entrepreneur"})
    assert ranked[0]["scheme"]["scheme_name"] == "Payroll Subsidy"
    assert ranked[0]["domain_match"] == ["business"]


def test_query_domain_classifier_recognises_major_domains():
    assert classify_query_domain("I am a student looking for scholarships and education support.") == "education"
    assert classify_query_domain("I am a farmer needing irrigation and seed subsidy.") == "agriculture"
    assert classify_query_domain("I run a micro enterprise and need MSME business support.") == "business"
    assert classify_query_domain("I need help with house construction and affordable housing.") == "housing"
    assert classify_query_domain("I need a job placement or employment training program.") == "employment"
    assert classify_query_domain("I need a government grant for my situation.") == "other"


def test_rerank_uses_domain_intent_signal_without_inferring_new_profile_facts():
    candidates = [
        {"similarity_score": 0.80, "eligibility_status": "POTENTIALLY_ELIGIBLE", "scheme": {"category": "Housing & Shelter", "scheme_name": "Affordable Housing Grant"}},
        {"similarity_score": 0.79, "eligibility_status": "POTENTIALLY_ELIGIBLE", "scheme": {"category": "Education & Learning", "scheme_name": "Engineering Scholarship"}},
    ]
    ranked = rerank(
        candidates,
        query="I am a female engineering student looking for scholarships.",
        profile={"gender": "female", "education": "engineering"},
        use_domain_intent=True,
    )
    assert ranked[0]["scheme"]["scheme_name"] == "Engineering Scholarship"
    assert ranked[0]["domain_intent"] == "education"
    assert ranked[0]["domain_match"] == ["education"]
    assert "income" not in ranked[0].get("domain_intent", "")
