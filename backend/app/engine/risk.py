"""
VERIACT — Multi-Factor Mathematical Risk Engine
Computes calibrated continuous risk score R in [0.0, 1.0].
"""
from typing import Optional
from app.models.schemas import NormalizedAction, ActionType, RiskBreakdown, RiskWeights, GroundTruthEvidence

class RiskEngine:
    def __init__(self, weights: Optional[RiskWeights] = None):
        self.weights = weights or RiskWeights()

    def calculate_risk(
        self,
        action: NormalizedAction,
        contradiction_score: float,
        evidence: Optional[GroundTruthEvidence]
    ) -> RiskBreakdown:
        # F: Financial Impact
        amount = action.parameters.get("amount", 0.0)
        try:
            amount_val = float(amount)
            f_score = min(1.0, amount_val / 100000.0)
        except (ValueError, TypeError):
            f_score = 0.0

        # I: Irreversibility
        if action.action_type in [ActionType.FINANCIAL, ActionType.DATA_MUTATION]:
            i_score = 1.0 if "delete" in action.tool_name or "drop" in action.tool_name or "payment" in action.tool_name else 0.8
        elif action.action_type == ActionType.EXTERNAL_COMMUNICATION:
            i_score = 0.5
        else:
            i_score = 0.1

        # P: Permission Sensitivity
        role = action.agent_role.upper()
        if "MANAGER" in role or "ADMIN" in role:
            p_score = 0.1
        elif "OPERATOR" in role:
            p_score = 0.3 if f_score < 0.25 else 0.6
        else:  # JUNIOR or ASSISTANT
            p_score = 0.8 if action.action_type != ActionType.READ_ONLY else 0.1

        # U: Evidence Uncertainty
        if evidence is not None:
            u_score = max(0.0, 1.0 - evidence.confidence_score)
        else:
            u_score = 0.1 if action.action_type == ActionType.READ_ONLY else 1.0

        # C: Contradiction Severity
        c_score = contradiction_score

        # Composite Weighted Score
        r_composite = (
            self.weights.w_financial * f_score +
            self.weights.w_irreversibility * i_score +
            self.weights.w_permission * p_score +
            self.weights.w_uncertainty * u_score +
            self.weights.w_contradiction * c_score
        )
        r_clamped = round(max(0.0, min(1.0, r_composite)), 4)

        return RiskBreakdown(
            financial_impact=round(f_score, 4),
            irreversibility=round(i_score, 4),
            permission_risk=round(p_score, 4),
            evidence_uncertainty=round(u_score, 4),
            contradiction_severity=round(c_score, 4),
            total_risk_score=r_clamped
        )

risk_engine = RiskEngine()
