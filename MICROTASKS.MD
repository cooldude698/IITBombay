# Microtasks & 48-Hour Sprint Breakdown — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Document:** Team Work Breakdown Structure (WBS) & Sprint Schedule  
> **Sprint Horizon:** 48 Hours / 5 Team Members  
> **Version:** 1.0.0  

---

## 1. Team Roles & Ownership Matrix

| Role | Team Member | Primary Responsibility Domain |
|---|---|---|
| **Member 1** | Lead Agent Engineer | LangGraph orchestration, tool interceptor hook, mock tool handlers. |
| **Member 2** | Grounding & Ingestion Lead | Action normalizer, ERP SQLite database, hybrid vector retrieval, PDF parser. |
| **Member 3** | Risk & Policy Architect | Risk mathematical engine ($R = \sum w_i X_i$), RBAC matrix, policy AST engine. |
| **Member 4** | Benchmark & Evaluation Lead | `VERIACT-ASB` dataset (250 scenarios), baseline harness, Pareto curve generator. |
| **Member 5** | Frontend & Integration Lead | Next.js Command Center, Auditable Trace Drawer, Live Sandbox, API client. |

---

## 2. Sprint Schedule & Microtasks Breakdown

### 2.1 Sprint Block 1: Architecture Freeze & Ground Truth Seeding (Hours 0 – 6)

| Task ID | Assignee | Microtask Description | Dependency | Acceptance Criteria |
|---|---|---|---|---|
| `TSK-101` | Member 2 | Define SQLAlchemy models & seed SQLite ERP DB with 10 invoices and 10 vendors. | None | `seed_db.py` creates SQLite file with verified seed records. |
| `TSK-102` | Member 3 | Implement Pydantic schemas for `NormalizedAction`, `RiskBreakdown`, `VerificationResult`. | None | All Pydantic models pass validation tests. |
| `TSK-103` | Member 1 | Setup baseline LangGraph state graph with mock tools (`make_payment`, `read_invoice`). | `TSK-102` | Agent attempts tool calls and captures proposed payloads. |
| `TSK-104` | Member 5 | Initialize Next.js 14 project, configure Tailwind dark mode tokens and layout frame. | None | Running dev server displays header ribbon and base grid. |
| `TSK-105` | Member 4 | Define benchmark schema and create first 25 ground-truth adversarial scenarios. | `TSK-102` | JSON fixtures stored in `/benchmark/data/`. |

---

### 2.2 Sprint Block 2: Core Verification Pipeline (Hours 6 – 18)

| Task ID | Assignee | Microtask Description | Dependency | Acceptance Criteria |
|---|---|---|---|---|
| `TSK-201` | Member 2 | Build `ActionNormalizer` to map diverse tool calls into canonical JSON. | `TSK-102` | Normalizes 10 different tool signatures correctly. |
| `TSK-202` | Member 2 | Build `ParameterGroundingEngine`: deterministic exact match & numeric range checks. | `TSK-101` | Flags mismatch if proposed amount differs from DB by even ₹0.01. |
| `TSK-203` | Member 3 | Implement RBAC privilege filter and enterprise policy evaluator (`POL-FIN-001`). | `TSK-102` | Blocks unauthorized roles; flags threshold violations. |
| `TSK-204` | Member 3 | Implement multi-factor Risk Engine: $R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$. | `TSK-202` | Outputs continuous score $R \in [0.0, 1.0]$. |
| `TSK-205` | Member 1 | Construct pre-execution interception wrapper intercepting LangGraph tool calls. | `TSK-103` | Holds action in memory; awaits verification result. |

---

### 2.3 Sprint Block 3: Adaptive Tiers & Decision Gate (Hours 18 – 30)

| Task ID | Assignee | Microtask Description | Dependency | Acceptance Criteria |
|---|---|---|---|---|
| `TSK-301` | Member 3 | Implement Tier 1 (Fast Verifier): pure deterministic check ($< 150\text{ms}$). | `TSK-204` | Verified in $< 40\text{ms}$ without model invocation. |
| `TSK-302` | Member 2 | Implement Tier 2 (Strong Verifier): DB grounding + fast semantic LLM check. | `TSK-202` | Verified in $< 750\text{ms}$ with Gemini 1.5 Flash / GPT-4o-Mini. |
| `TSK-303` | Member 3 | Implement Tier 3 (Deep Verifier): multi-source verification + deep LLM. | `TSK-203` | Detects subtle injection attacks and cross-source conflicts. |
| `TSK-304` | Member 1 | Implement Tri-State Decision Gate: `EXECUTE`, `ESCALATE`, `BLOCK`. | `TSK-301` | Issues signed HMAC token on `EXECUTE`; returns 403 on `BLOCK`. |
| `TSK-305` | Member 5 | Build Live Action Stream table with status badges and risk meters in Next.js. | `TSK-104` | Renders simulated stream with color-coded status chips. |

---

### 2.4 Sprint Block 4: Benchmark Expansion & UI Integration (Hours 30 – 40)

| Task ID | Assignee | Microtask Description | Dependency | Acceptance Criteria |
|---|---|---|---|---|
| `TSK-401` | Member 4 | Scale `VERIACT-ASB` to full 250 red-team scenarios across 10 failure classes. | `TSK-105` | 250 validated JSON fixtures in repository. |
| `TSK-402` | Member 4 | Build automated comparison runner for the 4 baselines (No Guard, Judge, Heavy, VERIACT). | `TSK-401` | Exports confusion matrices, safety recall, and latency metrics. |
| `TSK-403` | Member 5 | Build **Auditable Action Trace Drawer** (Side slide-out with parameter diff matrix). | `TSK-305` | Clicking table row shows detailed evidence without raw CoT. |
| `TSK-404` | Member 5 | Build **Human Escalation Queue** view with Approve/Reject buttons and live resolution. | `TSK-304` | Approving action dispatches signed execution token. |
| `TSK-405` | Member 5 | Build **Benchmark Pareto Frontier Chart** using Recharts. | `TSK-402` | Displays interactive curve showing VERIACT's optimal tradeoff. |

---

### 2.5 Sprint Block 5: Hardening, Pitch Rehearsal & Freeze (Hours 40 – 48)

| Task ID | Assignee | Microtask Description | Dependency | Acceptance Criteria |
|---|---|---|---|---|
| `TSK-501` | Team | Execute full end-to-end integration test across all 4 demo scenarios. | All | 100% demo scenario reliability on local environment. |
| `TSK-502` | Member 2 | Build local offline fallback runner (`demo_offline.py`) for venue Wi-Fi failure. | `TSK-501` | Runs entire demo using local SQLite and mock responses. |
| `TSK-503` | Member 5 | Record 4K 60fps backup demo walkthrough video. | `TSK-501` | Video file saved locally on presentation machines. |
| `TSK-504` | Team | Polish 10-slide pitch presentation deck aligning with live demo flow. | All | Presentation rehearsed to strict 4-minute time limit. |
| `TSK-505` | Member 1 | Code freeze, tag `v1.0.0-hackathon`, verify GitHub README links and documentation. | All | Repository clean, passes CI, ready for submission. |
