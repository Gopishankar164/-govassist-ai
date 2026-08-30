import json
from pathlib import Path
import random

def generate_benchmark():
    root = Path(__file__).resolve().parent.parent.parent
    
    benchmark = []
    
    # 100 Q&A cases
    for i in range(100):
        # Generate a random profile
        profile = {}
        if random.random() > 0.5: profile['gender'] = random.choice(["Male", "Female"])
        if random.random() > 0.5: profile['age'] = random.randint(18, 65)
        if random.random() > 0.5: profile['state'] = random.choice(["Tamil Nadu", "Maharashtra", "Karnataka", "Delhi"])
        if random.random() > 0.5: profile['income'] = random.choice([50000, 150000, 300000])
        if random.random() > 0.5: profile['occupation'] = random.choice(["farmer", "student", "worker"])
        
        # Recommendations mock
        recs = []
        if random.random() > 0.3:
            recs = [
                {"scheme_name": f"Scheme {i}", "missing_information": ["caste" if random.random() > 0.5 else "age"]}
            ]
            
        benchmark.append({
            "profile": profile,
            "recommendations": recs,
            "query_domain": random.choice(["agriculture", "education", "health", "other"])
        })
        
    out_dir = root / "evaluation" / "conference" / "datasets"
    with open(out_dir / "grounding_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=4)
        
    print(f"Generated {len(benchmark)} grounding cases.")

if __name__ == "__main__":
    generate_benchmark()
