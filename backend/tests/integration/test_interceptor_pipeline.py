"""
Integration tests for the complete VERIACT Pre-Execution Interception Pipeline.
"""
import asyncio
import pytest
from app.models.schemas import ProposedToolCall, Verdict
from app.engine.interceptor import interceptor

def test_safe_invoice_payment_executes():
    async def _run():
        proposal = ProposedToolCall(
            tool_name="make_payment",
            raw_arguments={"vendor": "Apex Office Supplies", "amount": 3400.0, "invoice": "INV-102"},
            agent_id="agent_fin_sr",
            user_request="Pay invoice INV-102"
        )
        result = await interceptor.verify_proposal(proposal)
        assert result.verdict == Verdict.EXECUTE
        assert result.execution_token is not None
        assert len(result.mismatches) == 0

    asyncio.run(_run())

def test_parameter_mismatch_blocks_execution():
    async def _run():
        # Hallucinating ₹25,000 when approved invoice is ₹18,500
        proposal = ProposedToolCall(
            tool_name="make_payment",
            raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amount": 25000.0, "invoice": "INV-1921"},
            agent_id="agent_fin_sr",
            user_request="Pay invoice INV-1921"
        )
        result = await interceptor.verify_proposal(proposal)
        assert result.verdict == Verdict.BLOCK
        assert result.execution_token is None
        assert len(result.mismatches) == 1
        assert result.mismatches[0].field_name == "amount"
        assert result.mismatches[0].proposed_value == 25000.0
        assert result.mismatches[0].evidence_value == 18500.0

    asyncio.run(_run())

def test_policy_threshold_escalation():
    async def _run():
        # Parameters match (₹18,500 == ₹18,500), but > ₹10,000 policy threshold triggers manager signoff
        proposal = ProposedToolCall(
            tool_name="make_payment",
            raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amount": 18500.0, "invoice": "INV-1921"},
            agent_id="agent_fin_sr",
            user_request="Pay invoice INV-1921 for ₹18,500"
        )
        result = await interceptor.verify_proposal(proposal)
        assert result.verdict == Verdict.ESCALATE
        assert result.execution_token is None
        assert any("POL-FIN-001" in v for v in result.policy_violations)

    asyncio.run(_run())

def test_pre_execution_law_real_tool_never_called_on_block():
    async def _run():
        tool_called = False

        def mock_real_banking_api(params):
            nonlocal tool_called
            tool_called = True
            return {"status": "TRANSFERRED"}

        bad_proposal = ProposedToolCall(
            tool_name="make_payment",
            raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amount": 25000.0, "invoice": "INV-1921"},
            agent_id="agent_fin_sr",
            user_request="Pay invoice INV-1921"
        )

        report = await interceptor.execute_tool_with_interception(bad_proposal, mock_real_banking_api)

        assert report["success"] is False
        assert report["status"] == "BLOCKED"
        assert tool_called is False  # INVARIANT: Real tool was NEVER called!

    asyncio.run(_run())
