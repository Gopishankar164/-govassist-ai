import matplotlib.pyplot as plt
import numpy as np
import os

# Create figures directory
out_dir = "conference_figures"
os.makedirs(out_dir, exist_ok=True)

# Common styling
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'figure.titlesize': 16,
    'font.family': 'sans-serif'
})

# =====================================================================
# FIGURE 3: Retrieval Evaluation (Methodology since data unavailable)
# =====================================================================
def plot_fig3():
    # evaluate_indices.py evaluates latency (Min, Avg, Max) across 10 queries for OLD and NEW FAISS indices.
    # Since actual numeric logs aren't saved, we'll draw the evaluation architecture mechanism.
    
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450">
    <rect width="800" height="450" fill="white"/>
    
    <rect x="50" y="50" width="180" height="60" rx="5" fill="#f5f5f5" stroke="#333" stroke-width="2"/>
    <text x="140" y="75" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Evaluation Queries</text>
    <text x="140" y="95" font-family="sans-serif" font-size="12" text-anchor="middle">(N = 10 Reference Queries)</text>

    <line x1="230" y1="80" x2="280" y2="80" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>

    <rect x="280" y="50" width="160" height="60" rx="5" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
    <text x="360" y="75" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">BGE-Small-EN-v1.5</text>
    <text x="360" y="95" font-family="sans-serif" font-size="12" text-anchor="middle">(Query Embedding)</text>

    <line x1="440" y1="80" x2="520" y2="80" stroke="black" stroke-width="2"/>
    <line x1="520" y1="80" x2="520" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- Old Index Path -->
    <line x1="520" y1="120" x2="410" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="330" y="150" width="160" height="70" rx="5" fill="#ffecb3" stroke="#ffa000" stroke-width="2"/>
    <text x="410" y="175" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">OLD FAISS Index</text>
    <text x="410" y="195" font-family="sans-serif" font-size="12" text-anchor="middle">(Baseline Vector Store)</text>

    <!-- New Index Path -->
    <line x1="520" y1="120" x2="630" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <rect x="550" y="150" width="160" height="70" rx="5" fill="#c8e6c9" stroke="#388e3c" stroke-width="2"/>
    <text x="630" y="175" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">NEW FAISS Index</text>
    <text x="630" y="195" font-family="sans-serif" font-size="12" text-anchor="middle">(Updated Vector Store)</text>
    
    <!-- Top-K Retrieval Output -->
    <line x1="410" y1="220" x2="410" y2="260" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <line x1="630" y1="220" x2="630" y2="260" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="300" y="260" width="440" height="150" rx="10" fill="#fce4ec" stroke="#d81b60" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="520" y="290" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">Semantic Retrieval Evaluation Metrics</text>
    
    <text x="330" y="325" font-family="sans-serif" font-size="14" font-weight="bold">Top-K Validation</text>
    <text x="330" y="345" font-family="sans-serif" font-size="14">- Similarity Score Ranking</text>
    <text x="330" y="365" font-family="sans-serif" font-size="14">- Candidate Verification (URL)</text>
    
    <text x="550" y="325" font-family="sans-serif" font-size="14" font-weight="bold">Latency Profiling</text>
    <text x="550" y="345" font-family="sans-serif" font-size="14">- Minimum Latency (ms)</text>
    <text x="550" y="365" font-family="sans-serif" font-size="14">- Average Latency (ms)</text>
    <text x="550" y="385" font-family="sans-serif" font-size="14">- Maximum Latency (ms)</text>

    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
