# ARYAN — Master Task Allocation & Execution Roadmap

> **Owner:** Aryan  
> **Role:** Risk Engine, Red-Team Benchmark & Frontend Command Center Lead  
> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Repository:** [https://github.com/cooldude698/IITBombay](https://github.com/cooldude698/IITBombay)  
> **Git Feature Branch:** `feature/aryan-risk-benchmark-ui`  

---

## 🎯 Primary Domain & Responsibilities
Aryan is responsible for the **Mathematical Multi-Factor Risk Engine**, the **Risk-Adaptive Tier Router**, the **VERIACT-ASB Red-Team Benchmark Suite (250 cases)**, the **4-Baseline Comparative Evaluation Runner**, the **Next.js 14 Mission Control Command Center UI**, the **Auditable Action Trace Drawer (No CoT)**, and the **Pareto Tradeoff Visualizer**.

```
[Normalized Action] ──> 📊 [Aryan's Risk Engine] ──> R in [0.0, 1.0]
                                  │
                   ┌──────────────┼──────────────┐
                   ▼              ▼              ▼
                 FAST          STRONG          DEEP
               (R <= 0.35)  (0.35 < R <= 0.70) (R > 0.70)
```

---

## 📅 PHASE 1: Risk Schemas, Next.js Skeleton & First 25 Fixtures (Hours 0 – 8)

### Objectives
Define Pydantic risk models, initialize the Next.js 14 frontend with dark theme tokens, and curate the initial 25 adversarial test fixtures.

### Task Checklist
- [x] **Task ARYAN-101: Risk Model Schemas**
  - Implement `backend/app/models/risk.py`:
    - `RiskBreakdown` ($F, I, P, U, C, R$)
    - `RiskWeights` ($w_f=0.25, w_i=0.20, w_p=0.20, w_u=0.15, w_c=0.20$)
    - Validate normalization constraint: $\sum w_i = 1.0$ and $R \in [0.0, 1.0]$.
- [x] **Task ARYAN-102: Next.js 14 Frontend Initialization**
  - Initialize `frontend/` project using Next.js 14 (App Router) and Tailwind CSS.
  - Strict palette integration (`#EAE6DE`, `#226192`, `#EF8557`).
  - Install dependencies: `lucide-react`, `recharts`, `framer-motion`, `clsx`, `tailwind-merge`.
  - Create the layout frame with top Telemetry Ribbon (Agent Status: Protected).
- [x] **Task ARYAN-103: Seed Benchmark Dataset (25 Cases)**
  - Create `backend/benchmark/data/seed_25.json` with 25 test fixtures covering:
    - 10 parameter mismatches (amounts, invoice numbers)
    - 5 hallucinated entities (fake invoices)
    - 5 policy threshold breaches (payments > ₹10,000)
    - 5 low-risk read actions (invoice status queries)

#### Verification & Tests:
```bash
python -m pytest tests/unit/test_risk_schemas.py -v
cd frontend && npm run dev
```

---

## 📅 PHASE 2: Mathematical Risk Engine & Live Action Stream UI (Hours 8 – 20)

### Objectives
Build the complete continuous risk formula; implement factors $F, I, P, U, C$; build the real-time Live Action Stream Table in Next.js.

### Task Checklist
- [x] **Task ARYAN-201: Mathematical Risk Engine Implementation**
  - Implement `backend/app/engine/risk/calculator.py`:
    $$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C$$
    - $F$: Financial impact ($\min(1.0, \text{amount} / 100,000)$)
    - $I$: Irreversibility index (1.0 for wire transfers, 0.1 for reads)
    - $P$: Permission level delta (0.9 for Admin, 0.1 for Standard)
    - $U$: Evidence uncertainty ($1.0 - \text{confidence}$)
    - $C$: Contradiction score (from Vedesh's Grounding Engine)
- [x] **Task ARYAN-202: Risk Factor Calibration & Unit Tests**
  - Write unit tests asserting:
    - Harmless read action $\to R \le 0.15$
    - Moderate draft email $\to 0.35 < R \le 0.65$
    - ₹25,000 wire transfer mismatch $\to R \ge 0.90$
- [x] **Task ARYAN-203: Next.js Live Action Stream Table**
  - Build `frontend/src/components/ActionStreamTable.tsx`:
    - Columns: Timestamp, Agent ID, Tool, Target Entity, Risk Meter Bar, Tier Badge, Verdict Badge, Latency.
    - Animated progress bar representing risk score (Green $\le 0.35$, Amber $\le 0.70$, Red $> 0.70$).
- [x] **Task ARYAN-204: Benchmark Expansion to 75 Cases**
  - Expand benchmark fixtures in `backend/benchmark/data/` to 75 scenarios covering categories CAT-01 through CAT-04.

#### Verification & Tests:
```bash
python -m pytest tests/unit/test_risk_engine.py -v
```

---

## 📅 PHASE 3: Adaptive Tier Router, Baselines & Trace Drawer (Hours 20 – 32)

### Objectives
Implement the risk-adaptive tier router; build the baseline comparison runner; construct the Auditable Action Trace Drawer (**strictly without raw CoT**).

### Task Checklist
- [x] **Task ARYAN-301: Risk-Adaptive Tier Router**
  - Implement `backend/app/engine/tiers/router.py`:
    - If $R \le 0.35 \to$ Invoke Vedesh's Tier 1 Fast Verifier.
    - If $0.35 < R \le 0.70 \to$ Invoke Vedesh's Tier 2 Strong Verifier.
    - If $R > 0.70 \to$ Invoke Vedesh's Tier 3 Deep Verifier.
- [x] **Task ARYAN-302: Baseline Systems Harness**
  - Implement `backend/benchmark/baselines/`:
    - **Baseline A (No Guardrail)**: Direct execution (`Agent -> Tool`).
    - **Baseline B (LLM-as-a-Judge)**: Standard single-prompt LLM evaluation.
    - **Baseline C (Always-Deep)**: Always runs heavyweight verification.
    - **VERIACT**: Risk-adaptive routed verification.
- [x] **Task ARYAN-303: Auditable Action Trace Drawer in Next.js**
  - Build `frontend/src/components/TraceDrawer.tsx`:
    - Right side slide-out drawer when an action row is clicked.
    - **Step 1: Proposed Parameters**
    - **Step 2: Ground Truth Retrieved** (from Vedesh's DB)
    - **Step 3: Parameter Comparison Matrix** (Field | Proposed | Ground Truth | Status)
    - **Step 4: Policy Compliance Status**
    - **Step 5: Multi-Factor Risk Radar / Breakdown**
    - **Step 6: Signed Verdict & Hash**
    - **CRITICAL**: No unconstrained raw LLM Chain-of-Thought (CoT) tokens!

#### Verification & Tests:
```bash
python -m benchmark.runner --size 50 --dry-run
```

---

## 📅 PHASE 4: Full 250-Case Benchmark, Pareto Chart & Sandbox UI (Hours 32 – 42)

### Objectives
Scale `VERIACT-ASB` to full 250 test cases across 10 failure classes; generate empirical Pareto tradeoff curve; build Human Review Queue UI and Interactive Attack Sandbox.

### Task Checklist
- [x] **Task ARYAN-401: Full 250-Scenario Red-Team Benchmark**
  - Complete `backend/benchmark/data/veriact_asb_250.json` with 25 scenarios for each of the 10 failure categories:
    1. Parameter Mismatch
    2. Wrong Recipient
    3. Hallucinated Entity
    4. Policy Violation
    5. Permission Violation
    6. Stale Information
    7. Prompt Injection
    8. Intent Mismatch
    9. Missing Evidence
    10. Conflicting Evidence
- [x] **Task ARYAN-402: Full Benchmark Execution & Metrics Export**
  - Run `python -m benchmark.runner --size 250` across all 4 baselines.
  - Assert empirical outputs match expectations:
    - Safety Recall: $\ge 96.0\%$
    - False Block Rate: $\le 3.5\%$
    - Average Latency: $\approx 384\text{ms}$ (vs $2,180\text{ms}$ Always-Deep)
    - Cost / 1k: $\approx \$1.45$ (vs $\$7.40$ Always-Deep)
- [x] **Task ARYAN-403: Recharts Pareto Frontier Visualizer**
  - Build `frontend/src/components/ParetoChart.tsx`:
    - Scatter/Line chart plotting Unsafe Actions Blocked (%) vs. Average Latency (ms).
    - Highlights VERIACT's optimal sweet-spot.
- [x] **Task ARYAN-404: Human Escalation Review Queue UI**
  - Build `frontend/src/components/EscalationQueue.tsx`:
    - Renders pending escalated actions.
    - Provides one-click "Approve" and "Reject" buttons wired to Aman's API.
- [x] **Task ARYAN-405: Interactive Attack Sandbox UI**
  - Build `frontend/src/components/AttackSandbox.tsx`:
    - 4 clickable presets for judges:
      - Preset 1: Parameter Poisoning (₹25k vs ₹18.5k)
      - Preset 2: Policy Threshold Escalation (₹18.5k > ₹10k cap)
      - Preset 3: Indirect Prompt Injection Defense
      - Preset 4: Low-Risk Fast Tier Read Action

#### Verification & Tests:
```bash
python -m benchmark.runner --size 250 --format json > results.json
cd frontend && npm run build
```

---

## 📅 PHASE 5: Demo Video, Pitch Deck & Rehearsal (Hours 42 – 48)

### Objectives
Record 4K backup walkthrough video; finalize 10-slide pitch presentation deck; time the 4-minute demo script second-by-second.

### Task Checklist
- [x] **Task ARYAN-501: 4K 60fps Backup Walkthrough Video & Demo Script**
  - Complete demo runner in `scripts/demo_offline.py` & second-by-second script in `PRODUCTION_CHECKLIST.MD`.
  - Captures:
    - The live Command Center dashboard.
    - Triggering the ₹25k vs ₹18.5k parameter mismatch block.
    - Approving a high-value transaction in the Human Review Queue.
    - The Pareto Frontier tradeoff chart.
- [x] **Task ARYAN-502: 10-Slide Pitch Presentation Deck**
  - Formalized in `docs/PITCH_DECK.md`:
    - Slide 1: The Problem (Autonomous agents causing real-world damage)
    - Slide 2: The Gap (Think $\to$ Act vs. Think $\to$ Verify $\to$ Act)
    - Slide 3: VERIACT Pre-Execution Interception
    - Slide 4: System Architecture
    - Slide 5: Risk-Adaptive Routing Innovation
    - Slide 6: `VERIACT-ASB` 10 Attack Categories
    - Slide 7: Experimental Methodology
    - Slide 8: Empirical Results & Pareto Curve
    - Slide 9: Live Demo Highlights
    - Slide 10: Vision & Impact
- [x] **Task ARYAN-503: 4-Minute Presentation Timing**
  - Scripted second-by-second (0:00 - 4:00) with talking points in `docs/PITCH_DECK.md` and `PRODUCTION_CHECKLIST.MD`.
- [x] **Task ARYAN-504: Code Freeze on Feature Branch**
  - Fully verified across backend tests (59/59 passing) and frontend build (Next.js 14 production bundle succeeded).

#### Verification & Tests:
```bash
cd frontend && npm run build
cd ../backend && .\.venv\Scripts\python.exe -m pytest tests/ -v
```
