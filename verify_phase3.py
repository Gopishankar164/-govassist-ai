import subprocess
import time
import requests
import uuid
import sys

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    for _ in range(30):
        try:
            resp = requests.get(f"{BASE_URL}/health")
            if resp.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    return False

def run_tests():
    print("Starting server...")
    server = subprocess.Popen([".\\.venv\\Scripts\\python.exe", "-m", "uvicorn", "backend.main:app", "--port", "8000"])
    if not wait_for_server():
        print("Server failed to start")
        server.kill()
        sys.exit(1)

    print("Server is up. Testing endpoints...")
    
    # 1. Register
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = requests.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    token = resp.json().get("access_token")

    # 2. Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. GET me
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert resp.status_code == 200, f"GET me failed: {resp.text}"

    # 4. Persistence Test - Restart server
    print("Restarting server for persistence test...")
    server.terminate()
    server.wait()
    
    server = subprocess.Popen([".\\.venv\\Scripts\\python.exe", "-m", "uvicorn", "backend.main:app", "--port", "8000"])
    if not wait_for_server():
        print("Server failed to restart")
        server.kill()
        sys.exit(1)

    print("Server restarted. Checking token persistence...")
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert resp.status_code == 200, f"Persistence test failed (token invalid after restart): {resp.text}"
    print("Token is still valid after restart!")

    # 5. CORS Test
    print("Testing CORS...")
    # Allowed origin
    resp = requests.options(f"{BASE_URL}/api/auth/me", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET"
    })
    assert "http://localhost:5173" in resp.headers.get("access-control-allow-origin", ""), f"CORS allowed origin failed: {resp.headers}"
    
    # Disallowed origin
    resp = requests.options(f"{BASE_URL}/api/auth/me", headers={
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET"
    })
    assert "http://evil.com" not in resp.headers.get("access-control-allow-origin", ""), f"CORS disallowed origin failed: {resp.headers}"

    # 6. RAG Regression Test
    print("Testing RAG pipeline...")
    resp = requests.post(f"{BASE_URL}/api/recommend", json={"query": "Need scholarship for engineering student in Tamil Nadu"})
    assert resp.status_code == 200, f"RAG recommend failed: {resp.text}"
    data = resp.json()
    assert "recommendations" in data, "No recommendations key in response"
    assert len(data["recommendations"]) > 0, "No recommendations returned"

    # 7. Logout
    print("Testing Logout...")
    resp = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    assert resp.status_code == 204, f"Logout failed: {resp.text}"

    # 8. Check token is invalidated
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    assert resp.status_code == 401, f"Token still valid after logout: {resp.text}"

    print("ALL TESTS PASSED SUCCESSFULLY!")
    server.terminate()
    server.wait()

if __name__ == "__main__":
    run_tests()
