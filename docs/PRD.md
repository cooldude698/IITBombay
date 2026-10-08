# Product Requirements Document (PRD) — VERIACT

> **Project Name:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Tagline:** Verify the Action. Then Let the Agent Act.  
> **Target Forum:** IIT Bombay Techfest / Inter-IIT Hackathon (Problem Statement 9: Autonomous Agent Guardrails)  
> **Version:** 1.0.0  
> **Status:** Approved for Implementation  

---

## 1. Executive Summary

Autonomous AI agents are shifting from passive conversational engines into active transaction agents. Agents now interact with production databases, invoke banking APIs, send enterprise emails, modify customer records, and dispatch real-world operations via tool calls. However, modern LLMs remain susceptible to hallucinations, parameter drift, goal misinterpretation, and indirect prompt injections. 

When an agent hallucinates text, the damage is negligible; **when an agent hallucinates an executable tool call, financial and operational damage is immediate and irreversible.**

**VERIACT** is an enterprise-grade pre-execution verification middleware for autonomous AI agents. Instead of relying on a post-facto guardrail or a fallible secondary LLM judge, VERIACT intercepts every proposed tool action *before* execution. It standardizes the action payload, grounds its parameters against trusted external state (ERP databases, invoices, employee master registries), evaluates deterministic company policies and RBAC permissions, scores multi-dimensional risk, and routes the action through an adaptive verification tier (**Fast**, **Strong**, or **Deep**). The system concludes with a definitive tri-state outcome: **EXECUTE**, **ESCALATE**, or **BLOCK**.

---

## 2. Problem Statement & Market Gap

### 2.1 The Problem
Existing agent guardrail frameworks (e.g., NeMo Guardrails, Llama Guard, Guardrails AI) primarily operate at the prompt or token-generation layer. They evaluate whether an agent's conversational response contains toxic language, off-topic discourse, or prompt leakage. 

However, in an autonomous tool-calling pipeline:
1. **Plausible Hallucinations**: An agent can generate a perfectly polite, syntactically flawless tool call that contains a catastrophic parameter error (e.g., transferring ₹25,000 instead of an approved ₹18,500 invoice).
2. **Untrusted Ground Truth**: Typical LLM judges lack access to verifiable external records or compute deterministic ground truth; they simply "hallucinate their verification".
3. **Compute Inefficiency**: Existing verification frameworks either verify nothing (insecure) or execute heavyweight multi-agent deliberation on every single action (crippling latency and API budget).
4. **Binary Naivety**: Traditional systems output binary `ALLOW`/`DENY`. In real enterprise environments, ambiguity requires a conditional `ESCALATE` state to engage human oversight.

### 2.2 The VERIACT Gap Resolution
| Dimension | Traditional Guardrails | LLM-as-a-Judge | VERIACT |
|---|---|---|---|
| **Target** | Prompts / Output text / Schemas | Conversational responses | Executable tool calls & concrete parameters |
| **Trust Source** | In-context tokens / LLM memory | LLM internal weights | External ground truth (ERP, DBs, Policies, RBAC) |
| **Verification Depth** | Static / Uniform | Static single-model prompt | **Risk-Adaptive (Fast, Strong, Deep)** |
| **Decision Space** | Allow / Deny | Safe / Unsafe | **Execute / Escalate / Block** |
| **Verification Logic** | Heuristics / Regex / Classifier | Subjective model judgment | Deterministic code + targeted semantic verification |
| **Cost / Latency Optimization** | None | High latency on every step | **Tiered compute allocation based on action risk** |

---

## 3. Goals and Non-Goals

### 3.1 Primary Goals
- **G-01 (Zero-Leakage Interception)**: Guarantee that 100% of intercepted tool actions are held in a pending state until explicit verification resolution.
- **G-02 (External Parameter Grounding)**: Validate concrete parameters (e.g., `recipient`, `amount`, `item_id`, `date`) against verifiable external records using deterministic code before LLM deliberation.
- **G-03 (Risk-Adaptive Verification Routing)**: Implement a mathematical risk scoring model ($R \in [0, 1]$) that routes actions dynamically to Fast ($<150\text{ms}$), Strong ($<800\text{ms}$), or Deep ($<2000\text{ms}$) verification tiers.
- **G-04 (Tri-State Decision Engine)**: Return deterministic `EXECUTE`, `ESCALATE`, or `BLOCK` verdicts accompanied by a tamper-evident audit trace.
- **G-05 (Red-Team Benchmark)**: Provide a comprehensive 250+ scenario evaluation dataset (`VERIACT-ASB`) covering 10 failure classes with reproducible metrics proving superior safety-latency Pareto efficiency.
- **G-06 (Mission Control UI)**: Deliver a high-density, real-time command dashboard showing live action streams, auditable traces (without raw CoT), risk breakdown visualizers, and benchmark comparisons.

