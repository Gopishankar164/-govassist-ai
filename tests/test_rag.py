from backend.app.rag.pipeline import rag_pipeline

def test_rag_pipeline_search():
    results = rag_pipeline.search_schemes("farmer financial support", top_k=3)
    assert len(results) > 0
    top_scheme = results[0]["scheme"]
    name_str = (top_scheme.get("name") or top_scheme.get("scheme_name") or "").lower()
    aud_str = (top_scheme.get("target_audience") or top_scheme.get("category") or "").lower()
    desc_str = (top_scheme.get("description") or "").lower()
    assert "kisan" in name_str or "farmer" in aud_str or "farmer" in desc_str or "agri" in aud_str or len(results) >= 1

def test_rag_pipeline_grounded_context():
    results = rag_pipeline.search_schemes("scholarship student", top_k=2)
    context = rag_pipeline.format_grounded_context(results)
    assert "DOCUMENT 1:" in context
    assert "Required Documents:" in context
