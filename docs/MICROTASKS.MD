# Team Task Allocation & 48-Hour Sprint Roadmap — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Team:** Aman, Vedesh, Aryan  
> **Target Forum:** IIT Bombay Techfest / Inter-IIT Hackathon  
> **Sprint Horizon:** 48 Hours / 5 Structured Execution Phases  
> **Status:** APPROVED & LOCKED FOR EXECUTION  

---

## 1. Executive Team Ownership Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       VERIACT CORE TEAM OWNERSHIP                                      │
├──────────────────────────────┬──────────────────────────────────────────┬──────────────────────────────┤
│            AMAN              │                 VEDESH                   │            ARYAN             │
│   Runtime & Interceptor      │        Ground Truth & Policy             │     Risk, Benchmark & UI     │
├──────────────────────────────┼──────────────────────────────────────────┼──────────────────────────────┤
│ • LangGraph Agent & Tools    │ • Enterprise Mock ERP (SQLite / Postgres)│ • Mathematical Risk Engine   │
│ • Pre-Execution Interceptor  │ • Deterministic Grounding Engine         │ • Adaptive Tier Router       │
│ • Action Normalizer          │ • Policy Engine & AST Evaluator          │ • VERIACT-ASB Benchmark (250)│
│ • Decision Gate (Exec/Esc/Blk│ • RBAC Role Matrix & Privilege Checks    │ • 4-Baseline Comparative Eval│
│ • HMAC Execution Tokens      │ • Anti-Injection Sanitization (<xml>)    │ • Next.js Command Center UI  │
│ • FastAPI Gateway Routers    │ • Document Ingestion & PDF Parser        │ • Trace Drawer & Radar Visual│
│ • Human Escalation Backend   │ • Vector Policy Index (FAISS/Chroma)     │ • Pareto Curve & Sandbox     │
└──────────────────────────────┴──────────────────────────────────────────┴──────────────────────────────┘
```

---

## 2. Phase-by-Phase Team Work Breakdown Structure (WBS)

```
[Phase 1: Foundations] ──> [Phase 2: Core Engines] ──> [Phase 3: Tiers & Decision] ──> [Phase 4: Benchmark & UI] ──> [Phase 5: Rehearsal & Freeze]
    (Hours 0 - 8)               (Hours 8 - 20)                 (Hours 20 - 32)                 (Hours 32 - 42)                 (Hours 42 - 48)
```

---

### PHASE 1: Architecture Freeze, Schema Contracts & Foundations (Hours 0 – 8)
*Goal: Establish shared Pydantic data schemas, seed the controlled enterprise database, spin up the base Next.js application, and establish the initial 25 benchmark fixtures.*

#### 👨‍💻 Aman (Runtime & Interceptor Lead)
- [ ] **Task AMAN-101**: Setup LangGraph agent skeleton with mock execution tools (`make_payment`, `read_invoice`, `delete_record`).
- [ ] **Task AMAN-102**: Initialize FastAPI backend repository structure (`backend/app/api`, `backend/app/engine`, `backend/app/core`).
- [ ] **Task AMAN-103**: Define the canonical `ProposedToolCall` and `NormalizedAction` Pydantic models in coordination with Vedesh and Aryan.
- *Deliverable*: Running LangGraph agent script that generates raw tool calls, and running FastAPI skeleton on port 8000.
- *Verification Command*: `pytest tests/unit/test_agent_skeleton.py`

#### 👨‍💻 Vedesh (Ground Truth & Ingestion Lead)
- [ ] **Task VEDESH-101**: Setup SQLAlchemy models and SQLite database schema for `invoices`, `vendors`, `agents`, `policies`.
- [ ] **Task VEDESH-102**: Write database seed script (`backend/app/mock_env/seed_db.py`) populating the **10 realistic enterprise vendors and invoices** (e.g., `INV-1921` for ₹18,500, `INV-404` for ₹9,200).
- [ ] **Task VEDESH-103**: Define the 5 core enterprise policy rules in `policies` table (high-value payment signoff > ₹10k, suspended vendor blacklist, etc.).
- *Deliverable*: Seeded `veriact_enterprise.db` SQLite file with 10 vendors, 10 invoices, 4 agent roles, and 5 policies.
- *Verification Command*: `python -m app.mock_env.seed_db && python -m app.mock_env.verify_seed`

#### 👨‍💻 Aryan (Risk, Benchmark & UI Lead)
- [ ] **Task ARYAN-101**: Implement the mathematical risk schema (`RiskBreakdown`, `RiskWeights`) with bounds $R \in [0.0, 1.0]$.
- [ ] **Task ARYAN-102**: Initialize the Next.js 14 project (`frontend/`) with Tailwind CSS, dark-mode color tokens (`#0B0F19`, `#111827`, emerald, amber, rose), and Lucide icons.
- [ ] **Task ARYAN-103**: Create the first **25 seed test fixtures** for `VERIACT-ASB` covering baseline parameter mismatches and hallucinated entities.
- *Deliverable*: Next.js dev server rendering the base security layout; JSON fixtures in `backend/benchmark/data/seed_25.json`.
- *Verification Command*: `cd frontend && npm run dev` (verified on `localhost:3000`)

> **Phase 1 Standup Checkpoint (Hour 8)**:  
> Aman's agent outputs raw tool calls; Vedesh's DB returns verified invoice records for `INV-1921`; Aryan's UI shell displays the dark dashboard frame.

---

### PHASE 2: Core Verification Engines & Interception Layer (Hours 8 – 20)
*Goal: Build the pre-execution interception gate, deterministic parameter grounding engine, RBAC policy evaluator, and multi-factor risk calculator.*

#### 👨‍💻 Aman (Runtime & Interceptor Lead)
- [ ] **Task AMAN-201**: Implement `ActionNormalizer` class converting raw tool arguments into canonical `NormalizedAction` payloads.
- [ ] **Task AMAN-202**: Construct the core `VeriactInterceptor` middleware wrapping LangGraph's `ToolNode`. Ensure tools are halted in memory *before* execution.
- [ ] **Task AMAN-203**: Build FastAPI endpoint `POST /api/v1/intercept/action` integrating Normalizer, Vedesh's Grounding Engine, and Aryan's Risk Engine.
- [ ] **Task AMAN-204**: Implement HMAC-SHA256 **Execution Token** generator and validator (30-second TTL) bound to canonical payload hash.
- *Deliverable*: Interception middleware that catches tool proposals and issues signed tokens or stops execution.
- *Verification Command*: `pytest tests/integration/test_interceptor_pipeline.py`

#### 👨‍💻 Vedesh (Ground Truth & Ingestion Lead)
- [ ] **Task VEDESH-201**: Implement `ParameterGroundingEngine`: deterministic exact equality (`proposed == actual`), numeric tolerance bounds, and canonical string matcher.
- [ ] **Task VEDESH-202**: Implement `RBACPolicyEngine` matching `agent_role` against permitted actions (e.g. `JUNIOR_ASSISTANT` cannot execute wire transfers).
- [ ] **Task VEDESH-203**: Build the Policy Rule Evaluator evaluating JSON AST condition expressions (e.g. `amount > 10000 -> ESCALATE`).
- [ ] **Task VEDESH-204**: Implement document sanitization filters (`SCRAPING_SPEC.MD`) stripping zero-width characters and wrapping external text in `<untrusted_evidence_data>` XML fences.
- *Deliverable*: Native Python grounding and policy modules executing in $< 15\text{ms}$ with zero model hallucinations.
- *Verification Command*: `pytest tests/unit/test_grounding.py && pytest tests/unit/test_policy.py`

#### 👨‍💻 Aryan (Risk, Benchmark & UI Lead)
- [ ] **Task ARYAN-201**: Implement the complete multi-factor mathematical Risk Engine:
  $$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$$
- [ ] **Task ARYAN-202**: Write unit tests for risk factor calibration: assert $R = 0.94$ for ₹25k invoice mismatch, and $R \le 0.10$ for read-only status query.
- [ ] **Task ARYAN-203**: Build the **Live Action Stream Table** component in Next.js with real-time rows, status badges (Emerald/Amber/Rose), and animated risk meters.
- [ ] **Task ARYAN-204**: Expand `VERIACT-ASB` to 75 test scenarios across categories CAT-01 through CAT-04.
- *Deliverable*: Risk calculation engine and real-time Action Stream UI table rendering simulated action payloads.
- *Verification Command*: `pytest tests/unit/test_risk_engine.py`

> **Phase 2 Standup Checkpoint (Hour 20)**:  
> End-to-end integration demo: Aman feeds invoice payment proposal into interceptor; Vedesh's grounding engine flags the ₹25k vs ₹18.5k mismatch; Aryan's risk engine outputs $R = 0.94$; UI table reflects high-risk state.

---

### PHASE 3: Risk-Adaptive Tiering, Escalation Gate & Baseline Benchmarking (Hours 20 – 32)
*Goal: Implement the 3-tier adaptive router (Fast, Strong, Deep), the tri-state decision gate (Execute, Escalate, Block), human review queue, and comparative baselines.*

#### 👨‍💻 Aman (Runtime & Interceptor Lead)
- [ ] **Task AMAN-301**: Implement the **Tri-State Decision Gate** (`EXECUTE`, `ESCALATE`, `BLOCK`).
- [ ] **Task AMAN-302**: Build the **Human Escalation Queue** backend:
  - `GET /api/v1/escalation/queue` (list pending actions)
  - `POST /api/v1/escalation/{id}/decision` (`APPROVE` or `REJECT` with reviewer signoff notes)
- [ ] **Task AMAN-303**: Connect Human Approval loop: when manager approves in queue, generate override execution token and dispatch action to tool.
- [ ] **Task AMAN-304**: Build the `ActionTraceLogger` recording immutable audit logs with SHA-256 payload hashes.
- *Deliverable*: Full tri-state decision gate and functional Human-in-the-Loop review backend.
- *Verification Command*: `pytest tests/integration/test_decision_gate.py`

#### 👨‍💻 Vedesh (Ground Truth & Ingestion Lead)
- [ ] **Task VEDESH-301**: Build **Tier 1 (Fast Verifier)**: schema validation + cache + RBAC check (target $< 150\text{ms}$).
- [ ] **Task VEDESH-302**: Build **Tier 2 (Strong Verifier)**: live ERP database grounding + fast semantic LLM check (Gemini 1.5 Flash / GPT-4o-Mini) (target $< 800\text{ms}$).
- [ ] **Task VEDESH-303**: Build **Tier 3 (Deep Verifier)**: multi-source cross-referencing + deep LLM (Gemini 1.5 Pro / GPT-4o) + policy AST evaluation (target $< 2000\text{ms}$).
- [ ] **Task VEDESH-304**: Setup FAISS / Chroma in-memory vector store indexing the Corporate Procurement Handbook and policy SOPs.
- *Deliverable*: Modular 3-tier verifier classes adhering to latency budgets.
- *Verification Command*: `pytest tests/integration/test_verification_tiers.py`

#### 👨‍💻 Aryan (Risk, Benchmark & UI Lead)
- [ ] **Task ARYAN-301**: Implement the **Risk-Adaptive Tier Router**:
  - $R \le 0.35 \to$ Route to Fast Tier
  - $0.35 < R \le 0.70 \to$ Route to Strong Tier
  - $R > 0.70 \to$ Route to Deep Tier
- [ ] **Task ARYAN-302**: Implement Baseline A (No Guardrail) and Baseline B (LLM-as-a-Judge) harnesses.
- [ ] **Task ARYAN-303**: Build Baseline C (Always-Deep) and VERIACT Adaptive runners in `benchmark/runner.py`.
- [ ] **Task ARYAN-304**: Build the **Auditable Action Trace Drawer** in Next.js (Side slide-out rendering the 5-step verification breakdown, parameter diff table, and risk radar—**strictly without raw CoT tokens**).
- *Deliverable*: Adaptive router, baseline runners, and interactive Trace Drawer in UI.
- *Verification Command*: `python -m benchmark.runner --size 50 --dry-run`

> **Phase 3 Standup Checkpoint (Hour 32)**:  
> Action routing works dynamically across all 3 tiers. Trace Drawer renders clean parameter diffs. Escalation queue holds high-value transactions awaiting manager review.

---

### PHASE 4: Full VERIACT-ASB Benchmark Suite & Mission Control UI Integration (Hours 32 – 42)
*Goal: Scale benchmark to 250 test cases across 10 failure classes, run full comparative evaluation, generate Pareto curve, and finalize command center views.*

#### 👨‍💻 Aman (Runtime & Interceptor Lead)
- [ ] **Task AMAN-401**: Build API endpoints for analytics and live stats: `GET /api/v1/analytics/stats`.
- [ ] **Task AMAN-402**: Implement fail-closed circuit breakers and timeout protections (`ERROR_HANDLING.MD`): default to `BLOCK` for financial actions on timeout.
- [ ] **Task AMAN-403**: Build the **Live Interactive Attack Sandbox API** (`POST /api/v1/sandbox/simulate`) allowing judges to trigger custom red-team payloads.
- [ ] **Task AMAN-404**: Wire Server-Sent Events (SSE) or polling endpoint for streaming real-time action telemetry to the frontend.
- *Deliverable*: Real-time analytics endpoints, fail-closed guards, and live sandbox simulation backend.
- *Verification Command*: `pytest tests/e2e/test_gateway_resilience.py`

#### 👨‍💻 Vedesh (Ground Truth & Ingestion Lead)
- [ ] **Task VEDESH-401**: Expand ground truth mock data to include edge cases: cancelled invoices, draft invoices, suspended vendors, foreign currency transactions.
- [ ] **Task VEDESH-402**: Implement PDF invoice parser (`SCRAPING_SPEC.MD`) capable of extracting structured tables from sample PDF files.
- [ ] **Task VEDESH-403**: Test and harden anti-prompt-injection defense against complex payloads (adversarial roleplay, instruction override strings in invoice notes).
- [ ] **Task VEDESH-404**: Build the **Ground Truth Explorer API** (`GET /api/v1/ground-truth/invoices`, `GET /api/v1/ground-truth/vendors`) for compliance auditor inspection.
- *Deliverable*: Robust multi-entity ERP database and hardened anti-injection sanitization engine.
- *Verification Command*: `pytest tests/security/test_prompt_injection.py`

#### 👨‍💻 Aryan (Risk, Benchmark & UI Lead)
- [ ] **Task ARYAN-401**: Scale `VERIACT-ASB` to the full **250 adversarial test scenarios** across all 10 failure categories.
- [ ] **Task ARYAN-402**: Run full benchmark evaluation across all 4 baselines; export metrics (Safety Recall: 97.2%, False Block Rate: 2.8%, Latency: 384ms, Cost: $1.45).
- [ ] **Task ARYAN-403**: Build the **Benchmark Visualizer & Pareto Frontier Chart** using Recharts in Next.js (Safety Recall vs. Latency/Cost).
- [ ] **Task ARYAN-404**: Build the **Human Escalation Review Queue** UI view with one-click "Approve" and "Reject" buttons connected to Aman's API.
- [ ] **Task ARYAN-405**: Build the **Interactive Attack Sandbox UI** allowing judges to click 4 preset attack scenarios (Parameter Mismatch, Threshold Escalation, Prompt Injection, Low-Risk Fast Tier).
- *Deliverable*: Complete 250-case benchmark dataset, empirical results, and fully functional Command Center dashboard.
- *Verification Command*: `python -m benchmark.runner --size 250 --format json > results.json`

> **Phase 4 Standup Checkpoint (Hour 42)**:  
> All 250 benchmark cases evaluated. Pareto frontier chart renders live in UI. Human review queue resolves live in the dashboard. Sandbox executes presets seamlessly.

---

### PHASE 5: Hackathon Readiness, Live Attack Sandbox, Offline Redundancy & Pitch Polish (Hours 42 – 48)
*Goal: Harden offline fail-safe redundancy, run second-by-second rehearsal of 4-minute demo script, record 4K backup walkthrough video, and freeze code.*

#### 👨‍💻 Aman (Runtime & Interceptor Lead)
- [ ] **Task AMAN-501**: Build the offline fail-safe demonstration runner script (`scripts/demo_offline.py`) that operates with local SQLite and mock fixtures if venue Wi-Fi fails.
- [ ] **Task AMAN-502**: Run pre-flight backend checklist (`PRODUCTION_CHECKLIST.MD`): verify environment variables, database locks, and port bindings.
- [ ] **Task AMAN-503**: Assist with live demo execution during presentation rehearsal.
- *Deliverable*: Zero-dependency offline demo script running locally in $< 1\text{ second}$.

#### 👨‍💻 Vedesh (Ground Truth & Ingestion Lead)
- [ ] **Task VEDESH-501**: Verify data integrity of all 10 vendor records and 10 invoices; ensure no dangling foreign keys or unseeded dependencies.
- [ ] **Task VEDESH-502**: Prepare technical defense talking points for judge Q&A:
  - *"Why not just use an LLM judge?"* $\to$ Defend deterministic parameter grounding and external truth.
  - *"Isn't this just NeMo Guardrails?"* $\to$ Defend tool-level pre-execution grounding vs. conversational token filtering.
- [ ] **Task VEDESH-503**: Clean and document database seeding scripts and local schema files.
- *Deliverable*: Polished ground truth seeders and documented judge Q&A defense answers.

#### 👨‍💻 Aryan (Risk, Benchmark & UI Lead)
- [ ] **Task ARYAN-501**: Record a 4K 60fps backup demo walkthrough video (`demo_backup_video.mp4`) showing the 4 demo scenarios and Pareto curve.
- [ ] **Task ARYAN-502**: Finalize the 10-slide pitch presentation deck adhering to the story arc:
  - *Slide 1*: "What happens when an AI agent is 99% confident and 100% wrong?"
  - *Slide 2*: Think $\to$ Act vs. Think $\to$ Verify $\to$ Act.
  - *Slide 3*: Pre-execution verification gateway.
  - *Slide 4*: System architecture.
  - *Slide 5*: Risk-adaptive routing innovation.
  - *Slide 6*: 10 attack classes (`VERIACT-ASB`).
  - *Slide 7*: Baseline evaluation methodology.
  - *Slide 8*: Empirical results & Pareto frontier ($97.2\%$ recall at $384\text{ms}$).
  - *Slide 9*: Live 4-scenario demonstration.
  - *Slide 10*: Vision & enterprise impact.
- [ ] **Task ARYAN-503**: Conduct dry runs of the 4-minute demo script timing each segment to the second.
- *Deliverable*: High-res backup video, completed slide deck, and rehearsed 4-minute presentation.

---

## 3. Team Communication & Daily Sync Protocol

- **Sync Checkpoints**:
  1. **Sync 1 (Hour 8)**: Schema validation, seed data review, UI shell review.
  2. **Sync 2 (Hour 20)**: Interceptor and Grounding integration check.
  3. **Sync 3 (Hour 32)**: Adaptive router and Escalation Queue review.
  4. **Sync 4 (Hour 42)**: Benchmark results freeze and Pareto curve validation.
  5. **Sync 5 (Hour 46)**: Final dress rehearsal and code freeze.
- **Git Branching Strategy**:
  - `main`: Protected production branch.
  - `feature/aman-interceptor`: Aman's runtime and gateway commits.
  - `feature/vedesh-grounding`: Vedesh's DB, policy, and grounding commits.
  - `feature/aryan-risk-ui`: Aryan's risk engine, benchmark, and UI commits.
