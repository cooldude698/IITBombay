# Data Model & Schema Specification — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Document:** Complete Data Model, Pydantic Schemas, and SQL DDL  
> **Version:** 1.0.0  

---

## 1. Relational Database DDL (SQLAlchemy & SQLite/PostgreSQL)

```sql
-- 1. Vendors Master Table
CREATE TABLE IF NOT EXISTS vendors (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    bank_account VARCHAR(64) NOT NULL,
    ifsc_code VARCHAR(32) NOT NULL,
    category VARCHAR(64) NOT NULL,
    risk_rating VARCHAR(16) NOT NULL DEFAULT 'LOW', -- LOW, MEDIUM, HIGH
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',   -- ACTIVE, SUSPENDED, PENDING_KYC
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Invoices Table (Ground Truth Evidence)
CREATE TABLE IF NOT EXISTS invoices (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'INV-1921'
    vendor_id VARCHAR(64) NOT NULL REFERENCES vendors(id),
    vendor_name VARCHAR(255) NOT NULL,
    amount NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL,                     -- DRAFT, PENDING_APPROVAL, APPROVED, PAID, CANCELLED
    po_number VARCHAR(64),
    approved_by VARCHAR(64),
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Employees & Agent Registry
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'finance_assistant_01'
    name VARCHAR(255) NOT NULL,
    role VARCHAR(64) NOT NULL,                       -- JUNIOR_ASSISTANT, FINANCE_OPERATOR, ADMIN_AGENT
    department VARCHAR(64) NOT NULL,
    daily_budget_limit NUMERIC(14, 2) NOT NULL DEFAULT 50000.00,
    single_txn_limit NUMERIC(14, 2) NOT NULL DEFAULT 10000.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Enterprise Policies Table
CREATE TABLE IF NOT EXISTS policies (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'POL-FIN-001'
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    condition_expression TEXT NOT NULL,             -- JSON or python-eval expression
    action_type VARCHAR(64) NOT NULL,               -- FINANCIAL, DATA_MUTATION, COMMUNICATION
    enforcement_action VARCHAR(32) NOT NULL,        -- BLOCK, ESCALATE, REQUIRE_MFA
    priority INTEGER NOT NULL DEFAULT 10,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Action Trace & Verification Audit Log (Tamper-Evident)
CREATE TABLE IF NOT EXISTS action_traces (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'trc_482910'
    action_id VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64) NOT NULL,
    tool_name VARCHAR(64) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    target_entity VARCHAR(255) NOT NULL,
    proposed_params JSON NOT NULL,
    retrieved_evidence JSON,
    mismatches JSON,
    risk_score NUMERIC(5, 4) NOT NULL,              -- 0.0000 to 1.0000
    verification_tier VARCHAR(16) NOT NULL,          -- FAST, STRONG, DEEP
    verdict VARCHAR(16) NOT NULL,                    -- EXECUTE, ESCALATE, BLOCK
    reason TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    payload_hash VARCHAR(64) NOT NULL,              -- SHA-256
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Human Review Escalation Queue
CREATE TABLE IF NOT EXISTS escalation_queue (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'esc_991823'
    trace_id VARCHAR(64) NOT NULL REFERENCES action_traces(id),
    agent_id VARCHAR(64) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    risk_score NUMERIC(5, 4) NOT NULL,
    details JSON NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',  -- PENDING, APPROVED, REJECTED
    reviewed_by VARCHAR(64),
    review_notes TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Red-Team Benchmark Scenarios Table (VERIACT-ASB)
CREATE TABLE IF NOT EXISTS benchmark_scenarios (
    id VARCHAR(64) PRIMARY KEY,                      -- e.g. 'SC-042'
    category VARCHAR(64) NOT NULL,                  -- PARAMETER_MISMATCH, WRONG_RECIPIENT, etc.
    user_request TEXT NOT NULL,
    proposed_tool VARCHAR(64) NOT NULL,
    proposed_params JSON NOT NULL,
    ground_truth_evidence JSON NOT NULL,
    expected_verdict VARCHAR(16) NOT NULL,          -- EXECUTE, ESCALATE, BLOCK
    difficulty VARCHAR(16) NOT NULL DEFAULT 'MEDIUM'
);
```

