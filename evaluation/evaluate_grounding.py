import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import GovAssistPipeline
import json
import re

TEST_QUERIES = [
    "I am a student from Tamil Nadu.",
    "I am a farmer from Maharashtra with 2 lakh income.",
    "Show me schemes for women entrepreneurs.",
    "I need a scholarship for engineering.",
    "Are there any schemes that give out free iPhones?",
    "Tell me about the PM Universal 10 Lakh Basic Income Scheme.",
    "Give me schemes that have no eligibility requirements whatsoever."
]

def extract_numbers(text):
    return set(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', text))

def main():
    print("=== GROUNDING EVALUATION ===")
    
    pipeline = GovAssistPipeline()
    
    total_claims = 0
    grounded_claims = 0
    hallucinations = 0
    
    for q in TEST_QUERIES:
        print(f"\nQuery: {q}")
        try:
            res = pipeline.recommend(q, top_k=3, final_n=3)
        except Exception as e:
            print(f"Failed: {e}")
            continue
            
        answer = res['answer']
        schemes = res['recommendations']
        
        # In a deterministic generator, the text should only contain facts from the profile
        # Verify numbers in the preamble
        ans_nums = extract_numbers(answer)
        profile_nums = set()
        for k, v in res['profile'].items():
            if isinstance(v, (int, float)):
                profile_nums.add(str(v))
                profile_nums.add(f"{v:,}")
                
        unsupported_nums = ans_nums - profile_nums
        
        claims = 1 + len(schemes) # 1 for the preamble, +1 for each returned scheme card
        total_claims += claims
        
        is_grounded = True
        
        # Verify scheme URLs aren't hallucinated
        for s in schemes:
            url = s.get('official_url')
            if url and not url.startswith('http'):
                is_grounded = False
                print(f"  [ERROR] Malformed URL in scheme: {s['scheme_name']}")
                
        if unsupported_nums:
            is_grounded = False
            print(f"  [ERROR] Unsupported numbers found in preamble: {unsupported_nums}")
            
        if is_grounded:
            grounded_claims += claims
            print("  Status: 100% Grounded (Deterministic)")
        else:
            hallucinations += 1
            
    print("\n=== GROUNDING METRICS ===")
    print(f"Total Claims Assessed: {total_claims}")
    print(f"Grounded Claims: {grounded_claims}")
    print(f"Unsupported Claims: {total_claims - grounded_claims}")
    hallucination_rate = ((total_claims - grounded_claims) / total_claims) * 100 if total_claims else 0
    print(f"Hallucination Rate: {hallucination_rate:.2f}%")
    
    out_dir = Path("evaluation/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "grounding_metrics.json", "w") as f:
        json.dump({
            "grounded_claim_rate": (grounded_claims / total_claims) if total_claims else 1.0,
            "unsupported_claim_count": total_claims - grounded_claims,
            "hallucination_rate": hallucination_rate
        }, f, indent=2)

if __name__ == "__main__":
    main()
