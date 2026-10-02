import time
import io
import pypdf
from typing import Dict, Any
from backend.app.rag.pipeline import rag_pipeline
from backend.app.database import db
from backend.app.config import settings, logger

class PDFIngestionEngine:
    """
    Admin Pipeline for PDF Ingestion:
    PDF Upload ➔ PyPDF Text Extraction ➔ Text Chunking ➔ BGE Embeddings ➔ FAISS Indexing ➔ MongoDB Persistence
    """
    @staticmethod
    def process_pdf(file_contents: bytes, filename: str) -> Dict[str, Any]:
        text_content = ""
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_contents))
            for page_num, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text_content += f"\n--- Page {page_num+1} ---\n" + extracted
        except Exception as e:
            logger.error(f"Error reading PDF file {filename}: {e}")
            raise RuntimeError(f"PyPDF extraction error: {e}")

        if not text_content.strip():
            text_content = f"Official Gazette Document: {filename}"

        chunks = rag_pipeline.splitter.split_text(text_content)
        
        clean_title = filename.replace(".pdf", "").replace("_", " ").title()
        scheme_id = f"pdf_{time.time_ns()}"

        scheme_document = {
            "id": scheme_id,
            "scheme_id": scheme_id,
            "name": clean_title,
            "scheme_name": clean_title,
            "category": "Official PDF Gazette",
            "target_audience": "General Citizens",
            "description": text_content[:600] + "..." if len(text_content) > 600 else text_content,
            "eligibility": {
                "min_age": 0,
                "max_age": 100,
                "max_income": 2000000,
                "occupations": ["All"],
                "gender": "All"
            },
            "benefits": f"Directly extracted from uploaded official gazette '{filename}'. Total text length: {len(text_content)} characters.",
            "documents_required": ["Aadhaar Card", "Official Gazette Certificate", "Application Form"],
            "required_documents": ["Aadhaar Card", "Official Gazette Certificate", "Application Form"],
            "application_url": "#",
            "official_application_url": "#"
        }

        # Store in MongoDB schemes and uploaded_pdfs collections
        db.insert_one("schemes", scheme_document)
        db.insert_one("uploaded_pdfs", {
            "filename": filename,
            "length": len(text_content),
            "chunk_count": len(chunks),
            "scheme_id": scheme_id,
            "timestamp": time.time()
        })

        # Dynamically reload FAISS Index with new document vector
        rag_pipeline.reload_index()
        logger.info(f"Ingested PDF gazette '{filename}' ({len(chunks)} chunks). FAISS vector index updated.")

        return {
            "status": "success",
            "scheme_id": scheme_id,
            "filename": filename,
            "extracted_length": len(text_content),
            "chunks_created": len(chunks),
            "message": f"PDF '{filename}' processed via BGE embeddings & indexed into FAISS."
        }

pdf_ingest_engine = PDFIngestionEngine()
