"""
VERIACT — Core Pydantic Schemas & Data Contracts (Pydantic v2)
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

# ==============================================================================
# ENUMS
# ==============================================================================

class ActionType(str, Enum):
    FINANCIAL = "FINANCIAL"
    DATA_MUTATION = "DATA_MUTATION"
    EXTERNAL_COMMUNICATION = "EXTERNAL_COMMUNICATION"
    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    READ_ONLY = "READ_ONLY"

class VerificationTier(str, Enum):
    FAST = "FAST"
    STRONG = "STRONG"
    DEEP = "DEEP"

class Verdict(str, Enum):
    EXECUTE = "EXECUTE"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"

class EscalationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# ==============================================================================
# ACTION PROPOSAL & NORMALIZATION
# ==============================================================================

class ProposedToolCall(BaseModel):
    tool_name: str = Field(..., description="Name of the tool the agent intended to execute")
    raw_arguments: Dict[str, Any] = Field(..., description="Raw tool invocation arguments")
    agent_id: str = Field(default="agent_fin_sr", description="Identifier of the calling agent")
    user_request: str = Field(..., description="Original user prompt trigger")
    session_id: Optional[str] = Field(default=None)

class NormalizedAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    agent_role: str = "FINANCE_OPERATOR"
    action_type: ActionType
    target_entity: str
    tool_name: str
    parameters: Dict[str, Any]
    user_context: str
    session_id: Optional[str] = None

# ==============================================================================
# EVIDENCE & GROUNDING
# ==============================================================================

class GroundTruthEvidence(BaseModel):
    evidence_id: str
    source_type: str = "DATABASE"  # DATABASE, POLICY_STORE, VECTOR_DOC
    entity_key: str
    data: Dict[str, Any]
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    is_authoritative: bool = True
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class ParameterMismatch(BaseModel):
    field_name: str
    proposed_value: Any
    evidence_value: Any
    severity: str = "CRITICAL"  # CRITICAL, WARNING
    message: str

# ==============================================================================
# RISK ENGINE SCHEMAS
# ==============================================================================
from app.models.risk import RiskBreakdown, RiskWeights

# ==============================================================================
# VERIFICATION RESULT & ACTION TRACE
# ==============================================================================

class VerificationResult(BaseModel):
    action_id: str
    verdict: Verdict
    verification_tier: VerificationTier
    risk_assessment: RiskBreakdown
    mismatches: List[ParameterMismatch] = []
    policy_violations: List[str] = []
    reason: str
    execution_token: Optional[str] = None
    latency_ms: int = 0
    trace_id: str

class ActionTrace(BaseModel):
    trace_id: str = Field(default_factory=lambda: f"trc_{uuid4().hex[:12]}")
    action_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    tool_name: str
    action_type: ActionType
    target_entity: str
    proposed_params: Dict[str, Any]
    retrieved_evidence: Optional[Dict[str, Any]] = None
    mismatches: List[ParameterMismatch] = []
    risk_score: float
    verification_tier: VerificationTier
    verdict: Verdict
    reason: str
    latency_ms: int
    payload_hash: str

# ==============================================================================
# ESCALATION & HUMAN IN THE LOOP
# ==============================================================================

class EscalationItem(BaseModel):
    item_id: str = Field(default_factory=lambda: f"esc_{uuid4().hex[:8]}")
    action_id: str
    trace_id: str
    agent_id: str
    tool_name: str
    action_type: ActionType
    target_entity: str
    proposed_params: Dict[str, Any]
    retrieved_evidence: Optional[Dict[str, Any]] = None
    risk_score: float
    reason: str
    status: EscalationStatus = EscalationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    execution_token: Optional[str] = None

class EscalationDecisionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVE' or 'REJECT'")
    reviewer_id: str = Field(default="mgr_vikram")
    notes: Optional[str] = Field(default="")

# ==============================================================================
# ANALYTICS & SANDBOX
# ==============================================================================

class AnalyticsStats(BaseModel):
    total_actions_today: int
    verified_executed: int
    escalated: int
    blocked: int
    fast_tier_count: int
    strong_tier_count: int
    deep_tier_count: int
    average_latency_ms: int
    p95_latency_ms: int
    safety_recall_rate: float

class SandboxSimulateRequest(BaseModel):
    scenario_name: Optional[str] = "custom"
    agent_id: str = "agent_fin_sr"
    tool_name: str = "make_payment"
    raw_arguments: Dict[str, Any]
    user_request: str
