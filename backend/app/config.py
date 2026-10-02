import os
import logging
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "GovAssist AI"
    APP_VERSION: str = "2.5.0"
    DEBUG: bool = True
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/govassist_db")
    MONGODB_DB_NAME: str = "govassist_db"
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    FAISS_INDEX_PATH: str = "backend/data/faiss_index"
    SAMPLE_SCHEMES_PATH: str = "backend/data/sample_schemes.json"
    DEFAULT_LANGUAGE: str = "en"
    RATE_LIMIT_PER_MINUTE: int = 60

settings = Settings()

# Structured Logging Setup
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("GovAssistAI")
logging.getLogger("pymongo").setLevel(logging.WARNING)

