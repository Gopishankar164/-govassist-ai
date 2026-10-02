import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.config import settings, logger
from backend.app.database import db

class FAISSVectorStore:
    """
    Production-grade Vector Store using:
    - BAAI/bge-small-en-v1.5 (SentenceTransformers)
    - FAISS IndexFlatIP (Cosine Similarity Search)
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.dimension = 384  # bge-small-en-v1.5 vector dimension
        self.encoder = None
        self.faiss_index = None
        self.documents: List[Dict[str, Any]] = []
        self.vectors: List[np.ndarray] = []

        self._init_encoder()
        self._init_faiss()
        if not self.load_persisted_index():
            self.reload_index()

    def load_persisted_index(self) -> bool:
        index_file = settings.FAISS_INDEX_PATH + ".bin"
        meta_file = settings.FAISS_INDEX_PATH + "_meta.json"
        
        if os.path.exists(index_file) and os.path.exists(meta_file):
            try:
                import faiss
                self.faiss_index = faiss.read_index(index_file)
                with open(meta_file, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded persisted FAISS index from {index_file} with {len(self.documents)} documents.")
                return True
            except Exception as e:
                logger.warning(f"Failed to load persisted index: {e}")
        return False

    def save_persisted_index(self):
        index_file = settings.FAISS_INDEX_PATH + ".bin"
        meta_file = settings.FAISS_INDEX_PATH + "_meta.json"
        
        try:
            if self.faiss_index is not None:
                import faiss
                faiss.write_index(self.faiss_index, index_file)
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(self.documents, f, indent=2)
                logger.info(f"Persisted FAISS index to {index_file}")
        except Exception as e:
            logger.error(f"Failed to persist index: {e}")

    def _init_encoder(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer embedding model: '{self.model_name}'...")
            self.encoder = SentenceTransformer(self.model_name)
            self.dimension = self.encoder.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model successfully (dimension: {self.dimension}).")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer '{self.model_name}': {e}. Using deterministic semantic vectorizer fallback.")
            self.encoder = None

    def _init_faiss(self):
        try:
            import faiss
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            logger.info("Initialized FAISS IndexFlatIP for Cosine Similarity search.")
        except Exception as e:
            logger.warning(f"FAISS module unavailable ({e}). Utilizing NumPy Cosine Similarity matrix search.")
            self.faiss_index = None

    def _encode_text(self, text: str) -> np.ndarray:
        if self.encoder is not None:
            vec = self.encoder.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vec.astype(np.float32)
        else:
            # Deterministic pseudo-embedding generator (dimension 384) for fallback environment
            np.random.seed(abs(hash(text)) % (2**32))
            vec = np.random.randn(self.dimension).astype(np.float32)
            # Add term frequency weights for common scheme tokens to maintain keyword alignment
            tokens = text.lower().replace(".", " ").replace(",", " ").split()
            for i, t in enumerate(tokens[:30]):
                idx = abs(hash(t)) % self.dimension
                vec[idx] += 1.5
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec

    def reload_index(self):
        """
        Reloads all schemes from database/file, chunks them, generates BGE embeddings, and populates FAISS index.
        """
        schemes = db.find_all("schemes")
        if not schemes and os.path.exists(settings.SAMPLE_SCHEMES_PATH):
            with open(settings.SAMPLE_SCHEMES_PATH, "r", encoding="utf-8") as f:
                schemes = json.load(f)

        self.documents = []
        raw_chunks = []

        for s in schemes:
            name = s.get("name") or s.get("scheme_name") or "Government Scheme"
            category = s.get("category", "")
            target = s.get("target_audience", "")
            desc = s.get("description", "")
            benefits = s.get("benefits", "")
            docs = ", ".join(s.get("documents_required") or s.get("required_documents") or [])
            elig = s.get("eligibility", {})
            if isinstance(elig, dict):
                min_age = elig.get("min_age", 0)
                max_age = elig.get("max_age", 100)
                max_income = elig.get("max_income", "N/A")
                occs = ", ".join(elig.get("occupations", ["All"]))
            else:
                min_age = 0
                max_age = 100
                max_income = "N/A"
                occs = str(elig)

            # Structural metadata chunking
            chunk_text = (
                f"Government Scheme: {name}. Category: {category}. Target Audience: {target}. "
                f"Description: {desc}. Benefits: {benefits}. Required Documents: {docs}. "
                f"Eligibility Bracket: Min Age {min_age}, Max Age {max_age}, "
                f"Max Family Income ₹{max_income}, Occupations: {occs}."
            )

            doc_entry = {
                "id": s.get("id") or s.get("scheme_id"),
                "scheme": s,
                "text": chunk_text
            }
            self.documents.append(doc_entry)
            raw_chunks.append(chunk_text)

        if not raw_chunks:
            logger.warning("No scheme documents found to index.")
            return

        # Batch encode chunk embeddings
        embeddings_list = []
        for text in raw_chunks:
            embeddings_list.append(self._encode_text(text))

        self.vectors = embeddings_list

        if self.faiss_index is not None and embeddings_list:
            import faiss
            matrix = np.array(embeddings_list, dtype=np.float32)
            # Re-initialize index flat IP
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            self.faiss_index.add(matrix)
            logger.info(f"FAISS index reloaded with {self.faiss_index.ntotal} dense document vectors.")
            self.save_persisted_index()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes Cosine Similarity vector search over top_k documents.
        """
        if not self.documents:
            self.reload_index()
            if not self.documents:
                return []

        q_vec = self._encode_text(query)

        if self.faiss_index is not None and self.faiss_index.ntotal > 0:
            import faiss
            query_matrix = np.array([q_vec], dtype=np.float32)
            k = min(top_k, self.faiss_index.ntotal)
            scores, indices = self.faiss_index.search(query_matrix, k)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.documents):
                    continue
                doc = self.documents[idx]
                sim = float(score)
                # Bound similarity between 0 and 1
                sim_bounded = round(min(0.99, max(0.15, sim)), 4)
                results.append({
                    "scheme": doc["scheme"],
                    "score": sim_bounded,
                    "matched_chunk": doc["text"]
                })
            return results
        else:
            # Fallback NumPy Inner Product / Cosine Similarity calculation
            results = []
            for doc, v in zip(self.documents, self.vectors):
                score = float(np.dot(q_vec, v))
                sim_bounded = round(min(0.99, max(0.15, score)), 4)
                results.append({
                    "scheme": doc["scheme"],
                    "score": sim_bounded,
                    "matched_chunk": doc["text"]
                })
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]

# Maintain global reference
vector_store = FAISSVectorStore()
