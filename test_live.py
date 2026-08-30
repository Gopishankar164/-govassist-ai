import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api"
RESULTS = {}
CONVERSATION_LOG = []
MEMORY_LOG = []

def run_tests():
    global RESULTS, CONVERSATION_LOG, MEMORY_LOG
    
    # 1. Test Auth
    email = f"test_{int(time.time())}@example.com"
    pw = "password123"
    try:
        # Register
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": pw,
            "confirm_password": pw
        })
        RESULTS["Signup"] = "PASS" if r.status_code == 201 else f"FAIL ({r.status_code})"
        token = r.json().get("access_token")
        
        # Logout
        r_out = requests.post(f"{BASE_URL}/auth/logout", headers={"Authorization": f"Bearer {token}"})
        RESULTS["Logout"] = "PASS" if r_out.status_code == 204 else f"FAIL ({r_out.status_code})"
        
        # Login
        r_in = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": pw})
        RESULTS["Login"] = "PASS" if r_in.status_code == 200 else f"FAIL ({r_in.status_code})"
        token = r_in.json().get("access_token")
    except Exception as e:
        RESULTS["Signup"] = f"FAIL Exception: {e}"
        RESULTS["Logout"] = "FAIL"
        RESULTS["Login"] = "FAIL"
        token = None

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 2. Conversation 1
    turns = [
        "I am 25 years old.",
        "I am a farmer.",
        "I live in Tamil Nadu.",
        "I need a government loan.",
        "What schemes can I get?",
        "Which one is best for me?",
        "What are the eligibility requirements?",
        "What documents do I need?",
        "How much financial assistance can I get?",
        "Give me the official application link."
    ]
    
    conv_id = None
    turn_latency = []
    
    for i, query in enumerate(turns):
        payload = {"query": query}
        if conv_id:
            payload["conversation_id"] = conv_id
            
        start = time.time()
        r = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)
        lat = (time.time() - start) * 1000
        turn_latency.append(lat)
        
        if r.status_code == 200:
            data = r.json()
            conv_id = data["conversation_id"]
            CONVERSATION_LOG.append({
                "turn": i + 1,
                "user": query,
                "assistant": data["grounded_answer"],
                "recommendation_count": len(data["recommendations"])
            })
            MEMORY_LOG.append({
                "turn": i + 1,
                "user": query,
                "profile_state": data["what_i_understood"]
            })
            
            # Check profile correctness
            if i == 0 and data["what_i_understood"].get("age") == 25:
                pass
            if i == 1 and data["what_i_understood"].get("occupation") == "farmer":
                pass
            if i == 2 and data["what_i_understood"].get("state") == "Tamil Nadu":
                pass
                
        else:
            CONVERSATION_LOG.append({"turn": i+1, "error": r.text})

    RESULTS["average_latency_ms"] = sum(turn_latency) / len(turn_latency) if turn_latency else 0
    turn_latency.sort()
    RESULTS["p95_latency_ms"] = turn_latency[int(len(turn_latency)*0.95)] if turn_latency else 0

    # 3. Conversation 2 (Isolation)
    r2 = requests.post(f"{BASE_URL}/chat", json={"query": "I am a student from Tamil Nadu."}, headers=headers)
    if r2.status_code == 200:
        data2 = r2.json()
        prof2 = data2["what_i_understood"]
        if "student" in str(prof2.get("education", "")) and prof2.get("age") != 25 and prof2.get("occupation") != "farmer":
            RESULTS["Conversation_Isolation"] = "PASS"
        else:
            RESULTS["Conversation_Isolation"] = f"FAIL (Got {prof2})"
    else:
        RESULTS["Conversation_Isolation"] = "FAIL"

    # Write files
    with open("evaluation/live_demo/live_test_results.json", "w") as f:
        json.dump(RESULTS, f, indent=2)
        
    with open("evaluation/live_demo/live_conversation.json", "w") as f:
        json.dump(CONVERSATION_LOG, f, indent=2)
        
    with open("evaluation/live_demo/conversation_memory_results.json", "w") as f:
        json.dump(MEMORY_LOG, f, indent=2)

if __name__ == "__main__":
    time.sleep(2) # Give backend time to spin up
    run_tests()
