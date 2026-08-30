import sys
import os
import requests
import json
from pathlib import Path

# Assumes backend is running locally for the API tests.
BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("=== PHASE 13: END TO END TEST ===")
    
    # 1. Register a user.
    email = "testuser_e2e_01@example.com"
    password = "SecurePassword123"
    print(f"\nRegistering user {email}...")
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "E2E Tester",
            "email": email,
            "password": password,
            "confirm_password": password
        })
        if resp.status_code == 409:
            print("User already exists, proceeding to login.")
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": email,
                "password": password
            })
    except requests.exceptions.ConnectionError:
        print("Backend server is not running at 127.0.0.1:8000. Skipping E2E network test.")
        return

    resp.raise_for_status()
    data = resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Login successful. Token acquired.")
    
    # 3. Provide profile naturally.
    print("\nSending Query 1 (State & Occupation): 'I am a student from Tamil Nadu.'")
    resp = requests.post(f"{BASE_URL}/api/recommend", json={"query": "I am a student from Tamil Nadu."}, headers=headers)
    resp.raise_for_status()
    data1 = resp.json()
    print("Understood Profile:", data1["what_i_understood"])
    
    print("\nSending Query 2 (Income update): 'My family income is 2.5 lakh.'")
    resp = requests.post(f"{BASE_URL}/api/recommend", json={"query": "My family income is 250000."}, headers=headers)
    resp.raise_for_status()
    data2 = resp.json()
    print("Understood Profile:", data2["what_i_understood"])
    
    print("\nSending Query 3 (Income correction): 'Actually my income is 2 lakh.'")
    resp = requests.post(f"{BASE_URL}/api/recommend", json={"query": "Actually my income is 200000."}, headers=headers)
    resp.raise_for_status()
    data3 = resp.json()
    print("Understood Profile:", data3["what_i_understood"])
    
    # Verify memory
    assert data3["what_i_understood"].get("state") == "Tamil Nadu"
    assert data3["what_i_understood"].get("occupation") == "student"
    assert data3["what_i_understood"].get("income") == 200000
    print("\n[+] CONVERSATIONAL MEMORY VERIFIED: Profile retained and updated correctly.")
    
    print("\nChecking scheme details retrieval...")
    if data3["recommendations"]:
        first_scheme_id = data3["recommendations"][0]["scheme_id"]
        scheme_resp = requests.get(f"{BASE_URL}/api/schemes/{first_scheme_id}")
        scheme_resp.raise_for_status()
        print(f"Details fetched for scheme {first_scheme_id}: {scheme_resp.json()['scheme_name']}")
    else:
        print("No recommendations returned to test scheme details endpoint.")
        
    print("\nLogging out...")
    resp = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    resp.raise_for_status()
    print("Logged out successfully.")
    
    print("\nVerifying protected endpoint rejection...")
    resp = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if resp.status_code == 401:
        print("[+] PROTECTED ENDPOINT REJECTION VERIFIED (401 returned)")
    else:
        print(f"[-] FAILED: Expected 401, got {resp.status_code}")

if __name__ == "__main__":
    run_test()
