"""
Stage 3 — Document construction + real dense embeddings.

Builds one semantic document per scheme (name, description, benefits,
eligibility, category, state, application, documents -- only fields that
actually exist/are non-empty are included), then embeds every document with
BAAI/bge-small-en-v1.5 via sentence-transformers. Embeddings are L2-normalized
so inner product == cosine similarity for the FAISS IndexFlatIP used later.
"""
import json
import time
from pathlib import Path
from typing import List, Dict

from sentence_transformers import SentenceTransformer

from src.config import PROCESSED_JSONL_PATH, EMBEDDING_MODEL_NAME, EMBEDDING_INFO_PATH


def load_processed_records(path: Path = PROCESSED_JSONL_PATH) -> List[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run ingestion (Stage 2) first."
        )
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_document_text(record: dict) -> str:
    """
    Construct a meaningful semantic document for a scheme.
    Only fields with actual non-empty content are included -- we never
    inject a "field: N/A" placeholder that would pollute the embedding.
    """
    parts = []

    def add(label: str, value):
        if value is None:
            return
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value if v)
        value = str(value).strip()
        if value:
            parts.append(f"{label}:\n{value}")

    add("SCHEME NAME", record.get("scheme_name"))
    add("DESCRIPTION", record.get("description"))
    add("BENEFITS", record.get("benefits"))
    add("ELIGIBILITY", record.get("eligibility_text"))
    add("CATEGORY", record.get("category"))
    add("TAGS", record.get("tags"))
    add("LEVEL", record.get("level"))
    if record.get("state") and record.get("state") != "unknown":
        add("STATE", record.get("state"))
    add("APPLICATION PROCESS", record.get("application_process"))
    add("REQUIRED DOCUMENTS", record.get("documents"))

    return "\n\n".join(parts)


import torch
import os
import pickle
import numpy as np

def load_embedding_model(model_name: str = EMBEDDING_MODEL_NAME) -> SentenceTransformer:
    # Automatically detect whether PyTorch can use CUDA/GPU.
    # If CUDA is available, use GPU. Otherwise use CPU.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading embedding model {model_name} on device: {device}")
    return SentenceTransformer(model_name, device=device, local_files_only=True)

def embed_records(records: List[dict], model: SentenceTransformer = None,
                   batch_size: int = 32, verbose: bool = True) -> Dict:
    """
    Returns a dict:
        {
            "embeddings": np.ndarray [N, D] float32, L2-normalized,
            "documents": List[str],
            "model_name": str,
            "dimension": int,
            "generation_time_seconds": float,
        }
    """
    if model is None:
        model = load_embedding_model()

    documents = [build_document_text(r) for r in records]
    
    # Resumable build logic
    cache_dir = PROCESSED_JSONL_PATH.parent / "embeddings_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "embeddings_checkpoint.pkl"
    
    embeddings_list = []
    start_idx = 0
    total = len(documents)
    
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                checkpoint = pickle.load(f)
                embeddings_list = checkpoint.get("embeddings", [])
                start_idx = len(embeddings_list)
                if verbose:
                    print(f"Resumed from checkpoint: {start_idx} embeddings already computed.")
        except Exception as e:
            print(f"Failed to load checkpoint: {e}")
            embeddings_list = []
            start_idx = 0
    
    t0 = time.time()
    
    threads = os.cpu_count() or 4
    torch.set_num_threads(threads)
    
    if start_idx < total:
        for i in range(start_idx, total, batch_size):
            batch_docs = documents[i:i+batch_size]
            
            # Progress indicator setup
            start_batch_time = time.time()
            
            with torch.inference_mode():
                batch_embs = model.encode(
                    batch_docs,
                    batch_size=len(batch_docs),
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
            embeddings_list.extend(batch_embs)
            
            # Save checkpoint
            with open(cache_file, "wb") as f:
                pickle.dump({"embeddings": embeddings_list}, f)
                
            elapsed_batch = time.time() - start_batch_time
            processed = len(embeddings_list)
            percentage = (processed / total) * 100
            elapsed_total = time.time() - t0
            
            # Estimate remaining time
            rate = processed - start_idx
            if rate > 0:
                time_per_item = elapsed_total / rate
                remaining_items = total - processed
                est_remaining_sec = time_per_item * remaining_items
                rem_m, rem_s = divmod(est_remaining_sec, 60)
                rem_h, rem_m = divmod(rem_m, 60)
                rem_str = f"{int(rem_h):02d}:{int(rem_m):02d}:{int(rem_s):02d}"
            else:
                rem_str = "Unknown"
                
            if verbose:
                print(f"Processed: {processed}/{total} ({percentage:.2f}%) | "
                      f"Elapsed: {elapsed_total:.2f}s | "
                      f"Est. Remaining: {rem_str}")
    
    elapsed = time.time() - t0
    embeddings = np.array(embeddings_list)
    dim = embeddings.shape[1]

    if verbose:
        print("Embedding model:", EMBEDDING_MODEL_NAME)
        print("Embedding dimension:", dim)
        print("Documents embedded:", len(documents))
        print(f"Embedding time: {elapsed:.2f}s")

    assert embeddings.shape[0] == len(records), (
        f"MISMATCH: {embeddings.shape[0]} embeddings != {len(records)} canonical records"
    )

    EMBEDDING_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EMBEDDING_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "model_name": EMBEDDING_MODEL_NAME,
            "dimension": int(dim),
            "num_documents": len(documents),
            "generation_time_seconds": elapsed,
            "normalized": True,
        }, f, indent=2)
        
    # Clear cache upon full completion
    if cache_file.exists():
        os.remove(cache_file)

    return {
        "embeddings": embeddings,
        "documents": documents,
        "model_name": EMBEDDING_MODEL_NAME,
        "dimension": dim,
        "generation_time_seconds": elapsed,
    }


def embed_query(query: str, model: SentenceTransformer):
    return model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]


if __name__ == "__main__":
    records = load_processed_records()
    print(f"Loaded {len(records)} canonical records.")
    model = load_embedding_model()
    result = embed_records(records, model)
    print("\nNumber of embeddings == number of canonical records:",
          result["embeddings"].shape[0] == len(records))
