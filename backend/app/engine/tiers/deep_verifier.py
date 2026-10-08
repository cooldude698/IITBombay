"""Tier 3: Deep Verifier for VERIACT Pre-Execution Gateway.

Performs multi-source cross-referencing, anti-injection analysis, policy AST
evaluation, and vector SOP retrieval (<2000ms latency target).
Used for high-consequence transactions (R > 0.70).
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
from app.mock_env.db import get_invoice, get_vendor, get_agent, get_policies
from app.engine.policy.rbac import default_rbac
from app.engine.grounding.matcher import default_matcher
from app.engine.policy.evaluator import default_policy_evaluator
from app.engine.retrieval.sanitizer import default_sanitizer
from app.engine.retrieval.vector_store import default_vector_store
from app.engine.risk.scorer import default_risk_scorer
from app.core.security import generate_execution_token


class DeepVerifier:
    """Tier 3 verification engine for high-consequence and adversarial actions."""

    async def verify(
        self,
        action: NormalizedAction,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        start_time = time.perf_counter()
        trace_id = f"trc_{uuid4().hex[:12]}"
        policy_violations = []

        # 1. Anti-Prompt-Injection Sanitization on Context and Parameters
        full_context_text = f"{action.user_context} {str(action.parameters)}"
        sanitization = default_sanitizer.sanitize(full_context_text, source_id=action.action_id)

        if not sanitization.is_safe:
            risk = default_risk_scorer.compute_risk(
                action=action,
                uncertainty_score=1.0,
                contradiction_score=1.0,
                permission_risk=1.0,
            )
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=VerificationTier.DEEP,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=["CRITICAL_SECURITY: Potential Adversarial Prompt Injection Detected in Request"],
                reason="Deep Tier Block: Prompt injection directives identified and quarantined.",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 2. RBAC Verification & Agent Profile
        profile = agent_profile or get_agent(action.agent_id)
        allowed, rbac_err = default_rbac.check_permission(
            agent_role=action.agent_role,
            tool_name=action.tool_name,
            parameters=action.parameters,
            agent_profile=profile,
        )
        if not allowed and rbac_err:
            policy_violations.append(rbac_err)
            risk = default_risk_scorer.compute_risk(
                action=action,
                permission_risk=1.0,
                contradiction_score=0.8,
            )
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=VerificationTier.DEEP,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=f"Deep Tier RBAC Block: {rbac_err}",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 3. Multi-Source Evidence Cross-Referencing
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

        # 4. Deterministic Parameter Grounding
        grounding_res = default_matcher.match_invoice_payment(
            proposed_params=action.parameters,
            ground_truth_invoice=invoice,
            ground_truth_vendor=vendor,
        )

        if not grounding_res.is_grounded:
            risk = default_risk_scorer.compute_risk(
                action=action,
                contradiction_score=grounding_res.contradiction_score,
                uncertainty_score=0.9 if invoice is None else 0.3,
            )
            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=Verdict.BLOCK,
                verification_tier=VerificationTier.DEEP,
                risk_assessment=risk,
                mismatches=grounding_res.mismatches,
                policy_violations=["Multi-Source Grounding Contradiction Detected"],
                reason="Deep Tier Block: Parameters contradict verified ERP records.",
                execution_token=None,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 5. Semantic Vector SOP Search (Corpus Contextualization)
        sop_matches = default_vector_store.search(
            f"{action.tool_name} {action.target_entity} {str(action.parameters)}",
            top_k=2,
        )

        # 6. Policy AST Evaluation
        policies = get_policies(action_type=action.action_type.value)
        policy_res = default_policy_evaluator.evaluate_policies(
            policies=policies,
            action_data={"parameters": action.parameters, "tool_name": action.tool_name},
            invoice_data=invoice,
            vendor_data=vendor,
            agent_profile=profile,
        )

        if not policy_res.passed:
            reasons = [f"{p.policy_id}: {p.reason}" for p in policy_res.triggered_policies]
            policy_violations.extend(reasons)

            if policy_res.required_enforcement == "BLOCK":
                risk = default_risk_scorer.compute_risk(
                    action=action,
                    permission_risk=0.9,
                    contradiction_score=0.6,
                )
                verdict = Verdict.BLOCK
                reason = f"Deep Tier Block: Policy condition violated ({', '.join(reasons)})"
                token = None
            else:
                # ESCALATE
                risk = default_risk_scorer.compute_risk(
                    action=action,
                    permission_risk=0.5,
                    uncertainty_score=0.5,
                )
                verdict = Verdict.ESCALATE
                reason = f"Deep Tier Escalation: Action exceeds autonomous threshold ({', '.join(reasons)})"
                token = None

            elapsed_ms = max(1, int((time.perf_counter() - start_time) * 1000))
            return VerificationResult(
                action_id=action.action_id,
                verdict=verdict,
                verification_tier=VerificationTier.DEEP,
                risk_assessment=risk,
                mismatches=[],
                policy_violations=policy_violations,
                reason=reason,
                execution_token=token,
                latency_ms=elapsed_ms,
                trace_id=trace_id,
            )

        # 7. Deep Verification Passed
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
            verification_tier=VerificationTier.DEEP,
            risk_assessment=risk,
            mismatches=[],
            policy_violations=[],
            reason="Deep Tier Passed: Multi-source verification, policy compliance, and anti-injection confirmed.",
            execution_token=token,
            latency_ms=elapsed_ms,
            trace_id=trace_id,
        )


default_deep_verifier = DeepVerifier()
