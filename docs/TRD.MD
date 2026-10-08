# Technical Requirements Document (TRD) — VERIACT

> **Project Name:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Document:** Technical Requirements & Engineering Specification  
> **Version:** 1.0.0  
> **Status:** Production-Ready Architecture  

---

## 1. Technical Architecture Overview

VERIACT acts as an inline, synchronous pre-execution gateway between an autonomous agent and external system tools. 

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    AGENT RUNTIME                       │
                               │  User Request ──> Reasoning Loop ──> Proposed Tool Call │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                                                           ▼ (Intercepted Tool Invocation)
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 VERIACT GATEWAY CORE                                                  │
│                                                                                                                       │
│  ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────────────────────────────┐  │
│  │ 1. Action Normalizer  │ ───> │ 2. Ground Truth Lookup  │ ───> │ 3. Deterministic Grounding & Policy Evaluation  │  │
│  │ Canonical JSON Schema │      │ Hybrid SQL + Vector DB  │      │ Exact match, range checks, RBAC verification    │  │
│  └───────────────────────┘      └─────────────────────────┘      └────────────────────────┬────────────────────────┘  │
│                                                                                           │                           │
│                                                                                           ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 4. Multi-Factor Risk Assessment Engine:  R = w_f·F + w_i·I + w_p·P + w_u·U + w_c·C                             │  │
│  └────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────┘  │
│                                                   │                                                                   │
│                                                   ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 5. Risk-Adaptive Tier Router                                                                                    │  │
│  │                                                                                                                 │  │
│  │        [R <= 0.35]                          [0.35 < R <= 0.70]                          [R > 0.70]              │  │
│  │       ┌───────────┐                            ┌───────────┐                           ┌───────────┐            │  │
│  │       │ FAST TIER │                            │STRONG TIER│                           │ DEEP TIER │            │  │
│  │       │ Schema &  │                            │ Tier 1 +  │                           │ Tier 2 +  │            │  │
│  │       │ Cached DB │                            │ Fast LLM  │                           │ Multi-DB+ │            │  │
│  │       │ (< 150ms) │                            │ (< 800ms) │                           │ Deep LLM  │            │  │
│  │       └─────┬─────┘                            └─────┬─────┘                           └─────┬─────┘            │  │
│  └─────────────┼────────────────────────────────────────┼───────────────────────────────────────┼──────────────────┘  │
│                │                                        │                                       │                     │
│                └────────────────────────────────────────┼───────────────────────────────────────┘                     │
│                                                         │                                                             │
│                                                         ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 6. Tri-State Decision Gate                                                                                      │  │
│  │                                                                                                                 │  │
│  │              🟢 EXECUTE                           🟡 ESCALATE                           🔴 BLOCK                │  │
│  │          (Forward to Tool)                   (Queue for Review)                   (Reject & Alert)              │  │
│  └──────────────────────┬───────────────────────────────────┬───────────────────────────────────┬──────────────────┘  │
└─────────────────────────┼───────────────────────────────────┼───────────────────────────────────┼─────────────────────┘
                          │                                   │                                   │
                          ▼                                   ▼                                   ▼
                   [Real Tool Call]                [Human Review Queue]                 [Agent Rejection]
