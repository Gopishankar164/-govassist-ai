"""Isolated ranking experiments for the persisted GovAssist BGE + FAISS system.

This module never writes the FAISS index, embeddings, production pipeline, or
locked baseline.  It evaluates only ranking representations over the existing
index and writes a separate experiment artifact.
"""
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
BASELINE_PATH = ROOT / "results" / "baseline.json"
RESULTS_PATH = ROOT / "results" / "ranking_experiments.json"
METRIC_KS = (1, 3, 5, 10, 20)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    position = 0.95 * (len(ordered) - 1)
    lower, upper = int(position), min(int(position) + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def metric_report(runs: list[dict]) -> dict:
    precision = {k: [] for k in METRIC_KS}
    recall = {k: [] for k in METRIC_KS}
    hit_rate = {k: [] for k in METRIC_KS}
    reciprocal_ranks, latencies = [], []
    for run in runs:
        relevant = set(run["expected_scheme_ids"])
        retrieved = run["retrieved_scheme_ids"]
        for k in METRIC_KS:
            hits = len(set(retrieved[:k]) & relevant)
            precision[k].append(hits / k)
            recall[k].append(hits / len(relevant))
            hit_rate[k].append(1.0 if hits else 0.0)
        first_rank = next((rank for rank, scheme_id in enumerate(retrieved, 1) if scheme_id in relevant), None)
        run["first_relevant_rank"] = first_rank
        run["reciprocal_rank"] = 1 / first_rank if first_rank else 0.0
        reciprocal_ranks.append(run["reciprocal_rank"])
        latencies.append(run["latency_ms"])
    return {
        **{f"precision_at_{k}": mean(precision[k]) for k in METRIC_KS},
        **{f"recall_at_{k}": mean(recall[k]) for k in METRIC_KS},
        **{f"hit_rate_at_{k}": mean(hit_rate[k]) for k in METRIC_KS},
        "mrr": mean(reciprocal_ranks),
        "latency_ms": {"mean": mean(latencies), "median": statistics.median(latencies), "p95": p95(latencies)},
    }


def evaluate(pipeline: GovAssistPipeline, labels: list[dict], name: str, query_mode: str, candidate_k: int, apply_reranker: bool) -> dict:
    """Run an isolated ranking mode against the loaded production index."""
    runs = []
    for label in labels:
        profile = extract_profile(label["query"])
        representation = label["query"] if query_mode == "raw" else rewrite_query(label["query"], profile)
        start = time.perf_counter()
        candidates = pipeline.store.search(embed_query(representation, pipeline.model), top_k=candidate_k)
        if apply_reranker:
            analyzed = []
            for candidate in candidates:
                candidate = dict(candidate)
                candidate.update(analyze_eligibility(candidate["scheme"], profile))
                analyzed.append(candidate)
            candidates = rerank(analyzed, limit=candidate_k)
        latency_ms = (time.perf_counter() - start) * 1000
        runs.append({
            "query": label["query"],
            "query_representation": representation,
            "expected_scheme_ids": label["relevant_scheme_ids"],
            "retrieved_scheme_ids": [candidate["scheme_id"] for candidate in candidates],
            "latency_ms": latency_ms,
        })
    return {
        "name": name,
        "query_mode": query_mode,
        "candidate_k": candidate_k,
        "existing_reranker_applied": apply_reranker,
        "metrics": metric_report(runs),
        "per_query": runs,
    }


def failure_analysis(pipeline: GovAssistPipeline, labels: list[dict]) -> list[dict]:
    targets = {"cm-swaniyojan-yojana", "aabcs"}
    metadata_by_id = {record["scheme_id"]: record for record in pipeline.store.metadata}
    output = []
    for label in labels:
        target_id = next((scheme_id for scheme_id in label["relevant_scheme_ids"] if scheme_id in targets), None)
        if not target_id:
            continue
        profile = extract_profile(label["query"])
        raw = label["query"]
        enhanced = rewrite_query(raw, profile)
        rankings = {}
        for mode, representation in (("raw", raw), ("enhanced", enhanced)):
            full_ranking = pipeline.store.search(embed_query(representation, pipeline.model), top_k=pipeline.store.index.ntotal)
            target_rank = next((item["rank"] for item in full_ranking if item["scheme_id"] == target_id), None)
            rankings[mode] = {
                "target_rank": target_rank,
                "top_10": [{"scheme_id": item["scheme_id"], "scheme_name": item["scheme_name"], "similarity_score": item["similarity_score"]} for item in full_ranking[:10]],
            }
        target = metadata_by_id[target_id]
        output.append({
            "query": raw,
            "target_scheme_id": target_id,
            "target_scheme_name": target["scheme_name"],
            "target_category": target.get("category"),
            "target_tags": target.get("tags"),
            "target_description_excerpt": (target.get("description") or "")[:500],
            "target_eligibility_excerpt": (target.get("eligibility_text") or "")[:500],
            "raw_query_representation": raw,
            "enhanced_query_representation": enhanced,
            "rankings": rankings,
        })
    return output


def row(name: str, metrics: dict) -> str:
    return " | ".join((
        name,
        f"{metrics['precision_at_1']:.4f}", f"{metrics['precision_at_3']:.4f}", f"{metrics['precision_at_5']:.4f}",
        f"{metrics['recall_at_3']:.4f}", f"{metrics['recall_at_5']:.4f}", f"{metrics['recall_at_10']:.4f}",
        f"{metrics['mrr']:.4f}", f"{metrics['hit_rate_at_5']:.4f}", f"{metrics['latency_ms']['mean']:.2f}",
    ))


def main() -> None:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(f"Locked baseline missing: {BASELINE_PATH}")
    labels = json.loads(LABELS_PATH.read_text(encoding="utf-8"))["queries"]
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline_metrics = {**baseline["retrieval_metrics"], "latency_ms": baseline["latency_ms"]}
    pipeline = GovAssistPipeline()

    methods = [
        evaluate(pipeline, labels, "Raw query, BGE + FAISS (K=10)", "raw", 10, False),
        evaluate(pipeline, labels, "Enhanced stated-profile query, BGE + FAISS (K=10)", "enhanced", 10, False),
        evaluate(pipeline, labels, "Enhanced query, BGE + FAISS + existing reranker (K=10)", "enhanced", 10, True),
        evaluate(pipeline, labels, "Enhanced query, BGE + FAISS (K=5)", "enhanced", 5, False),
        evaluate(pipeline, labels, "Enhanced query, BGE + FAISS (K=20)", "enhanced", 20, False),
    ]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_path": str(BASELINE_PATH),
        "baseline_preserved": True,
        "query_count": len(labels),
        "baseline_metrics": baseline_metrics,
        "methods": methods,
        "failure_analysis": failure_analysis(pipeline, labels),
        "eligibility_note": "Eligibility correctness is not evaluated. The reranker experiment uses existing eligibility statuses only as a ranking feature.",
    }
    RESULTS_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("GovAssist isolated ranking experiments")
    print("Method | P@1 | P@3 | P@5 | R@3 | R@5 | R@10 | MRR | Hit@5 | Mean Latency (ms)")
    print(row("Locked baseline", baseline_metrics))
    for method in methods:
        print(row(method["name"], method["metrics"]))
    print(f"Results saved: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
