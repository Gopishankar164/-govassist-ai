import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT_DIR = Path("evaluation/conference/final/plots/model_results")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Dataset size OLD vs NEW
plt.figure(figsize=(6, 4))
labels = ['Old Index', 'New Index']
sizes = [3397, 4858]
plt.bar(labels, sizes, color=['#4F46E5', '#10B981'])
plt.title('Dataset Size (Number of Schemes)')
plt.ylabel('Count')
for i, v in enumerate(sizes):
    plt.text(i, v + 50, str(v), ha='center', fontweight='bold')
plt.savefig(OUT_DIR / "dataset_size.png", dpi=300, bbox_inches='tight')
plt.close()

# 2. Retrieval Latency OLD vs NEW
plt.figure(figsize=(6, 4))
labels = ['Avg', 'p50', 'p95']
old_lat = [1.11, 1.09, 1.22]
new_lat = [1.44, 1.29, 1.88]

x = np.arange(len(labels))
width = 0.35
fig, ax = plt.subplots(figsize=(6, 4))
rects1 = ax.bar(x - width/2, old_lat, width, label='Old Index', color='#9CA3AF')
rects2 = ax.bar(x + width/2, new_lat, width, label='New Index', color='#3B82F6')

ax.set_ylabel('Latency (ms)')
ax.set_title('Retrieval Latency Comparison')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
plt.savefig(OUT_DIR / "retrieval_latency.png", dpi=300, bbox_inches='tight')
plt.close()

# 3. Eligibility Metrics
plt.figure(figsize=(6, 4))
metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
values = [1.0, 1.0, 1.0, 1.0]
plt.bar(metrics, values, color='#10B981')
plt.title('Eligibility Engine Performance')
plt.ylabel('Score')
plt.ylim(0, 1.1)
plt.savefig(OUT_DIR / "eligibility_metrics.png", dpi=300, bbox_inches='tight')
plt.close()

# 4. Grounding vs Hallucination
plt.figure(figsize=(6, 4))
labels = ['Grounded', 'Hallucinated']
values = [100, 0]
plt.bar(labels, values, color=['#10B981', '#EF4444'])
plt.title('Response Grounding Rate (%)')
plt.ylabel('Percentage')
plt.savefig(OUT_DIR / "grounding_rate.png", dpi=300, bbox_inches='tight')
plt.close()

print("Plots generated successfully!")
