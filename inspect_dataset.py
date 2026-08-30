import csv
import os
import platform
import sys

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Schemes.csv")

# Windows terminals may default to cp1252, which cannot print currency and
# other Unicode characters present in the source dataset.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 70)
print("GOVASSIST AI - DATASET INSPECTION")
print("=" * 70)

# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

print("\n[1] ENVIRONMENT")
print("Python:", sys.version)
print("OS:", platform.platform())
print("Machine:", platform.machine())

try:
    import torch
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))
except ImportError:
    print("PyTorch: not installed (not required for inspection)")

# --------------------------------------------------
# DATASET CHECK
# --------------------------------------------------

print("\n[2] DATASET")

if not os.path.exists(CSV_PATH):
    print("ERROR: Dataset not found:")
    print(os.path.abspath(CSV_PATH))
    sys.exit(1)

print("Dataset:", os.path.abspath(CSV_PATH))

# --------------------------------------------------
# LOAD CSV
# --------------------------------------------------

with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)

    columns = reader.fieldnames
    rows = list(reader)

print("\nRows:", len(rows))
print("Columns:", len(columns))

# --------------------------------------------------
# COLUMN NAMES
# --------------------------------------------------

print("\n[3] ALL COLUMN NAMES")

for i, col in enumerate(columns, 1):
    print(f"{i:3}. {col}")

# --------------------------------------------------
# SAMPLE RECORDS
# --------------------------------------------------

print("\n[4] FIVE SAMPLE RECORDS")

for i, row in enumerate(rows[:5], 1):
    print("\n" + "-" * 70)
    print("RECORD", i)

    for key, value in row.items():
        value = "" if value is None else value

        # prevent terminal flooding
        if len(value) > 500:
            value = value[:500] + "... [truncated]"

        print(f"{key}: {value}")

# --------------------------------------------------
# MISSING VALUES
# --------------------------------------------------

print("\n[5] MISSING VALUES")

missing_total = 0

for col in columns:
    count = 0

    for row in rows:
        value = row.get(col)

        if value is None or str(value).strip() == "":
            count += 1

    if count > 0:
        missing_total += count
        percentage = (count / len(rows)) * 100
        print(f"{col}: {count} missing ({percentage:.2f}%)")

if missing_total == 0:
    print("No missing values detected.")

# --------------------------------------------------
# DUPLICATES
# --------------------------------------------------

print("\n[6] DUPLICATE RECORDS")

seen = set()
duplicates = 0

for row in rows:
    record = tuple((col, row.get(col, "")) for col in columns)

    if record in seen:
        duplicates += 1
    else:
        seen.add(record)

print("Exact duplicate rows:", duplicates)

# --------------------------------------------------
# AUTOMATIC SCHEMA ANALYSIS
# --------------------------------------------------

print("\n[7] GOVERNMENT SCHEME SCHEMA ANALYSIS")

keywords = {
    "scheme_id": [
        "id", "scheme_id", "schemeid", "code", "scheme_code"
    ],

    "scheme_name": [
        "name", "scheme_name", "scheme", "title"
    ],

    "description": [
        "description", "about", "details", "overview", "summary"
    ],

    "eligibility": [
        "eligibility", "eligible", "criteria", "qualification"
    ],

    "benefits": [
        "benefit", "benefits", "financial", "assistance", "amount"
    ],

    "application_process": [
        "application", "apply", "process", "procedure", "how_to_apply"
    ],

    "documents": [
        "document", "documents", "required_documents", "proof"
    ],

    "state": [
        "state", "states", "location", "region"
    ],

    "ministry": [
        "ministry", "department", "authority"
    ],

    "category": [
        "category", "sector", "scheme_category", "type"
    ],

    "target_beneficiaries": [
        "beneficiary", "beneficiaries", "target", "audience"
    ],

    "income_criteria": [
        "income", "annual_income", "family_income"
    ],

    "age_criteria": [
        "age", "minimum_age", "maximum_age"
    ],

    "gender_criteria": [
        "gender", "sex"
    ],

    "education_criteria": [
        "education", "qualification", "student", "academic"
    ],

    "occupation_criteria": [
        "occupation", "profession", "employment"
    ],

    "caste_category": [
        "caste", "sc", "st", "obc", "ews", "category"
    ],

    "location_criteria": [
        "location", "state", "district", "residence", "domicile"
    ],

    "official_url": [
        "url", "website", "link", "portal", "official"
    ]
}

lower_columns = {
    col: col.lower().replace(" ", "_").replace("-", "_")
    for col in columns
}

for concept, terms in keywords.items():

    matches = []

    for original, normalized in lower_columns.items():

        for term in terms:

            if term in normalized:
                matches.append(original)
                break

    matches = list(dict.fromkeys(matches))

    print(f"\n{concept}:")
    
    if matches:
        for match in matches:
            print("   ->", match)
    else:
        print("   -> NOT FOUND")

# --------------------------------------------------
# UNIQUE VALUES / IDENTIFIER CANDIDATES
# --------------------------------------------------

print("\n[8] POSSIBLE UNIQUE IDENTIFIER COLUMNS")

for col in columns:

    values = [
        row.get(col, "").strip()
        for row in rows
    ]

    non_empty = [v for v in values if v]

    if len(non_empty) == len(set(non_empty)) and len(non_empty) > 0:
        print(
            f"{col}: UNIQUE "
            f"({len(non_empty)} non-empty values)"
        )

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)

print(f"Rows       : {len(rows)}")
print(f"Columns    : {len(columns)}")
print(f"Duplicates : {duplicates}")

print("\nIMPORTANT:")
print("No RAG packages were installed.")
print("No data was modified.")
print("This was only dataset inspection.")
print("=" * 70)
