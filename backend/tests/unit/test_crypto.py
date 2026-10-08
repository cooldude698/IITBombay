"""
Unit tests for HMAC Execution Token generation, signature validation, and anti-tamper.
"""
from app.core.crypto import generate_execution_token, verify_execution_token

def test_execution_token_roundtrip():
    action_id = "act_test_99"
    tool = "make_payment"
    params = {"vendor": "ABC Tech", "amount": 18500.0}

    token = generate_execution_token(action_id, tool, params, ttl_seconds=30)
    assert token.startswith("veriact_tok_")

    is_valid, reason = verify_execution_token(token, action_id, tool, params)
    assert is_valid is True
    assert "Valid" in reason

def test_execution_token_tamper_detection():
    action_id = "act_test_99"
    tool = "make_payment"
    params = {"vendor": "ABC Tech", "amount": 18500.0}

    token = generate_execution_token(action_id, tool, params, ttl_seconds=30)

    # Tamper with amount parameter (e.g. attacker changes ₹18,500 to ₹25,000 post-verification)
    tampered_params = {"vendor": "ABC Tech", "amount": 25000.0}
    is_valid, reason = verify_execution_token(token, action_id, tool, tampered_params)
    assert is_valid is False
    assert "mismatch" in reason.lower()
