"""
build_index.py -- Stage 3 + Stage 4 combined runner.

RUN THIS ON A MACHINE WITH NORMAL INTERNET ACCESS (e.g. your Windows box),
NOT inside a network-restricted sandbox -- it needs to download
BAAI/bge-small-en-v1.5 from Hugging Face Hub the first time it runs.

Usage:
    python build_index.py

What it does (no fabricated data, no shortcuts):
    1. Loads the canonical processed dataset (must already exist -- run
       `python -m src.ingestion` first).
    2. Builds a real semantic document per scheme.
    3. Embeds every document with the real bge-small-en-v1.5 model.
    4. Verifies embedding count == record count (stops otherwise).
    5. Runs 4 sanity-check queries and prints top-5 nearest schemes for each,
       purely for you to visually judge whether retrieval looks reasonable.
       These are NOT final recommendations -- eligibility isn't applied yet.
    6. Builds a real FAISS IndexFlatIP index.
    7. Saves the index + metadata to data/index/.
    8. Destroys the in-memory index and reloads it from disk to prove
       persistence works, then re-runs one query to confirm identical results.
    9. Runs the 5 required retrieval-only test queries and prints top-10
       results with real similarity scores for each.
"""
import time
import numpy as np

from src.embeddings import load_processed_records, load_embedding_model, embed_records, embed_query
from src.vector_store import SchemeVectorStore
from src.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH, DEFAULT_TOP_K


SANITY_QUERIES = [
    "I am a female engineering student from Tamil Nadu",
    "I am a farmer looking for government assistance",
    "I am a woman entrepreneur looking for financial support",
    "I need a scholarship for education",
]

RETRIEVAL_TEST_QUERIES = [
    "I am a female engineering student from Tamil Nadu. What government schemes may be relevant to me?",
    "I am a farmer looking for financial assistance.",
    "I am a woman entrepreneur looking for government support.",
    "I need financial help for education.",
    "What government schemes are available?",
]


import sys
import torch

def main():
    import os
    from src.config import RAW_CSV_PATH
    
    print("\n=== PHASE 2: CPU-SAFE INDEX HANDLING ===")
    print(f"Dataset path: {RAW_CSV_PATH}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device being used: {device.upper()}")
    
    print("Loading canonical processed records...")
    records = load_processed_records()
    print(f"Loaded {len(records)} records.\n")

    if device == "cpu" and len(records) > 4000:
        if "--allow-cpu" not in sys.argv:
            print("[WARNING] CPU indexing for 4,858 records would take several hours.")
            print("[BLOCKED] Aborting automatic FAISS index build on CPU.")
            print("To build the index, please run this script on a CUDA-enabled machine, or use --allow-cpu to force CPU execution:")
            print("    python build_index.py --allow-cpu")
            sys.exit(0)
        else:
            print("[WARNING] Proceeding with full 4858-record index build on CPU as requested (--allow-cpu).")

    print("Loading embedding model (this downloads the model on first run)...")
    model = load_embedding_model()

    print("\n=== EMBEDDING GENERATION ===")
    result = embed_records(records, model)
    embeddings = result["embeddings"]

    assert embeddings.shape[0] == len(records), "STOP: embedding count != record count"
    print("Number of embeddings == number of canonical records: True\n")

    print("=== EMBEDDING VALIDATION (sanity checks only -- NOT final recommendations) ===")
    for q in SANITY_QUERIES:
        qvec = embed_query(q, model)
        sims = embeddings @ qvec  # embeddings already normalized -> cosine similarity
        top5_idx = np.argsort(-sims)[:5]
        print(f"\nQuery: {q}")
        for rank, idx in enumerate(top5_idx, start=1):
            print(f"  {rank}. {records[idx]['scheme_name']} -- similarity={sims[idx]:.4f}")

    print("\n=== BUILDING FAISS INDEX ===")
    metadata = records  # full canonical record retained per vector, nothing lost
    store = SchemeVectorStore()
    build_time = store.build_index(embeddings, metadata)
    store.save()
    print(f"Saved FAISS index -> {FAISS_INDEX_PATH}")
    print(f"Saved metadata -> {FAISS_METADATA_PATH}")

    print("\n=== INDEX RELOAD TEST ===")
    test_query_vec = embed_query(SANITY_QUERIES[0], model)
    results_before = store.search(test_query_vec, top_k=5)

    del store
    reloaded = SchemeVectorStore.load()
    results_after = reloaded.search(test_query_vec, top_k=5)

    consistent = (
        [r["scheme_id"] for r in results_before] == [r["scheme_id"] for r in results_after]
        and all(abs(a["similarity_score"] - b["similarity_score"]) < 1e-5
                for a, b in zip(results_before, results_after))
    )
    print("Index vectors:", reloaded.index.ntotal)
    print("Metadata records:", len(reloaded.metadata))
    print("Dimension:", reloaded.index.d)
    print("Reload successful:", reloaded.index.ntotal == len(records))
    print("Search consistency:", consistent)
    if reloaded.index.ntotal != len(reloaded.metadata):
        raise RuntimeError("STOP: metadata count != FAISS vector count after reload.")

    print("\n=== RETRIEVAL-ONLY TESTS (candidates, NOT final recommendations) ===")
    for q in RETRIEVAL_TEST_QUERIES:
        qvec = embed_query(q, model)
        t0 = time.time()
        results = reloaded.search(qvec, top_k=DEFAULT_TOP_K)
        latency = time.time() - t0
        print("\n" + "-" * 60)
        print("QUERY:", q)
        print("-" * 60)
        print(f"Retrieval latency: {latency*1000:.2f}ms")
        print("TOP 10 RETRIEVAL RESULTS:")
        for r in results:
            print(f"  {r['rank']:2d}. {r['scheme_name']} -- similarity={r['similarity_score']:.4f}")

    print("\nDone. This is retrieval only -- eligibility filtering happens in a later stage.")


if __name__ == "__main__":
    main()
