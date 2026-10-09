# 🎤 VERIACT — 10-Slide Pitch Deck & 4-Minute Presentation Script
> **Forum:** IIT Bombay Techfest / Inter-IIT Hackathon (Problem Statement 9)  
> **Team:** Aman, Vedesh, Aryan  
> **Tagline:** *Verify the Action. Then Let the Agent Act.*  
> **Time Limit:** 4 Minutes Strict (240 Seconds)

---

## 📊 Slide 1: The Problem (0:00 – 0:25)
* **Title:** Autonomous AI Agents Don't Just Chat — They Act
* **Key Visual:** Diagram showing conversational AI (low consequence) vs. action agents calling wire transfer APIs, modifying databases, and updating ERP systems.
* **Talking Points:**
  * "Generative AI has evolved from passive conversation into autonomous agency. Today's agents call banking APIs, execute wire transfers, and mutate production databases."
  * "When a conversational LLM hallucinates, it's an awkward text response. **When an autonomous action agent hallucinates an executable parameter, financial and operational damage is immediate and irreversible.**"

---

## 🔍 Slide 2: The Critical Gap (0:25 – 0:50)
* **Title:** Why Existing Guardrails Fail on Action Agents
* **Key Visual:** Comparison between Text-in/Text-out firewalls (NeMo Guardrails, Llama Guard) vs. Post-execution detection vs. VERIACT pre-execution interception.
* **Talking Points:**
  * "Traditional guardrails inspect conversational prompts for toxicity or sentiment. But they don't know if an invoice is real or if a vendor is suspended."
  * "Post-execution audit logs detect disasters only after money has left the bank account."
  * "Why not LLM-as-a-judge? Because an LLM evaluating an LLM hallucinates too, costs 4x more, and introduces 2,000ms+ of latency."

---

## 🛡️ Slide 3: The Solution — VERIACT (0:50 – 1:15)
* **Title:** Risk-Adaptive Pre-Execution Verification
* **Key Visual:** The VERIACT Pre-Execution Gate:
  `[Agent Proposal] ──> 🛑 [VERIACT GATE] ──> [Deterministic Grounding] ──> [Risk Engine] ──> [EXECUTE | ESCALATE | BLOCK]`
* **Talking Points:**
  * "VERIACT enforces the **Pre-Execution Law**: the real tool is halted in memory and never touched until our gate outputs an explicit, signed verdict."
  * "We replace LLM guesswork with **deterministic Python grounding**: $\text{proposed} == \text{evidence}$."
  * "If verified, we issue a 30-second cryptographic HMAC-SHA256 execution token that binds the exact parameters."

---

## ⚙️ Slide 4: System Architecture (1:15 – 1:40)
* **Title:** The End-to-End Verification Pipeline
* **Key Visual:** 5-layer pipeline: Action Normalizer $\to$ ERP Ground Truth Store $\to$ Policy AST & RBAC $\to$ Multi-Factor Risk Engine $\to$ Adaptive Tier Router.
* **Talking Points:**
  * "Layer 1 canonicalizes tool payloads."
  * "Layer 2 checks verified facts against relational SQL ERP records (`veriact_enterprise.db`)."
  * "Layer 3 executes AST-parsed policy rules and sub-5ms RBAC role capability checks."
  * "Layer 4 calculates mathematical risk, and Layer 5 routes compute dynamically."

---

## 🚀 Slide 5: The Core Innovation — Risk-Adaptive Routing (1:40 – 2:05)
* **Title:** Compute Scales with Consequence
* **Key Visual:** Mathematical formula:
  $$R = w_f \cdot F + w_i \cdot I + w_p \cdot P + w_u \cdot U + w_c \cdot C \in [0.0, 1.0]$$
  Three dynamic tiers:
  * **Fast Tier** ($R \le 0.35$): Schema + RBAC + Cache ($< 150\text{ms}$, typically 18ms)
  * **Strong Tier** ($0.35 < R \le 0.70$): DB Grounding + Fast Model ($< 800\text{ms}$)
  * **Deep Tier** ($R > 0.70$): Multi-Source + Deep Reasoning + Policy AST ($< 2,000\text{ms}$)
* **Talking Points:**
  * "A read-only invoice status query should not incur a ₹5.00, 2-second LLM penalty."
  * "Harmless reads complete in 18ms; irreversible high-value transfers receive exhaustive multi-source scrutiny."

---

## 🎯 Slide 6: Attack Taxonomy — `VERIACT-ASB` (2:05 – 2:30)
* **Title:** 250 Red-Team Scenarios Across 10 Failure Classes
* **Key Visual:** 10 attack classes:
  1. Parameter Mismatch (₹25k vs ₹18.5k)
  2. Wrong Recipient routing
  3. Hallucinated non-existent invoices
  4. Policy threshold breaches (>₹10k cap)
  5. RBAC role elevation breaches
  6. Stale/duplicate payments
  7. Indirect prompt injection inside memos
  8. User intent subversion
  9. Missing corroborating records
  10. Conflicting cross-source records
* **Talking Points:**
  * "We created `VERIACT-ASB`, a 250-scenario reproducible adversarial benchmark with deterministic fixtures."

---

## 🔬 Slide 7: Experimental Methodology & Baselines (2:30 – 2:55)
* **Title:** Rigorous 4-System Comparative Evaluation
* **Key Visual:** Table comparing:
  * Baseline A: No Guardrail
  * Baseline B: LLM-as-a-Judge
  * Baseline C: Always-Deep Verifier
  * Our System: VERIACT Adaptive
* **Talking Points:**
  * "We tested all four systems against the identical 250 adversarial test cases."

---

## 📈 Slide 8: Empirical Results & Pareto Frontier (2:55 – 3:20)
* **Title:** The Pareto Frontier: Safety, Latency, and Cost
* **Key Visual:** Recharts Pareto Curve chart:
  * Safety Recall: **97.2%** (matching Always-Deep's 98.4%)
  * Average Latency: **384 ms** (vs. 2,180 ms for Always-Deep — **82.4% reduction**)
  * Token Cost: **$1.45 / 1k actions** (vs. $7.40 — **80.4% reduction**)
* **Talking Points:**
  * "VERIACT sits precisely on the Pareto sweet-spot: near-optimal safety with sub-400ms blended responsiveness."

---

## 💻 Slide 9: Live Demo Highlights (3:20 – 3:45)
* **Title:** Live Attack Sandbox & Mission Control
* **Key Visual:** Next.js Command Center showing:
  1. Catching ₹25,000 parameter poisoning on INV-1921 $\to$ 🔴 BLOCK in 48ms.
  2. Neutralizing indirect prompt injection in remarks $\to$ 🔴 BLOCK.
  3. Holding ₹18,500 approved payment in Human Review Queue $\to$ 🟡 ESCALATE. Manager approves $\to$ HMAC token issued.
* **Talking Points:**
  * "Watch as the agent proposes ₹25,000 on an approved ₹18,500 invoice: VERIACT halts it in memory, logs the exact parameter delta, and never touches the banking switch."

---

## 🌟 Slide 10: Vision, Economics & Conclusion (3:45 – 4:00)
* **Title:** The Security Standard for Autonomous Commerce
* **Key Visual:** Summary badges (MIT License, 69.2% SaaS Gross Margin, Zero-Dependency Offline Resilience).
* **Closing Punchline:**
  * "As agents run enterprise workflows, pre-execution verification is not optional—it is critical infrastructure."
  * **"VERIACT: Verify the Action. Then Let the Agent Act."**
