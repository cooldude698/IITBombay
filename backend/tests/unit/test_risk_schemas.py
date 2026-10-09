"""
Unit tests for VERIACT Risk Schemas (Task ARYAN-101).
Asserts validation of normalization constraint (sum = 1.0) and factor bounds in [0.0, 1.0].
"""
import pytest
from pydantic import ValidationError
from app.models.risk import RiskBreakdown, RiskWeights


def test_risk_weights_default_valid():
    """Default weights sum to exactly 1.0 and pass validation."""
    weights = RiskWeights()
    total = (
        weights.w_financial
        + weights.w_irreversibility
        + weights.w_permission
        + weights.w_uncertainty
        + weights.w_contradiction
    )
    assert abs(total - 1.0) < 1e-4
    assert weights.w_financial == 0.25
    assert weights.w_irreversibility == 0.20
    assert weights.w_permission == 0.20
    assert weights.w_uncertainty == 0.15
    assert weights.w_contradiction == 0.20


def test_risk_weights_custom_valid():
    """Custom weights that sum to 1.0 pass validation."""
    weights = RiskWeights(
        w_financial=0.30,
        w_irreversibility=0.20,
        w_permission=0.20,
        w_uncertainty=0.10,
        w_contradiction=0.20,
    )
    assert weights.w_financial == 0.30


def test_risk_weights_invalid_sum_raises_error():
    """Weights that do not sum to 1.0 fail validation."""
    with pytest.raises(ValidationError) as exc_info:
        RiskWeights(
            w_financial=0.50,
            w_irreversibility=0.50,
            w_permission=0.20,
            w_uncertainty=0.10,
            w_contradiction=0.20,
        )
    assert "Risk weights must sum to 1.0" in str(exc_info.value)


def test_risk_breakdown_valid():
    """Valid components within [0.0, 1.0] instantiate successfully."""
    breakdown = RiskBreakdown(
        financial_impact=0.185,
        irreversibility=1.0,
        permission_risk=0.3,
        evidence_uncertainty=0.0,
        contradiction_severity=0.0,
        total_risk_score=0.3062,
    )
    assert breakdown.financial_impact == 0.185
    assert breakdown.total_risk_score == 0.3062


def test_risk_breakdown_out_of_bounds_raises_error():
    """Components outside [0.0, 1.0] fail validation."""
    with pytest.raises(ValidationError):
        RiskBreakdown(
            financial_impact=1.5,  # Invalid
            irreversibility=0.5,
            permission_risk=0.1,
            evidence_uncertainty=0.0,
            contradiction_severity=0.0,
            total_risk_score=0.5,
        )

    with pytest.raises(ValidationError):
        RiskBreakdown(
            financial_impact=0.5,
            irreversibility=0.5,
            permission_risk=0.1,
            evidence_uncertainty=0.0,
            contradiction_severity=0.0,
            total_risk_score=-0.1,  # Invalid
        )
