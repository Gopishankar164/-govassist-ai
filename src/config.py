"""
Central configuration for GovAssist AI RAG engine.
All paths are relative to the project root.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_CSV_PATH = PROJECT_ROOT / "Merged_Schemes.csv"

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

PROCESSED_JSONL_PATH = PROCESSED_DIR / "schemes_processed.jsonl"
INGESTION_STATS_PATH = PROCESSED_DIR / "ingestion_stats.json"

FAISS_INDEX_PATH = INDEX_DIR / "schemes.faiss"
FAISS_METADATA_PATH = INDEX_DIR / "schemes_metadata.jsonl"
EMBEDDING_INFO_PATH = INDEX_DIR / "embedding_info.json"

# Embedding model. Chosen per project spec (Phase 7).
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# Retrieval defaults (Phase 11)
DEFAULT_TOP_K = 10
FINAL_TOP_N = 3

# Reranker (Phase 12) - set to a cross-encoder model name, or None to force
# the lightweight structured-field reranker documented in reranker.py
CROSS_ENCODER_MODEL_NAME = "BAAI/bge-reranker-base"

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Puducherry", "Chandigarh", "Andaman and Nicobar",
]

CASTE_CATEGORY_TERMS = [
    "SC", "ST", "OBC", "Scheduled Caste", "Scheduled Tribe",
    "Other Backward Class", "EWS", "Minority",
]

DOMAIN_LABELS = (
    "education",
    "agriculture",
    "business",
    "housing",
    "employment",
    "social_welfare",
    "health",
    "other",
)

QUERY_DOMAIN_KEYWORDS = {
    "education": (
        "student", "scholarship", "education", "school", "college", "university",
        "degree", "engineering", "academic", "tuition", "fellowship", "study", "admission",
        "training", "scholar",
    ),
    "agriculture": (
        "farmer", "farming", "agriculture", "crop", "tractor", "irrigation", "seed",
        "cultivation", "livestock", "horticulture", "paddy", "fertilizer", "farm",
    ),
    "business": (
        "business", "entrepreneur", "enterprise", "msme", "startup", "self employment",
        "industrial", "industry", "trade", "micro enterprise", "employer", "payroll", "epf",
        "loan", "credit", "vendor",
    ),
    "housing": (
        "housing", "house", "home", "home construction", "house construction", "shelter",
        "dwelling", "construction", "rent", "flat", "homeless", "rehabilitation",
    ),
    "employment": (
        "job", "jobs", "employment", "unemployed", "work", "placement", "salary",
        "recruitment", "skill", "vocational", "labor", "career", "training",
    ),
    "social_welfare": (
        "widow", "pension", "senior citizen", "destitute", "welfare", "support",
        "allowance", "assistance", "dependant", "orph", "social welfare", "empowerment",
    ),
    "health": (
        "health", "medical", "insurance", "hospital", "nutrition", "pregnancy",
        "wellness", "treatment", "disease", "healthcare", "doctor", "care",
    ),
}

SCHEME_DOMAIN_CATEGORIES = {
    "education": ("education & learning",),
    "agriculture": ("agriculture,rural & environment",),
    "business": ("business & entrepreneurship", "skills & employment"),
    "housing": ("housing & shelter",),
    "employment": ("skills & employment",),
    "social_welfare": ("social welfare & empowerment",),
    "health": ("health & wellness",),
}

SCHEME_DOMAIN_TERMS = {
    "education": (
        "student", "scholarship", "school", "college", "university", "tuition",
        "academic", "fellowship", "education", "course", "degree",
    ),
    "agriculture": (
        "farmer", "farming", "crop", "livestock", "irrigation", "tractor", "horticulture",
        "seed", "cultivation", "paddy", "farm",
    ),
    "business": (
        "business", "entrepreneur", "enterprise", "msme", "micro enterprise", "employer",
        "payroll", "epf", "industrial", "industry", "trade", "startup",
    ),
    "housing": (
        "housing", "house", "home construction", "house construction", "shelter",
        "dwelling", "flat", "rehabilitation",
    ),
    "employment": (
        "job", "jobs", "employment", "unemployed", "work", "placement", "salary",
        "training", "skill", "vocational", "labor",
    ),
    "social_welfare": (
        "widow", "pension", "senior citizen", "destitute", "welfare", "support",
        "allowance", "assistance", "empowerment",
    ),
    "health": (
        "health", "medical", "insurance", "hospital", "nutrition", "pregnancy",
        "wellness", "doctor", "care",
    ),
}
