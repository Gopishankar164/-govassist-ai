import os
import subprocess
from pathlib import Path

def run_script(script_name):
    print(f"--- Running {script_name} ---")
    root = Path(__file__).resolve().parent.parent.parent
    script_path = root / "evaluation" / "conference" / script_name
    subprocess.run([r".\.venv\Scripts\python.exe", str(script_path)], check=True, cwd=str(root))

def main():
    scripts = [
        "dataset_audit.py",
        "generate_retrieval_benchmark.py",
        "generate_eligibility_benchmark.py",
        "generate_grounding_benchmark.py",
        "run_retrieval_eval.py",
        "run_eligibility_eval.py",
        "run_grounding_eval.py",
        "run_e2e_eval.py"
    ]
    for s in scripts:
        run_script(s)
    print("All experiments completed successfully.")

if __name__ == "__main__":
    main()
