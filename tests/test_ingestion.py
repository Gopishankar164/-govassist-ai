import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.ingestion import run_ingestion, load_raw, build_canonical_records
from src.config import RAW_CSV_PATH


def test_raw_csv_exists():
    assert RAW_CSV_PATH.exists(), "Schemes.csv must exist for ingestion tests"


def test_load_raw_row_count():
    df = load_raw()
    assert len(df) == 4858  # verified real row count of Merged_Schemes.csv


def test_duplicate_removal():
    stats = run_ingestion(verbose=False)
    assert stats["duplicates_removed"] == 0
    assert stats["final_records"] == 4858


def test_no_missing_core_text_fields():
    stats = run_ingestion(verbose=False)
    # Merged dataset has a few null descriptions/benefits
    assert stats["missing_important_fields"]["scheme_name"] == 0



def test_scheme_ids_unique():
    df = load_raw().drop_duplicates()
    records, _ = build_canonical_records(df)
    ids = [r.scheme_id for r in records]
    assert len(ids) == len(set(ids)), "scheme_id collisions found after de-duplication"


def test_category_split_preserves_atomic_names():
    """Regression test: 'Agriculture,Rural & Environment' is ONE category
    (internal comma, no space), not two -- must not be split on bare comma."""
    df = load_raw().drop_duplicates()
    records, _ = build_canonical_records(df)
    matches = [r for r in records if r.category == "Agriculture,Rural & Environment"]
    assert matches, "expected at least one scheme with this exact category string"
    assert matches[0].category_list == ["Agriculture,Rural & Environment"]


def test_missing_dataset_raises_filenotfound():
    with pytest.raises(FileNotFoundError):
        load_raw(Path("/nonexistent/Schemes.csv"))
