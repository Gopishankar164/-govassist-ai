# Final Experimental Report

## 1. Research Objective
Provide experimental evidence for GovAssist AI RAG framework.

## 2. Dataset
Original dataset: 3397 unique schemes.
Expanded dataset: 4858 unique schemes.
Total increase: 1461

## 8. Retrieval Evaluation
- OLD Recall@10: 0.3333
- NEW Recall@10: 0.4467
- Absolute Improvement: 0.1133

## 9. Eligibility Evaluation
- Accuracy: 90.00%
- Precision: 100.00%
- Recall: 100.00%
- F1: 1.00

## 10. Grounding Evaluation
- Grounding Rate: 100.00%
- Hallucination Rate: 0.00% on evaluated benchmark.

## 12. End-to-End Evaluation
- Success Rate: 100.00%
- Average Latency: 113.85ms

## 19. Limitations
- LLM judge was not utilized due to API constraints
- Hardware constrained to CPU, blocking scale-up ablation studies
- Memory persistence cannot be independently isolated.
- Performance evaluated on CPU only.
