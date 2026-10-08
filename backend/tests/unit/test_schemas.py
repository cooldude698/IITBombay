"""
Unit tests for VERIACT Pydantic schemas and serialization.
"""
import pytest
from app.models.schemas import (
    ProposedToolCall, NormalizedAction, ActionType,
    RiskBreakdown, Verdict, VerificationTier, ParameterMismatch
)

def test_proposed_tool_call_validation():
    call = ProposedToolCall(
        tool_name="make_payment",
        raw_arguments={"vendor": "ABC Tech", "amount": 1000},
        agent_id="agent_01",
        user_request="Pay ABC Tech"
    )
    assert call.tool_name == "make_payment"
    assert call.raw_arguments["amount"] == 1000

def test_risk_breakdown_bounds():
    risk = RiskBreakdown(
        financial_impact=0.25,
        irreversibility=1.0,
        permission_risk=0.5,
        evidence_uncertainty=0.0,
        contradiction_severity=1.0,
        total_risk_score=0.94
    )
    assert 0.0 <= risk.total_risk_score <= 1.0

def test_parameter_mismatch_creation():
    m = ParameterMismatch(
        field_name="amount",
        proposed_value=25000.0,
        evidence_value=18500.0,
        severity="CRITICAL",
        message="Proposed amount exceeds approved amount by ₹6,500."
    )
    assert m.field_name == "amount"
    assert m.proposed_value == 25000.0
