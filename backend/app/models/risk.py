"""
VERIACT — Mathematical Risk Model Schemas (Task ARYAN-101)
Defines Pydantic models for continuous multi-factor risk estimation:
  R = w_f * F + w_i * I + w_p * P + w_u * U + w_c * C
"""
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class RiskWeights(BaseModel):
    """
    Normalized weight configuration for the 5-factor risk formula.
    Constraint: w_financial + w_irreversibility + w_permission + w_uncertainty + w_contradiction == 1.0
    """
    w_financial: float = Field(default=0.25, ge=0.0, le=1.0, description="w_f: Weight for financial value exposure")
    w_irreversibility: float = Field(default=0.20, ge=0.0, le=1.0, description="w_i: Weight for action irreversibility")
    w_permission: float = Field(default=0.20, ge=0.0, le=1.0, description="w_p: Weight for RBAC role delta")
    w_uncertainty: float = Field(default=0.15, ge=0.0, le=1.0, description="w_u: Weight for evidence uncertainty")
    w_contradiction: float = Field(default=0.20, ge=0.0, le=1.0, description="w_c: Weight for contradiction severity")

    @model_validator(mode="after")
    def validate_sum_to_one(self) -> "RiskWeights":
        total = (
            self.w_financial
            + self.w_irreversibility
            + self.w_permission
            + self.w_uncertainty
            + self.w_contradiction
        )
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Risk weights must sum to 1.0 (got {total:.4f})")
        return self


class RiskBreakdown(BaseModel):
    """
    Detailed multi-factor risk assessment breakdown:
      F: Financial Impact in [0.0, 1.0]
      I: Irreversibility Index in [0.0, 1.0]
      P: Permission Sensitivity in [0.0, 1.0]
      U: Evidence Uncertainty in [0.0, 1.0]
      C: Contradiction Severity in [0.0, 1.0]
      R: Composite Weighted Risk Score in [0.0, 1.0]
    """
    financial_impact: float = Field(default=0.0, ge=0.0, le=1.0, description="F: Monetary exposure")
    irreversibility: float = Field(default=0.0, ge=0.0, le=1.0, description="I: Action write/delete nature")
    permission_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="P: RBAC elevation needed")
    evidence_uncertainty: float = Field(default=0.0, ge=0.0, le=1.0, description="U: Missing or weak evidence")
    contradiction_severity: float = Field(default=0.0, ge=0.0, le=1.0, description="C: Direct mismatches")
    total_risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="R: Weighted composite score")

    @model_validator(mode="after")
    def validate_bounds(self) -> "RiskBreakdown":
        for field_name in [
            "financial_impact",
            "irreversibility",
            "permission_risk",
            "evidence_uncertainty",
            "contradiction_severity",
            "total_risk_score",
        ]:
            val = getattr(self, field_name)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"Risk component '{field_name}' must be in [0.0, 1.0] (got {val})")
        return self
