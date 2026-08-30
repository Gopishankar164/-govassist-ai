# Final Model Execution Audit

| Metric | Value | Test Cases | Source File | Status |
| :--- | :--- | :--- | :--- | :--- |
| Retrieval Latency (New) | 1.44 ms | 5 queries | `raw_retrieval.txt` | REAL |
| Eligibility Accuracy | 1.00 | 24 combinations | `eligibility_metrics.json` | REAL |
| Grounding Rate | 100% | 28 claims | `grounding_metrics.json` | REAL |
| Total Inference Latency | 120.87 ms | 1 pipeline run | `performance_metrics.json` | REAL |
| Multi-turn functionality | Confirmed | 5 turns | `02_multiturn_conversation.json` | REAL |
| Out of Domain handling | Confirmed | 2 turns | `07_out_of_domain.json` | REAL |

*Note: Recall@1, Recall@5, MRR, NDCG are marked as NOT VERIFIED since the `evaluate_retrieval.py` script provided didn't actually compute them due to empty ground-truth labels in its test set. The latencies were successfully computed and reported.*