</svg>"""
    with open(os.path.join(out_dir, 'fig3_retrieval_performance.svg'), 'w') as f:
        f.write(svg_content)
    
    # We remove the old misleading chart and put a stub PNG directing to the SVG
    fig, ax = plt.subplots(figsize=(8,4))
    ax.text(0.5, 0.5, "Please see SVG for the retrieval evaluation mechanism.", ha='center', va='center')
    ax.axis('off')
    plt.savefig(os.path.join(out_dir, 'fig3_retrieval_performance.png'), dpi=300)
    plt.close()

# =====================================================================
# FIGURE 4: Eligibility Decision Mechanism
# =====================================================================
def plot_fig4():
    # Visualizing exact src/agents/eligibility.py logic
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600">
    <rect width="900" height="600" fill="white"/>
    
    <!-- Input -->
    <rect x="350" y="20" width="200" height="60" rx="5" fill="#f5f5f5" stroke="#333" stroke-width="2"/>
    <text x="450" y="45" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Rule Evaluation Engine</text>
    <text x="450" y="65" font-family="sans-serif" font-size="12" text-anchor="middle">(Profile Attributes vs Scheme Rules)</text>

    <line x1="450" y1="80" x2="450" y2="120" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- Step 1: Attribute checking -->
    <rect x="250" y="120" width="400" height="80" rx="5" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
    <text x="450" y="145" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Demographic Parameter Matching</text>
    <text x="450" y="165" font-family="sans-serif" font-size="12" text-anchor="middle">1. Income  2. Age  3. Gender  4. Occupation  5. State</text>
    <text x="450" y="185" font-family="sans-serif" font-size="12" text-anchor="middle">(Aggregates 'failed_criteria' and 'passed_criteria' counts)</text>
    
    <line x1="450" y1="200" x2="450" y2="240" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Decision Tree -->
    <polygon points="450,240 600,290 450,340 300,290" fill="#fff9c4" stroke="#fbc02d" stroke-width="2"/>
    <text x="450" y="285" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Length of</text>
    <text x="450" y="305" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">failed_criteria?</text>
    
    <!-- Path: == 0 -->
    <line x1="300" y1="290" x2="160" y2="290" stroke="black" stroke-width="2"/>
    <text x="230" y="280" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">== 0</text>
    <line x1="160" y1="290" x2="160" y2="400" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <!-- Path: == 1 -->
    <line x1="450" y1="340" x2="450" y2="380" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="465" y="365" font-family="sans-serif" font-size="14" font-weight="bold">== 1 &amp;</text>
    <text x="465" y="385" font-family="sans-serif" font-size="14" font-weight="bold">passed >= 2</text>
    
    <!-- Path: > 1 or else -->
    <line x1="600" y1="290" x2="740" y2="290" stroke="black" stroke-width="2"/>
    <text x="670" y="280" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Otherwise</text>
    <line x1="740" y1="290" x2="740" y2="400" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>

    <!-- Outcomes -->
    <rect x="60" y="400" width="200" height="70" rx="5" fill="#c8e6c9" stroke="#388e3c" stroke-width="2"/>
    <text x="160" y="430" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">Eligible</text>
    <text x="160" y="450" font-family="sans-serif" font-size="12" text-anchor="middle">(Eligibility Factor = 1.0)</text>
    
    <rect x="350" y="400" width="200" height="70" rx="5" fill="#fff59d" stroke="#fbc02d" stroke-width="2"/>
    <text x="450" y="430" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">Partially Eligible</text>
    <text x="450" y="450" font-family="sans-serif" font-size="12" text-anchor="middle">(Eligibility Factor = 0.65)</text>

    <rect x="640" y="400" width="200" height="70" rx="5" fill="#ffcdd2" stroke="#d32f2f" stroke-width="2"/>
    <text x="740" y="430" font-family="sans-serif" font-size="16" font-weight="bold" text-anchor="middle">Not Eligible</text>
    <text x="740" y="450" font-family="sans-serif" font-size="12" text-anchor="middle">(Eligibility Factor = 0.25)</text>
    
    <!-- Final Calculation -->
    <line x1="160" y1="470" x2="160" y2="520" stroke="black" stroke-width="2"/>
    <line x1="740" y1="470" x2="740" y2="520" stroke="black" stroke-width="2"/>
    <line x1="450" y1="470" x2="450" y2="520" stroke="black" stroke-width="2"/>
    <line x1="160" y1="520" x2="450" y2="520" stroke="black" stroke-width="2"/>
    <line x1="740" y1="520" x2="450" y2="520" stroke="black" stroke-width="2"/>
    <line x1="450" y1="520" x2="450" y2="550" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>

    <rect x="250" y="550" width="400" height="40" rx="5" fill="#f5f5f5" stroke="#333" stroke-width="2"/>
    <text x="450" y="575" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Confidence Score = (Sim * 0.4) + (Factor * 0.4) + (Verif * 0.2)</text>

    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
</svg>"""
    with open(os.path.join(out_dir, 'fig4_eligibility_decision_mechanism.svg'), 'w') as f:
        f.write(svg_content)
    # Removing the old incorrect name
    if os.path.exists(os.path.join(out_dir, 'fig4_eligibility_distribution.svg')):
        os.remove(os.path.join(out_dir, 'fig4_eligibility_distribution.svg'))
    if os.path.exists(os.path.join(out_dir, 'fig4_eligibility_distribution.png')):
        os.remove(os.path.join(out_dir, 'fig4_eligibility_distribution.png'))

    fig, ax = plt.subplots(figsize=(8,4))
    ax.text(0.5, 0.5, "Please see SVG for the eligibility mechanism.", ha='center', va='center')
    ax.axis('off')
    plt.savefig(os.path.join(out_dir, 'fig4_eligibility_decision_mechanism.png'), dpi=300)
    plt.close()

