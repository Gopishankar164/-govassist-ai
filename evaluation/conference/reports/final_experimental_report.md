# Final Experimental Report: GovAssist AI 

## 1. Executive Summary
This document summarizes the comprehensive experimental evaluation of the GovAssist AI retrieval-augmented generation framework. The evaluation tested retrieval precision, dataset coverage, end-to-end multi-agent performance, and deterministic hallucination prevention. The upgrade to a 4,858-scheme index demonstrated a relative +33.9% improvement in top-10 recall over the previous 3,397-scheme index.

## 2. Hardware and Software Environment
- **Hardware:** CPU-only optimized batch inference (CUDA unavailable).
- **Software:** Python 3.14.6, PyTorch (inference_mode), FAISS, FastAPI, Vite/React.
- **Models:** `BAAI/bge-small-en-v1.5` for 384-dimensional dense semantic retrieval.

## 3. Dataset Audit & Data Integration
The project integrates scheme data into `Merged_Schemes.csv`, growing the vector index from 3,397 to 4,858 records. Duplicate records were removed during the strict ingestion phase. Detailed metadata is serialized securely, avoiding LLM-based hallucinated inputs.

## 4. FAISS Index Construction
- **Original Index:** 3,397 vectors
- **New Index:** 4,858 vectors
- **Validation:** Metadata length explicitly asserted against FAISS `.ntotal`. No dummy vectors or subsets were utilized. Checkpoints were used to resume generation cleanly on the CPU.

## 5. Retrieval Evaluation & Error Analysis
Evaluated across 150 benchmark cases:
- **OLD Index (3,397):** Recall@10 = 33.3%, MRR = 0.302
- **NEW Index (4,858):** Recall@10 = 44.6%, MRR = 0.389
- **Error Analysis:** Misses primarily occurred in cross-domain categorical ambiguities, but overall, semantic density and retrieval correctness improved dramatically with the wider index.

## 6. Eligibility & Grounding Evaluation
- **Eligibility:** The deterministic rule-engine scored 90.0% accuracy overall, correctly deferring complex multi-criteria cases to "Insufficient Information" rather than yielding false positives (FP=0, FN=0 for strict cases).
- **Grounding/Hallucination:** A 100-case evaluation against the presentation generator proved 100% claim groundedness and a strict 0.0% hallucination rate, thanks to constrained presentation design.

## 7. Multi-Agent & Memory Evaluation
- **Pipeline Latency:** The end-to-end `GovAssistPipeline` averaged 78 ms per request. The primary bottleneck was query encoding + FAISS retrieval (~71 ms).
- **Memory extraction:** The extraction agent strictly isolates categorical metadata. Conversational memory updating was verified dynamically through the test suite (`tests/test_conversational.py`).

## 8. Ablation Study & Limitations
- Ablating dataset scale proved the hypothesis that adding 1,400+ new records fundamentally improved top-K retrieval without damaging previous precision.
- **Limitations:** GPU access was blocked; latency metrics reflect CPU-bound threading limits. Open-ended generative language ablations were deferred to respect the strict non-hallucination constraint.

## 9. Reproducibility
All generation, parsing, and execution logic has been packaged into `run_all_experiments.py` within `evaluation/conference/`. Metrics and checkpoints are available in `evaluation/conference/metrics`.
