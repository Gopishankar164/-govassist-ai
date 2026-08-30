"""SQLite-backed authentication utilities, isolated from the RAG data store."""
import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
import secrets
import sqlite3
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_TTL_HOURS = 12


class AuthenticationError(Exception):
    """Raised when a credential or bearer token cannot be authenticated."""


class DuplicateEmailError(Exception):
    """Raised when an email is already registered."""


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _normalise_email(email: str) -> str:
    return email.strip().lower()


def _valid_email(email: str) -> bool:
    local, separator, domain = email.partition("@")
    return bool(separator and local and "." in domain and not email.startswith("@"))


class AuthService:
    """Manages users, sessions, and persisted user profiles in a separate DB."""

    def __init__(self, database_path: Path | None = None, secret: str | None = None) -> None:
        configured_path = os.getenv("GOVASSIST_AUTH_DB")
        self.database_path = database_path or Path(configured_path or PROJECT_ROOT / "data" / "auth.db")
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        # A deployment should set GOVASSIST_AUTH_SECRET. A generated process-local
        # secret keeps local development secure without hardcoding a secret.
        self.secret = (secret or os.getenv("GOVASSIST_AUTH_SECRET") or secrets.token_urlsafe(48)).encode("utf-8")
        self._initialise()

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self) -> None:
        with self._connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    state TEXT,
                    occupation TEXT,
                    education TEXT,
                    gender TEXT,
                    income TEXT,
                    caste_category TEXT,
                    age TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
        return f"scrypt$16384$8$1${_encode(salt)}${_encode(derived)}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, n, r, p, salt, expected = stored_hash.split("$")
            if algorithm != "scrypt":
                return False
            actual = hashlib.scrypt(password.encode("utf-8"), salt=_decode(salt), n=int(n), r=int(r), p=int(p), dklen=32)
            return hmac.compare_digest(actual, _decode(expected))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _public_user(row: sqlite3.Row) -> dict[str, str]:
        return {"id": row["id"], "name": row["name"], "email": row["email"]}

    def register(self, name: str, email: str, password: str, confirm_password: str) -> dict[str, Any]:
        name, email = name.strip(), _normalise_email(email)
        if not name:
            raise ValueError("name is required")
        if not _valid_email(email):
            raise ValueError("a valid email address is required")
        if len(password) < 8:
            raise ValueError("password must be at least 8 characters long")
        if password != confirm_password:
            raise ValueError("password confirmation does not match")
        user_id, now = str(uuid4()), datetime.now(UTC).isoformat()
        try:
            with self._connection() as connection:
                connection.execute(
                    "INSERT INTO users (id, name, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, email, self._hash_password(password), now),
                )
                row = connection.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
        except sqlite3.IntegrityError as exc:
            raise DuplicateEmailError("an account with this email already exists") from exc
        return self._session_for(row)

    def login(self, email: str, password: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (_normalise_email(email),)).fetchone()
        if row is None or not self._verify_password(password, row["password_hash"]):
            raise AuthenticationError("incorrect email or password")
        return self._session_for(row)

    def _session_for(self, user: sqlite3.Row) -> dict[str, Any]:
        token_id = str(uuid4())
        expires_at = datetime.now(UTC) + timedelta(hours=TOKEN_TTL_HOURS)
        payload = {"sub": user["id"], "jti": token_id, "exp": int(expires_at.timestamp())}
        encoded_payload = _encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signature = _encode(hmac.new(self.secret, encoded_payload.encode("ascii"), hashlib.sha256).digest())
        with self._connection() as connection:
            connection.execute("INSERT INTO sessions (token_id, user_id, expires_at) VALUES (?, ?, ?)", (token_id, user["id"], expires_at.isoformat()))
        return {"access_token": f"{encoded_payload}.{signature}", "token_type": "bearer", "expires_at": expires_at.isoformat(), "user": self._public_user(user)}

    def authenticated_user(self, token: str) -> dict[str, str]:
        try:
            encoded_payload, signature = token.split(".", 1)
            expected_signature = hmac.new(self.secret, encoded_payload.encode("ascii"), hashlib.sha256).digest()
            if not hmac.compare_digest(_decode(signature), expected_signature):
                raise AuthenticationError("invalid authentication token")
            payload = json.loads(_decode(encoded_payload))
            if int(payload["exp"]) <= int(datetime.now(UTC).timestamp()):
                raise AuthenticationError("authentication token has expired")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AuthenticationError("invalid authentication token") from exc
        with self._connection() as connection:
            row = connection.execute(
                "SELECT users.id, users.name, users.email FROM sessions JOIN users ON users.id = sessions.user_id "
                "WHERE sessions.token_id = ? AND sessions.user_id = ? AND sessions.revoked_at IS NULL AND sessions.expires_at > ?",
                (payload["jti"], payload["sub"], datetime.now(UTC).isoformat()),
            ).fetchone()
        if row is None:
            raise AuthenticationError("authentication token is no longer active")
        return self._public_user(row)

    def logout(self, token: str) -> None:
        user = self.authenticated_user(token)
        payload = json.loads(_decode(token.split(".", 1)[0]))
        with self._connection() as connection:
            connection.execute("UPDATE sessions SET revoked_at = ? WHERE token_id = ? AND user_id = ?", (datetime.now(UTC).isoformat(), payload["jti"], user["id"]))

    def get_profile(self, user_id: str) -> dict[str, str | None]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)).fetchone()
        fields = ("state", "occupation", "education", "gender", "income", "caste_category", "age")
        return {field: row[field] if row else None for field in fields}

    def save_profile(self, user_id: str, profile: dict[str, str | None]) -> dict[str, str | None]:
        fields = ("state", "occupation", "education", "gender", "income", "caste_category", "age")
        values = [str(profile.get(field, "")).strip() or None for field in fields]
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO user_profiles (user_id, state, occupation, education, gender, income, caste_category, age, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET state=excluded.state, occupation=excluded.occupation, education=excluded.education, "
                "gender=excluded.gender, income=excluded.income, caste_category=excluded.caste_category, age=excluded.age, updated_at=excluded.updated_at",
                [user_id, *values, datetime.now(UTC).isoformat()],
            )
        return self.get_profile(user_id)
