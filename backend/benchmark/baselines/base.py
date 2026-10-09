"""
Base interfaces and result models for benchmark evaluation.
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class BaselineEvaluationResult(BaseModel):
    scenario_id: str
    baseline_name: str
    verdict: str  # EXECUTE, ESCALATE, BLOCK
    is_safe: bool
    latency_ms: int
    token_cost: float
    blocked_unsafe: bool
    false_block: bool
    decision_reason: str
    tier_used: Optional[str] = None
