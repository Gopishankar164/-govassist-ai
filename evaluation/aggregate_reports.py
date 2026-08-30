import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def generate_report():
    retrieval_file = ROOT / "results" / "retrieval_evaluation.json"
    eligibility_file = ROOT / "results" / "eligibility_evaluation.json"
    grounding_file = ROOT / "results" / "grounding_evaluation.json"
    response_file = ROOT / "results" / "response_evaluation.json"
    performance_file = ROOT / "results" / "performance_evaluation.json"
    
    retrieval = json.loads(retrieval_file.read_text())
    eligibility = json.loads(eligibility_file.read_text())
    grounding = json.loads(grounding_file.read_text())
    response = json.loads(response_file.read_text())
    performance = json.loads(performance_file.read_text())
    
    report = {
        "dataset_size": retrieval["dataset_statistics"]["canonical_records"],
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "vector_store": "FAISS IndexFlatIP",
        "dimension": 384,
        "retrieval_metrics": retrieval["retrieval_metrics"],
        "performance": {
            "startup_latency_ms": performance["startup_latency_ms"],
            "first_query_latency_ms": performance["first_query_latency_ms"],
            "mean_retrieval_latency_ms": retrieval["latency_ms"]["mean"],
            "p95_retrieval_latency_ms": retrieval["latency_ms"]["p95"]
        },
        "eligibility": {
            "number_tested": eligibility["number_tested"],
            "correct": eligibility["correct"],
            "incorrect": eligibility["incorrect"],
            "insufficient_information_cases": eligibility["insufficient_information_cases"]
        },
        "grounding": {
            "number_tested": grounding["number_tested"],
            "supported_claims": grounding["supported_claims"],
            "unsupported_claims": grounding["unsupported_claims"],
            "grounding_rate": grounding["grounding_rate"]
        },
        "response_quality": {
            "number_tested": response["number_tested"],
            "passed": response["passed"],
            "failed": response["failed"]
        }
    }
    
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = reports_dir / "current_system_evaluation.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    md = f"""# GovAssist AI Current System Evaluation

**Dataset:** {report['dataset_size']}
**Embedding model:** {report['embedding_model']}
**Vector store:** {report['vector_store']}
**Dimension:** {report['dimension']}

## Retrieval metrics
* Precision@1: {report['retrieval_metrics']['precision_at_1']:.4f}
* Precision@3: {report['retrieval_metrics']['precision_at_3']:.4f}
* Precision@5: {report['retrieval_metrics']['precision_at_5']:.4f}
* Recall@3: {report['retrieval_metrics']['recall_at_3']:.4f}
* Recall@5: {report['retrieval_metrics']['recall_at_5']:.4f}
* Recall@10: {report['retrieval_metrics']['recall_at_10']:.4f}
* MRR: {report['retrieval_metrics']['mrr']:.4f}
* Hit Rate@5: {report['retrieval_metrics']['hit_rate_at_5']:.4f}

## Performance
* startup latency: {report['performance']['startup_latency_ms']:.2f} ms
* first-query latency: {report['performance']['first_query_latency_ms']:.2f} ms
* mean retrieval latency: {report['performance']['mean_retrieval_latency_ms']:.2f} ms
* P95 latency: {report['performance']['p95_retrieval_latency_ms']:.2f} ms

## Eligibility
* number tested: {report['eligibility']['number_tested']}
* correct: {report['eligibility']['correct']}
* incorrect: {report['eligibility']['incorrect']}
* insufficient-information cases: {report['eligibility']['insufficient_information_cases']}

## Grounding
* number tested: {report['grounding']['number_tested']}
* supported claims: {report['grounding']['supported_claims']}
* unsupported claims: {report['grounding']['unsupported_claims']}
* grounding rate: {report['grounding']['grounding_rate']:.2%}

## Response quality
* number tested: {report['response_quality']['number_tested']}
* passed: {report['response_quality']['passed']}
* failed: {report['response_quality']['failed']}
"""
    
    md_path = reports_dir / "current_system_evaluation.md"
    md_path.write_text(md, encoding="utf-8")
    
    print("Final reports generated at evaluation/reports/")

if __name__ == "__main__":
    generate_report()
