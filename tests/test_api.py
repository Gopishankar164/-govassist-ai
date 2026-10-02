from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "GovAssist AI" in data["app"]

def test_schemes_list_endpoint():
    response = client.get("/api/v1/schemes")
    assert response.status_code == 200
    assert "schemes" in response.json()

def test_agent_chat_endpoint():
    payload = {
        "session_id": "test_api_sess",
        "query": "I am an engineering student looking for scholarships",
        "language": "en",
        "user_profile": {
            "age": 22,
            "income": 150000,
            "state": "Tamil Nadu",
            "occupation": "Student",
            "gender": "Female"
        }
    }
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "workflow_trace" in res_data
    assert "eligible_schemes" in res_data
    assert "metrics" in res_data
    assert res_data["metrics"]["precision"] >= 0.0
