# System Architecture Specification — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Tagline:** Verify the Action. Then Let the Agent Act.  
> **Document:** High-Level & Low-Level Architectural Design  
> **Version:** 1.0.0  

---

## 1. High-Level Architecture

VERIACT operates as a transparent, inline verification proxy between an Autonomous AI Agent (built on LangGraph or custom orchestrators) and the real execution tools (APIs, databases, payment gateways).

```mermaid
graph TD
    User([User Request]) --> Agent[AI Agent - LangGraph Reasoning]
    Agent --> ProposedAction[Proposed Tool Action / Payload]
    
    subgraph VERIACT_GATEWAY [VERIACT Pre-Execution Gateway]
        direction TB
        Interceptor[Action Interceptor Hook] --> Normalizer[Action Normalizer]
        Normalizer --> GroundTruth[Evidence Retrieval Engine<br/>SQL & Vector Knowledge Base]
        GroundTruth --> DetCheck[Deterministic Grounding Engine<br/>Exact match, Thresholds, RBAC]
        DetCheck --> RiskEngine[Risk Assessment Engine<br/>R = w_f·F + w_i·I + w_p·P + w_u·U + w_c·C]
        
        RiskEngine --> Router{Risk-Adaptive<br/>Tier Router}
        
        Router -->|R <= 0.35| FastTier[Tier 1: Fast Verifier<br/>Schema + RBAC + Cache<br/>&lt; 150ms]
        Router -->|0.35 &lt; R &lt;= 0.70| StrongTier[Tier 2: Strong Verifier<br/>Live DB Grounding + Fast LLM<br/>&lt; 800ms]
        Router -->|R &gt; 0.70| DeepTier[Tier 3: Deep Verifier<br/>Multi-Source + Deep LLM + Policy<br/>&lt; 2000ms]
        
        FastTier --> DecisionGate[Tri-State Decision Gate]
        StrongTier --> DecisionGate
        DeepTier --> DecisionGate
    end
    
    ProposedAction --> Interceptor
    
    DecisionGate -->|Verified & Safe| Execute[🟢 EXECUTE<br/>Dispatches to Real Tool]
    DecisionGate -->|Uncertain / High Policy Risk| Escalate[🟡 ESCALATE<br/>Human-in-the-Loop Review Queue]
    DecisionGate -->|Contradiction / Policy Violation| Block[🔴 BLOCK<br/>Security Rejection to Agent]
    
    Execute --> Tool([Target Tool / API Execution])
    Escalate --> HITL([Operations Reviewer Dashboard])
    Block --> AuditLog[(Tamper-Evident Audit Trace)]
    Execute --> AuditLog
    Escalate --> AuditLog
```

---

## 2. Sequence Diagrams

### 2.1 Scenario 1: Invoice Payment Parameter Mismatch (BLOCK)
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Agent as LangGraph Agent
    participant Interceptor as VERIACT Interceptor
    participant Normalizer as Action Normalizer
    participant DB as ERP Ground Truth DB
    participant Grounding as Parameter Grounding
    participant Risk as Risk Engine
    participant Decision as Decision Gate
    participant Tool as Bank Payment Tool

    User->>Agent: "Pay the approved invoice INV-1921 for ABC Technologies"
    Agent->>Agent: Reasons over query (hallucinates ₹25,000)
    Agent->>Interceptor: make_payment(vendor="ABC Technologies", amount=25000, invoice="INV-1921")
    Note over Interceptor: Action paused. Held in memory.
    Interceptor->>Normalizer: normalize_tool_call(...)
    Normalizer-->>Interceptor: NormalizedAction(FINANCIAL, amount=25000, target="ABC Technologies")
    Interceptor->>DB: Query Invoice INV-1921
    DB-->>Interceptor: Invoice(vendor="ABC Technologies", approved_amount=18500, status="APPROVED")
    Interceptor->>Grounding: Compare (Agent: 25000 vs DB: 18500)
    Grounding-->>Interceptor: Mismatch Detected (Delta: +₹6,500, Contradiction C=1.0)
    Interceptor->>Risk: Compute Risk (F=0.25, I=1.0, C=1.0) -> R = 0.94 (HIGH)
    Risk->>Decision: Evaluate Verdict (Tier 3 Deep)
    Decision-->>Interceptor: Verdict: 🔴 BLOCK (Reason: Parameter Mismatch)
    Interceptor-->>Agent: Error 403: "Action Blocked: Proposed amount ₹25,000 contradicts verified invoice ₹18,500"
    Note over Tool: Real tool NEVER executed!
