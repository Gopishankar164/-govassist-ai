import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pytest
from src.vector_store import SchemeVectorStore


def _synthetic(n=200, dim=384, seed=1):
    rng = np.random.default_rng(seed)
    vecs = rng.normal(size=(n, dim)).astype("float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    meta = [{"scheme_id": f"S{i}", "scheme_name": f"Scheme {i}"} for i in range(n)]
    return vecs, meta


def test_embedding_metadata_alignment_enforced():
    vecs, meta = _synthetic(n=10)
    store = SchemeVectorStore()
    with pytest.raises(ValueError):
        store.build_index(vecs, meta[:5])  # deliberately mismatched


def test_index_size_matches_input():
    vecs, meta = _synthetic(n=150)
    store = SchemeVectorStore()
    store.build_index(vecs, meta, verbose=False)
    assert store.index.ntotal == 150
    assert store.index.d == 384


def test_search_returns_top_k():
    vecs, meta = _synthetic(n=50)
    store = SchemeVectorStore()
    store.build_index(vecs, meta, verbose=False)
    results = store.search(vecs[0], top_k=5)
    assert len(results) == 5


def test_search_scores_are_real_numeric_values():
    vecs, meta = _synthetic(n=50)
    store = SchemeVectorStore()
    store.build_index(vecs, meta, verbose=False)
    results = store.search(vecs[0], top_k=3)
    for r in results:
        assert isinstance(r["similarity_score"], float)
    # self-search must yield similarity ~1.0 (exact match, normalized vectors)
    assert abs(results[0]["similarity_score"] - 1.0) < 1e-4


def test_index_reload_consistency():
    vecs, meta = _synthetic(n=80)
    with tempfile.TemporaryDirectory() as tmp:
        idx_path = Path(tmp) / "i.faiss"
        meta_path = Path(tmp) / "m.jsonl"
        store = SchemeVectorStore()
        store.build_index(vecs, meta, verbose=False)
        store.save(idx_path, meta_path)

        before = store.search(vecs[3], top_k=5)
        del store
        reloaded = SchemeVectorStore.load(idx_path, meta_path)
        after = reloaded.search(vecs[3], top_k=5)

        assert [r["scheme_id"] for r in before] == [r["scheme_id"] for r in after]


def test_missing_index_raises():
    with pytest.raises(FileNotFoundError):
        SchemeVectorStore.load(Path("/nonexistent/x.faiss"), Path("/nonexistent/x.jsonl"))


def test_empty_query_handling():
    vecs, meta = _synthetic(n=20)
    store = SchemeVectorStore()
    store.build_index(vecs, meta, verbose=False)
    # a zero vector is a valid (if degenerate) query -- must not crash
    zero_query = np.zeros(384, dtype="float32")
    results = store.search(zero_query, top_k=5)
    assert len(results) == 5
