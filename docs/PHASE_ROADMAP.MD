# Phase-by-Phase Execution Roadmap — VERIACT

> **Team Members:** Aman, Vedesh, Aryan  
> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Repository:** [https://github.com/cooldude698/IITBombay](https://github.com/cooldude698/IITBombay)  
> **Timeline:** 48-Hour Hackathon Delivery  

---

## Quick Reference: Who Owns What?

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     CORE RESPONSIBILITIES                                        │
├────────────────────────────┬────────────────────────────────────┬────────────────────────────────┤
│       👨‍💻 AMAN              │            👨‍💻 VEDESH              │           👨‍💻 ARYAN             │
│   Runtime & Interceptor    │      Ground Truth & Policy         │      Risk, Benchmark & UI      │
├────────────────────────────┼────────────────────────────────────┼────────────────────────────────┤
│ • LangGraph Agent & Tools  │ • SQLite ERP DB & 10 Seed Invoices │ • Mathematical Risk Engine     │
│ • Pre-Execution Middleware │ • Deterministic Grounding Engine   │ • Adaptive Tier Router         │
│ • Action Normalizer        │ • Policy AST & Rule Evaluator      │ • VERIACT-ASB (250 Cases)      │
│ • Decision Gate & HMAC     │ • RBAC Role Matrix & Caps          │ • 4-Baseline Comparative Eval  │
│ • FastAPI Gateway Routers  │ • Anti-Injection Sanitization      │ • Next.js Command Center UI    │
│ • Escalation Queue Backend │ • Document Ingestion & PDF Parser  │ • Trace Drawer & Pareto Curve  │
│ • Offline Fail-Safe Runner │ • Vector Policy Store (FAISS)      │ • Live Interactive Sandbox     │
└────────────────────────────┴────────────────────────────────────┴────────────────────────────────┘
```

---

## 📅 PHASE 1: Architecture Freeze & Foundations (Hours 0 – 8)

### Target Milestone:
Shared Pydantic schemas established, SQLite mock ERP seeded with 10 invoices/vendors, basic Next.js dark-mode UI shell running, initial 25 benchmark fixtures created.

### Task Checklist:
- **Aman**:
  - [ ] Initialize FastAPI app layout in `backend/app/main.py`.
  - [ ] Build LangGraph agent loop with mock tools (`make_payment`, `read_invoice`, `delete_record`).
  - [ ] Define shared `ProposedToolCall` and `NormalizedAction` schemas.
- **Vedesh**:
  - [ ] Create SQLAlchemy database tables in `backend/app/mock_env/models.py`.
  - [ ] Write `seed_db.py` seeding the 10 vendors (e.g. `ABC Technologies`) and 10 invoices (e.g. `INV-1921` for ₹18,500).
  - [ ] Insert the 5 enterprise policies (High-value signoff > ₹10k, suspended vendor blacklist, etc.).
- **Aryan**:
  - [ ] Implement `RiskBreakdown` schema with normalized factors ($R \in [0, 1]$).
  - [ ] Initialize Next.js 14 project in `frontend/` with Tailwind CSS dark theme tokens (`#0B0F19`, `#111827`, emerald, amber, rose).
  - [ ] Create initial 25 adversarial benchmark JSON fixtures in `backend/benchmark/data/`.

**Phase 1 Gate Criteria**:
- `python -m app.mock_env.seed_db` populates SQLite database without errors.
- `cd frontend && npm run dev` loads dark theme dashboard frame at `http://localhost:3000`.

---

## 📅 PHASE 2: Core Verification Engines & Interception Layer (Hours 8 – 20)

### Target Milestone:
Pre-execution interception halts actions in memory; deterministic grounding catches parameter mismatches; RBAC blocks unauthorized roles; risk engine outputs calibrated continuous scores.

### Task Checklist:
- **Aman**:
  - [ ] Implement `ActionNormalizer` mapping varied tool parameters into canonical format.
  - [ ] Build `VeriactInterceptor` middleware hooking LangGraph `ToolNode`. Ensure real tool is NEVER executed without verification.
  - [ ] Build `POST /api/v1/intercept/action` route.
  - [ ] Implement HMAC-SHA256 Execution Token generator (30-second TTL).
- **Vedesh**:
  - [ ] Build `ParameterGroundingEngine`: exact parameter match (`proposed == actual`), range validator, and tolerance checks.
  - [ ] Build `RBACPolicyEngine` verifying agent role against permitted actions list.
  - [ ] Implement JSON AST Policy Rule Evaluator for spending caps.
  - [ ] Build anti-prompt-injection sanitizer wrapping extracted text in `<untrusted_evidence_data>` tags.
- **Aryan**:
  - [ ] Code the complete mathematical risk formula:
    $$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$$
  - [ ] Calibrate weights ($w_f=0.25, w_i=0.20, w_p=0.20, w_u=0.15, w_c=0.20$).
  - [ ] Build the Next.js **Live Action Stream Table** component with color-coded status badges and risk meters.
  - [ ] Expand benchmark fixtures to 75 scenarios (Categories CAT-01 through CAT-04).

**Phase 2 Gate Criteria**:
- Submitting an invoice payment of ₹25,000 for `INV-1921` (approved for ₹18,500) triggers a contradiction ($C = 1.0$), risk score $R = 0.94$, and is halted before the banking tool.

---

## 📅 PHASE 3: Risk-Adaptive Tiering & Human Escalation (Hours 20 – 32)

### Target Milestone:
Risk-adaptive routing dynamically sends actions to Fast ($<150\text{ms}$), Strong ($<800\text{ms}$), or Deep ($<2000\text{ms}$) verifiers; tri-state decision gate issues `EXECUTE`, `ESCALATE`, or `BLOCK`; human review queue captures threshold violations.

### Task Checklist:
- **Aman**:
  - [ ] Implement `DecisionGate` outputting `EXECUTE`, `ESCALATE`, or `BLOCK`.
  - [ ] Build Human Escalation API (`GET /api/v1/escalation/queue`, `POST /api/v1/escalation/{id}/decision`).
  - [ ] Implement manager approval resume flow: approving action issues signed execution token to dispatch tool.
  - [ ] Build `ActionTraceLogger` recording immutable audit logs with SHA-256 payload hashes.
- **Vedesh**:
  - [ ] Build **Tier 1 (Fast Verifier)**: schema check + cache + RBAC in $< 150\text{ms}$.
  - [ ] Build **Tier 2 (Strong Verifier)**: live ERP lookup + fast semantic LLM (Gemini 1.5 Flash / GPT-4o-Mini) in $< 800\text{ms}$.
  - [ ] Build **Tier 3 (Deep Verifier)**: multi-source cross-referencing + deep LLM (Gemini 1.5 Pro / GPT-4o) + policy AST evaluation in $< 2000\text{ms}$.
  - [ ] Setup FAISS vector store indexing corporate procurement SOPs.
- **Aryan**:
  - [ ] Implement **Risk-Adaptive Tier Router**:
    - $R \le 0.35 \to$ Fast Tier
    - $0.35 < R \le 0.70 \to$ Strong Tier
    - $R > 0.70 \to$ Deep Tier
  - [ ] Build Baseline A (No Guardrail) and Baseline B (LLM-as-Judge) evaluation runners.
  - [ ] Build Next.js **Auditable Action Trace Drawer** displaying parameter diff matrix, evidence, and risk radar (**strictly without raw CoT**).

**Phase 3 Gate Criteria**:
- Low-risk read actions finish in $< 50\text{ms}$ via Fast Tier; payments $> ₹10,000$ enter the `escalation_queue` table as `ESCALATE`.

---

## 📅 PHASE 4: Red-Team Benchmark & UI Integration (Hours 32 – 42)

### Target Milestone:
Full 250-scenario `VERIACT-ASB` benchmark evaluated across all 4 baselines; Pareto curve proves safety-latency tradeoff; full Command Center UI with Live Stream, Trace Drawer, Human Queue, and Attack Sandbox operational.

### Task Checklist:
- **Aman**:
  - [ ] Implement analytics and KPI stats endpoint: `GET /api/v1/analytics/stats`.
  - [ ] Build fail-closed timeout guards and circuit breakers (`ERROR_HANDLING.MD`).
  - [ ] Build Live Sandbox backend endpoint (`POST /api/v1/sandbox/simulate`).
  - [ ] Setup SSE / polling telemetry stream connecting backend events to Next.js.
- **Vedesh**:
  - [ ] Add remaining ERP edge cases (cancelled, draft, and duplicate invoices).
  - [ ] Build PDF invoice parser extracting structured key-values from sample PDFs (`SCRAPING_SPEC.MD`).
  - [ ] Harden anti-prompt-injection regex and passive data fencing.
  - [ ] Build Ground Truth Explorer endpoints (`GET /api/v1/ground-truth/invoices`).
- **Aryan**:
  - [ ] Expand `VERIACT-ASB` to full **250 adversarial test cases** across all 10 failure classes.
  - [ ] Run benchmark evaluation across all 4 systems (No Guardrail, LLM Judge, Always Deep, VERIACT Adaptive).
  - [ ] Build **Benchmark Pareto Frontier Chart** using Recharts in Next.js (Safety Recall vs. Latency/Cost).
  - [ ] Build **Human Escalation Review Queue UI** with one-click "Approve" and "Reject" actions.
  - [ ] Build **Interactive Attack Sandbox UI** with 4 presets for hackathon judges.

**Phase 4 Gate Criteria**:
- Benchmark reports: $\ge 96\%$ Safety Recall, $\le 3.5\%$ False Block Rate, and $\approx 384\text{ms}$ average latency.
- Full Next.js Command Center operational without console errors.

---

## 📅 PHASE 5: Rehearsal, Offline Redundancy & Pitch Polish (Hours 42 – 48)

### Target Milestone:
System hardened against venue Wi-Fi failure; demo script rehearsed second-by-second (4 minutes); 4K backup video recorded; 10-slide deck finalized; code frozen.

### Task Checklist:
- **Aman**:
  - [ ] Build local zero-dependency offline fallback runner (`scripts/demo_offline.py`).
  - [ ] Run pre-flight checklist (`PRODUCTION_CHECKLIST.MD`).
  - [ ] Code freeze on `main` branch.
- **Vedesh**:
  - [ ] Verify data integrity of all 10 vendor and invoice seed records.
  - [ ] Prepare technical defense talking points for judge Q&A (why external truth beats LLM judge; why action-level beats prompt safety).
- **Aryan**:
  - [ ] Record high-resolution 60fps backup demo walkthrough video (`demo_backup_video.mp4`).
  - [ ] Finalize 10-slide pitch presentation deck.
  - [ ] Lead rehearsal of the 4-minute demo script timing each segment.

**Phase 5 Gate Criteria**:
- Offline runner executes all 4 demo scenarios without internet in $< 1\text{ second}$.
- Presentation team executes 4-minute pitch cleanly within time limits.

---

## Git Workflow for Aman, Vedesh, and Aryan

To work concurrently without merge conflicts:
```bash
# Branch convention:
git checkout -b feature/aman-runtime-interceptor
git checkout -b feature/vedesh-ground-truth-policy
git checkout -b feature/aryan-risk-benchmark-ui

# Pushing feature branch:
git push origin feature/<your-branch-name>

# Merging into main at phase checkpoints:
git checkout main
git pull origin main
git merge feature/<your-branch-name>
git push origin main
```
