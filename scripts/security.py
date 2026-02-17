"""
Security Module
Provides input validation, sanitization, rate limiting, and API key auth.
"""

import re
import time
import hashlib
import secrets
from typing import Optional, Dict, List
from functools import wraps
from collections import defaultdict


# ─── Input Validation & Sanitization ────────────────────────

# Maximum lengths per field type
MAX_LENGTHS = {
    "prompt": 10000,
    "code": 50000,
    "query": 2000,
    "product_name": 200,
    "description": 5000,
    "contract_text": 100000,
    "default": 5000,
}

# Patterns to strip (prevent injection)
DANGEROUS_PATTERNS = [
    r"<script[^>]*>.*?</script>",    # XSS
    r"javascript:",                    # JS injection
    r"on\w+\s*=",                      # Event handlers
    r"\{\{.*?\}\}",                    # Template injection
    r"\$\{.*?\}",                      # Template literal injection
    r"<!--.*?-->",                     # HTML comments
]

# Sensitive data patterns (PII)
PII_PATTERNS = {
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b(?:\+1)?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}


def validate_input(text: str, field_type: str = "default") -> Dict:
    """
    Validate and report issues with input text.
    Returns dict with 'valid' boolean and any 'issues' found.
    """
    issues = []
    
    # Check length
    max_len = MAX_LENGTHS.get(field_type, MAX_LENGTHS["default"])
    if len(text) > max_len:
        issues.append(f"Input exceeds maximum length of {max_len} characters")
    
    # Check for empty
    if not text.strip():
        issues.append("Input is empty or whitespace-only")
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            issues.append(f"Potentially unsafe content detected")
            break
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "length": len(text),
        "field_type": field_type,
    }


def sanitize_input(text: str) -> str:
    """Remove dangerous patterns from input text."""
    sanitized = text
    for pattern in DANGEROUS_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Strip null bytes
    sanitized = sanitized.replace("\x00", "")
    
    return sanitized.strip()


def detect_pii(text: str) -> List[Dict]:
    """Detect PII in text. Returns list of findings."""
    findings = []
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            findings.append({
                "type": pii_type,
                "start": match.start(),
                "end": match.end(),
                "value": mask_value(match.group(), pii_type),
            })
    return findings


def mask_value(value: str, pii_type: str) -> str:
    """Mask a PII value for safe logging."""
    if pii_type == "email":
        parts = value.split("@")
        return f"{parts[0][:2]}***@{parts[1]}"
    elif pii_type == "credit_card":
        clean = re.sub(r"[\s-]", "", value)
        return f"****-****-****-{clean[-4:]}"
    elif pii_type == "ssn":
        return f"***-**-{value[-4:]}"
    else:
        return f"{value[:3]}***"


def redact_pii(text: str) -> str:
    """Replace PII with redaction markers."""
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f"[REDACTED-{pii_type.upper()}]", result)
    return result


# ─── Rate Limiting ───────────────────────────────────────────

class RateLimiter:
    """
    In-memory sliding-window rate limiter.
    
    Usage:
        limiter = RateLimiter(max_requests=60, window_seconds=60)
        if limiter.is_allowed("user_123"):
            process_request()
        else:
            return "Rate limit exceeded"
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request from client_id is allowed."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old entries
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > cutoff
        ]

        # Check limit
        if len(self._requests[client_id]) >= self.max_requests:
            return False

        # Record request
        self._requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for a client."""
        now = time.time()
        cutoff = now - self.window_seconds
        recent = [t for t in self._requests[client_id] if t > cutoff]
        return max(0, self.max_requests - len(recent))

    def reset(self, client_id: Optional[str] = None):
        """Reset rate limits."""
        if client_id:
            self._requests.pop(client_id, None)
        else:
            self._requests.clear()


# ─── API Key Management ─────────────────────────────────────

class APIKeyManager:
    """
    Simple API key management for authentication.
    
    Usage:
        manager = APIKeyManager()
        key = manager.generate_key("admin")
        assert manager.validate_key(key) == True
    """

    def __init__(self):
        self._keys: Dict[str, Dict] = {}

    def generate_key(self, name: str, permissions: List[str] = None) -> str:
        """Generate a new API key."""
        key = f"gai_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        self._keys[key_hash] = {
            "name": name,
            "permissions": permissions or ["read", "write"],
            "created_at": time.time(),
            "active": True,
        }
        
        return key

    def validate_key(self, key: str) -> bool:
        """Validate an API key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        entry = self._keys.get(key_hash)
        return entry is not None and entry.get("active", False)

    def get_key_info(self, key: str) -> Optional[Dict]:
        """Get metadata for an API key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self._keys.get(key_hash)

    def revoke_key(self, key: str) -> bool:
        """Revoke an API key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        if key_hash in self._keys:
            self._keys[key_hash]["active"] = False
            return True
        return False


# ─── FastAPI Security Dependencies ──────────────────────────
# These can be used as FastAPI Depends() parameters

_rate_limiter = RateLimiter(max_requests=60, window_seconds=60)
_key_manager = APIKeyManager()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter."""
    return _rate_limiter


def get_key_manager() -> APIKeyManager:
    """Get the global API key manager."""
    return _key_manager
