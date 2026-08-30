"""
Phase 5 — Data ingestion.

Loads Schemes.csv, removes exact duplicate rows, normalizes text, applies
conservative structured-field extraction, and converts every row into a
CanonicalScheme. Never fabricates values. Saves the processed dataset as
JSONL for downstream stages.
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import RAW_CSV_PATH, PROCESSED_DIR, PROCESSED_JSONL_PATH, INGESTION_STATS_PATH
from src.schema import CanonicalScheme
from src.preprocessing import (
    normalize_text, split_multi, split_category, extract_state, extract_gender,
    extract_caste, extract_income_ceiling, extract_age_range, extract_first_url,
)

RAW_TEXT_COLUMNS = ["scheme_name", "details", "benefits", "eligibility", "application", "documents"]
IMPORTANT_FIELDS = ["scheme_name", "details", "benefits", "eligibility"]


def load_raw(csv_path: Path = RAW_CSV_PATH) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. Ingestion cannot proceed without the real CSV."
        )
    df = pd.read_csv(csv_path)
    return df


def build_canonical_records(df: pd.DataFrame):
    records = []
    missing_important = {f: 0 for f in IMPORTANT_FIELDS}

    for idx, row in df.iterrows():
        name = normalize_text(row.get("scheme_name"))
        slug = normalize_text(row.get("slug"))
        details = normalize_text(row.get("details"))
        benefits = normalize_text(row.get("benefits"))
        eligibility = normalize_text(row.get("eligibility"))
        application = normalize_text(row.get("application"))
        documents = normalize_text(row.get("documents"))
        level = normalize_text(row.get("level"))
        category_raw = normalize_text(row.get("schemeCategory"))
        tags_raw = normalize_text(row.get("tags"))

        for col, val in [("scheme_name", name), ("details", details),
                          ("benefits", benefits), ("eligibility", eligibility)]:
            if not val:
                missing_important[col] += 1

        elig_and_details = f"{eligibility} {details}"
        income_ceiling = extract_income_ceiling(elig_and_details)
        age_min, age_max = extract_age_range(elig_and_details)

        record = CanonicalScheme(
            scheme_id=slug,
            scheme_name=name,
            slug=slug,
            source_row=int(idx),
            description=details,
            benefits=benefits,
            eligibility_text=eligibility,
            application_process=application,
            documents=documents,
            level=level,
            category=category_raw,
            category_list=split_category(category_raw),
            tags=split_multi(tags_raw),
            state=extract_state(elig_and_details),
            ministry="unknown",  # NOT FOUND in dataset -- never guessed
            gender_criteria=extract_gender(elig_and_details),
            caste_criteria=extract_caste(elig_and_details),
            income_ceiling_inr=income_ceiling,
            age_min=age_min,
            age_max=age_max,
            official_url=extract_first_url(application),
        )
        records.append(record)

    return records, missing_important


def run_ingestion(csv_path: Path = RAW_CSV_PATH, verbose: bool = True) -> dict:
    df_raw = load_raw(csv_path)
    original_count = len(df_raw)

    df_dedup = df_raw.drop_duplicates().reset_index(drop=True)
    duplicates_removed = original_count - len(df_dedup)

    slug_dupes = df_dedup["slug"].duplicated().sum()
    if slug_dupes:
        # We never silently overwrite data; report and keep going, downstream
        # code disambiguates by appending source_row to any residual collision.
        if verbose:
            print(f"WARNING: {slug_dupes} slug collisions remain after exact-duplicate removal.")

    records, missing_important = build_canonical_records(df_dedup)

    # Disambiguate any residual scheme_id collisions deterministically (rare/none expected)
    seen = {}
    for rec in records:
        if rec.scheme_id in seen:
            seen[rec.scheme_id] += 1
            rec.scheme_id = f"{rec.scheme_id}__{seen[rec.scheme_id]}"
        else:
            seen[rec.scheme_id] = 0

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_JSONL_PATH, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")

    stats = {
        "original_records": original_count,
        "duplicates_removed": int(duplicates_removed),
        "final_records": len(records),
        "missing_important_fields": missing_important,
        "structured_field_coverage": {
            "state_known": sum(1 for r in records if r.state != "unknown"),
            "gender_known": sum(1 for r in records if r.gender_criteria != "unknown"),
            "caste_known": sum(1 for r in records if r.caste_criteria),
            "income_ceiling_known": sum(1 for r in records if r.income_ceiling_inr is not None),
            "age_range_known": sum(1 for r in records if r.age_min is not None),
        },
    }
    with open(INGESTION_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    if verbose:
        print("=== INGESTION COMPLETE ===")
        print("Original records:", stats["original_records"])
        print("Duplicates removed:", stats["duplicates_removed"])
        print("Final records:", stats["final_records"])
        print("Missing important fields:", stats["missing_important_fields"])
        print("Structured field coverage:", stats["structured_field_coverage"])
        print(f"Saved processed dataset -> {PROCESSED_JSONL_PATH}")

    return stats


if __name__ == "__main__":
    run_ingestion()
