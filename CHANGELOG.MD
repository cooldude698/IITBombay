# Changelog — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Standard:** [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
> **Versioning:** Semantic Versioning (`MAJOR.MINOR.PATCH`)  

---

## [Unreleased] — Post-Hackathon Roadmap
### Planned
- **Distributed Swarm Consensus**: Multi-agent consensus verification for peer-to-peer agent collaborations.
- **Zero-Knowledge Action Proofs (zk-SNARKs)**: Cryptographic proofs of invoice verification without disclosing underlying vendor financial data.
- **Hardware Enclave (TEE) Attestation**: Running the deterministic verification core inside Intel SGX or AWS Nitro Enclaves.

---

## [1.0.0] — 2026-10-07 (Hackathon Round-1 Release)

### Added
- **Core Interceptor Gateway**: Seamless pre-execution hook wrapping LangGraph tool nodes, holding proposed actions until verified.
- **Action Normalizer**: Canonical transformation layer mapping heterogeneous tool signatures into standard `NormalizedAction` schemas.
- **Controlled Ground Truth Store**: Relational SQLite database seeded with 10 realistic enterprise vendors, 10 invoices, 4 agent roles, and corporate policies.
- **Deterministic Parameter Grounding**: Native Python exact matching and numeric range validator preventing LLM hallucination in quantitative checks.
- **RBAC & Policy Engine**: Declarative condition evaluator enforcing single transaction limits, manager signoffs, and blacklists.
- **Multi-Factor Risk Assessment Engine**: Continuous risk score $R \in [0.0, 1.0]$ formulating financial exposure, irreversibility, permission risk, evidence uncertainty, and contradiction severity.
- **Risk-Adaptive 3-Tier Router**:
  - Tier 1 (Fast): Schema & cached checks ($< 150\text{ms}$).
  - Tier 2 (Strong): DB grounding & fast semantic model ($< 800\text{ms}$).
  - Tier 3 (Deep): Multi-source cross-referencing & high-capacity model ($< 2000\text{ms}$).
- **Tri-State Decision Gate**: Returns deterministic `EXECUTE` (with short-lived HMAC execution token), `ESCALATE` (to review queue), or `BLOCK` (with structured reason).
- **VERIACT-ASB Benchmark Suite**: 250 structured adversarial red-team scenarios covering 10 failure categories (Parameter Mismatch, Prompt Injection, Stale Info, etc.).
- **Comparative Baseline Harness**: Automated evaluation runner comparing No Guardrail, LLM-as-a-Judge, Always-Deep Verifier, and VERIACT.
- **Next.js 14 Mission Control Dashboard**:
  - High-density dark-mode operations console.
  - Live Action Stream table with status badges and risk meters.
  - Auditable Action Trace Drawer (rendering evidence diffs without exposing internal CoT).
  - Human Escalation Review Queue with one-click Approve/Reject actions.
  - Interactive Pareto Tradeoff Curve (Safety Recall vs. Latency).
- **CI/CD Quality Gates**: Automated GitHub Actions asserting linting, type safety, and an invariant safety regression gate ($\text{Recall} \ge 95\%$).

---

## [0.2.0] — 2026-10-06 (Alpha Architecture Milestone)
### Added
- Mathematical risk score formulation and initial weight calibration.
- Initial 50-case adversarial dataset fixtures.
- FastAPI REST endpoint prototypes for `/intercept/action` and `/verify/evaluate`.

---

## [0.1.0] — 2026-10-05 (Project Inception)
### Added
- Problem statement analysis for Inter-IIT / Techfest Problem Statement 9.
- Core philosophy formulated: "Think -> Verify -> Act".
- Rejection of naive LLM-as-a-Judge in favor of deterministic grounded verification.