```

---

## 2. Technology Stack & Specifications

| Layer | Technology | Version | Purpose & Rationale |
|---|---|---|---|
| **Runtime / Language** | Python | 3.11+ | Native async event loop, typing performance, extensive AI library ecosystem. |
| **Backend Framework** | FastAPI + Uvicorn | 0.111+ | Asynchronous RESTful API, auto OpenAPI 3.1 docs, native Pydantic v2 support. |
| **Agent Orchestration** | LangGraph / LangChain | 0.1.0+ | StateGraph abstraction, tool interceptor hooks, reversible state execution. |
| **Data Validation** | Pydantic v2 | 2.7+ | Ultra-fast Rust-based schema validation and serialization. |
| **Relational Database** | SQLite (dev) / PostgreSQL (prod) | SQLite 3 / PG 16 | Relational store for ERP data (Invoices, Vendors, Employees, Policies, Logs). |
| **ORM / Migration** | SQLAlchemy + Alembic | 2.0+ (async) | Fully asynchronous database operations with type-safe schema definitions. |
| **Vector Store** | FAISS / ChromaDB | Latest | In-memory embedding search for unstructured policies and compliance standards. |
| **Embedding Model** | `text-embedding-3-small` / `all-MiniLM-L6-v2` | Latest | Fast dense vector generation (1536d / 384d) for policy semantic retrieval. |
| **Fast LLM Verifier** | Gemini 1.5 Flash / GPT-4o-Mini | Cloud API | Sub-400ms semantic consistency checks and lightweight document grounding. |
| **Deep LLM Verifier** | Gemini 1.5 Pro / GPT-4o / Claude 3.5 Sonnet | Cloud API | Multi-source adversarial reasoning, nuanced edge-case and injection analysis. |
| **Frontend Framework** | Next.js (App Router) + React | 14.2+ / 18 | High-performance React server components, streaming SSR, API routes. |
| **Styling & Icons** | Tailwind CSS + Lucide React | 3.4+ / Latest | Cyber-security dark theme, utility-first rapid styling, accessible icons. |
| **Telemetry & Visuals** | Recharts + Framer Motion | 2.12+ / 11+ | Real-time risk radar, Pareto trade-off curve charts, fluid trace transitions. |

---

## 3. Subsystem Specifications

### 3.1 Subsystem 1: Interception Middleware
- **Hook Point**: LangGraph `ToolNode` or custom decorator `@intercept_action`.
- **Interception Mechanism**:
  ```python
  class VeriactInterceptor:
      async def intercept(self, agent_id: str, tool_name: str, raw_arguments: dict) -> VerificationResult:
          # 1. Normalize
          normalized = self.normalizer.normalize(agent_id, tool_name, raw_arguments)
          # 2. Verify
          result = await self.verification_engine.verify(normalized)
          # 3. Intervene
          if result.verdict == Verdict.EXECUTE:
              return await self.execute_tool(tool_name, raw_arguments)
          elif result.verdict == Verdict.ESCALATE:
              return self.escalate_to_human(result)
          else:
              return self.block_action(result)
  ```
- **Execution Token**: Upon `EXECUTE`, a short-lived cryptographic execution token (HMAC-SHA256, 30s TTL) is issued. The underlying tool verifies this token before dispatching actual I/O.

### 3.2 Subsystem 2: Action Normalizer
Standardizes heterogeneous agent tool calls into a canonical Pydantic model:
```python
class NormalizedAction(BaseModel):
    action_id: UUID
    timestamp: datetime
    agent_id: str
    agent_role: str
    action_type: ActionType  # FINANCIAL, DATA_MODIFICATION, EXTERNAL_COMMUNICATION, READ_ONLY
    target_entity: str       # e.g., "ABC Technologies", "invoice_1921", "customer_table"
    tool_name: str           # e.g., "make_payment"
    parameters: dict[str, Any]
    user_context: str
    session_id: str
```

### 3.3 Subsystem 3: Evidence Retrieval Engine
- **Hybrid Retrieval Protocol**:
  1. **Deterministic Primary Key / Foreign Key Lookup**: Directly queries the SQL mock ERP database using normalized keys (e.g., `invoice_id`, `vendor_id`, `employee_id`).
  2. **Vector Similarity Fallback**: For unstructured policy clauses or ambiguous entity names, queries FAISS/Chroma with cosine similarity threshold $\tau_{sim} \ge 0.82$.
- **Evidence Output**: Returns a typed `GroundTruthEvidence` structure containing retrieved database fields, timestamp, source database, and confidence score.

### 3.4 Subsystem 4: Parameter Grounding & Policy Engine
Executes deterministic validation in native Python code without model latency:
1. **Parameter Grounding**:
   - `proposed_amount == evidence.approved_amount`
   - `proposed_vendor == evidence.vendor_name`
   - `evidence.status == "APPROVED"`
2. **Role-Based Access Control (RBAC)**:
   - Validates `agent_role` against `RolePermissionMatrix`.
   - Example: `Junior_Agent` $\notin \{\text{EXECUTE\_PAYMENT}, \text{DELETE\_RECORD}\}$.
3. **Enterprise Policy Rules**:
   - `RULE_FIN_01`: `amount > 10000 -> requires_manager_approval`
   - `RULE_FIN_02`: `daily_total + amount <= daily_budget_limit`
   - `RULE_OPS_01`: `execution_time between 09:00 and 18:00 IST`

### 3.5 Subsystem 5: Multi-Factor Risk Assessment Engine
Computes continuous risk score $R \in [0.0, 1.0]$:
$$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$$

**Weights Configuration**:
- $w_f = 0.25$ (Financial Impact)
- $w_i = 0.20$ (Irreversibility)
- $w_p = 0.20$ (Permission Sensitivity)
- $w_u = 0.15$ (Evidence Uncertainty)
- $w_c = 0.20$ (Contradiction / Mismatch Severity)
$$\sum w_i = 1.0$$

**Variable Formulations**:
- **Financial Impact ($F$)**:
  $$F = \min\left(1.0, \frac{\text{amount}}{100,000}\right)$$
- **Irreversibility ($I$)**:
  $$I = \begin{cases} 1.0 & \text{if action is WIRE\_TRANSFER, PERMANENT\_DELETE} \\ 0.6 & \text{if action is UPDATE\_RECORD, SEND\_EXTERNAL\_EMAIL} \\ 0.1 & \text{if action is READ\_ONLY} \end{cases}$$
- **Permission Sensitivity ($P$)**:
  $$P = \begin{cases} 0.9 & \text{if role requires Admin/Executive signoff} \\ 0.5 & \text{if role requires Manager signoff} \\ 0.1 & \text{if role is Standard / Read-Only} \end{cases}$$
- **Evidence Uncertainty ($U$)**:
  $$U = 1.0 - \text{evidence\_confidence\_score}$$
- **Contradiction / Mismatch ($C$)**:
  $$C = \begin{cases} 1.0 & \text{if exact parameter mismatch found} \\ 0.5 & \text{if fuzzy or partial match} \\ 0.0 & \text{if all parameters perfectly match} \end{cases}$$

### 3.6 Subsystem 6: Adaptive Verification Tier Router
```
                    Calculated Risk (R)
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
       R <= 0.35      0.35 < R <= 0.70     R > 0.70
         FAST             STRONG             DEEP
       VERIFIER          VERIFIER          VERIFIER
