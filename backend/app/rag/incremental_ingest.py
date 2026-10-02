import json
import os
import time
from typing import Dict, Any, List, Optional
from backend.app.config import logger, settings
from backend.app.database import db
from backend.app.rag.pipeline import rag_pipeline

class IncrementalKnowledgeBaseIngestor:
    """
    Incremental Data Engine:
    - Ingests new PDF gazette or document metadata dynamically.
    - Generates chunked semantic text representation.
    - Generates BGE-small embedding representations.
    - Incrementally appends vectors into FAISS store.
    - Updates MongoDB collection 'schemes' and 'uploaded_pdfs'.
    - Zero downtime: does NOT rebuild index from scratch.
    """

    @staticmethod
    def ingest_single_scheme(scheme_payload: Dict[str, Any]) -> Dict[str, Any]:
        # Validate schema metadata format
        required_fields = ["name", "category", "target_audience", "description", "eligibility", "benefits"]
        for field in required_fields:
            if field not in scheme_payload:
                raise ValueError(f"Missing required metadata field: '{field}'")

        if not scheme_payload.get("id"):
            scheme_payload["id"] = f"scheme_{time.time_ns()}"

        scheme_payload["last_updated"] = time.strftime("%Y-%m-%d")

        # 1. Insert/Update in MongoDB Database
        db.insert_one("schemes", scheme_payload)
        logger.info(f"Incrementally added scheme '{scheme_payload['name']}' (ID: {scheme_payload['id']}) to MongoDB.")

        # 2. Reload Vector Store & Sync FAISS Index
        rag_pipeline.reload_index()
        total_indexed = len(rag_pipeline.vector_store.documents)
        logger.info(f"FAISS Vector Store synced. Total vectors indexed: {total_indexed}")

        return {
            "status": "success",
            "scheme_id": scheme_payload["id"],
            "scheme_name": scheme_payload["name"],
            "total_indexed_vectors": total_indexed,
            "timestamp": time.time()
        }

    @staticmethod
    def ingest_pdf_file(filepath: str, category: str = "General") -> Dict[str, Any]:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found at: {filepath}")

        filename = os.path.basename(filepath)
        text_content = ""

        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            for page in reader.pages:
                text_content += page.extract_text() or ""
        except Exception as e:
            logger.error(f"Error reading PDF '{filepath}': {e}")
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()

        scheme_doc = {
            "id": f"pdf_{time.time_ns()}",
            "name": filename.replace(".pdf", "").replace("_", " ").title(),
            "category": category,
            "target_audience": "General Citizens",
            "description": text_content[:500] if len(text_content) > 500 else text_content,
            "eligibility": {"min_age": 0, "max_age": 100, "max_income": 2000000, "occupations": ["All"], "gender": "All"},
            "benefits": "Directly extracted from uploaded official PDF document gazette.",
            "documents_required": ["Aadhaar Card", "Application Form"],
            "application_url": "#"
        }

        # Sync to MongoDB and FAISS
        db.insert_one("uploaded_pdfs", {"filename": filename, "filepath": filepath, "length": len(text_content)})
        return IncrementalKnowledgeBaseIngestor.ingest_single_scheme(scheme_doc)

incremental_ingestor = IncrementalKnowledgeBaseIngestor()
