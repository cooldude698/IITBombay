"""
VERIACT — Cryptographic HMAC Execution Tokens (Anti-TOCTOU & Tamper-Proofing)
"""
import hmac
import hashlib
import time
import json
from typing import Dict, Any, Tuple
from app.core.config import settings

def _canonicalize_parameters(params: Dict[str, Any]) -> str:
    """Sorts and serializes parameters deterministically."""
    try:
        return json.dumps(params, sort_keys=True, default=str)
    except Exception:
        return str(sorted(params.items()))

def generate_execution_token(
    action_id: str,
    tool_name: str,
    parameters: Dict[str, Any],
    ttl_seconds: int = settings.EXECUTION_TOKEN_TTL_SECONDS
) -> str:
    """
    Generates a cryptographically signed HMAC-SHA256 execution token.
    Format: veriact_tok_{timestamp}_{expires_at}_{signature}
    """
    now = int(time.time())
    expires_at = now + ttl_seconds
    canonical_params = _canonicalize_parameters(parameters)
    message = f"{action_id}:{tool_name}:{canonical_params}:{now}:{expires_at}"
    
    signature = hmac.new(
        settings.HMAC_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"veriact_tok_{now}_{expires_at}_{signature}"

def verify_execution_token(
    token: str,
    action_id: str,
    tool_name: str,
    parameters: Dict[str, Any]
) -> Tuple[bool, str]:
    """
    Validates token authenticity, signature integrity, and TTL expiration.
    Returns (is_valid, reason).
    """
    if not token or not token.startswith("veriact_tok_"):
        return False, "Invalid token format."
    
    parts = token.split("_")
    if len(parts) != 5:  # ['veriact', 'tok', created_at, expires_at, signature]
        return False, "Malformed token structure."
    
    try:
        created_at = int(parts[2])
        expires_at = int(parts[3])
        received_sig = parts[4]
    except ValueError:
        return False, "Token timestamp components corrupted."
    
    now = int(time.time())
    if now > expires_at:
        return False, f"Token expired. Expired at {expires_at}, current time is {now}."
    
    # Reconstruct expected signature
    canonical_params = _canonicalize_parameters(parameters)
    expected_message = f"{action_id}:{tool_name}:{canonical_params}:{created_at}:{expires_at}"
    
    expected_sig = hmac.new(
        settings.HMAC_SECRET_KEY.encode("utf-8"),
        expected_message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(received_sig, expected_sig):
        return False, "Signature mismatch. Parameters or action ID tampered."
    
    return True, "Valid execution token."
