# AMAN — Master Task Allocation & Execution Roadmap

> **Owner:** Aman  
> **Role:** System Architect & Runtime Interceptor Lead  
> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Repository:** [https://github.com/cooldude698/IITBombay](https://github.com/cooldude698/IITBombay)  
> **Git Feature Branch:** `feature/aman-runtime-interceptor`  

---

## 🎯 Primary Domain & Responsibilities
Aman is responsible for the **Agent Execution Loop**, **Pre-Execution Interception Middleware**, **Action Normalization**, **Tri-State Decision State Machine**, **Cryptographic HMAC Execution Tokens**, and the **Human-in-the-Loop Escalation Backend**.

```
[User Request] ──> [LangGraph Agent] ──> 🛑 [Aman's Interceptor Gate] ──> [Tool Execution]
                                                │
                                    [EXECUTE | ESCALATE | BLOCK]
```

---

## 📅 PHASE 1: Architecture Freeze & LangGraph Agent Setup (Hours 0 – 8)

### Objectives
Establish shared Pydantic data schemas, set up the FastAPI service skeleton, and build the initial LangGraph agent loop with mock tools.

### Task Checklist
- [x] **Task AMAN-101: Repository & FastAPI Initialization**
  - Create backend directory tree (`backend/app/{api,core,engine,models,mock_env}`).
  - Setup `backend/app/main.py` with FastAPI instance and CORS middleware.
- [x] **Task AMAN-102: Shared Pydantic Schema Contracts**
  - Define `ProposedToolCall`, `NormalizedAction`, `ActionType`, `VerificationTier`, `Verdict`, `RiskBreakdown`, `VerificationResult`, `ActionTrace`, etc. in `backend/app/models/schemas.py`.
- [x] **Task AMAN-103: LangGraph Agent Loop & Mock Tools**
  - Construct LangGraph StateGraph & autonomous agent in `backend/app/engine/agent.py`.
  - Implement real mock tools requiring HMAC execution tokens:
    - `make_payment(token, vendor, amount, invoice)`
    - `read_invoice(token, invoice_id)`
    - `delete_record(token, table, record_id)`
  - Verify that the agent can reason over a prompt and propose a tool invocation.

#### Verification & Tests:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests/unit/test_schemas.py -v
python3 -m app.engine.agent --test-run
```

---

## 📅 PHASE 2: Action Normalizer & Pre-Execution Interception (Hours 8 – 20)

### Objectives
Ensure tool calls are intercepted in memory **BEFORE** touching real APIs; normalize diverse tool payloads into canonical schemas; implement HMAC-SHA256 execution tokens.

### Task Checklist
- [x] **Task AMAN-201: Action Normalization Engine**
  - Implement `ActionNormalizer` in `backend/app/engine/normalizer/normalizer.py`.
  - Canonicalize diverse tool arguments into standard `NormalizedAction`.
- [x] **Task AMAN-202: Pre-Execution Interception Hook**
  - Construct `VeriactInterceptor` middleware wrapping tool dispatch.
  - **Invariant Enforced**: Real tool execution is blocked until an explicit `EXECUTE` verdict is reached.
- [x] **Task AMAN-203: Core Gateway API Endpoint**
  - Implement `POST /api/v1/intercept/action`:
    1. Receives `ProposedToolCall`
    2. Calls `ActionNormalizer`
    3. Fetches ground truth from ERP/mock database
    4. Computes risk from multi-factor risk evaluator
    5. Returns tri-state verdict with HMAC execution token on approval
- [x] **Task AMAN-204: Cryptographic HMAC Execution Tokens**
  - Implement `backend/app/core/crypto.py`:
    - `generate_execution_token(action_id, tool_name, params)` (HMAC-SHA256, 30-second TTL)
    - `verify_execution_token(token, action_id, tool_name, params)`
  - Mock tools strictly reject any execution call lacking a valid cryptographic token.

#### Verification & Tests:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests/integration/test_interceptor_pipeline.py -v
```

---

## 📅 PHASE 3: Tri-State Decision Gate & Human Escalation (Hours 20 – 32)

### Objectives
Build the decision engine returning `EXECUTE`, `ESCALATE`, or `BLOCK`; implement the Human-in-the-Loop review queue backend; enable manager overrides.

### Task Checklist
- [x] **Task AMAN-301: Tri-State Decision Gate Engine**
  - Implement `backend/app/engine/decision/gate.py`.
  - Evaluate tier verification outputs and risk score:
    - **🟢 EXECUTE**: Issue signed execution token.
    - **🟡 ESCALATE**: Route to human review queue; return status `HELD_FOR_REVIEW`.
    - **🔴 BLOCK**: Reject action with structured failure explanation (`ERR_CONTRADICTION`, `ERR_POLICY_BREACH`).
- [x] **Task AMAN-302: Human Escalation Queue Backend**
  - Implement `backend/app/api/v1/escalation.py` and `backend/app/engine/decision/escalation_queue.py`:
    - `GET /api/v1/escalation/queue`: Returns all pending actions.
    - `POST /api/v1/escalation/{item_id}/decision`: Accepts `decision: "APPROVE" | "REJECT"`, reviewer ID, and notes.
- [x] **Task AMAN-303: Manager Approval Resume Flow**
  - When an escalated action is approved by a manager, generate an override HMAC token and dispatch tool execution.
- [x] **Task AMAN-304: Auditable Trace Logger**
  - Implement `backend/app/engine/trace_logger.py`:
    - Writes immutable audit traces.
    - Computes `payload_hash = sha256(action_id + params + verdict)`.

#### Verification & Tests:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests/unit/test_crypto.py -v
```

---

## 📅 PHASE 4: Resilience, Telemetry Stream & Sandbox API (Hours 32 – 42)

### Objectives
Implement fail-closed circuit breakers and timeouts; provide real-time telemetry stream for Aryan's Next.js frontend; build backend for judge interactive sandbox.

### Task Checklist
- [x] **Task AMAN-401: Fail-Closed Circuit Breakers & Timeouts**
  - Implement strict latency timeouts in `backend/app/core/resilience.py`:
    - Fast Tier timeout: 200ms
    - Strong Tier timeout: 1000ms
    - Deep Tier timeout: 2500ms
  - Under timeout or external exception, **STRICTLY FAIL-CLOSED** to `BLOCK` for financial actions or `ESCALATE` for read-only actions.
- [x] **Task AMAN-402: Analytics & Live Telemetry Endpoint**
  - Implement `GET /api/v1/analytics/stats`:
    - Total actions today, verified count, escalated count, blocked count, average latency.
- [x] **Task AMAN-403: Interactive Attack Sandbox API**
  - Implement `POST /api/v1/sandbox/simulate`:
    - Allows judges to submit arbitrary tool actions (e.g. ₹25k payment) and receive instant trace logs.
- [x] **Task AMAN-404: Telemetry Streaming Hook**
  - Implement Server-Sent Events (SSE) `GET /api/v1/telemetry/stream` and `GET /api/v1/actions/stream` for pushing live actions to Aryan's UI table.

#### Verification & Tests:
```bash
PYTHONPATH=backend python3 -m pytest backend/tests/e2e/test_gateway_resilience.py -v
```

---

## 📅 PHASE 5: Offline Redundancy, Rehearsal & Code Freeze (Hours 42 – 48)

### Objectives
Harden the system against venue Wi-Fi failure with a zero-dependency offline runner; assist in presentation rehearsals; freeze code on `main`.

### Task Checklist
- [x] **Task AMAN-501: Zero-Dependency Offline Demo Script**
  - Write `scripts/demo_offline.py`:
    - Runs completely offline against local SQLite.
    - Executes the 4 main demo scenarios in under 1 second.
    - Prints formatted ANSI color traces to terminal if web UI is disconnected.
- [x] **Task AMAN-502: Pre-Flight Backend Checklist**
  - Verify all environment variables and port bindings (port 8000 for backend).
  - Ensure zero port conflicts or dangling background workers.
- [x] **Task AMAN-503: Code Freeze & Git Tag**
  - Feature merged into `main`.
  - Tag release `v1.0.0-hackathon`.

#### Verification & Tests:
```bash
python3 scripts/demo_offline.py
```
