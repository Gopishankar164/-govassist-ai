import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
import faiss
import numpy as np

from src.vector_store import SchemeVectorStore
from src.embeddings import load_embedding_model, embed_query
from src.config import DEFAULT_TOP_K

# Curated evaluation queries and the expected relevant scheme slug/ID
# Assuming we have some ground truth labels to test Recall@K
EVAL_DATA = [
    {
        "query": "I am a female engineering student from Tamil Nadu. What government schemes may be relevant to me?",
        "expected_ids": [] # We will just collect metrics if no ground truth
    },
    {
        "query": "I am a farmer looking for financial assistance.",
        "expected_ids": []
    },
    {
        "query": "I am a woman entrepreneur looking for government support.",
        "expected_ids": []
    },
    {
        "query": "I need financial help for education.",
        "expected_ids": []
    },
    {
        "query": "What government schemes are available?",
        "expected_ids": []
    }
]

def compute_metrics(results, expected_ids):
    retrieved_ids = [r['scheme_id'] for r in results]
    recall_1 = int(any(eid in retrieved_ids[:1] for eid in expected_ids)) if expected_ids else None
    recall_5 = int(any(eid in retrieved_ids[:5] for eid in expected_ids)) if expected_ids else None
    recall_10 = int(any(eid in retrieved_ids[:10] for eid in expected_ids)) if expected_ids else None
    
    mrr = 0.0
    if expected_ids:
        for i, rid in enumerate(retrieved_ids[:10], 1):
            if rid in expected_ids:
                mrr = 1.0 / i
                break
                
    return recall_1, recall_5, recall_10, mrr

def evaluate_index(store: SchemeVectorStore, model, name: str):
    print(f"\n{'='*60}")
    print(f"EVALUATING {name} INDEX")
    print(f"Vectors: {store.index.ntotal} | Metadata: {len(store.metadata)}")
    print(f"{'='*60}")
    
    latencies = []
    
    for item in EVAL_DATA:
        query = item['query']
        expected_ids = item['expected_ids']
        
        qvec = embed_query(query, model)
        t0 = time.time()
        results = store.search(qvec, top_k=10)
        latency = (time.time() - t0) * 1000
        latencies.append(latency)
        
        r1, r5, r10, mrr = compute_metrics(results, expected_ids)
        
        print(f"\nQUERY: {query}")
        print(f"Latency: {latency:.2f} ms")
        for i, r in enumerate(results[:5], 1):
            url = r['scheme'].get('official_url', 'N/A')
            is_expected = "Yes" if expected_ids and r['scheme_id'] in expected_ids else ("N/A" if not expected_ids else "No")
            print(f"  {i}. {r['scheme_name']} (Score: {r['similarity_score']:.4f})")
            print(f"     URL: {url} | Expected Match: {is_expected}")
            
    print(f"\n{name} OVERALL LATENCY:")
    print(f"  Avg: {np.mean(latencies):.2f} ms")
    print(f"  p50: {np.percentile(latencies, 50):.2f} ms")
    print(f"  p95: {np.percentile(latencies, 95):.2f} ms")

def main():
    print("Loading embedding model...")
    model = load_embedding_model()
    
    print("\nAttempting to load OLD index backup...")
    try:
        old_store = SchemeVectorStore()
        old_store.index_path = Path("data/index/schemes_backup.faiss")
        old_store.metadata_path = Path("data/index/schemes_metadata_backup.jsonl")
        old_store.index = faiss.read_index(str(old_store.index_path))
        
        records = []
        with open(old_store.metadata_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        old_store.metadata = records
        evaluate_index(old_store, model, "OLD")
    except Exception as e:
        print(f"Could not load OLD index: {e}")
        
    print("\nAttempting to load NEW production index...")
    try:
        new_store = SchemeVectorStore.load()
        if new_store.index.ntotal != 4858:
            print(f"[BLOCKED] NEW index has {new_store.index.ntotal} vectors instead of 4858. Please run build_index.py on GPU.")
        else:
            evaluate_index(new_store, model, "NEW")
    except Exception as e:
        print(f"[BLOCKED] Could not load NEW index: {e}")

if __name__ == "__main__":
    main()
