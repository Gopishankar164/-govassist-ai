import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.eligibility import analyze_eligibility

def main():
    root = Path(__file__).resolve().parent.parent.parent
    bench_file = root / "evaluation" / "conference" / "datasets" / "eligibility_benchmark.json"
    
    with open(bench_file, 'r', encoding='utf-8') as f:
        benchmark = json.load(f)
        
    correct = 0
    total = len(benchmark)
    
    # We will treat POTENTIALLY_ELIGIBLE as Positive, NOT_ELIGIBLE as Negative, INSUFFICIENT as Neutral.
    # To compute TP/TN we need binary logic. Let's do a strict multi-class accuracy for now,
    # and binary metrics for Eligible vs Ineligible.
    
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    
    confusion = {
        "expected_POTENTIALLY_ELIGIBLE": {"actual_POTENTIALLY_ELIGIBLE": 0, "actual_NOT_ELIGIBLE": 0, "actual_INSUFFICIENT_INFORMATION": 0},
        "expected_NOT_ELIGIBLE": {"actual_POTENTIALLY_ELIGIBLE": 0, "actual_NOT_ELIGIBLE": 0, "actual_INSUFFICIENT_INFORMATION": 0},
        "expected_INSUFFICIENT_INFORMATION": {"actual_POTENTIALLY_ELIGIBLE": 0, "actual_NOT_ELIGIBLE": 0, "actual_INSUFFICIENT_INFORMATION": 0},
    }
    
    for item in benchmark:
        scheme = item['scheme']
        profile = item['profile']
        expected = item['expected_status']
        
        result = analyze_eligibility(scheme, profile)
        actual = result['eligibility_status']
        
        # Depending on the extracted logic, there might be slight discrepancies if the free text has "disability"
        # We will track exactly what happened
        expected_key = f"expected_{expected}"
        actual_key = f"actual_{actual}"
        
        if expected_key in confusion and actual_key in confusion[expected_key]:
            confusion[expected_key][actual_key] += 1
            
        if actual == expected:
            correct += 1
            
        # Binary stats (ignoring Insufficient for strict FP/FN)
        if expected == "POTENTIALLY_ELIGIBLE" and actual == "POTENTIALLY_ELIGIBLE": tp += 1
        if expected == "POTENTIALLY_ELIGIBLE" and actual == "NOT_ELIGIBLE": fn += 1
        if expected == "NOT_ELIGIBLE" and actual == "NOT_ELIGIBLE": tn += 1
        if expected == "NOT_ELIGIBLE" and actual == "POTENTIALLY_ELIGIBLE": fp += 1
            
    accuracy = correct / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "confusion_matrix": confusion,
        "total": total
    }
    
    out_dir = root / "evaluation" / "conference" / "metrics"
    with open(out_dir / "eligibility_metrics.json", "w", encoding='utf-8') as f:
        json.dump(metrics, f, indent=4)
        
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
