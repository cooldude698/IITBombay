"""Unit tests for Deterministic Parameter Grounding Engine."""

import pytest
from app.mock_env.db import get_invoice, get_vendor
from app.engine.grounding.matcher import ParameterMatcher, default_matcher


def test_exact_match_grounded_invoice():
    """Valid parameters matching approved invoice INV-1921 exactly."""
    inv = get_invoice("INV-1921")
    assert inv is not None

    proposed_params = {
        "invoice_id": "INV-1921",
        "vendor": "ABC Technologies Pvt Ltd",
        "amount": 18500.0,
    }

    result = default_matcher.match_invoice_payment(proposed_params, inv)
    assert result.is_grounded is True
    assert result.contradiction_score == 0.0
    assert len(result.mismatches) == 0


def test_amount_mismatch_triggers_contradiction():
    """Agent hallucinates ₹25,000 on an approved ₹18,500 invoice."""
    inv = get_invoice("INV-1921")
    assert inv is not None

    proposed_params = {
        "invoice_id": "INV-1921",
        "vendor": "ABC Technologies Pvt Ltd",
        "amount": 25000.0,  # Delta: +6500.0
    }

    result = default_matcher.match_invoice_payment(proposed_params, inv)
    assert result.is_grounded is False
    assert result.contradiction_score == 1.0
    assert len(result.mismatches) == 1
    assert result.mismatches[0].field_name == "amount"
    assert result.mismatches[0].severity == "CRITICAL"
    assert "Delta: +INR 6,500.00" in result.mismatches[0].message


def test_wrong_vendor_recipient_mismatch():
    """Agent attempts to pay Vendor B (XYZ Logistics) using invoice for Vendor A."""
    inv = get_invoice("INV-1921")
    assert inv is not None

    proposed_params = {
        "invoice_id": "INV-1921",
        "vendor": "XYZ Logistics India",
        "amount": 18500.0,
    }

    result = default_matcher.match_invoice_payment(proposed_params, inv)
    assert result.is_grounded is False
    assert result.contradiction_score == 1.0
    assert any(m.field_name == "vendor" for m in result.mismatches)


def test_hallucinated_invoice_entity():
    """Agent creates a fictitious invoice INV-9999 not in the ERP."""
    proposed_params = {
        "invoice_id": "INV-9999",
        "vendor": "ABC Technologies",
        "amount": 5000.0,
    }

    result = default_matcher.match_invoice_payment(proposed_params, None)
    assert result.is_grounded is False
    assert result.contradiction_score == 1.0
    assert any(m.field_name == "invoice_id" for m in result.mismatches)


def test_unapproved_invoice_status_block():
    """Agent attempts to pay invoice INV-312 which is already PAID."""
    inv = get_invoice("INV-312")
    assert inv is not None
    assert inv["status"] == "PAID"

    proposed_params = {
        "invoice_id": "INV-312",
        "vendor": "QuickCourier Services",
        "amount": 1200.0,
    }

    result = default_matcher.match_invoice_payment(proposed_params, inv)
    assert result.is_grounded is False
    assert any(m.field_name == "status" for m in result.mismatches)


def test_suspended_vendor_transaction_block():
    """Agent attempts to pay invoice with suspended vendor VND-005."""
    inv = get_invoice("INV-771")
    vnd = get_vendor("VND-005")
    assert vnd is not None
    assert vnd["status"] == "SUSPENDED"

    proposed_params = {
        "invoice_id": "INV-771",
        "vendor": "CyberShield Security",
        "amount": 50000.0,
    }

    result = default_matcher.match_invoice_payment(proposed_params, inv, vnd)
    assert result.is_grounded is False
    assert any(m.field_name == "vendor_status" for m in result.mismatches)
