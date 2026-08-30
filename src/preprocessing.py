"""
Text normalization and conservative field extraction.

Extraction functions here NEVER guess. Each returns "unknown"/None/[] when
no confident pattern match exists. Coverage was measured empirically against
the full 3,397-row dataset (see project chat log):
    state extraction   : 60.4% of schemes
    gender extraction  : 18.5% of schemes
    caste extraction   : 16.2% of schemes
    income extraction  : 11.7% of schemes
    age-range extraction: 6.0% of schemes
The remainder are explicitly marked unknown -- this is expected, not a bug,
because the source dataset itself does not state these criteria explicitly
for most schemes.
"""
import re
from typing import Optional, List, Tuple

from src.config import INDIAN_STATES, CASTE_CATEGORY_TERMS

_URL_RE = re.compile(r'https?://[^\s)\]"\'\u200b\ufeff]+')


def normalize_text(value) -> str:
    """Normalize a raw CSV cell to a clean string without destroying content."""
    if value is None:
        return ""
    text = str(value)
    if text.strip().lower() in ("nan", "none"):
        return ""
    # collapse whitespace, strip zero-width/BOM junk seen in the raw CSV
    text = text.replace("\ufeff", "").replace("\u200b", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_multi(value: str, sep: str = ",") -> List[str]:
    """Split a delimiter-joined field into a clean list."""
    if not value:
        return []
    return [p.strip() for p in value.split(sep) if p.strip()]


def split_category(value: str) -> List[str]:
    """
    Split schemeCategory into individual category labels.

    IMPORTANT: verified against the real data that some atomic category
    names themselves contain an internal comma with NO following space
    (e.g. "Agriculture,Rural & Environment", "Banking,Financial Services
    and Insurance" -- these are single categories, not two). True
    multi-category rows are joined with ", " (comma + space). So the
    correct separator is ", " (comma+space), NOT a bare comma.
    """
    return split_multi(value, sep=", ")


def extract_state(*texts: str) -> str:
    combined = " ".join(texts)
    for state in INDIAN_STATES:
        if re.search(r"\b" + re.escape(state) + r"\b", combined, re.IGNORECASE):
            return state
    return "unknown"


def extract_gender(*texts: str) -> str:
    combined = " ".join(texts).lower()
    has_female = bool(re.search(r"\b(female|women|woman|girl|widow)\b", combined))
    has_male = bool(re.search(r"\bmale\b", combined)) and not re.search(r"\bfemale\b", combined)
    if has_female and not has_male:
        return "female"
    if has_male and not has_female:
        return "male"
    return "unknown"


def extract_caste(*texts: str) -> List[str]:
    combined = " ".join(texts)
    found = []
    for term in CASTE_CATEGORY_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", combined, re.IGNORECASE):
            found.append(term)
    return found


def extract_income_ceiling(*texts: str) -> Optional[int]:
    combined = " ".join(texts)
    m = re.search(
        r"(?:income)[^.]{0,60}?(?:up ?to|below|less than|not exceed(?:ing)?|does not exceed)"
        r"\D{0,10}(?:rs\.?|\u20b9|inr)?\s?([\d,]{4,})",
        combined, re.IGNORECASE,
    )
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def extract_age_range(*texts: str) -> Tuple[Optional[int], Optional[int]]:
    combined = " ".join(texts)
    m = re.search(
        r"age[^.]{0,40}?between\s*(\d{1,2})\s*(?:years)?\s*(?:and|to|-)\s*(\d{1,3})\s*years",
        combined, re.IGNORECASE,
    )
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def extract_first_url(*texts: str) -> Optional[str]:
    combined = " ".join(texts)
    m = _URL_RE.search(combined)
    if m:
        # strip trailing punctuation frequently glued to URLs in prose
        return m.group(0).rstrip(".,;)")
    return None
