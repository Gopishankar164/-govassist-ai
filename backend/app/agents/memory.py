import time
from typing import Dict, Any, List, Optional
from backend.app.database import db
from backend.app.config import logger

class MemoryAgent:
    """
    Independent Memory Agent module:
    - Reads session history and citizen demographic memory from MongoDB 'conversation_memory'
    - Merges current request profile with stored profile
    - Persists turn-by-turn chat history
    """
    def get_session_memory(self, session_id: str) -> Dict[str, Any]:
        mem_doc = db.find_one("conversation_memory", {"session_id": session_id})
        if mem_doc:
            return {
                "profile": mem_doc.get("profile", {}),
                "history": mem_doc.get("history", [])
            }
        return {
            "profile": {
                "age": None,
                "income": None,
                "occupation": None,
                "state": "Tamil Nadu",
                "gender": None,
                "education": None,
                "category": None,
                "caste": None
            },
            "history": []
        }

    def merge_profile(self, session_id: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
        existing = self.get_session_memory(session_id)
        saved_profile = existing["profile"]
        merged = dict(saved_profile)

        for k, v in current_profile.items():
            if v is not None and v != "":
                merged[k] = v

        return merged

    def record_turn(self, session_id: str, query: str, profile: Dict[str, Any], assistant_response: str):
        existing = self.get_session_memory(session_id)
        history = existing.get("history", [])

        history.append({
            "role": "user",
            "query": query,
            "timestamp": time.time()
        })
        history.append({
            "role": "assistant",
            "response": assistant_response[:300] + "...",
            "timestamp": time.time()
        })

        db.update_one(
            "conversation_memory",
            {"session_id": session_id},
            {
                "session_id": session_id,
                "profile": profile,
                "history": history,
                "last_updated": time.time()
            }
        )
        # If document didn't exist, insert one
        if not db.find_one("conversation_memory", {"session_id": session_id}):
            db.insert_one("conversation_memory", {
                "session_id": session_id,
                "profile": profile,
                "history": history
            })

memory_agent = MemoryAgent()
