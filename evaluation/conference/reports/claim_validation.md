# Claim Validation

| Claim | Evidence | Source | Verified? |
|---|---|---|---|
| Dataset expanded to 4,858 schemes | Final row count: 4858 | dataset_audit.json | VERIFIED |
| 1,461 additional schemes | Difference between 4858 and 3397 | dataset_audit.json | VERIFIED |
| Recall@10 improvement | Old 0.333 -> New 0.447 | retrieval_metrics.json | VERIFIED |
| Eligibility precision | 100.0% | eligibility_metrics.json | VERIFIED |
| Grounding rate | 100.0% | grounding_metrics.json | VERIFIED |
| Hallucination rate | 0.0% on benchmark | grounding_metrics.json | VERIFIED |
| End-to-end success | 100.0% | e2e_metrics.json | VERIFIED |
| P95 Latency | 192.11 ms | e2e_metrics.json | VERIFIED |
| Memory extraction | 18.0% strict | e2e_metrics.json | VERIFIED |
| Memory persistence | Cannot independently isolate | N/A | PARTIALLY VERIFIED |
