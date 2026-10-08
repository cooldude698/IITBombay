"""
Unit tests for VERIACT Action Normalizer.
"""
from app.models.schemas import ProposedToolCall, ActionType
from app.engine.normalizer.normalizer import normalizer

def test_financial_action_normalization():
    proposal = ProposedToolCall(
        tool_name="make_payment",
        raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amt": "25000", "invoice_id": "inv-1921"},
        agent_id="agent_fin_sr",
        user_request="Pay invoice"
    )
    normalized = normalizer.normalize(proposal)
    assert normalized.action_type == ActionType.FINANCIAL
    assert normalized.parameters["amount"] == 25000.0
    assert normalized.parameters["invoice"] == "INV-1921"
    assert normalized.target_entity == "ABC Technologies Pvt Ltd"

def test_read_action_normalization():
    proposal = ProposedToolCall(
        tool_name="read_invoice",
        raw_arguments={"invoice_id": "inv-102"},
        agent_id="agent_fin_jr",
        user_request="Check invoice"
    )
    normalized = normalizer.normalize(proposal)
    assert normalized.action_type == ActionType.READ_ONLY
    assert normalized.parameters["invoice"] == "INV-102"