```

---

### 2.2 Scenario 2: Policy Threshold Escalation (ESCALATE)
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Agent as LangGraph Agent
    participant Interceptor as VERIACT Interceptor
    participant DB as ERP Ground Truth DB
    participant Policy as Policy Engine
    participant Queue as Human Review Queue
    actor Human as Compliance Officer
    participant Tool as Real Tool

    User->>Agent: "Pay vendor XYZ Logistics ₹18,500 per invoice INV-404"
    Agent->>Interceptor: make_payment(vendor="XYZ Logistics", amount=18500, invoice="INV-404")
    Interceptor->>DB: Query Invoice INV-404
    DB-->>Interceptor: Invoice(vendor="XYZ Logistics", approved_amount=18500, status="APPROVED")
    Note over Interceptor: Parameters MATCH (Amount & Vendor Verified)
    Interceptor->>Policy: Evaluate Policy Rules
    Note over Policy: Rule POL-FIN-01: "Payments > ₹10,000 require manager approval"
    Policy-->>Interceptor: Condition Met: Approval Missing -> Policy Alert
    Interceptor->>Decision Gate: Verdict: 🟡 ESCALATE
    Interceptor->>Queue: Push to Review Queue (Action ID: act_9912)
    Interceptor-->>Agent: Status: "Action held for manager signoff"
    Human->>Queue: Inspect action trace & verified invoice
    Human->>Queue: Click "APPROVE"
    Queue->>Tool: Execute make_payment(vendor="XYZ Logistics", amount=18500)
    Tool-->>User: Payment Successful (₹18,500)
```

---

## 3. Subsystem Detailed Decomposition

### 3.1 Layer 1: Agent & Interceptor Interface
- **Integration**: Plugs into LangGraph via a custom `VeriactToolNode`. Replaces default `ToolNode` in the state graph.
- **Interception Guarantee**: Tools are not executed directly by the LLM. Instead, the `tool_calls` generated by the LLM are routed into `veriact_pre_execution_node`.
- **State Capture**: Stores the agent conversation context, proposed tool, arguments, agent identity, and request timestamp.

### 3.2 Layer 2: Action Normalizer
- **Purpose**: Decouples the verification logic from model-specific tool schemas.
- **Transformation Pipeline**:
  1. Identifies the action domain: `FINANCIAL`, `SYSTEM_WRITE`, `DATA_MUTATION`, `COMMUNICATION`, or `READ_ONLY`.
  2. Extracts core entities: `target_entity` (vendor, user, table), `primary_value` (amount, record_id), `auxiliary_params`.
  3. Validates required fields against standard Pydantic models.

### 3.3 Layer 3: Controlled Ground Truth Store
- **Relational Mock ERP (SQLite / PostgreSQL)**:
  - `invoices`: id, vendor_id, amount, status, approved_by, issue_date, po_number
  - `vendors`: id, name, bank_account, ifsc_code, status, risk_tier
  - `employees`: id, name, role, department, approval_limit
  - `purchase_orders`: id, vendor_id, total_amount, fulfilled_amount
  - `policies`: id, code, description, condition_json, required_role, action_effect
- **Vector Knowledge Base (FAISS)**:
  - Chunks of corporate policy handbooks, compliance guidelines, and procurement SOPs.
  - Hybrid retrieval queries both relational tables and vector embeddings simultaneously.

### 3.4 Layer 4: Deterministic Grounding Engine
- **Non-Model Rule Execution**:
  - Compares proposed numerical values using $\Delta = |\text{proposed} - \text{actual}|$. If $\Delta > 0$, flag mismatch.
  - Compares string tokens using case-insensitive canonical normalization.
  - Checks state machine status: only invoices with `status == "APPROVED"` are eligible for payment.
- **Speed**: Executes in $<10\text{ms}$.