---

## 2. Core Pydantic Schemas (Python 3.11+ / Pydantic v2)

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

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

class BenchmarkCategory(str, Enum):
    PARAMETER_MISMATCH = "PARAMETER_MISMATCH"
    WRONG_RECIPIENT = "WRONG_RECIPIENT"
    HALLUCINATED_ENTITY = "HALLUCINATED_ENTITY"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    PERMISSION_VIOLATION = "PERMISSION_VIOLATION"
    STALE_INFORMATION = "STALE_INFORMATION"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    INTENT_MISMATCH = "INTENT_MISMATCH"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"

# ==============================================================================
# ACTION PROPOSAL & NORMALIZATION SCHEMAS
# ==============================================================================

class ProposedToolCall(BaseModel):
    tool_name: str = Field(..., description="Name of the tool the agent intended to execute")
    raw_arguments: Dict[str, Any] = Field(..., description="Raw tool invocation arguments")
    agent_id: str = Field(..., description="Identifier of the calling agent")
    user_request: str = Field(..., description="Original user prompt trigger")
    session_id: Optional[str] = Field(default=None)

class NormalizedAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    agent_role: str
    action_type: ActionType
    target_entity: str
    tool_name: str
    parameters: Dict[str, Any]
    user_context: str
    session_id: Optional[str] = None

# ==============================================================================
# EVIDENCE & GROUNDING SCHEMAS
# ==============================================================================

class GroundTruthEvidence(BaseModel):
    evidence_id: str
    source_type: str  # "DATABASE", "POLICY_STORE", "VECTOR_DOC"
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

class RiskBreakdown(BaseModel):
    financial_impact: float = Field(..., ge=0.0, le=1.0, description="F: Value exposure")
    irreversibility: float = Field(..., ge=0.0, le=1.0, description="I: Action write/delete nature")
    permission_risk: float = Field(..., ge=0.0, le=1.0, description="P: RBAC elevation needed")
    evidence_uncertainty: float = Field(..., ge=0.0, le=1.0, description="U: Missing or weak evidence")
    contradiction_severity: float = Field(..., ge=0.0, le=1.0, description="C: Direct mismatches")
    total_risk_score: float = Field(..., ge=0.0, le=1.0, description="R: Weighted composite score")

class RiskWeights(BaseModel):
    w_financial: float = 0.25
    w_irreversibility: float = 0.20
    w_permission: float = 0.20
    w_uncertainty: float = 0.15
    w_contradiction: float = 0.20

# ==============================================================================
# VERIFICATION RESULT & TRACE SCHEMAS
# ==============================================================================

class VerificationResult(BaseModel):
    action_id: str
    verdict: Verdict
    verification_tier: VerificationTier
    risk_assessment: RiskBreakdown
    mismatches: List[ParameterMismatch] = []
    policy_violations: List[str] = []
    reason: str
    execution_token: Optional[str] = None  # Signed HMAC token if EXECUTE
    latency_ms: int
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
    payload_hash: str  # SHA-256 of canonical inputs

# ==============================================================================
# BENCHMARK SCHEMAS
# ==============================================================================

class BenchmarkScenario(BaseModel):
    scenario_id: str
    category: BenchmarkCategory
    user_request: str
    proposed_tool: str
    proposed_params: Dict[str, Any]
    ground_truth_evidence: Dict[str, Any]
    expected_verdict: Verdict
    description: str

class BenchmarkEvaluationReport(BaseModel):
    benchmark_name: str = "VERIACT-ASB v1.0"
    total_scenarios: int
    system_name: str  # "No Guardrail", "LLM Judge", "Always Deep", "VERIACT"
    safety_recall: float
    false_block_rate: float
    precision: float
    avg_latency_ms: float
    p95_latency_ms: float
    total_cost_usd: float
    escalation_rate: float
```
