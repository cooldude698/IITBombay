"""Tier 2: Strong Verifier for VERIACT Pre-Execution Gateway.

Performs live database ground-truth validation and semantic consistency checks
(<800ms latency target). Used for medium-risk actions (0.35 < R <= 0.70).
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
from app.mock_env.db import get_invoice, get_vendor, get_policies
from app.engine.policy.rbac import default_rbac
from app.engine.grounding.matcher import default_matcher
from app.engine.policy.evaluator import default_policy_evaluator
from app.engine.risk.scorer import default_risk_scorer
from app.core.security import generate_execution_token


class StrongVerifier:
    """Tier 2 verification engine for medium-consequence operations."""

    async def verify(
        self,
        action: NormalizedAction,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        start_time = time.perf_counter()
        trace_id = f"trc_{uuid4().hex[:12]}"
        policy_violations = []

        # 1. RBAC Verification
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
                verification_tier=VerificationTier.STRONG,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=f"Strong Tier RBAC Block: {rbac_err}",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 2. Ground Truth Database Retrieval
        invoice_id = (
            action.parameters.get("invoice_id")
            or action.parameters.get("invoice")
            or action.parameters.get("inv_id")
        )
        invoice = get_invoice(str(invoice_id)) if invoice_id else None

        vendor_id = (
            action.parameters.get("vendor_id")
            or (invoice.get("vendor_id") if invoice else None)
        )
        vendor = get_vendor(str(vendor_id)) if vendor_id else None

        # 3. Deterministic Parameter Grounding
        grounding_res = default_matcher.match_invoice_payment(
            proposed_params=action.parameters,
            ground_truth_invoice=invoice,
            ground_truth_vendor=vendor,
        )

        if not grounding_res.is_grounded:
            risk = default_risk_scorer.compute_risk(
                action=action,
                contradiction_score=grounding_res.contradiction_score,
                uncertainty_score=0.7 if invoice is None else 0.2,
            )
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=VerificationTier.STRONG,
                risk_assessment=risk,
                mismatches=grounding_res.mismatches,
                policy_violations=["Parameter Grounding Contradiction Detected"],
                reason="Strong Tier Block: Proposed parameters contradict authoritative ground truth.",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 4. Enterprise Policy Evaluation
        policies = get_policies(action_type=action.action_type.value)
        policy_res = default_policy_evaluator.evaluate_policies(
            policies=policies,
            action_data={"parameters": action.parameters, "tool_name": action.tool_name},
            invoice_data=invoice,
            vendor_data=vendor,
            agent_profile=agent_profile,
        )

        if not policy_res.passed:
            reasons = [f"{p.policy_id}: {p.reason}" for p in policy_res.triggered_policies]
            policy_violations.extend(reasons)

            if policy_res.required_enforcement == "BLOCK":
                risk = default_risk_scorer.compute_risk(
                    action=action,
                    permission_risk=0.8,
                    contradiction_score=0.5,
                )
                verdict = Verdict.BLOCK
                reason = f"Strong Tier Block: Policy violation ({', '.join(reasons)})"
                token = None
            else:
                # ESCALATE (e.g. amount > 10,000 requiring manager approval)
                risk = default_risk_scorer.compute_risk(
                    action=action,
                    permission_risk=0.4,
                    uncertainty_score=0.4,
                )
                verdict = Verdict.ESCALATE
                reason = f"Strong Tier Escalation: {', '.join(reasons)}"
                token = None

            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=verdict,
                verification_tier=VerificationTier.STRONG,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=reason,
                execution_token=token,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 5. Passed Strong Verification
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
            verification_tier=VerificationTier.STRONG,
            risk_assessment=risk,
            mismatches=[],
            policy_violations=[],
            reason="Strong Tier Passed: Live DB ground-truth matches and policies satisfied.",
            execution_token=token,
            latency_ms=elapsed_ms,
            trace_id=trace_id,
        )


default_strong_verifier = StrongVerifier()
