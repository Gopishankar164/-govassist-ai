import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import GovAssistPipeline

def run_tests():
    pipeline = GovAssistPipeline()
    
    test_queries = [
        "student scholarship",
        "farmer assistance in Maharashtra",
        "MSME loan for business",
        "employment skill development",
        "housing scheme",
        "women welfare program",
        "healthcare assistance",
        "disability welfare pension",
        "social welfare"
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for q in test_queries:
        try:
            res = pipeline.recommend(q, final_n=2)
            
            # Check for required structural elements
            has_answer = bool(res.get("answer"))
            has_recommendations = len(res.get("recommendations", [])) > 0
            
            valid_recs = True
            for rec in res.get("recommendations", []):
                # Ensure each scheme has eligibility status, why it matched, etc.
                if not rec.get("eligibility_status"): valid_recs = False
                if "missing_information" not in rec: valid_recs = False
                
            is_pass = has_answer and has_recommendations and valid_recs
            
            if is_pass:
                passed += 1
            else:
                failed += 1
                
            results.append({
                "query": q,
                "passed": is_pass,
                "has_answer": has_answer,
                "num_recommendations": len(res.get("recommendations", []))
            })
        except Exception as e:
            failed += 1
            results.append({"query": q, "passed": False, "error": str(e)})
            
    report = {
        "number_tested": len(test_queries),
        "passed": passed,
        "failed": failed,
        "details": results
    }
    
    out_path = Path(__file__).parent / "results" / "response_evaluation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    print(f"Response tests run: {len(test_queries)}. Passed: {passed}. Failed: {failed}.")

if __name__ == "__main__":
    run_tests()
