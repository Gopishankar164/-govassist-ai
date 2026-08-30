import os
import time
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from src.embeddings import load_processed_records, build_document_text

def run_benchmark():
    records = load_processed_records()[:50]
    docs = [build_document_text(r) for r in records]
    
    print("Loading model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu", local_files_only=True)
    
    # 1. Unoptimized baseline
    print("\n--- UNOPTIMIZED BASELINE ---")
    t0 = time.time()
    embs_unopt = model.encode(docs, batch_size=32, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    time_unopt = time.time() - t0
    print(f"Time for 50 records: {time_unopt:.2f}s")
    
    # 2. Optimized
    print("\n--- OPTIMIZED CPU INFERENCE ---")
    threads = os.cpu_count() or 4
    torch.set_num_threads(threads)
    print(f"Set PyTorch threads to: {threads}")
    
    t0 = time.time()
    with torch.inference_mode():
        embs_opt = model.encode(docs, batch_size=32, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
    time_opt = time.time() - t0
    print(f"Time for 50 records: {time_opt:.2f}s")
    
    # Compare
    print("\n--- COMPARISON ---")
    print(f"Dimension matches: {embs_unopt.shape[1] == embs_opt.shape[1]} ({embs_opt.shape[1]})")
    
    sim = np.sum(embs_unopt * embs_opt, axis=1) # Cosine similarity
    print(f"Average Cosine Similarity: {np.mean(sim):.6f}")
    print(f"Minimum Cosine Similarity: {np.min(sim):.6f}")
    
    speedup = time_unopt / time_opt
    print(f"Speedup: {speedup:.2f}x")
    
    total_records = 4858
    est_total_time = (time_opt / 50) * total_records
    print(f"\nEstimated total time for {total_records} records: {est_total_time/60:.2f} minutes")

if __name__ == "__main__":
    run_benchmark()
