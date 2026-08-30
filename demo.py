"""Run the four required end-to-end GovAssist RAG demonstrations."""
import sys

from src.pipeline import GovAssistPipeline

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUERIES = [
    "I am a female engineering student from Tamil Nadu looking for scholarships.",
    "I am a farmer looking for government financial assistance.",
    "I am looking for a government housing scheme.",
    "I am a small business owner looking for a government loan.",
]

if __name__ == "__main__":
    pipeline = GovAssistPipeline()
    for query in QUERIES:
        result = pipeline.recommend(query)
        print("\n" + "=" * 72 + "\nUSER QUERY\n" + "=" * 72 + "\n" + query)
        print("\nPROFILE\n", result["profile"])
        print("\nREWRITTEN QUERY\n", result["rewritten_query"])
        print("\nTOP 10 RETRIEVED SCHEMES / REAL SIMILARITY SCORES")
        for item in result["retrieved_schemes"]:
            print(f"{item['rank']:2d}. {item['scheme_name']} | {item['similarity_score']:.4f} | {item['eligibility_status']}")
        print("\nFINAL TOP 3")
        for item in result["recommendations"]:
            print(f"- {item['scheme_name']} | final={item['final_rank_score']:.4f}")
        print("\nEVIDENCE / FINAL GROUNDED ANSWER\n" + result["answer"])
        print(f"\nRetrieval latency: {result['retrieval_latency_ms']:.2f} ms")
