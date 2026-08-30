import json
import pandas as pd
from pathlib import Path
import random

def generate_benchmark():
    root = Path(__file__).resolve().parent.parent.parent
    ds_path = root / "data" / "index" / "schemes_metadata.jsonl"
    
    records = []
    with open(ds_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    random.seed(42)
    sample_indices = random.sample(range(len(records)), 150)
    sampled_records = [records[i] for i in sample_indices]
    
    benchmark = []
    
    for row in sampled_records:
        sid = row.get('scheme_id')
        name = str(row.get('scheme_name', ''))
        state = str(row.get('state', ''))
        cat = str(row.get('category', ''))
        
        q_type = random.choice(["exact_name", "category_state", "benefit_focused"])
        
        if q_type == "exact_name":
            query = f"I want to know about the {name}."
            difficulty = "easy"
        elif q_type == "category_state":
            query = f"What are the government schemes for {cat} in {state}?" if state and state != 'unknown' else f"What are the government schemes for {cat}?"
            difficulty = "medium"
        else:
            query = f"I need financial assistance related to {cat}."
            difficulty = "hard"
            
        benchmark.append({
            "query": query,
            "expected_scheme_ids": [sid],
            "category": cat,
            "difficulty": difficulty,
            "ground_truth_source": "dataset_procedural",
            "notes": f"Procedurally generated targeting {name}"
        })
        
    out_dir = root / "evaluation" / "conference" / "datasets"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "retrieval_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=4)
        
    print(f"Generated {len(benchmark)} retrieval benchmark queries.")

if __name__ == "__main__":
    generate_benchmark()
