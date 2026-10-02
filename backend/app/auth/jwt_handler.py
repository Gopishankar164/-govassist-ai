import time
import jwt
from typing import Dict, Any, Optional
from passlib.context import CryptContext

SECRET_KEY = "govassist_ai_super_secret_jwt_key_production_grade"
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 86400 * 7 # 7 Days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTAuthHandler:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_access_token(cls, payload: Dict[str, Any], expires_in: int = TOKEN_EXPIRE_SECONDS) -> str:
        to_encode = payload.copy()
        to_encode.update({"exp": int(time.time()) + expires_in, "iat": int(time.time())})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_access_token(cls, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

auth_handler = JWTAuthHandler()
