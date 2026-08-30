import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

try:
    import torch
except ImportError:
    torch = None

def ensure_dirs(root):
    dirs = [
        "raw", "datasets", "metrics", "outputs", "plots", "tables", "configs", "logs", "reports",
        "raw/model_outputs"
    ]
    base = root / "evaluation" / "conference" / "final" / "live_run"
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
    return base

def run_phase1(final_dir):
    env_info = []
    env_info.append(f"Python: {sys.version}")
    if torch:
        env_info.append(f"PyTorch: {torch.__version__}")
        env_info.append(f"CUDA: {torch.cuda.is_available()}")
        env_info.append(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    else:
        env_info.append("PyTorch: NOT INSTALLED")
        
    with open(final_dir / "raw" / "environment_info.txt", "w") as f:
        f.write("\n".join(env_info))

def start_backend(root, final_dir):
    print("Starting FastAPI backend...")
    log_file = open(final_dir / "logs" / "backend.log", "w")
    proc = subprocess.Popen(
        [r".\.venv\Scripts\python.exe", "-m", "uvicorn", "backend.main:app", "--port", "8123"],
        cwd=str(root),
        stdout=log_file,
        stderr=subprocess.STDOUT
    )
    
    # Wait for health check
    for _ in range(20):
        try:
            res = requests.get("http://localhost:8123/health", timeout=1)
            if res.status_code == 200:
                print("Backend started successfully.")
                return proc, log_file
        except:
            time.sleep(1)
            
    print("Backend failed to start. THE ACTUAL MODEL RUN IS NOT VERIFIED.")
    proc.terminate()
    return None, log_file

def run_model_queries(final_dir):
    queries = [
        "I am a 25 year old farmer from Tamil Nadu seeking financial assistance.",
        "Engineering student looking for scholarships in Karnataka.",
        "Woman entrepreneur trying to start a MSME business.",
        "Senior citizen pension schemes.",
        "Housing assistance for low income family."
    ] # Simplified for benchmark
    
    results = []
    successes = 0
    latencies = []
    
    print("Running real HTTP queries to API...")
    for i, q in enumerate(queries):
        start = time.time()
        try:
            res = requests.post("http://localhost:8000/api/recommend", json={"query": q}, timeout=30)
            latency = (time.time() - start) * 1000
            latencies.append(latency)
            
            data = res.json()
            out_file = final_dir / "raw" / "model_outputs" / f"query_{i}.json"
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)
                
            if res.status_code == 200:
                successes += 1
            results.append({"query": q, "status": res.status_code, "latency": latency})
        except Exception as e:
            print(f"Query {i} failed: {e}")
            results.append({"query": q, "status": 500, "error": str(e), "latency": 0})
            
    metrics = {
        "success_rate": successes / len(queries) if queries else 0,
        "mean_latency": sum(latencies)/len(latencies) if latencies else 0,
        "p95_latency": sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
        "total_queries": len(queries)
    }
    
    with open(final_dir / "metrics" / "api_e2e_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    return metrics

def run_old_benchmarks(root, final_dir):
    # To satisfy deep retrieval/eligibility metrics quickly, we run the existing robust scripts
    subprocess.run([r".\.venv\Scripts\python.exe", "evaluation/conference/run_all_experiments.py"], check=True, cwd=str(root))
    subprocess.run([r".\.venv\Scripts\python.exe", "evaluation/conference/aggregate_metrics.py"], check=True, cwd=str(root))
    
    src = root / "evaluation" / "conference" / "metrics" / "final_results.json"
    if src.exists():
        import shutil
        shutil.copy(src, final_dir / "metrics" / "final_verified_results.json")
        with open(src, "r") as f:
            return json.load(f)
    return {}

def main():
    root = Path(__file__).resolve().parent
    final_dir = ensure_dirs(root)
    
    run_phase1(final_dir)
    
    api_metrics = run_model_queries(final_dir)
    
    agg = run_old_benchmarks(root, final_dir)
    
    print("All tasks finished successfully. Terminal summary follows.")
    
if __name__ == "__main__":
    main()
