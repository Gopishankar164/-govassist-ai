"""HTTP API that delegates recommendations to the existing RAG pipeline."""
from functools import lru_cache
import os
from typing import Any

from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from src.pipeline import GovAssistPipeline
from src.profile import extract_profile
from backend.auth import AuthService, AuthenticationError, DuplicateEmailError
from backend.memory import ConversationStore


class RecommendationRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Natural-language description of the user's need and profile (up to 4,000 characters).",
    )
    state_filter: str | None = Field(default=None, description="Optional strict filter for state")
    category_filter: str | None = Field(default=None, description="Optional strict filter for category")

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("query must not be empty")
        return value.strip()


class ProfileRequest(RecommendationRequest):
    pass


class ChatRequest(RecommendationRequest):
    conversation_id: str | None = Field(default=None, description="The ID of the conversation if continuing an existing one.")

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=256)
    confirm_password: str = Field(..., min_length=1, max_length=256)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=254)
    password: str = Field(..., min_length=1, max_length=256)


class UserProfileRequest(BaseModel):
    state: str | None = Field(default=None, max_length=100)
    occupation: str | None = Field(default=None, max_length=120)
    education: str | None = Field(default=None, max_length=120)
    gender: str | None = Field(default=None, max_length=50)
    income: str | None = Field(default=None, max_length=100)
    caste_category: str | None = Field(default=None, max_length=100)
    age: str | None = Field(default=None, max_length=20)


@lru_cache(maxsize=1)
def get_pipeline() -> GovAssistPipeline:
    """Load the existing local BGE model and persisted FAISS index once."""
    return GovAssistPipeline()


@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    """Load the small, separate SQLite authentication store."""
    return AuthService()

@lru_cache(maxsize=1)
def get_memory_store() -> ConversationStore:
    """Load the SQLite conversation memory store."""
    return ConversationStore()


def _bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="authentication required")
    return authorization.removeprefix("Bearer ").strip()


def _authenticated_user(authorization: str | None = Header(default=None)) -> dict[str, str]:
    try:
        return get_auth_service().authenticated_user(_bearer_token(authorization))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="invalid or expired authentication token") from exc


