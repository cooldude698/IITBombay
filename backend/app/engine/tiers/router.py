"""
VERIACT — Risk-Adaptive Tier Router (Task ARYAN-301)

Dynamically routes intercepted actions to the appropriate verification tier
based on continuous multi-factor risk score R in [0.0, 1.0]:
  - R <= 0.35: Tier 1 FAST VERIFIER (< 150ms)
  - 0.35 < R <= 0.70: Tier 2 STRONG VERIFIER (< 800ms)
  - R > 0.70: Tier 3 DEEP VERIFIER (< 2000ms)
"""
from typing import Optional, Dict, Any, Tuple
from app.models.schemas import (
    NormalizedAction,
    VerificationResult,
    VerificationTier,
    RiskBreakdown,
)
from app.engine.tiers.fast_verifier import default_fast_verifier, FastVerifier
from app.engine.tiers.strong_verifier import default_strong_verifier, StrongVerifier
from app.engine.tiers.deep_verifier import default_deep_verifier, DeepVerifier


class TierRouter:
    """Routes actions to the optimal verification tier on the safety/latency Pareto frontier."""

    def __init__(
        self,
        fast_verifier: Optional[FastVerifier] = None,
        strong_verifier: Optional[StrongVerifier] = None,
        deep_verifier: Optional[DeepVerifier] = None,
    ):
        self.fast_verifier = fast_verifier or default_fast_verifier
        self.strong_verifier = strong_verifier or default_strong_verifier
        self.deep_verifier = deep_verifier or default_deep_verifier

    def select_tier(self, risk_score: float) -> VerificationTier:
        """Determines tier assignment based on risk score thresholds."""
        if risk_score <= 0.35:
            return VerificationTier.FAST
        elif risk_score <= 0.70:
            return VerificationTier.STRONG
        else:
            return VerificationTier.DEEP

    async def route_and_verify(
        self,
        action: NormalizedAction,
        risk: RiskBreakdown,
        cached_evidence: Optional[Dict[str, Any]] = None,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[VerificationTier, VerificationResult]:
        """Dispatches action to the appropriate verifier based on total_risk_score."""
        tier = self.select_tier(risk.total_risk_score)

        if tier == VerificationTier.FAST:
            result = await self.fast_verifier.verify(
                action=action,
                cached_evidence=cached_evidence,
                agent_profile=agent_profile,
            )
        elif tier == VerificationTier.STRONG:
            result = await self.strong_verifier.verify(
                action=action,
                agent_profile=agent_profile,
            )
        else:  # DEEP
            result = await self.deep_verifier.verify(
                action=action,
                agent_profile=agent_profile,
            )

        return tier, result


tier_router = TierRouter()
