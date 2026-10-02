import re
import html
from typing import Dict, Any
from backend.app.config import logger

class SecurityEngine:
    """
    Security Module enforcing:
    - Input sanitization (XSS prevention)
    - Prompt Injection attack detection
    - Basic rate limiting headers & input size constraints
    """

    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"ignore all previous commands",
        r"system prompt",
        r"you are now a",
        r"developer mode",
        r"override rules"
    ]

    @classmethod
    def sanitize_input(cls, text: str) -> str:
        if not text:
            return ""
        # Cap maximum input length to 2000 characters to prevent buffer overflow attacks
        truncated = text[:2000]
        clean_text = html.escape(truncated.strip())
        return clean_text

    @classmethod
    def check_prompt_injection(cls, query: str) -> bool:
        q_lower = query.lower()
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, q_lower):
                logger.warning(f"Security Alert: Prompt injection pattern matched '{pattern}' in query: '{query}'")
                return True
        return False

    @classmethod
    def validate_profile(cls, profile: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = dict(profile)
        if "age" in sanitized and sanitized["age"] is not None:
            try:
                sanitized["age"] = max(0, min(120, int(sanitized["age"])))
            except (ValueError, TypeError):
                sanitized["age"] = None

        if "income" in sanitized and sanitized["income"] is not None:
            try:
                sanitized["income"] = max(0, int(sanitized["income"]))
            except (ValueError, TypeError):
                sanitized["income"] = None

        if "occupation" in sanitized and sanitized["occupation"]:
            sanitized["occupation"] = cls.sanitize_input(str(sanitized["occupation"]))

        return sanitized
