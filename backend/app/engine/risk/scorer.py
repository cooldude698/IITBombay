"""Multi-Factor Mathematical Risk Assessment Engine for VERIACT.

Formulation:
    R = w_f * F + w_i * I + w_p * P + w_u * U + w_c * C
where:
    F: Financial Impact (min(1.0, amount / 100,000.0))
    I: Irreversibility index (write/delete/transfer vs. read)
    P: Permission risk (role elevation delta vs. action cap)
    U: Evidence uncertainty (missing record or injection flag)
    C: Contradiction severity (exact parameter mismatch)
"""

from typing import Any, Dict, Optional
from app.models.schemas import (
    ActionType,
    NormalizedAction,
    RiskBreakdown,
    RiskWeights,
)


class RiskScorer:
    """Calculates continuous risk score R in [0.0, 1.0] from multidimensional signals."""

    def __init__(self, weights: Optional[RiskWeights] = None):
        self.weights = weights or RiskWeights()

    def compute_risk(
        self,
        action: NormalizedAction,
        contradiction_score: float = 0.0,
        uncertainty_score: float = 0.0,
        permission_risk: float = 0.0,
    ) -> RiskBreakdown:
        # 1. Financial Impact (F)
        amount = 0.0
        if action.parameters:
            try:
                raw_amt = action.parameters.get("amount") or action.parameters.get("total_amount")
                if raw_amt is not None:
                    amount = float(raw_amt)
            except (ValueError, TypeError):
                amount = 100000.0  # Max risk on corrupted monetary value

        f_score = min(1.0, max(0.0, amount / 100000.0))

        # 2. Irreversibility (I)
        tool_clean = action.tool_name.lower()
        if action.action_type == ActionType.READ_ONLY or tool_clean.startswith("read_") or tool_clean.startswith("get_"):
            i_score = 0.1
        elif action.action_type == ActionType.FINANCIAL or "payment" in tool_clean or "wire" in tool_clean or "transfer" in tool_clean:
            i_score = 1.0
        elif action.action_type == ActionType.DATA_MUTATION or "delete" in tool_clean or "drop" in tool_clean:
            i_score = 1.0
        elif "update" in tool_clean or "modify" in tool_clean:
            i_score = 0.6
        else:
            i_score = 0.4

        # 3. Permission Risk (P)
        p_score = min(1.0, max(0.0, permission_risk))

        # 4. Evidence Uncertainty (U)
        u_score = min(1.0, max(0.0, uncertainty_score))

        # 5. Contradiction Severity (C)
        c_score = min(1.0, max(0.0, contradiction_score))

        # Composite Weighted Risk Score
        total_risk = (
            self.weights.w_financial * f_score
            + self.weights.w_irreversibility * i_score
            + self.weights.w_permission * p_score
            + self.weights.w_uncertainty * u_score
            + self.weights.w_contradiction * c_score
        )
        total_risk = round(min(1.0, max(0.0, total_risk)), 4)

        return RiskBreakdown(
            financial_impact=round(f_score, 4),
            irreversibility=round(i_score, 4),
            permission_risk=round(p_score, 4),
            evidence_uncertainty=round(u_score, 4),
            contradiction_severity=round(c_score, 4),
            total_risk_score=total_risk,
        )


default_risk_scorer = RiskScorer()