# =====================================================================
# FIGURE 5: Pipeline execution time
# =====================================================================
def plot_fig5():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    stages = [
        'Profile extraction', 
        'Query rewriting', 
        'Embedding', 
        'FAISS retrieval', 
        'Eligibility analysis', 
        'Reranking'
    ]
    times = [0.29, 0.01, 57.98, 1.20, 0.52, 2.54]
    
    y_pos = np.arange(len(stages))
    
    bars = ax.barh(y_pos, times, color='#2c3e50')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages)
    ax.set_xlabel('Execution Time (ms)')
    ax.set_title('Deterministic Processing Pipeline (Before LLM Generation)\nTotal = ~62.54 ms')
    ax.invert_yaxis()
    
    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{times[i]:.2f} ms', 
                va='center', ha='left')
    
    ax.set_xlim(0, max(times) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fig5_pipeline_execution_time.png'), dpi=300)
    plt.savefig(os.path.join(out_dir, 'fig5_pipeline_execution_time.svg'))
    plt.close()

# =====================================================================
# FIGURE 6: Automated Software Validation
# =====================================================================
def plot_fig6():
    fig, ax = plt.subplots(figsize=(6, 5))
    
    categories = ['Passed', 'Failed', 'Skipped', 'Errors']
    values = [52, 0, 0, 0]
    colors = ['#2ca02c', '#d62728', '#ff7f0e', '#7f7f7f']
    
    bars = ax.bar(categories, values, color=colors)
    
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{int(bar.get_height())}', 
                va='bottom', ha='center', fontweight='bold', fontsize=14)
    
    ax.set_ylabel('Number of Tests')
    ax.set_title('Automated Software Validation Results')
    ax.set_ylim(0, 60)
    
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'fig6_system_validation.png'), dpi=300)
    plt.savefig(os.path.join(out_dir, 'fig6_system_validation.svg'))
    plt.close()

# =====================================================================
# FIGURE 7: Conversational Profile Update
# =====================================================================
def plot_fig7():
    # Utilizing exactly: Income, Age, Gender, Occupation, State based on eligibility.py
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 550">
    <rect width="850" height="550" fill="white"/>
    
    <rect x="50" y="50" width="240" height="60" rx="5" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
    <text x="170" y="75" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Initial Natural-Language Query</text>
    <text x="170" y="95" font-family="sans-serif" font-size="12" text-anchor="middle">"I am a 22-year-old student from Tamil Nadu"</text>
    
    <line x1="170" y1="110" x2="170" y2="150" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="50" y="150" width="240" height="80" rx="5" fill="#f1f8e9" stroke="#388e3c" stroke-width="2"/>
    <text x="170" y="175" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Profile Extraction</text>
    <text x="170" y="195" font-family="sans-serif" font-size="12" text-anchor="middle">Known: Age=22, Occup=Student, State=TN</text>
    <text x="170" y="215" font-family="sans-serif" font-size="12" text-anchor="middle">Missing: Income, Gender</text>
    
    <line x1="290" y1="190" x2="350" y2="190" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="350" y="160" width="180" height="60" rx="5" fill="#ffebee" stroke="#d32f2f" stroke-width="2"/>
    <text x="440" y="185" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Missing Information</text>
    <text x="440" y="205" font-family="sans-serif" font-size="12" text-anchor="middle">Identify missing parameters</text>
    
    <line x1="440" y1="220" x2="440" y2="270" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="350" y="270" width="180" height="60" rx="5" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
    <text x="440" y="295" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">User Follow-up</text>
    <text x="440" y="315" font-family="sans-serif" font-size="12" text-anchor="middle">"My family income is 50,000"</text>
    
    <line x1="440" y1="330" x2="440" y2="380" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="350" y="380" width="180" height="80" rx="5" fill="#f1f8e9" stroke="#388e3c" stroke-width="2"/>
    <text x="440" y="405" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Profile Update</text>
    <text x="440" y="425" font-family="sans-serif" font-size="12" text-anchor="middle">Age=22, Occup=Student</text>
    <text x="440" y="445" font-family="sans-serif" font-size="12" text-anchor="middle">State=TN, Income=50,000</text>
    
    <line x1="530" y1="420" x2="590" y2="420" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="590" y="390" width="220" height="60" rx="5" fill="#fff3e0" stroke="#f57c00" stroke-width="2"/>
    <text x="700" y="415" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Query/Context Update</text>
    <text x="700" y="435" font-family="sans-serif" font-size="12" text-anchor="middle">Incorporate contextual constraints</text>
    
    <line x1="700" y1="390" x2="700" y2="340" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>
    
    <rect x="590" y="280" width="220" height="60" rx="5" fill="#ede7f6" stroke="#5e35b1" stroke-width="2"/>
    <text x="700" y="305" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Fresh Retrieval</text>
    <text x="700" y="325" font-family="sans-serif" font-size="12" text-anchor="middle">Re-query semantic FAISS index</text>

    <line x1="700" y1="280" x2="700" y2="230" stroke="black" stroke-width="2" marker-end="url(#arrow)"/>

    <rect x="590" y="170" width="220" height="60" rx="5" fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>
    <text x="700" y="195" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">Updated Recommendation</text>
    <text x="700" y="215" font-family="sans-serif" font-size="12" text-anchor="middle">Filtered by evaluated eligibility</text>

    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#000" />
        </marker>
    </defs>
</svg>"""
    with open(os.path.join(out_dir, 'fig7_conversational_profile_update.svg'), 'w') as f:
        f.write(svg_content)
    
    fig, ax = plt.subplots(figsize=(8,4))
    ax.text(0.5, 0.5, "Please see SVG for the state transition diagram.", ha='center', va='center')
    ax.axis('off')
    plt.savefig(os.path.join(out_dir, 'fig7_conversational_profile_update.png'), dpi=300)
    plt.close()

if __name__ == "__main__":
    plot_fig3()
    plot_fig4()
    plot_fig5()
    plot_fig6()
    plot_fig7()
    print("Figures generated successfully.")
