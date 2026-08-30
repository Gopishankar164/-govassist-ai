# Reproducibility Manifest

## Metric: Dataset Audit
- **Dataset**: Schemes.csv, Merged_Schemes.csv
- **Script**: dataset_audit.py
- **Command**: `python evaluation/conference/dataset_audit.py`
- **Output**: metrics/dataset_audit.json

## Metric: Retrieval
- **Dataset**: retrieval_benchmark.json
- **Script**: run_retrieval_eval.py
- **Command**: `python evaluation/conference/run_retrieval_eval.py`
- **Output**: metrics/retrieval_metrics.json

## Metric: Eligibility
- **Dataset**: eligibility_benchmark.json
- **Script**: run_eligibility_eval.py
- **Command**: `python evaluation/conference/run_eligibility_eval.py`
- **Output**: metrics/eligibility_metrics.json

## Metric: Grounding
- **Dataset**: grounding_benchmark.json
- **Script**: run_grounding_eval.py
- **Command**: `python evaluation/conference/run_grounding_eval.py`
- **Output**: metrics/grounding_metrics.json

## Metric: End-to-End
- **Dataset**: None
- **Script**: run_e2e_eval.py
- **Command**: `python evaluation/conference/run_e2e_eval.py`
- **Output**: metrics/e2e_metrics.json

