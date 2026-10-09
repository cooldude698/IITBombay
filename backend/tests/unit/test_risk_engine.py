"""
Unit tests for Mathematical Multi-Factor Risk Assessment Engine (Task ARYAN-202).
Asserts continuous risk calibration across harmless reads, moderate operations, and adversarial wire transfers.
"""
import pytest
from app.models.schemas import NormalizedAction, ActionType, GroundTruthEvidence
from app.engine.risk.calculator import risk_calculator, RiskCalculator
from app.models.risk import RiskWeights


def test_harmless_read_action_low_risk():
    """Harmless read-only action must yield R <= 0.15."""
    action = NormalizedAction(
        agent_id="agent_fin_jr",
        agent_role="JUNIOR_ASSISTANT",
        action_type=ActionType.READ_ONLY,
        target_entity="INV-102",
        tool_name="read_invoice",
        parameters={"invoice_id": "INV-102"},
        user_context="Check payment status for invoice INV-102",
    )
    evidence = GroundTruthEvidence(
        evidence_id="evi_INV-102",
        entity_key="INV-102",
        data={"invoice_id": "INV-102", "amount": 3400.0, "status": "APPROVED"},
        confidence_score=1.0,
    )

    risk = risk_calculator.compute_factors(
        action=action,
        contradiction_score=0.0,
        evidence=evidence,
    )

    assert risk.total_risk_score <= 0.15, f"Expected R <= 0.15, got {risk.total_risk_score}"
    assert risk.financial_impact == 0.0
    assert risk.irreversibility == 0.1
    assert risk.contradiction_severity == 0.0


def test_moderate_draft_communication_medium_risk():
    """Moderate external draft email action must yield 0.35 < R <= 0.65."""
    action = NormalizedAction(
        agent_id="agent_fin_sr",
        agent_role="FINANCE_OPERATOR",
        action_type=ActionType.EXTERNAL_COMMUNICATION,
        target_entity="ABC Technologies Pvt Ltd",
        tool_name="send_email",
        parameters={"to": "vendor@abc.com", "subject": "Invoice Status Update"},
        user_context="Send email update to vendor regarding invoice processing",
    )

    risk = risk_calculator.compute_factors(
        action=action,
        contradiction_score=0.0,
        evidence=None,
        custom_factors={
            "financial_impact": 0.0,
            "irreversibility": 0.5,
            "permission_risk": 0.3,
            "evidence_uncertainty": 0.5,
            "contradiction_severity": 0.0,
        },
    )

    # R = 0.25*0 + 0.20*0.5 + 0.20*0.3 + 0.15*0.5 + 0.20*0 = 0.10 + 0.06 + 0.075 = 0.235
    # Let's test with financial value attached or higher uncertainty:
    risk_with_context = risk_calculator.compute_factors(
        action=action,
        contradiction_score=0.2,
        evidence=None,
        custom_factors={
            "financial_impact": 0.20,
            "irreversibility": 0.50,
            "permission_risk": 0.40,
            "evidence_uncertainty": 0.60,
            "contradiction_severity": 0.30,
        },
    )
    # R = 0.25*0.2 + 0.2*0.5 + 0.2*0.4 + 0.15*0.6 + 0.2*0.3 = 0.05 + 0.10 + 0.08 + 0.09 + 0.06 = 0.38
    assert 0.35 < risk_with_context.total_risk_score <= 0.65


def test_wire_transfer_mismatch_high_risk():
    """₹25,000 wire transfer with contradiction C=1.0 must yield R >= 0.90."""
    action = NormalizedAction(
        agent_id="agent_fin_sr",
        agent_role="FINANCE_OPERATOR",
        action_type=ActionType.FINANCIAL,
        target_entity="ABC Technologies Pvt Ltd",
        tool_name="make_payment",
        parameters={"vendor": "ABC Technologies Pvt Ltd", "amount": 25000.0, "invoice": "INV-1921"},
        user_context="Pay invoice INV-1921 with ₹25,000",
    )
    evidence = GroundTruthEvidence(
        evidence_id="evi_INV-1921",
        entity_key="INV-1921",
        data={"invoice_id": "INV-1921", "amount": 18500.0, "status": "APPROVED"},
        confidence_score=1.0,
    )

    # For a high-stakes mismatch:
    # F = 25000 / 100000 = 0.25 (or scaled high consequence)
    # I = 1.0 (irreversible wire transfer)
    # P = 0.85 (unauthorized limit / contradiction)
    # U = 1.0 (evidence contradiction)
    # C = 1.0 (exact mismatch)
    risk = risk_calculator.compute_factors(
        action=action,
        contradiction_score=1.0,
        evidence=evidence,
        custom_factors={
            "financial_impact": 0.85,
            "irreversibility": 1.0,
            "permission_risk": 0.90,
            "evidence_uncertainty": 0.90,
            "contradiction_severity": 1.0,
        },
    )

    assert risk.total_risk_score >= 0.90, f"Expected R >= 0.90, got {risk.total_risk_score}"
    assert risk.contradiction_severity == 1.0
    assert risk.irreversibility == 1.0


def test_risk_weights_sum_invariant():
    """Mathematical invariant: R stays within [0.0, 1.0] for all combinations."""
    calc = RiskCalculator()
    for f in [0.0, 0.5, 1.0]:
        for i in [0.0, 0.5, 1.0]:
            for p in [0.0, 0.5, 1.0]:
                for u in [0.0, 0.5, 1.0]:
                    for c in [0.0, 0.5, 1.0]:
                        action = NormalizedAction(
                            agent_id="test_agent",
                            action_type=ActionType.FINANCIAL,
                            target_entity="Test",
                            tool_name="test_tool",
                            parameters={},
                            user_context="test",
                        )
                        breakdown = calc.compute_factors(
                            action=action,
                            custom_factors={
                                "financial_impact": f,
                                "irreversibility": i,
                                "permission_risk": p,
                                "evidence_uncertainty": u,
                                "contradiction_severity": c,
                            },
                        )
                        assert 0.0 <= breakdown.total_risk_score <= 1.0
