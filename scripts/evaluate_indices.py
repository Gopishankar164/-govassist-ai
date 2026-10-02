import time
from pathlib import Path
import json

from src.vector_store import SchemeVectorStore
from src.embeddings import embed_query, load_embedding_model
from src.config import DEFAULT_TOP_K

QUERIES = [
    "I am a student looking for scholarships",
    "I am a farmer looking for financial assistance",
    "I am a woman entrepreneur looking for government support",
    "I am a senior citizen seeking pension benefits",
    "I run an MSME and need a loan",
    "I am unemployed and looking for jobs or skill training",
    "I need financial help for house construction",
    "I need medical insurance and healthcare support",
    "What are the government schemes for Tamil Nadu residents?",
    "I belong to a low-income family and need financial aid"
]

def evaluate_index(store: SchemeVectorStore, model, name: str):
    print(f"\n{'='*50}\nEVALUATING {name} INDEX\n{'='*50}")
    print(f"Index Vectors: {store.index.ntotal}")
    print(f"Metadata Records: {len(store.metadata)}")
    
    total_latency = 0
    min_latency = float('inf')
    max_latency = 0
    
    for q in QUERIES:
        qvec = embed_query(q, model)
        
        t0 = time.time()
        results = store.search(qvec, top_k=DEFAULT_TOP_K)
        latency = (time.time() - t0) * 1000  # ms
        
        total_latency += latency
        min_latency = min(min_latency, latency)
        max_latency = max(max_latency, latency)
        
        print(f"\nQUERY: {q}")
        print(f"Latency: {latency:.2f} ms")
        for i, r in enumerate(results[:5], 1):
            url = r.get('official_url', r.get('application_url', 'N/A'))
            print(f"  {i}. {r['scheme_name']} (Score: {r['similarity_score']:.4f}) | URL: {url}")
            
    avg_latency = total_latency / len(QUERIES)
    print(f"\n{name} LATENCY STATS:")
    print(f"  Avg: {avg_latency:.2f} ms")
    print(f"  Min: {min_latency:.2f} ms")
    print(f"  Max: {max_latency:.2f} ms")

def main():
    print("Loading embedding model...")
    model = load_embedding_model()
    
    # 1. Evaluate OLD backup index
    try:
        old_store = SchemeVectorStore()
        old_store.index_path = Path("data/index/schemes_backup.faiss")
        old_store.metadata_path = Path("data/index/schemes_metadata_backup.jsonl")
        
        # Manually load old store
        import faiss
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
        
    # 2. Evaluate NEW index
    try:
        new_store = SchemeVectorStore.load()
        evaluate_index(new_store, model, "NEW")
    except Exception as e:
        print(f"Could not load NEW index: {e}")

if __name__ == "__main__":
    main()
