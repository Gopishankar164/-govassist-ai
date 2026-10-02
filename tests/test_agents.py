from backend.app.agents.graph import langgraph_engine
from backend.app.agents.profile import profile_agent
from backend.app.agents.query_rewriter import query_rewriter_agent
from backend.app.agents.eligibility import eligibility_agent
from backend.app.agents.verification import verification_agent

def test_profile_extraction_agent():
    query = "I am a 21 year old female engineering student from Tamil Nadu"
    profile = profile_agent.extract_profile_from_text(query, {})
    assert profile.get("occupation") == "Student"
    assert profile.get("gender") == "Female"
    assert profile.get("state") == "Tamil Nadu"

def test_query_rewriter_agent():
    query = "I am a female engineering student"
    profile = {"occupation": "Student", "gender": "Female", "state": "Tamil Nadu"}
    rewritten = query_rewriter_agent.rewrite_query(query, profile)
    assert "scholarship" in rewritten or "student" in rewritten

def test_eligibility_agent():
    profile = {"age": 22, "income": 150000, "occupation": "Student", "gender": "Female"}
    scheme = {
        "id": "s1", "name": "Scholarship", "eligibility": {"min_age": 18, "max_age": 30, "max_income": 300000, "occupations": ["Student"], "gender": "All"}
    }
    eval_res = eligibility_agent.evaluate_scheme(profile, scheme)
    assert eval_res["status"] == "Eligible"
    assert eval_res["is_eligible"] is True

def test_langgraph_engine_execution():
    session_id = "test_sess_001"
    query = "I am an engineering student"
    profile = {"age": 22, "income": 150000, "occupation": "Student", "gender": "Female"}
    
    result = langgraph_engine.run(session_id, query, profile, "en")
    
    assert "workflow_trace" in result
    assert len(result["workflow_trace"]) >= 6
    assert "eligible_schemes" in result
    assert isinstance(result["eligible_schemes"], list)
    
    if result["eligible_schemes"]:
        top = result["eligible_schemes"][0]
        assert "confidence_score" in top
        assert top["confidence_score"] > 50.0
        assert "Document Grounded" in top["document_verification"]["badge"]