def _allowed_origins() -> list[str]:
    configured = os.getenv("GOVASSIST_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]


app = FastAPI(title="GovAssist AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe; deliberately does not trigger the expensive model load."""
    return {"status": "ok", "service": "govassist-api"}


@app.post("/api/profile")
def profile(request: ProfileRequest) -> dict[str, Any]:
    return {"query": request.query, "profile": extract_profile(request.query)}


@app.post("/api/auth/register", status_code=201)
def register(request: RegisterRequest) -> dict[str, Any]:
    try:
        return get_auth_service().register(request.name, request.email, request.password, request.confirm_password)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict[str, Any]:
    try:
        return get_auth_service().login(request.email, request.password)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="incorrect email or password") from exc


@app.post("/api/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None)) -> None:
    try:
        get_auth_service().logout(_bearer_token(authorization))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="invalid or expired authentication token") from exc


@app.get("/api/auth/me")
def current_user(user: dict[str, str] = Depends(_authenticated_user)) -> dict[str, dict[str, str]]:
    return {"user": user}


@app.get("/api/user/profile")
def user_profile(user: dict[str, str] = Depends(_authenticated_user)) -> dict[str, Any]:
    return {"user": user, "profile": get_auth_service().get_profile(user["id"])}


@app.put("/api/user/profile")
def save_user_profile(request: UserProfileRequest, user: dict[str, str] = Depends(_authenticated_user)) -> dict[str, Any]:
    return {"user": user, "profile": get_auth_service().save_profile(user["id"], request.model_dump())}


@app.post("/api/recommend")
def recommend(request: RecommendationRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    base_profile = None
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        try:
            user = get_auth_service().authenticated_user(_bearer_token(authorization))
            user_id = user["id"]
            base_profile = get_auth_service().get_profile(user_id)
        except AuthenticationError:
            pass
            
    try:
        result = get_pipeline().recommend(request.query, base_profile=base_profile, state_filter=request.state_filter, category_filter=request.category_filter)
        if user_id and result["profile"]:
            get_auth_service().save_profile(user_id, result["profile"])
    except (FileNotFoundError, OSError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=f"RAG pipeline unavailable: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {exc}") from exc

    recommendations = []
    for item in result["recommendations"]:
        scheme = item["scheme"]
        recommendations.append({
            "scheme_id": item["scheme_id"],
            "scheme_name": item["scheme_name"],
            "similarity_score": item["similarity_score"],
            "eligibility_status": item["eligibility_status"],
            "why_recommended": "; ".join(item["eligibility_evidence"]) or "Returned by semantic retrieval.",
            "missing_information": item.get("missing_information", []),
            "benefits": scheme.get("benefits"),
            "description": scheme.get("description"),
            "eligibility": scheme.get("eligibility_text"),
            "application": scheme.get("application_process"),
            "documents": scheme.get("documents"),
            "category": scheme.get("category"),
            "level": scheme.get("level"),
            "source_url": scheme.get("official_url"),
        })
    return {
        "query": result["user_query"],
        "what_i_understood": result["profile"],
        "recommendations": recommendations,
        "grounded_answer": result["answer"],
        "disclaimer": "This information is based on the verified dataset. Please verify all details on the official government portals.",
        "trace": [{
            "rewritten_query": result["rewritten_query"],
            "retrieval_latency_ms": result["retrieval_latency_ms"],
            "retrieved_candidate_count": len(result["retrieved_schemes"]),
        }],
    }

@app.post("/api/chat")
def chat(request: ChatRequest, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        try:
            user = get_auth_service().authenticated_user(_bearer_token(authorization))
            user_id = user["id"]
        except AuthenticationError:
            pass

    mem = get_memory_store()
    conv_id = request.conversation_id
    
    if conv_id:
        conv = mem.get_conversation(conv_id)
        if not conv:
            conv_id = mem.create_conversation(user_id)
            conv = mem.get_conversation(conv_id)
    else:
        conv_id = mem.create_conversation(user_id)
        conv = mem.get_conversation(conv_id)
        
    # Get base profile and contextual recommendations
    base_profile = conv["profile"]
    context = conv["retrieval_context"]
    
    try:
        pipeline = get_pipeline()
        
        # We need to extract the new profile from the current query and merge with base
        from src.profile import extract_profile, merge_profiles
        new_extracted = extract_profile(request.query)
        current_profile = merge_profiles(base_profile, new_extracted)
        
        result = pipeline.handle_conversation_turn(request.query, current_profile, context)
        
        if user_id and result.get("profile"):
            get_auth_service().save_profile(user_id, result["profile"])
            
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc

    # Format recommendations for frontend
    recommendations = []
    for item in result["recommendations"]:
        if "scheme" in item:
            scheme = item["scheme"]
        else:
            # If it's a follow-up, the recommendations are already formatted from previous turn!
            scheme = item
            
        recommendations.append({
            "scheme_id": item.get("scheme_id", scheme.get("scheme_id")),
            "scheme_name": item.get("scheme_name", scheme.get("scheme_name")),
            "similarity_score": item.get("similarity_score", 1.0),
            "eligibility_status": item.get("eligibility_status", "unknown"),
            "why_recommended": item.get("why_recommended", "; ".join(item.get("eligibility_evidence", [])) or "Returned by semantic retrieval."),
            "missing_information": item.get("missing_information", []),
            "benefits": scheme.get("benefits"),
            "description": scheme.get("description"),
            "eligibility": scheme.get("eligibility") or scheme.get("eligibility_text"),
            "application": scheme.get("application") or scheme.get("application_process"),
            "documents": scheme.get("documents"),
            "category": scheme.get("category"),
            "level": scheme.get("level"),
            "source_url": scheme.get("source_url") or scheme.get("official_url"),
        })

    # Update memory
    new_messages = conv["messages"] + [{"role": "user", "content": request.query}, {"role": "assistant", "content": result["answer"]}]
    # We only update context if it wasn't a follow-up
    new_context = recommendations if result.get("query_domain") != "followup" else context
    
    mem.update_conversation(conv_id, result["profile"], new_messages, new_context)

    return {
        "conversation_id": conv_id,
        "query": result["user_query"],
        "what_i_understood": result["profile"],
        "recommendations": recommendations,
        "grounded_answer": result["answer"],
        "disclaimer": "This information is based on the verified dataset. Please verify all details on the official government portals.",
        "trace": [{
            "rewritten_query": result.get("rewritten_query", ""),
            "retrieval_latency_ms": result.get("retrieval_latency_ms", 0),
            "retrieved_candidate_count": len(result.get("retrieved_schemes", [])),
        }],
    }

@app.get("/api/schemes/{scheme_id}")
def get_scheme_details(scheme_id: str) -> dict[str, Any]:
    try:
        pipeline = get_pipeline()
        for metadata in pipeline.store.metadata:
            if metadata["scheme_id"] == scheme_id:
                s = metadata
                return {
                    "scheme_id": scheme_id,
                    "scheme_name": s.get("scheme_name", "Not available in verified data."),
                    "ministry_department": s.get("ministry_department", "Not available in verified data."),
                    "description": s.get("description", "Not available in verified data."),
                    "benefits": s.get("benefits", "Not available in verified data."),
                    "eligibility": s.get("eligibility_text", "Not available in verified data."),
                    "application_process": s.get("application_process", "Not available in verified data."),
                    "required_documents": s.get("documents", "Not available in verified data."),
                    "state": s.get("state", "Not available in verified data."),
                    "category": s.get("category", "Not available in verified data."),
                    "official_url": s.get("official_url", "Not available in verified data."),
                    "source": s.get("source_provenance", "Not available in verified data.")
                }
        raise HTTPException(status_code=404, detail="Scheme not found in verified dataset.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch scheme: {exc}")
