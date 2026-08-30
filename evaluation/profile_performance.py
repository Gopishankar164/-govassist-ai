import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def run_tests():
    start_time = time.perf_counter()
    from src.pipeline import GovAssistPipeline
    pipeline = GovAssistPipeline()
    startup_latency = (time.perf_counter() - start_time) * 1000
    
    start_time = time.perf_counter()
    res1 = pipeline.recommend("scholarship for students")
    first_query_latency = (time.perf_counter() - start_time) * 1000
    
    subsequent_latencies = []
    for _ in range(5):
        start_time = time.perf_counter()
        pipeline.recommend("farmer loans")
        subsequent_latencies.append((time.perf_counter() - start_time) * 1000)
        
    mean_latency = sum(subsequent_latencies) / len(subsequent_latencies)
    
    report = {
        "startup_latency_ms": startup_latency,
        "first_query_latency_ms": first_query_latency,
        "mean_subsequent_latency_ms": mean_latency
    }
    
    out_path = Path(__file__).parent / "results" / "performance_evaluation.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    print(f"Startup latency: {startup_latency:.2f}ms")
    print(f"First query latency: {first_query_latency:.2f}ms")
    print(f"Mean subsequent latency: {mean_latency:.2f}ms")

if __name__ == "__main__":
    run_tests()
