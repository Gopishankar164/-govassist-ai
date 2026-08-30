from fastapi.testclient import TestClient
import pytest

from backend.main import app, get_auth_service, get_pipeline


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_auth_store(monkeypatch, tmp_path):
    """Keep authentication tests independent of the persistent local account DB."""
    monkeypatch.setenv("GOVASSIST_AUTH_DB", str(tmp_path / "auth-test.db"))
    monkeypatch.setenv("GOVASSIST_AUTH_SECRET", "test-only-signing-secret")
    get_auth_service.cache_clear()
    yield
    get_auth_service.cache_clear()


def register_user(email="student@example.com"):
    return client.post("/api/auth/register", json={
        "name": "Test Student", "email": email, "password": "secure-password-123", "confirm_password": "secure-password-123",
    })


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_profile_extracts_stated_facts():
    response = client.post("/api/profile", json={"query": "I am a female student from Tamil Nadu"})
    assert response.status_code == 200
    assert response.json()["profile"]["state"] == "Tamil Nadu"


def test_recommendation_uses_real_pipeline_and_index():
    response = client.post("/api/recommend", json={"query": "I am looking for a government housing scheme."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["recommendations"]
    first = payload["recommendations"][0]
    assert isinstance(first["similarity_score"], float)
    assert first["scheme_id"] in {record["scheme_id"] for record in get_pipeline().store.metadata}
    assert first["scheme_name"]
    assert payload["trace"][0]["retrieved_candidate_count"] > 0


def test_empty_query_is_rejected():
    response = client.post("/api/recommend", json={"query": "  "})
    assert response.status_code == 422


def test_missing_query_and_invalid_json_are_rejected():
    assert client.post("/api/recommend", json={}).status_code == 422
    assert client.post("/api/recommend", content="not-json", headers={"Content-Type": "application/json"}).status_code == 422


def test_overlong_query_is_rejected_before_pipeline_execution():
    response = client.post("/api/recommend", json={"query": "a" * 4001})
    assert response.status_code == 422


def test_registration_duplicate_and_validation():
    registered = register_user()
    assert registered.status_code == 201
    assert registered.json()["user"]["email"] == "student@example.com"
    assert registered.json()["access_token"]
    assert register_user().status_code == 409
    assert client.post("/api/auth/register", json={
        "name": "Invalid", "email": "not-an-email", "password": "secure-password-123", "confirm_password": "secure-password-123",
    }).status_code == 422
    assert client.post("/api/auth/register", json={
        "name": "Mismatch", "email": "mismatch@example.com", "password": "secure-password-123", "confirm_password": "different-password",
    }).status_code == 422


def test_login_rejects_bad_credentials_and_accepts_registered_user():
    assert client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "secure-password-123"}).status_code == 401
    register_user()
    assert client.post("/api/auth/login", json={"email": "student@example.com", "password": "wrong-password"}).status_code == 401
    response = client.post("/api/auth/login", json={"email": "student@example.com", "password": "secure-password-123"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_protected_user_and_profile_endpoints_require_and_accept_authentication():
    assert client.get("/api/auth/me").status_code == 401
    registration = register_user().json()
    headers = {"Authorization": f"Bearer {registration['access_token']}"}
    assert client.get("/api/auth/me", headers=headers).json()["user"]["name"] == "Test Student"
    saved = client.put("/api/user/profile", headers=headers, json={"state": "Tamil Nadu", "occupation": "Student", "age": "21"})
    assert saved.status_code == 200
    assert client.get("/api/user/profile", headers=headers).json()["profile"]["state"] == "Tamil Nadu"


def test_logout_invalidates_token():
    token = register_user().json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401

def test_get_scheme_details():
    # Test valid scheme
    pipeline = get_pipeline()
    first_scheme_id = pipeline.store.metadata[0]["scheme_id"]
    response = client.get(f"/api/schemes/{first_scheme_id}")
    assert response.status_code == 200
    assert response.json()["scheme_id"] == first_scheme_id
    
    # Test invalid scheme
    assert client.get("/api/schemes/does-not-exist").status_code == 404
