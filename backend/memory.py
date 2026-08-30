import json
import sqlite3
import os
from pathlib import Path
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class ConversationStore:
    def __init__(self, database_path: Optional[Path] = None):
        configured_path = os.getenv("GOVASSIST_AUTH_DB")
        self.database_path = database_path or Path(configured_path or PROJECT_ROOT / "data" / "auth.db")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self) -> None:
        with self._connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    profile TEXT NOT NULL,
                    messages TEXT NOT NULL,
                    retrieval_context TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

    def create_conversation(self, user_id: Optional[str] = None) -> str:
        conv_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO conversations (id, user_id, profile, messages, retrieval_context, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (conv_id, user_id, "{}", "[]", "[]", now, now)
            )
        return conv_id

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        
        if not row:
            return None
            
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "profile": json.loads(row["profile"]),
            "messages": json.loads(row["messages"]),
            "retrieval_context": json.loads(row["retrieval_context"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }

    def update_conversation(self, conv_id: str, profile: Dict[str, Any], messages: List[Dict[str, Any]], retrieval_context: List[Dict[str, Any]]) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connection() as connection:
            connection.execute(
                "UPDATE conversations SET profile = ?, messages = ?, retrieval_context = ?, updated_at = ? WHERE id = ?",
                (json.dumps(profile), json.dumps(messages), json.dumps(retrieval_context), now, conv_id)
            )
