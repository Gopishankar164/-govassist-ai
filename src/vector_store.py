"""
Stage 4 — Real FAISS vector store.

Uses IndexFlatIP over L2-normalized embeddings, so inner product == cosine
similarity. Metadata is stored separately (JSONL) and mapped 1:1 to FAISS
vector positions by row order -- vector i always corresponds to metadata
record i. This module never fabricates similarity scores; every score
returned by `search()` comes directly from the FAISS index.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
import faiss

from src.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH, EMBEDDING_INFO_PATH, INDEX_DIR


class SchemeVectorStore:
    def __init__(self, dimension: Optional[int] = None):
        self.dimension = dimension
        self.index: Optional[faiss.Index] = None
        self.metadata: List[dict] = []

    # ---------------------------------------------------------------- build
    def build_index(self, embeddings: np.ndarray, metadata: List[dict], verbose: bool = True):
        """
        embeddings: np.ndarray [N, D], float32, L2-normalized (unit norm).
        metadata:   list of N dicts, one per scheme, same row order as embeddings.
        """
        if embeddings.shape[0] != len(metadata):
            raise ValueError(
                f"Embedding/metadata count mismatch: {embeddings.shape[0]} vectors "
                f"vs {len(metadata)} metadata records. Refusing to build a misaligned index."
            )

        embeddings = np.ascontiguousarray(embeddings.astype("float32"))
        self.dimension = embeddings.shape[1]
        self.metadata = metadata

        t0 = time.time()
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        elapsed = time.time() - t0

        if verbose:
            print("FAISS index type: IndexFlatIP (cosine via normalized inner product)")
            print("Index dimension:", self.dimension)
            print("Vectors indexed:", self.index.ntotal)
            print(f"Index construction time: {elapsed:.3f}s")

        return elapsed

    # -------------------------------------------------------------- persist
    def save(self, index_path: Path = FAISS_INDEX_PATH, metadata_path: Path = FAISS_METADATA_PATH):
        if self.index is None:
            raise RuntimeError("No index built yet -- call build_index() first.")
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        with open(metadata_path, "w", encoding="utf-8") as f:
            for rec in self.metadata:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, index_path: Path = FAISS_INDEX_PATH, metadata_path: Path = FAISS_METADATA_PATH):
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {index_path}. Build it first.")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found at {metadata_path}. Build it first.")

        index = faiss.read_index(str(index_path))
        metadata = []
        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    metadata.append(json.loads(line))

        if index.ntotal != len(metadata):
            raise RuntimeError(
                f"STOP: metadata count ({len(metadata)}) != FAISS vector count "
                f"({index.ntotal}). Index and metadata are misaligned -- do not use."
            )

        store = cls(dimension=index.d)
        store.index = index
        store.metadata = metadata
        return store

    # --------------------------------------------------------------- search
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
        """
        query_embedding: 1D np.ndarray [D], should already be L2-normalized.
        Returns a list of dicts: {rank, scheme_id, scheme_name, similarity_score, scheme}
        similarity_score is the REAL raw inner-product value from FAISS -- never altered.
        """
        if self.index is None:
            raise RuntimeError("No index loaded -- call build_index() or load() first.")
        if self.index.ntotal == 0:
            return []

        q = np.ascontiguousarray(query_embedding.astype("float32")).reshape(1, -1)
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, top_k)

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx == -1:
                continue
            record = self.metadata[idx]
            results.append({
                "rank": rank,
                "scheme_id": record.get("scheme_id"),
                "scheme_name": record.get("scheme_name"),
                "similarity_score": float(score),  # real FAISS inner-product score
                "scheme": record,
            })
        return results


# ---------------------------------------------------------------------------
# MECHANICS-ONLY SELF TEST (synthetic vectors)
#
# This does NOT validate semantic retrieval quality -- it only proves the
# FAISS build/save/reload/search wiring is correct. Real semantic
# validation requires the actual bge-small-en-v1.5 embeddings, which must
# be generated in an environment that can reach Hugging Face Hub (this
# sandbox cannot -- see project chat log).
# ---------------------------------------------------------------------------
def _mechanics_self_test(verbose: bool = True):
    import tempfile
    rng = np.random.default_rng(42)
    n, dim = 500, 384  # 384 = actual bge-small-en-v1.5 output dimension
    synthetic = rng.normal(size=(n, dim)).astype("float32")
    synthetic /= np.linalg.norm(synthetic, axis=1, keepdims=True)  # unit-normalize
    synthetic_metadata = [
        {"scheme_id": f"SYNTH_{i}", "scheme_name": f"Synthetic Scheme {i}", "source_row": i}
        for i in range(n)
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_index_path = Path(tmp) / "test.faiss"
        tmp_meta_path = Path(tmp) / "test_metadata.jsonl"

        store = SchemeVectorStore()
        build_time = store.build_index(synthetic, synthetic_metadata, verbose=verbose)
        store.save(index_path=tmp_index_path, metadata_path=tmp_meta_path)

        query = synthetic[7].copy()  # a known vector -> should retrieve itself as rank 1, score ~1.0
        t0 = time.time()
        results_before = store.search(query, top_k=5)
        latency_before = time.time() - t0

        # destroy in-memory index, force reload from disk (isolated tmp path, not production data)
        del store
        reloaded = SchemeVectorStore.load(index_path=tmp_index_path, metadata_path=tmp_meta_path)
        results_after = reloaded.search(query, top_k=5)

    consistent = (
        [r["scheme_id"] for r in results_before] == [r["scheme_id"] for r in results_after]
        and all(
            abs(a["similarity_score"] - b["similarity_score"]) < 1e-5
            for a, b in zip(results_before, results_after)
        )
    )

    if verbose:
        print("\n=== FAISS MECHANICS SELF-TEST (synthetic vectors, NOT semantic data) ===")
        print("Index vectors:", reloaded.index.ntotal)
        print("Metadata records:", len(reloaded.metadata))
        print("Dimension:", reloaded.index.d)
        print("Reload successful:", reloaded.index.ntotal == n and len(reloaded.metadata) == n)
        print("Search consistency (pre vs post reload):", consistent)
        print(f"Index construction time: {build_time:.4f}s")
        print(f"Search latency: {latency_before*1000:.3f}ms")
        print("Top-1 result for self-query (expect SYNTH_7, score ~1.0):",
              results_after[0]["scheme_id"], results_after[0]["similarity_score"])

    return {
        "index_vectors": reloaded.index.ntotal,
        "metadata_records": len(reloaded.metadata),
        "dimension": reloaded.index.d,
        "reload_successful": reloaded.index.ntotal == n and len(reloaded.metadata) == n,
        "search_consistent": consistent,
        "build_time_seconds": build_time,
        "search_latency_seconds": latency_before,
    }


if __name__ == "__main__":
    _mechanics_self_test()
