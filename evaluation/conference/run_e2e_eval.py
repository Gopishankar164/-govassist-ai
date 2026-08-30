import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.pipeline import GovAssistPipeline

def main():
    root = Path(__file__).resolve().parent.parent.parent
    
    # We will use the first 50 cases from the retrieval benchmark for End-to-End
    bench_file = root / "evaluation" / "conference" / "datasets" / "retrieval_benchmark.json"
    
    with open(bench_file, 'r', encoding='utf-8') as f:
        benchmark = json.load(f)[:50]
        
    print("Loading End-to-End Pipeline...")
    pipeline = GovAssistPipeline()
    
    metrics = {
        "total_cases": len(benchmark),
        "success_cases": 0,
        "correct_recommendation_cases": 0,
        "latencies": [],
        "profile_extraction_success": 0
    }
    
    for item in benchmark:
        query = item['query']
        expected_ids = item['expected_scheme_ids']
        
        t0 = time.time()
        try:
            res = pipeline.recommend(query)
            latency = (time.time() - t0) * 1000
            metrics['latencies'].append(latency)
            metrics['success_cases'] += 1
            
            # Check if expected scheme is in the final recommendations (top 5 by default)
            retrieved_ids = [r['scheme_id'] for r in res['recommendations']]
            if any(eid in retrieved_ids for eid in expected_ids):
                metrics['correct_recommendation_cases'] += 1
                
            # Basic profile extraction check: if the query was category_state, it should extract state
            # We don't have strict ground truth for extraction here, so we just check if it extracted *something* 
            # if the query had entities.
            if res['profile']:
                metrics['profile_extraction_success'] += 1
                
        except Exception as e:
            print(f"Error on query '{query}': {e}")
            
    import numpy as np
    
    final_metrics = {
        "success_rate": metrics['success_cases'] / metrics['total_cases'],
        "correct_recommendation_rate": metrics['correct_recommendation_cases'] / metrics['total_cases'],
        "extraction_rate": metrics['profile_extraction_success'] / metrics['total_cases'],
        "mean_latency": np.mean(metrics['latencies']) if metrics['latencies'] else 0,
        "p95_latency": np.percentile(metrics['latencies'], 95) if metrics['latencies'] else 0
    }
    
    out_dir = root / "evaluation" / "conference" / "metrics"
    with open(out_dir / "e2e_metrics.json", "w", encoding='utf-8') as f:
        json.dump(final_metrics, f, indent=4)
        
    print(json.dumps(final_metrics, indent=2))

if __name__ == "__main__":
    main()
