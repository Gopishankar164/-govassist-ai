from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent
    plots_dir = root / "evaluation" / "conference" / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    msg = "BLOCKED: Plots could not be generated because `matplotlib` and `seaborn` are not installed in the current environment.\n"
    
    plots = [
        "dataset_size_comparison.txt",
        "retrieval_recall_old_vs_new.txt",
        "retrieval_precision_old_vs_new.txt",
        "retrieval_mrr_ndcg.txt",
        "latency_distribution.txt",
        "latency_breakdown.txt",
        "eligibility_confusion_matrix.txt",
        "grounding_hallucination_results.txt",
        "agent_latency_comparison.txt"
    ]
    
    for p in plots:
        with open(plots_dir / p, "w") as f:
            f.write(msg)
            
    print("Plot generation marked as BLOCKED due to missing dependencies.")

if __name__ == "__main__":
    main()