### 3.2 Non-Goals
- **NG-01 (Conversational Tone Filtering)**: VERIACT will not act as a profanity or sentiment filter for conversational chat outputs.
- **NG-02 (Blockchain Transactions)**: VERIACT is an enterprise runtime security layer; it does not deploy smart contracts or decentralized consensus.
- **NG-03 (Raw LLM Chain-of-Thought Exposure)**: VERIACT will not dump unconstrained hidden reasoning tokens to end-users or compliance auditors.

---

## 4. User Personas

### Persona 1: Enterprise AI Safety Architect (Vikram)
- **Role**: Head of AI Security at a Fintech Enterprise.
- **Need**: Deploy autonomous finance agents that process invoices and execute vendor payments without risking unauthorized funds transfer or regulatory fines.
- **Pain Point**: Cannot trust autonomous LLMs with tool execution; existing guardrails do not query ERP databases to verify amounts.

### Persona 2: AI Application Developer (Ananya)
- **Role**: Lead Engineer building LangGraph agent workflows for enterprise customer service.
- **Need**: Drop-in middleware that secures tool calling without introducing 3-second latency penalties on basic read-only actions.
- **Pain Point**: Heavyweight verifiers make the agent experience sluggish and consume entire OpenAI/Anthropic API quotas.

### Persona 3: Compliance & Human-in-the-Loop Auditor (Rajesh)
- **Role**: Operations Manager reviewing escalated transactions.
- **Need**: An actionable queue showing exactly why an action was escalated (e.g., *"Invoice approved amount is ₹18,500, but payment requires manager signoff since amount > ₹10,000"*).
- **Pain Point**: Existing alerts are cryptic or require digging through hundreds of raw prompt lines.

---

## 5. Core Features & Capabilities

### Feature 1: Action Interception & Normalization
- Intercepts LangGraph / LangChain tool proposals before invoking native functions.
- Transforms diverse tool payloads (e.g., `make_payment`, `send_wire`, `refund_order`) into a unified canonical schema (`NormalizedAction`).

### Feature 2: Evidence Grounding Engine
- Controlled enterprise database containing mock ERP invoices, vendor master files, employee directories, and purchase orders.
- Deterministic parameter matching: compares proposed targets and numerical values against ground-truth records.

### Feature 3: Policy & RBAC Engine
- Hierarchical policy evaluation rules (e.g., single transaction caps, dual-approval thresholds, prohibited operational hours).
- Role-Based Access Control (RBAC) ensuring an agent with role `Junior_Support_Agent` cannot invoke administrative or financial transfer capabilities.

### Feature 4: Multi-Dimensional Risk Engine
- Calculates action risk score $R \in [0, 1]$ via weighted formulation:
  $$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$$
  - $F$: Financial impact / transaction scale
  - $I$: Irreversibility (e.g., write/delete vs. read-only)
  - $P$: Permission sensitivity level
  - $U$: Evidence uncertainty / missing data
  - $C$: Parameter contradiction score

### Feature 5: Risk-Adaptive Verification Tiers
- **Tier 1 (Fast)**: $R \le 0.35$. Schema validation + RBAC check + basic cached lookup ($<150\text{ms}$).
- **Tier 2 (Strong)**: $0.35 < R \le 0.70$. Tier 1 + DB ground-truth matching + fast LLM semantic verifier ($<800\text{ms}$).
- **Tier 3 (Deep)**: $R > 0.70$. Tier 2 + multi-source cross-referencing + policy rule engine + deep LLM verification + conditional escalation ($<2000\text{ms}$).

### Feature 6: Tri-State Decision & Escalation Queue
- **EXECUTE**: Forward action to live tool handler; log audit trail.
- **ESCALATE**: Hold action in persistent pending queue; send notification to Human Reviewer dashboard with specific mismatch notes.
- **BLOCK**: Terminate action pipeline; return structured security rejection to agent with actionable failure code.

### Feature 7: Auditable Action Trace
- Generates a cryptographically hashed, step-by-step verification trace for every action.
- Displays exact parameter comparisons, matching policies, and risk score components without exposing internal model chain-of-thought tokens.

### Feature 8: VERIACT-ASB Red-Team Benchmark Suite
- 250+ curated adversarial test cases covering 10 distinct failure classes (Parameter Mismatch, Entity Hallucination, Stale Policy, Prompt Injection in Evidence, Permission Violation, etc.).
- Automated comparison runner evaluating VERIACT against 3 industry baselines: (1) No Guardrail, (2) LLM-as-Judge, and (3) Always-Deep Verifier.

---

## 6. Functional Requirements (FR)

