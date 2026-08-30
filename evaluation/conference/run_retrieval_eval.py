import json
import time
import math
import numpy as np
from pathlib import Path
import sys

# Ensure imports work from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.vector_store import SchemeVectorStore
from src.embeddings import load_embedding_model, embed_query
import faiss

def compute_ndcg(retrieved, expected, k):
    dcg = 0.0
    idcg = 0.0
    for i, res in enumerate(retrieved[:k]):
        if res in expected:
            dcg += 1.0 / math.log2(i + 2)
    for i in range(min(len(expected), k)):
        idcg += 1.0 / math.log2(i + 2)
    return dcg / idcg if idcg > 0 else 0.0

def run_evaluation(store: SchemeVectorStore, model, benchmark, name: str):
    metrics = {
        "recall_1": [], "recall_3": [], "recall_5": [], "recall_10": [],
        "precision_1": [], "precision_3": [], "precision_5": [], "precision_10": [],
        "mrr": [], "hit_rate": [], "ndcg_5": [], "ndcg_10": [],
        "latency": []
    }
    
    for item in benchmark:
        query = item['query']
        expected_ids = item['expected_scheme_ids']
        
        t0 = time.time()
        qvec = embed_query(query, model)
        results = store.search(qvec, top_k=10)
        latency = (time.time() - t0) * 1000
        metrics['latency'].append(latency)
        
        retrieved_ids = [r['scheme_id'] for r in results]
        
        # Calculate Metrics
        metrics['recall_1'].append(int(any(eid in retrieved_ids[:1] for eid in expected_ids)))
        metrics['recall_3'].append(int(any(eid in retrieved_ids[:3] for eid in expected_ids)))
        metrics['recall_5'].append(int(any(eid in retrieved_ids[:5] for eid in expected_ids)))
        metrics['recall_10'].append(int(any(eid in retrieved_ids[:10] for eid in expected_ids)))
        
        metrics['precision_1'].append(sum(1 for eid in expected_ids if eid in retrieved_ids[:1]) / 1)
        metrics['precision_3'].append(sum(1 for eid in expected_ids if eid in retrieved_ids[:3]) / 3)
        metrics['precision_5'].append(sum(1 for eid in expected_ids if eid in retrieved_ids[:5]) / 5)
        metrics['precision_10'].append(sum(1 for eid in expected_ids if eid in retrieved_ids[:10]) / 10)
        
        mrr = 0.0
        for i, rid in enumerate(retrieved_ids, 1):
            if rid in expected_ids:
                mrr = 1.0 / i
                break
        metrics['mrr'].append(mrr)
        metrics['hit_rate'].append(1 if mrr > 0 else 0)
        
        metrics['ndcg_5'].append(compute_ndcg(retrieved_ids, expected_ids, 5))
        metrics['ndcg_10'].append(compute_ndcg(retrieved_ids, expected_ids, 10))
        
    # Aggregate
    agg = {
        "recall_1": np.mean(metrics["recall_1"]),
        "recall_3": np.mean(metrics["recall_3"]),
        "recall_5": np.mean(metrics["recall_5"]),
        "recall_10": np.mean(metrics["recall_10"]),
        "precision_1": np.mean(metrics["precision_1"]),
        "precision_3": np.mean(metrics["precision_3"]),
        "precision_5": np.mean(metrics["precision_5"]),
        "precision_10": np.mean(metrics["precision_10"]),
        "mrr": np.mean(metrics["mrr"]),
        "hit_rate": np.mean(metrics["hit_rate"]),
        "ndcg_5": np.mean(metrics["ndcg_5"]),
        "ndcg_10": np.mean(metrics["ndcg_10"]),
        "mean_latency": np.mean(metrics["latency"]),
        "p50_latency": np.percentile(metrics["latency"], 50),
        "p95_latency": np.percentile(metrics["latency"], 95),
        "p99_latency": np.percentile(metrics["latency"], 99)
    }
    return agg

def main():
    root = Path(__file__).resolve().parent.parent.parent
    bench_file = root / "evaluation" / "conference" / "datasets" / "retrieval_benchmark.json"
    
    with open(bench_file, 'r', encoding='utf-8') as f:
        benchmark = json.load(f)
        
    print("Loading embedding model...")
    model = load_embedding_model()
    
    results = {}
    
    print("\nEvaluating OLD Index...")
    try:
        old_store = SchemeVectorStore()
        old_store.index_path = root / "data" / "index" / "schemes_backup.faiss"
        old_store.metadata_path = root / "data" / "index" / "schemes_metadata_backup.jsonl"
        old_store.index = faiss.read_index(str(old_store.index_path))
        
        records = []
        with open(old_store.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        old_store.metadata = records
        results["OLD"] = run_evaluation(old_store, model, benchmark, "OLD")
        print("OLD evaluation complete.")
    except Exception as e:
        print(f"Error evaluating OLD: {e}")
        
    print("\nEvaluating NEW Index...")
    try:
        new_store = SchemeVectorStore.load()
        results["NEW"] = run_evaluation(new_store, model, benchmark, "NEW")
        print("NEW evaluation complete.")
    except Exception as e:
        print(f"Error evaluating NEW: {e}")
        
    out_dir = root / "evaluation" / "conference" / "metrics"
    with open(out_dir / "retrieval_metrics.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(json.dumps(results, indent=2))
        
if __name__ == "__main__":
    main()
