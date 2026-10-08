"""
VERIACT — Resilience, Latency Timeouts & Fail-Closed Guards (Task AMAN-401)
Ensures any internal failure or timeout strictly defaults to BLOCK or ESCALATE.
"""
import asyncio
from typing import Callable, Any
from app.models.schemas import ActionType, Verdict, VerificationResult, VerificationTier, RiskBreakdown

class VerificationTimeoutException(Exception):
    """Raised when verification tier exceeds allotted latency budget."""
    pass

class ResilienceGuard:
    """Enforces fail-closed invariants and timeout circuit breakers."""

    @staticmethod
    async def execute_with_timeout(
        coro_func: Callable[[], Any],
        timeout_ms: int
    ) -> Any:
        timeout_seconds = timeout_ms / 1000.0
        try:
            return await asyncio.wait_for(coro_func(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            raise VerificationTimeoutException(f"Verification exceeded timeout budget of {timeout_ms}ms.")

    @staticmethod
    def fail_closed_fallback(
        action_id: str,
        action_type: ActionType,
        error_msg: str
    ) -> VerificationResult:
        """
        FAIL-CLOSED INVARIANT:
        If an exception or timeout occurs, NEVER allow execution.
        Financial/Destructive -> BLOCK
        Read-Only -> ESCALATE
        """
        is_high_risk = action_type in [ActionType.FINANCIAL, ActionType.DATA_MUTATION, ActionType.SYSTEM_CONFIG]
        fallback_verdict = Verdict.BLOCK if is_high_risk else Verdict.ESCALATE

        return VerificationResult(
            action_id=action_id,
            verdict=fallback_verdict,
            verification_tier=VerificationTier.DEEP,
            risk_assessment=RiskBreakdown(
                financial_impact=1.0 if is_high_risk else 0.1,
                irreversibility=1.0 if is_high_risk else 0.1,
                permission_risk=0.5,
                evidence_uncertainty=1.0,
                contradiction_severity=0.0,
                total_risk_score=0.95 if is_high_risk else 0.40
            ),
            mismatches=[],
            policy_violations=[f"SYSTEM_FAIL_CLOSED: Verification degraded ({error_msg})"],
            reason=f"Verification aborted safely under Fail-Closed Protocol: {error_msg}",
            execution_token=None,
            latency_ms=0,
            trace_id=f"trc_failclosed_{action_id}"
        )

resilience_guard = ResilienceGuard()
