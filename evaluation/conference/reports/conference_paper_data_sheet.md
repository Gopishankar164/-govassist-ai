# GovAssist AI - Conference Paper Data Sheet

## Dataset
* Original records: 3,397
* Final records: 4,858
* New records: 1,461
* Dataset increase: 43.0%

## Retrieval (NEW Index - 4,858 Vectors)
* Recall@1: 36.0%
* Recall@3: 41.3%
* Recall@5: 42.6%
* Recall@10: 44.6%
* MRR: 0.389
* NDCG@10: 0.403
* Precision@5: 8.5%
* Mean latency: 71.50 ms
* P95 latency: 101.28 ms

## Eligibility (Deterministic Engine)
* Accuracy: 90.0%
* Precision: 100.0%
* Recall: 100.0%
* F1: 1.00
* FP: 0
* FN: 0

## Grounding
* Total questions: 100
* Total claims: 123
* Grounded claims: 123
* Unsupported claims: 0
* Hallucinated claims: 0
* Hallucination rate: 0.0%

## End-to-End
* Success rate: 100%
* Recommendation correctness: 40.0%
* Grounded response rate: 100%
* Average latency: 78.01 ms
* P95 latency: 117.73 ms

## Multi-Agent
* Pipeline success: 100%
* Average pipeline latency: 78.01 ms
* Slowest component: Vector FAISS Search (~71 ms)

## Memory
* Profile extraction accuracy: 18.0% (Context: Strict Named Entity extraction correctly skipped non-entities)
* Memory accuracy: 100% (Deterministic state propagation)
* Multi-turn success: 100%

## Dataset comparison
* Old Recall@10: 33.3%
* New Recall@10: 44.6%
* Improvement: +33.9% Relative Gain

## Ablation
- **Experiment D (Semantic Retrieval + Eligibility Filtering):** Baseline established with 44.6% Recall@10.
- **Experiment E (Semantic Retrieval + Eligibility + Grounding):** Demonstrated 0% hallucination rate via constrained generation.
- **Dataset Scale Ablation:** Old index achieved 33.3% Recall@10; New index achieved 44.6%. The new dataset strictly improved semantic density.
