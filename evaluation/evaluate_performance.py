import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
from src.embeddings import load_embedding_model, embed_query
from src.vector_store import SchemeVectorStore
from src.eligibility import analyze_eligibility
from src.generator import build_grounded_answer

def main():
    print("=== PERFORMANCE EVALUATION ===")
    
    t0 = time.time()
    model = load_embedding_model()
    model_load_time = time.time() - t0
    print(f"Model Load Time: {model_load_time*1000:.2f} ms")
    
    t0 = time.time()
    store = SchemeVectorStore.load()
    faiss_load_time = time.time() - t0
    print(f"FAISS & Metadata Load Time: {faiss_load_time*1000:.2f} ms")
    
    query = "I am a female student looking for engineering scholarships."
    profile = {"gender": "female", "occupation": "student"}
    
    t0 = time.time()
    qvec = embed_query(query, model)
    embed_time = time.time() - t0
    print(f"Query Embedding Time: {embed_time*1000:.2f} ms")
    
    t0 = time.time()
    results = store.search(qvec, top_k=5)
    search_time = time.time() - t0
    print(f"FAISS Search Time (k=5): {search_time*1000:.2f} ms")
    
    t0 = time.time()
    for r in results:
        r.update(analyze_eligibility(r["scheme"], profile))
    eligibility_time = time.time() - t0
    print(f"Eligibility Processing Time (5 records): {eligibility_time*1000:.2f} ms")
    
    t0 = time.time()
    build_grounded_answer(results, profile, "education")
    generation_time = time.time() - t0
    print(f"Generation Time: {generation_time*1000:.2f} ms")
    
    total_latency = embed_time + search_time + eligibility_time + generation_time
    print(f"Total Inference Latency (excluding load): {total_latency*1000:.2f} ms")
    
    bottleneck = max([
        ("Embedding", embed_time),
        ("Search", search_time),
        ("Eligibility", eligibility_time),
        ("Generation", generation_time)
    ], key=lambda x: x[1])
    
    print(f"Bottleneck during inference: {bottleneck[0]}")
    
    out_dir = Path("evaluation/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "performance_metrics.json", "w") as f:
        json.dump({
            "model_load_ms": model_load_time * 1000,
            "faiss_load_ms": faiss_load_time * 1000,
            "embedding_ms": embed_time * 1000,
            "search_ms": search_time * 1000,
            "eligibility_ms": eligibility_time * 1000,
            "generation_ms": generation_time * 1000,
            "total_inference_ms": total_latency * 1000,
            "bottleneck": bottleneck[0]
        }, f, indent=2)

if __name__ == "__main__":
    main()
