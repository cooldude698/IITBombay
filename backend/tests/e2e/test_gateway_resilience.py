"""
VERIACT — E2E Gateway Resilience & Telemetry Tests (Tasks AMAN-401 & AMAN-404)
Validates fail-closed behavior under timeouts/exceptions and real-time telemetry streaming queue.
"""
import pytest
import asyncio
from app.core.resilience import resilience_guard, VerificationTimeoutException
from app.models.schemas import ActionType, Verdict, ProposedToolCall
from app.engine.trace_logger import trace_logger
from app.engine.interceptor import interceptor

def test_fail_closed_financial_action_timeout():
    """Ensure a financial action that times out is strictly BLOCKED (Fail-Closed Law)."""
    async def _run():
        async def hung_verification():
            await asyncio.sleep(0.5)
            return "unreachable"

        with pytest.raises(VerificationTimeoutException):
            await resilience_guard.execute_with_timeout(
                hung_verification,
                timeout_ms=50  # 50ms timeout < 500ms sleep
            )

        # Validate that fallback yields a strict BLOCK for FINANCIAL actions
        fallback_result = resilience_guard.fail_closed_fallback(
            action_id="act_test_timeout",
            action_type=ActionType.FINANCIAL,
            error_msg="Verification exceeded timeout budget of 50ms"
        )

        assert fallback_result.verdict == Verdict.BLOCK
        assert fallback_result.execution_token is None
        assert fallback_result.risk_assessment.total_risk_score >= 0.85
        assert "FAIL_CLOSED" in fallback_result.policy_violations[0]

    asyncio.run(_run())

def test_fail_closed_read_action_timeout():
    """Ensure a read-only action that times out is safely ESCALATED rather than blocked or silently executed."""
    fallback_result = resilience_guard.fail_closed_fallback(
        action_id="act_test_read_timeout",
        action_type=ActionType.READ_ONLY,
        error_msg="Verification exceeded timeout budget of 50ms"
    )

    assert fallback_result.verdict == Verdict.ESCALATE
    assert fallback_result.execution_token is None

def test_live_telemetry_stream_subscription():
    """Ensure new actions verified through the interceptor are broadcast to telemetry subscribers."""
    async def _run():
        sub_queue = trace_logger.subscribe()
        try:
            # Run a safe verification through interceptor
            proposal = ProposedToolCall(
                tool_name="make_payment",
                raw_arguments={"vendor": "Apex Office Supplies", "amount": 3400.0, "invoice": "INV-102"},
                user_request="Pay invoice INV-102"
            )
            result = await interceptor.verify_proposal(proposal)

            # The subscriber queue must immediately have received the trace
            assert not sub_queue.empty()
            trace = sub_queue.get_nowait()
            assert trace.action_id == result.action_id
            assert trace.verdict == result.verdict
            assert trace.tool_name == "make_payment"
        finally:
            trace_logger.unsubscribe(sub_queue)

    asyncio.run(_run())
