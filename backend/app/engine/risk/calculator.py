"""
VERIACT — Mathematical Multi-Factor Risk Assessment Engine (Task ARYAN-201)

Formulation:
    R = w_f * F + w_i * I + w_p * P + w_u * U + w_c * C
where:
    w_f = 0.25 (Financial Impact weight)
    w_i = 0.20 (Irreversibility weight)
    w_p = 0.20 (Permission Sensitivity weight)
    w_u = 0.15 (Evidence Uncertainty weight)
    w_c = 0.20 (Contradiction Severity weight)
Constraint:
    sum(w) == 1.0, and R in [0.0, 1.0]
"""
from typing import Optional, Dict, Any
from app.models.risk import RiskBreakdown, RiskWeights
from app.models.schemas import NormalizedAction, ActionType, GroundTruthEvidence


class RiskCalculator:
    """Computes continuous multi-factor risk score R in [0.0, 1.0]."""

    def __init__(self, weights: Optional[RiskWeights] = None):
        self.weights = weights or RiskWeights()

    def compute_factors(
        self,
        action: NormalizedAction,
        contradiction_score: float = 0.0,
        evidence: Optional[GroundTruthEvidence] = None,
        custom_factors: Optional[Dict[str, float]] = None,
    ) -> RiskBreakdown:
        custom_factors = custom_factors or {}

        # 1. Financial Impact (F): min(1.0, amount / 100,000.0)
        if "financial_impact" in custom_factors:
            f_score = custom_factors["financial_impact"]
        else:
            amount = 0.0
            if action.parameters:
                try:
                    raw_amt = action.parameters.get("amount") or action.parameters.get("amt") or action.parameters.get("total_amount")
                    if raw_amt is not None:
                        amount = float(raw_amt)
                except (ValueError, TypeError):
                    amount = 100000.0  # Max exposure on corrupted currency data
            f_score = min(1.0, max(0.0, amount / 100000.0))

        # 2. Irreversibility Index (I)
        # 1.0 for wire transfers / destructive ops, 0.5 for external communication, 0.1 for read-only
        if "irreversibility" in custom_factors:
            i_score = custom_factors["irreversibility"]
        else:
            tool_name = action.tool_name.lower()
            if action.action_type == ActionType.READ_ONLY or tool_name.startswith("read_") or tool_name.startswith("get_"):
                i_score = 0.1
            elif action.action_type == ActionType.FINANCIAL or any(k in tool_name for k in ["payment", "wire", "transfer", "payout"]):
                i_score = 1.0
            elif action.action_type == ActionType.DATA_MUTATION or any(k in tool_name for k in ["delete", "drop", "purge", "truncate"]):
                i_score = 1.0
            elif action.action_type == ActionType.EXTERNAL_COMMUNICATION or any(k in tool_name for k in ["email", "notify", "message"]):
                i_score = 0.5
            elif any(k in tool_name for k in ["update", "modify", "edit"]):
                i_score = 0.6
            else:
                i_score = 0.3

        # 3. Permission Risk (P)
        # Assesses role authorization delta:
        # standard authorized role -> 0.10; operator -> 0.25; elevated / junior mismatch -> 0.85; unauthorized -> 1.0
        if "permission_risk" in custom_factors:
            p_score = custom_factors["permission_risk"]
        else:
            role = (action.agent_role or "JUNIOR_ASSISTANT").upper()
            if "MANAGER" in role or "ADMIN" in role:
                p_score = 0.10
            elif "OPERATOR" in role:
                p_score = 0.20 if f_score < 0.25 else 0.40
            else:  # JUNIOR or OPS_BOT
                p_score = 0.10 if action.action_type == ActionType.READ_ONLY else 0.85

        # 4. Evidence Uncertainty (U)
        # 1.0 - confidence if evidence exists, 0.1 for read-only if missing, 1.0 for financial if missing
        if "evidence_uncertainty" in custom_factors:
            u_score = custom_factors["evidence_uncertainty"]
        elif evidence is not None:
            u_score = max(0.0, min(1.0, 1.0 - float(evidence.confidence_score)))
        else:
            u_score = 0.10 if action.action_type == ActionType.READ_ONLY else 1.0

        # 5. Contradiction Severity (C)
        if "contradiction_severity" in custom_factors:
            c_score = custom_factors["contradiction_severity"]
        else:
            c_score = min(1.0, max(0.0, float(contradiction_score)))

        # Composite Continuous Weighted Score
        r_composite = (
            self.weights.w_financial * f_score
            + self.weights.w_irreversibility * i_score
            + self.weights.w_permission * p_score
            + self.weights.w_uncertainty * u_score
            + self.weights.w_contradiction * c_score
        )
        r_clamped = round(max(0.0, min(1.0, r_composite)), 4)

        return RiskBreakdown(
            financial_impact=round(f_score, 4),
            irreversibility=round(i_score, 4),
            permission_risk=round(p_score, 4),
            evidence_uncertainty=round(u_score, 4),
            contradiction_severity=round(c_score, 4),
            total_risk_score=r_clamped,
        )


risk_calculator = RiskCalculator()
