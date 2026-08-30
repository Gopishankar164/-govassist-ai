"""Evaluate final-reranking variants without overwriting locked retrieval results."""
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.embeddings import embed_query
from src.eligibility import analyze_eligibility
from src.pipeline import GovAssistPipeline
from src.profile import extract_profile
from src.query_rewriter import rewrite_query
from src.reranker import rerank


ROOT = Path(__file__).resolve().parent
LABELS_PATH = ROOT / "evaluation_queries.json"
LOCKED_BASELINE_PATH = ROOT / "results" / "baseline.json"
RESULTS_PATH = ROOT / "results" / "final_reranking_evaluation.json"
K_VALUES = (1, 3, 5, 10)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    position = 0.95 * (len(ordered) - 1)
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def metrics(runs: list[dict]) -> dict:
    precision = {k: [] for k in K_VALUES}
    recall = {k: [] for k in K_VALUES if k > 1}
    hits, reciprocal_ranks, latencies = [], [], []
    for run in runs:
        relevant = set(run["expected_scheme_ids"])
        ranked = run["ranked_scheme_ids"]
        first_rank = next((rank for rank, scheme_id in enumerate(ranked, 1) if scheme_id in relevant), None)
        reciprocal_ranks.append(1 / first_rank if first_rank else 0.0)
        for k in K_VALUES:
            relevant_at_k = len(set(ranked[:k]) & relevant)
            precision[k].append(relevant_at_k / k)
            if k > 1:
                recall[k].append(relevant_at_k / len(relevant))
        hits.append(1.0 if set(ranked[:5]) & relevant else 0.0)
        latencies.append(run["latency_ms"])
    return {
        **{f"precision_at_{k}": mean(precision[k]) for k in K_VALUES},
        **{f"recall_at_{k}": mean(recall[k]) for k in recall},
        "mrr": mean(reciprocal_ranks),
        "hit_rate_at_5": mean(hits),
        "latency_ms": {"mean": mean(latencies), "median": statistics.median(latencies), "p95": p95(latencies)},
    }


def evaluate(pipeline: GovAssistPipeline, labels: list[dict], apply_guard: bool) -> dict:
    runs = []
    for label in labels:
        profile = extract_profile(label["query"])
        representation = rewrite_query(label["query"], profile)
        start = time.perf_counter()
        retrieved = pipeline.store.search(embed_query(representation, pipeline.model), top_k=10)
        analyzed = []
        for candidate in retrieved:
            candidate = dict(candidate)
            candidate.update(analyze_eligibility(candidate["scheme"], profile))
            analyzed.append(candidate)
        ranked = rerank(analyzed, limit=10, query=label["query"] if apply_guard else "", profile=profile if apply_guard else None)
        runs.append({
            "query": label["query"],
            "expected_scheme_ids": label["relevant_scheme_ids"],
            "ranked_scheme_ids": [item["scheme_id"] for item in ranked],
            "latency_ms": (time.perf_counter() - start) * 1000,
        })
    return {"name": "Domain-aware final reranker" if apply_guard else "Existing final reranker", "metrics": metrics(runs), "per_query": runs}


def main() -> None:
    labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))["queries"]
    locked_baseline = json.loads(LOCKED_BASELINE_PATH.read_text(encoding="utf-8"))
    pipeline = GovAssistPipeline()
    existing = evaluate(pipeline, labels, apply_guard=False)
    guarded = evaluate(pipeline, labels, apply_guard=True)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "query_count": len(labels),
        "locked_retrieval_baseline_path": str(LOCKED_BASELINE_PATH),
        "locked_retrieval_baseline_preserved": True,
        "locked_retrieval_baseline_metrics": locked_baseline["retrieval_metrics"],
        "methods": [existing, guarded],
        "note": "These are final-ranking metrics over the same top-10 FAISS candidates. They are separate from the locked retrieval-only baseline.",
    }
    RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    for method in report["methods"]:
        result = method["metrics"]
        print(method["name"])
        print(f"P@1={result['precision_at_1']:.4f} P@3={result['precision_at_3']:.4f} P@5={result['precision_at_5']:.4f}")
        print(f"R@3={result['recall_at_3']:.4f} R@5={result['recall_at_5']:.4f} R@10={result['recall_at_10']:.4f}")
        print(f"MRR={result['mrr']:.4f} Hit@5={result['hit_rate_at_5']:.4f} Mean latency={result['latency_ms']['mean']:.2f} ms")
    print(f"Results saved: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
