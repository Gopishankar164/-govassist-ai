import os
import time
import torch
from sentence_transformers import SentenceTransformer
from src.embeddings import load_processed_records, build_document_text

def run_benchmark():
    records = load_processed_records()[:50]
    docs = [build_document_text(r) for r in records]
    
    print("Loading model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu", local_files_only=True)
    
    threads = os.cpu_count() or 4
    torch.set_num_threads(threads)
    
    for bs in [1, 4, 8, 16, 32]:
        t0 = time.time()
        with torch.inference_mode():
            _ = model.encode(docs, batch_size=bs, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
        time_opt = time.time() - t0
        est = (time_opt / 50) * 4858
        print(f"Batch Size {bs}: {time_opt:.2f}s (Est Total: {est/60:.2f}m)")

if __name__ == "__main__":
    run_benchmark()