### 3.5 Layer 5: Policy & Authorization (RBAC) Engine
- **RBAC Matrix**:
  | Role | Can Read | Can Update | Can Transfer (<₹10k) | Can Transfer (>₹10k) | Can Delete |
  |---|---|---|---|---|---|
  | `Junior_Assistant` | Yes | No | No | No | No |
  | `Finance_Operator` | Yes | Yes | Yes (with PO) | No (Escalate) | No |
  | `Finance_Manager` | Yes | Yes | Yes | Yes | Yes (with audit) |
- **Rule Evaluator**: Evaluates predicate trees encoded in JSON/Python expressions against runtime variables.

### 3.6 Layer 6: Mathematical Risk Engine
- Continuous risk score formulation:
  $$R(a) = w_f \cdot F(a) + w_i \cdot I(a) + w_p \cdot P(a) + w_u \cdot U(a) + w_c \cdot C(a)$$
  $$\text{where } \sum w_i = 1.0, \quad R(a) \in [0.0, 1.0]$$
- Features:
  - $F$: Scaled financial exposure.
  - $I$: Irreversibility index (destructive writes and external transfers = 1.0).
  - $P$: Privilege level delta between agent role and action requirement.
  - $U$: Epistemic uncertainty (missing invoice or low semantic retrieval similarity).
  - $C$: Concrete parameter mismatch severity.

### 3.7 Layer 7: Adaptive Verification Tiers
```
                      Action Request
                             │
                      Risk Engine (R)
                             │
            ┌────────────────┼────────────────┐
            │                │                │
       R <= 0.35      0.35 < R <= 0.70     R > 0.70
       [FAST TIER]     [STRONG TIER]     [DEEP TIER]
            │                │                │
     - Schema Check   - Fast Tier      - Strong Tier
     - RBAC Check     - DB Grounding   - Multi-Source DB
     - Cache Lookup   - Fast LLM (Flash)- Deep LLM (Pro)
     - < 150ms        - < 800ms        - Policy Rules AST
                                       - Human Escalate Trigger
                                       - < 2000ms
```

### 3.8 Layer 8: Tri-State Decision Gate
- Encapsulates final gating logic:
  - **EXECUTE**: All validations pass; issued signed execution token `veriact_token_<uuid>`.
  - **ESCALATE**: Requires manual signoff; persisted to `EscalationQueue`.
  - **BLOCK**: Explicit failure; raises `ActionSecurityViolation` with explanation payload.

### 3.9 Layer 9: Auditable Action Trace Logger
- Records complete execution tree to immutable log:
  ```json
  {
    "trace_id": "trc_884920",
    "action_id": "act_1921",
    "timestamp": "2026-10-07T22:30:00Z",
    "agent_id": "finance_bot_v2",
    "tool": "make_payment",
    "proposed": {"vendor": "ABC Technologies", "amount": 25000},
    "retrieved_evidence": {"invoice_id": "INV-1921", "amount": 18500, "status": "APPROVED"},
    "mismatches": [{"field": "amount", "proposed": 25000, "expected": 18500}],
    "risk_score": 0.94,
    "tier_used": "DEEP",
    "verdict": "BLOCK",
    "hash": "sha256:4a3f12e8b..."
  }
  ```

---

## 4. State Machine Transition Diagram

```mermaid
stateDiagram-v2
    [*] --> Proposed: Agent generates tool call
    Proposed --> Normalizing: Interceptor captures call
    Normalizing --> Grounding: Canonical schema created
    Grounding --> RiskScoring: Ground truth queried
    RiskScoring --> TierFast: Risk <= 0.35
    RiskScoring --> TierStrong: 0.35 < Risk <= 0.70
    RiskScoring --> TierDeep: Risk > 0.70
    
    TierFast --> DecisionGate
    TierStrong --> DecisionGate
    TierDeep --> DecisionGate
    
    DecisionGate --> Executed: Parameters valid & Policy verified
    DecisionGate --> Escalated: Ambiguous / Threshold exceeded
    DecisionGate --> Blocked: Contradiction / Policy breach / RBAC deny
    
    Escalated --> Executed: Human Reviewer APPROVES
    Escalated --> Blocked: Human Reviewer REJECTS
    
    Executed --> [*]: Dispatched to real tool
    Blocked --> [*]: Action halted safely
```
