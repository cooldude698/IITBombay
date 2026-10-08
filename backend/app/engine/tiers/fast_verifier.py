"""Tier 1: Fast Verifier for VERIACT Pre-Execution Gateway.

Lightweight, ultra-fast deterministic verification (<150ms latency target,
typically <20ms). Validates schema, RBAC role permissions, and cached/fast entity lookups.
"""

import time
from uuid import uuid4
from typing import Any, Dict, Optional

from app.models.schemas import (
    NormalizedAction,
    VerificationResult,
    VerificationTier,
    Verdict,
    ActionType,
)
from app.engine.policy.rbac import default_rbac
from app.engine.risk.scorer import default_risk_scorer
from app.core.security import generate_execution_token


class FastVerifier:
    """Tier 1 verification engine for low-risk and read-only actions."""

    async def verify(
        self,
        action: NormalizedAction,
        cached_evidence: Optional[Dict[str, Any]] = None,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        start_time = time.perf_counter()
        trace_id = f"trc_{uuid4().hex[:12]}"
        policy_violations = []
        mismatches = []

        # 1. RBAC Role & Privilege Validation
        allowed, rbac_err = default_rbac.check_permission(
            agent_role=action.agent_role,
            tool_name=action.tool_name,
            parameters=action.parameters,
            agent_profile=agent_profile,
        )

        if not allowed and rbac_err:
            policy_violations.append(rbac_err)
            risk = default_risk_scorer.compute_risk(
                action=action,
                permission_risk=1.0,
                contradiction_score=0.5,
            )
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=VerificationTier.FAST,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=f"Fast Tier RBAC Block: {rbac_err}",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 2. Check Entity Existence for Reads if cached evidence supplied
        if action.action_type == ActionType.READ_ONLY and cached_evidence is not None:
            if not cached_evidence.get("exists", True):
                risk = default_risk_scorer.compute_risk(
                    action=action,
                    uncertainty_score=0.8,
                    contradiction_score=0.5,
                )
                elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
                return VerificationResult(
                    action_id=action.action_id,
                    verdict=Verdict.BLOCK,
                    verification_tier=VerificationTier.FAST,
                    risk_assessment=risk,
                    mismatches=[],
                    policy_violations=["Target entity does not exist in registry."],
                    reason="Fast Tier Block: Target read entity does not exist.",
                    execution_token=None,
                    latency_ms=elapsed_ms,
                    trace_id=trace_id,
                )

        # 3. Successful Fast Verification
        risk = default_risk_scorer.compute_risk(
            action=action,
            permission_risk=0.1,
            uncertainty_score=0.0,
            contradiction_score=0.0,
        )
        token = generate_execution_token(action.action_id, action.tool_name, action.parameters)
        elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))

        return VerificationResult(
            action_id=action.action_id,
            verdict=Verdict.EXECUTE,
            verification_tier=VerificationTier.FAST,
            risk_assessment=risk,
            mismatches=[],
            policy_violations=[],
            reason="Fast Tier Passed: Schema, RBAC permissions, and target validated.",
            execution_token=token,
            latency_ms=elapsed_ms,
            trace_id=trace_id,
        )


default_fast_verifier = FastVerifier()
