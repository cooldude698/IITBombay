"""
VERIACT — Tri-State Decision Gate (Task AMAN-301)
Evaluates inputs and outputs deterministic EXECUTE, ESCALATE, or BLOCK verdicts.
"""
from typing import List, Optional
from uuid import uuid4
from app.models.schemas import (
    NormalizedAction, VerificationTier, Verdict, 
    VerificationResult, RiskBreakdown, ParameterMismatch, GroundTruthEvidence
)
from app.core.crypto import generate_execution_token

class DecisionGate:
    """The central pre-execution gate enforcing safe execution."""

    def decide(
        self,
        action: NormalizedAction,
        risk: RiskBreakdown,
        tier: VerificationTier,
        mismatches: List[ParameterMismatch],
        policy_violations: List[str],
        requires_escalation: bool,
        evidence: Optional[GroundTruthEvidence],
        latency_ms: int = 0
    ) -> VerificationResult:
        trace_id = f"trc_{uuid4().hex[:12]}"

        # 1. Critical Contradictions & Direct Violations -> BLOCK
        if mismatches or any("VIOLATION" in v for v in policy_violations):
            reasons = []
            if mismatches:
                reasons.append("; ".join([m.message for m in mismatches]))
            if policy_violations:
                reasons.append("; ".join(policy_violations))
            
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=tier,
                risk_assessment=risk,
                mismatches=mismatches,
                policy_violations=policy_violations,
                reason=" | ".join(reasons),
                execution_token=None,
                latency_ms=latency_ms,
                trace_id=trace_id
            )

        # 2. Policy Thresholds / High Consequence -> ESCALATE
        if requires_escalation or any("ALERT" in v for v in policy_violations) or (risk.total_risk_score > 0.70 and action.action_type != "READ_ONLY"):
            escalation_reasons = policy_violations if policy_violations else [
                f"Action risk ({risk.total_risk_score:.2f}) exceeds autonomous threshold. Human managerial signoff required."
            ]
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.ESCALATE,
                verification_tier=tier,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=" | ".join(escalation_reasons),
                execution_token=None,
                latency_ms=latency_ms,
                trace_id=trace_id
            )

        # 3. Verified & Compliant -> EXECUTE
        # Mint cryptographic HMAC execution token
        token = generate_execution_token(
            action_id=action.action_id,
            tool_name=action.tool_name,
            parameters=action.parameters
        )

        return VerificationResult(
            action_id=action.action_id,
            verdict=Verdict.EXECUTE,
            verification_tier=tier,
            risk_assessment=risk,
            mismatches=[],
            policy_violations=[],
            reason=f"Action verified successfully under Tier {tier.value}. Authorized for tool execution.",
            execution_token=token,
            latency_ms=latency_ms,
            trace_id=trace_id
        )

decision_gate = DecisionGate()
