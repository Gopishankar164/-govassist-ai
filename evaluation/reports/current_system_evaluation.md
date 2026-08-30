# GovAssist AI Current System Evaluation

**Dataset:** 3397
**Embedding model:** BAAI/bge-small-en-v1.5
**Vector store:** FAISS IndexFlatIP
**Dimension:** 384

## Retrieval metrics
* Precision@1: 0.5000
* Precision@3: 0.2222
* Precision@5: 0.1533
* Recall@3: 0.6667
* Recall@5: 0.7667
* Recall@10: 0.9333
* MRR: 0.6223
* Hit Rate@5: 0.7667

## Performance
* startup latency: 16550.31 ms
* first-query latency: 101.90 ms
* mean retrieval latency: 49.13 ms
* P95 latency: 55.54 ms

## Eligibility
* number tested: 5
* correct: 4
* incorrect: 1
* insufficient-information cases: 3

## Grounding
* number tested: 4
* supported claims: 2
* unsupported claims: 2
* grounding rate: 50.00%

## Response quality
* number tested: 9
* passed: 9
* failed: 0
