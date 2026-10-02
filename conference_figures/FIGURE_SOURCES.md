# Figure Sources

## FIGURE 2 — DATASET COMPARISON AND KNOWLEDGE BASE CONSTRUCTION
- **Source file/test/log:** `overlap_results.json` and `phase2_results.json` (also user-provided project metadata)
- **Exact data used:** 3,400 old records, 3,397 unique old schemas, 4,693 new unique schemas, 3,232 common schemas, 1,461 new unique schemas, 4,858 final unique schemes.
- **Calculation performed:** None. Data directly matches the overlapping analysis output files.
- **Directly measured or derived:** Directly measured from dataset processing step outputs.

## FIGURE 3 — SEMANTIC RETRIEVAL EVALUATION
- **Source file/test/log:** `evaluate_indices.py` evaluation framework.
- **Exact data used:** N/A (Actual logged metric numbers were unavailable).
- **Calculation performed:** No numeric data fabricated. A technically accurate visualization of the `evaluate_indices.py` index evaluation mechanism (measuring Top-K ranking, latency vs query vectors against the Old and New FAISS index) is presented.
- **Directly measured or derived:** Derived structural diagram of the evaluation implementation logic.

## FIGURE 4 — ELIGIBILITY DECISION MECHANISM
- **Source file/test/log:** `src/agents/eligibility.py` implementation code.
- **Exact data used:** `evaluate_scheme()` rule mapping logic checking `failed_criteria` arrays across Income, Age, Gender, Occupation, and State fields.
- **Calculation performed:** N/A. Mapped logic constraints (`Length == 0` -> Eligible, `Length == 1 & passed >= 2` -> Partially Eligible, `Otherwise` -> Not Eligible) exactly to flow nodes.
- **Directly measured or derived:** Directly measured state mapping based on codebase.

## FIGURE 5 — PIPELINE EXECUTION TIME
- **Source file/test/log:** Profile extraction logs, user-provided pipeline metrics.
- **Exact data used:** Profile extraction: 0.29 ms, Query rewriting: 0.01 ms, Embedding: 57.98 ms, FAISS retrieval: 1.20 ms, Eligibility: 0.52 ms, Reranking: 2.54 ms.
- **Calculation performed:** Deterministic total sum calculated natively in graph bounds (~62.54 ms).
- **Directly measured or derived:** Directly measured deterministic execution timings.

## FIGURE 6 — AUTOMATED SOFTWARE VALIDATION RESULTS
- **Source file/test/log:** Automated test suite output (`run_tests.py` validation framework).
- **Exact data used:** Total tests: 52, Passed: 52, Failed: 0, Skipped: 0, Errors: 0.
- **Calculation performed:** None. 
- **Directly measured or derived:** Directly measured execution output.

## FIGURE 7 — CONVERSATIONAL PROFILE UPDATE
- **Source file/test/log:** `src/agents/eligibility.py` structural requirement constraints mapped across the NLP processing logic.
- **Exact data used:** Example user follow-up mapping attributes explicit to GovAssist: (Income, Age, Gender, Occupation, State) where 'Income' and 'Gender' start as missing.
- **Calculation performed:** Flow generated demonstrating entity capture mechanism update. 
- **Directly measured or derived:** Derived logically from the codebase dialogue manager and state entity logic.

## FIGURE 8 — ACTUAL GOVASSIST INTERFACE
- **Status:** Not generated.
- **Reason:** Metric unavailable in current headless implementation context. I cannot compile, launch, and visually scrape a high-fidelity frontend capture without a graphical browser environment. 
- **Action Required:** Please launch the local frontend React interface manually and take a native screenshot of the application interaction.