```

- **Tier 1 (Fast Verifier)**:
  - Latency Target: $<150\text{ms}$
  - Checks: Schema check + RBAC lookup + Cached parameter match.
  - Model: None (Pure deterministic Python code).
- **Tier 2 (Strong Verifier)**:
  - Latency Target: $<800\text{ms}$
  - Checks: Tier 1 + DB live grounding + Fast LLM semantic confirmation (Gemini 1.5 Flash / GPT-4o-Mini).
  - Purpose: Catch subtle entity variations, email text intent, and policy ambiguities.
- **Tier 3 (Deep Verifier)**:
  - Latency Target: $<2000\text{ms}$
  - Checks: Tier 2 + Multi-source cross-verification + High-capacity model (Gemini 1.5 Pro / GPT-4o) adversarial stress-test + Automatic escalation triggers for high financial risk.

### 3.7 Subsystem 7: Tri-State Decision Gate
- **EXECUTE**:
  - Condition: No deterministic contradictions, policy verified, $R < 0.70$ (or verified at Deep tier with valid approval), role authorized.
- **ESCALATE**:
  - Condition: Insufficient evidence ($U > 0.50$), policy requires manual signoff (`amount > ₹10,000`), or $R > 0.70$ without pre-existing approval.
  - Dispatches action to `escalation_queue` with snapshot for human reviewer.
- **BLOCK**:
  - Condition: Direct parameter contradiction ($C = 1.0$), explicit policy violation, unauthorized agent role, or detected prompt injection in arguments.

---

## 4. Performance, Concurrency & Latency Budgets

```
Action Ingestion ──> Normalizer ──> Evidence Lookup ──> Risk Eval ──> Tier Verification ──> Decision Gate
     [10ms]             [15ms]           [40ms]           [15ms]        [Fast: 50ms]            [10ms]
                                                                        [Strong: 650ms]
                                                                        [Deep: 1600ms]
```

### Total End-to-End Latency Targets:
- **Fast Tier (P95)**: $\le 140\text{ms}$
- **Strong Tier (P95)**: $\le 760\text{ms}$
- **Deep Tier (P95)**: $\le 1750\text{ms}$
- **VERIACT Blended Workload Average**: $\approx 420\text{ms}$ (Assuming 60% Low, 25% Medium, 15% High distribution).

---

## 5. Security & Isolation Specifications

1. **Prompt Injection Containment**: Evidence retrieved from mock ERP or PDFs is tagged with `<untrusted_evidence_data>` XML fences and never placed in system instruction positions.
2. **HMAC Action Sealing**: Every `NormalizedAction` is stamped with a SHA-256 payload digest. Any tampering between proposal and execution invalidates the verification token.
3. **Idempotency & Replay Protection**: Each action proposal requires a unique `action_id` (UUIDv4). Replay attempts return cached decisions within a 5-minute sliding window.
