"""
Canonical internal scheme representation (Phase 3).

IMPORTANT — this schema was designed AFTER inspecting the real Schemes.csv
(3,397 unique rows after de-duplication, 11 raw columns). Most demographic /
structured eligibility fields requested by the original project brief
(income, age, gender, caste, state, ministry, official URL, start/end date)
do NOT exist as separate columns in the source data. They are embedded as
free text inside `eligibility`, `details`, and `application`.

Fields below are therefore split into two groups:
  1. Fields FOUND directly in the CSV -> copied as-is (never fabricated).
  2. Fields NOT FOUND as columns -> populated ONLY via conservative regex
     extraction from free text (see preprocessing.py), and explicitly set
     to "unknown" when no confident match exists. They are never guessed.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class CanonicalScheme:
    # --- Identity (derived from CSV, deterministic) ---
    scheme_id: str          # = slug (unique after de-dup; see ingestion.py)
    scheme_name: str
    slug: str
    source_row: int          # original row index in Schemes.csv (0-based)

    # --- Directly-found free-text fields (copied verbatim from CSV) ---
    description: str         # <- details
    benefits: str             # <- benefits
    eligibility_text: str    # <- eligibility (raw)
    application_process: str  # <- application
    documents: str            # <- documents

    # --- Directly-found structured fields ---
    level: str                # "State" or "Central" <- level
    category: str             # raw comma-joined string <- schemeCategory
    category_list: List[str] = field(default_factory=list)  # schemeCategory split on ","
    tags: List[str] = field(default_factory=list)            # tags split on ","

    # --- NOT FOUND as columns: extracted conservatively from free text, else "unknown" ---
    state: str = "unknown"                 # extracted from eligibility/details text
    ministry: str = "unknown"              # NOT FOUND anywhere structured; always "unknown"
    gender_criteria: str = "unknown"       # "female" | "male" | "unknown"
    caste_criteria: List[str] = field(default_factory=list)  # e.g. ["SC","ST"], [] if none found
    income_ceiling_inr: Optional[int] = None   # None = not found / not applicable
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    official_url: Optional[str] = None     # extracted from application text if a URL is present

    def to_dict(self) -> dict:
        return asdict(self)