| ID | Title | Description | Priority |
|---|---|---|---|
| **FR-01** | Tool Call Interception | System must intercept 100% of registered tool calls via LangGraph node hooks before tool function execution. | P0 |
| **FR-02** | Action Normalization | Standardize varied tool signatures into `NormalizedAction` schema (UUID, action_type, target, parameters, agent_id, timestamp). | P0 |
| **FR-03** | Deterministic Evidence Lookup | Query ground-truth database (SQL/Vector) for entities referenced in the tool call and return typed evidence records. | P0 |
| **FR-04** | Exact & Range Parameter Match | Compare parameters (amount, recipient, date) deterministically using Python equality and numerical bounds; flag mismatches. | P0 |
| **FR-05** | RBAC Privilege Check | Match agent ID and role against role-permission matrix; instantly block unauthorized tool calls. | P0 |
| **FR-06** | Policy Rule Evaluation | Check actions against active enterprise policies (e.g., `amount > 10000 -> manager_approval_required`). | P0 |
| **FR-07** | Risk Calculation | Compute numerical risk score $R \in [0, 1]$ using weighted multi-factor equation. | P0 |
| **FR-08** | Adaptive Tier Routing | Route action to Tier 1 (Fast), Tier 2 (Strong), or Tier 3 (Deep) based on configurable risk thresholds ($\tau_1, \tau_2$). | P0 |
| **FR-09** | Fast Verifier Execution | Execute lightweight structural validation and cache verification in $<150\text{ms}$. | P0 |
| **FR-10** | Strong Verifier Execution | Run deterministic matching plus high-speed semantic verification model in $<800\text{ms}$. | P0 |
| **FR-11** | Deep Verifier Execution | Run multi-source consistency checks, policy compliance, and high-capacity model verification in $<2000\text{ms}$. | P0 |
| **FR-12** | Human Escalation Queue | Store escalated actions in SQLite/PostgreSQL queue with manual Approve/Reject endpoints. | P1 |
| **FR-13** | Action Trace Generation | Produce structured, non-CoT audit logs including evidence sources, mismatch details, and risk breakdowns. | P0 |
| **FR-14** | Benchmark Suite Runner | Programmatically execute `VERIACT-ASB` suite against all 4 baseline configurations and compile statistical metrics. | P0 |
| **FR-15** | Real-time Command UI | Provide Next.js web application displaying live action telemetry, trace details, and benchmark comparison charts. | P0 |

---

## 7. Non-Functional Requirements (NFR)

### 7.1 Performance & Latency
- **NFR-01**: Tier 1 (Fast) verification must complete in under $150\text{ms}$ at p95.
- **NFR-02**: Tier 2 (Strong) verification must complete in under $800\text{ms}$ at p95.
- **NFR-03**: Tier 3 (Deep) verification must complete in under $2000\text{ms}$ at p95.
- **NFR-04**: Weighted average latency across mixed enterprise workloads must achieve $\ge 60\%$ reduction compared to Always-Deep verification.

### 7.2 Safety & Reliability
- **NFR-05**: Fail-Closed Guarantee: Under system timeout, DB connection failure, or model service outage, system must resolve to `BLOCK` or `ESCALATE`; never `EXECUTE`.
- **NFR-06**: Indirect Injection Resistance: Documents containing prompt injection instructions must be parsed strictly as data strings and never execute as prompt directives.

### 7.3 Security & Compliance
- **NFR-07**: All API endpoints must authenticate via API Key or Bearer Token.
- **NFR-08**: Action audit traces must be tamper-evident with SHA-256 payload hashes.

---

## 8. Success Metrics & Target KPIs

| Metric | Target Goal | Baseline Comparison |
|---|---|---|
| **Safety Recall (Unsafe Blocked / Total Unsafe)** | **$\ge 96.0\%$** | vs. $\approx 18\%$ (No Guardrail), $\approx 78\%$ (LLM Judge) |
| **False Block Rate (Legitimate Actions Blocked)** | **$\le 3.5\%$** | vs. $\approx 14\%$ (LLM Judge), $\approx 5\%$ (Always Deep) |
| **Precision (True Unsafe / Total Blocked)** | **$\ge 95.0\%$** | vs. $\approx 65\%$ (LLM Judge) |
| **Average Latency (Enterprise Workload)** | **$\le 480\text{ms}$** | vs. $\approx 2200\text{ms}$ (Always Deep) — **$78\%$ reduction** |
| **Inference Token Cost per 1k Actions** | **$\le \$1.20$** | vs. $\approx \$6.50$ (Always Deep) — **$81\%$ reduction** |
| **Escalation Routing Efficiency** | **$100\%$ valid HITL triggers** | Captures all ambiguous / high-value exceptions |

---

## 9. Release & Demonstration Plan

- **Phase 1 (Round-1 Submission / Core MVP)**:
  - Complete LangGraph Action Interceptor & Normalizer.
  - Grounding Engine with Mock ERP database (10 realistic enterprise entities).
  - Risk scoring formulation & 3-tier routing implementation.
  - Core benchmark suite (50 test scenarios) proving safety-latency tradeoff.
  - Executive Pitch Deck & Architectural Specifications.
- **Phase 2 (Hackathon Working Prototype)**:
  - Full 250-scenario `VERIACT-ASB` benchmark execution and report generation.
  - Interactive Next.js Security Command Center with Live Action Stream & Trace Drawer.
  - Real-time Human Escalation Review Queue with live resolution loop.
- **Phase 3 (Grand Finale Presentation)**:
  - 4 live demonstration scenarios: (1) Safe read-only, (2) Parameter mismatch block, (3) Policy threshold escalation, (4) Prompt injection neutralization.
  - Live benchmark comparison radar showcasing the safety vs. cost Pareto frontier.
