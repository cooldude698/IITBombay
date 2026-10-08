# VEDESH — Master Task Allocation & Execution Roadmap

> **Owner:** Vedesh  
> **Role:** Ground Truth, Evidence Grounding & Policy / Ingestion Lead  
> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **Repository:** [https://github.com/cooldude698/IITBombay](https://github.com/cooldude698/IITBombay)  
> **Git Feature Branch:** `feature/vedesh-ground-truth-policy`  

---

## 🎯 Primary Domain & Responsibilities
Vedesh is responsible for the **Controlled Enterprise Mock ERP Database**, **Deterministic Parameter Grounding Engine**, **RBAC Role Matrix**, **Enterprise Policy Rules Evaluator**, **Document Ingestion & PDF Parser**, **Anti-Prompt-Injection Sanitization**, and the **3 Verification Tier Implementations** (Fast, Strong, Deep).

```
[Proposed Parameters] ──> ⚖️ [Vedesh's Grounding Engine] ──> Ground Truth Evidence (ERP)
                                       │
                      ├── Deterministic Parameter Match
                      ├── Policy & RBAC Evaluation
                      └── Anti-Injection Data Fencing
```

---

## 📅 PHASE 1: Enterprise Ground Truth Database & Seeding (Hours 0 – 8)

### Objectives
Build the relational SQLite mock ERP database, define SQLAlchemy models, and seed the database with 10 vendors, 10 invoices, 4 agent roles, and 5 policies.

### Task Checklist
- [x] **Task VEDESH-101: SQLAlchemy Models & Database DDL**
  - Implement `backend/app/mock_env/models.py`:
    - `Vendor` (id, name, bank_account, ifsc_code, status, risk_rating)
    - `Invoice` (id, vendor_id, vendor_name, amount, currency, status, po_number, approved_by)
    - `AgentRegistry` (id, name, role, single_txn_limit, daily_limit)
    - `PolicyRule` (id, name, condition_expression, action_type, enforcement_action)
- [x] **Task VEDESH-102: Master Database Seed Script**
  - Write `backend/app/mock_env/seed_db.py` populating the **10 realistic enterprise entities** (from `DATA_SOURCES.MD`):
    - `VND-001` (ABC Technologies) $\to$ `INV-1921`: ₹18,500 (`APPROVED`)
    - `VND-001` (ABC Technologies) $\to$ `INV-1922`: ₹42,000 (`PENDING_APPROVAL`)
    - `VND-002` (XYZ Logistics) $\to$ `INV-404`: ₹9,200 (`APPROVED`)
    - `VND-002` (XYZ Logistics) $\to$ `INV-405`: ₹125,000 (`APPROVED`)
    - `VND-005` (CyberShield Security) $\to$ `INV-771`: ₹50,000 (`SUSPENDED` vendor)
    - `VND-007` (QuickCourier) $\to$ `INV-312`: ₹1,200 (`PAID` - duplicate guard)
- [x] **Task VEDESH-103: Enterprise Policy Seed**
  - Insert the 5 core enterprise policies into the database:
    - `POL-FIN-001`: Amount > ₹10,000 requires manager approval (`ESCALATE`)
    - `POL-FIN-002`: Transactions to suspended vendors are strictly `BLOCKED`
    - `POL-FIN-003`: Duplicate payment guard (status must be `APPROVED`)
    - `POL-SEC-001`: Transaction exceeds agent single limit (`BLOCK`)
    - `POL-DATA-001`: Destructive table operations unconditionally `BLOCKED`

#### Verification & Tests:
```bash
python -m app.mock_env.seed_db
python -c "
from app.mock_env.db import get_invoice
inv = get_invoice('INV-1921')
assert inv['amount'] == 18500.0, 'Seed verification failed!'
print('Vedesh Seed Verified Successfully: INV-1921 is ₹18,500')
"
```

---

## 📅 PHASE 2: Deterministic Grounding & RBAC Policy Engine (Hours 8 – 20)

### Objectives
Build the deterministic parameter matcher (no model latency); implement RBAC privilege checks; build the policy AST evaluator; implement anti-prompt-injection text sanitization.

### Task Checklist
- [x] **Task VEDESH-201: Deterministic Parameter Grounding Engine**
  - Implement `backend/app/engine/grounding/matcher.py`:
    - Compares proposed parameters against retrieved ground truth.
    - Arithmetic equality check: $\Delta = |\text{proposed\_amount} - \text{approved\_amount}|$.
    - Returns `mismatches: List[ParameterMismatch]` and `contradiction_score: float` ($C \in \{0.0, 0.5, 1.0\}$).
- [x] **Task VEDESH-202: Role-Based Access Control (RBAC) Engine**
  - Implement `backend/app/engine/policy/rbac.py`:
    - Validates `agent_role` against allowed capabilities.
    - If `JUNIOR_ASSISTANT` proposes `make_payment`, return immediate `BLOCK` ($< 5\text{ms}$).
- [x] **Task VEDESH-203: Enterprise Policy AST Evaluator**
  - Implement `backend/app/engine/policy/evaluator.py`:
    - Evaluates JSON condition expressions safely without `eval()`.
    - Flags threshold exceedances (e.g. ₹18,500 > ₹10,000 cap).
- [x] **Task VEDESH-204: Anti-Prompt-Injection Sanitizer**
  - Implement `backend/app/engine/retrieval/sanitizer.py`:
    - Strips zero-width and obfuscated Unicode characters.
    - Neutralizes injection patterns (`"Ignore previous instructions"`).
    - Fences external document text in `<untrusted_evidence_data>` XML containers.

#### Verification & Tests:
```bash
python -m pytest tests/unit/test_grounding.py -v
python -m pytest tests/unit/test_policy.py -v
```

---

## 📅 PHASE 3: 3-Tier Verification Implementation & Vector Index (Hours 20 – 32)

### Objectives
Build the concrete verification tier modules (Fast, Strong, Deep); setup vector store indexing for policy handbooks.

### Task Checklist
- [x] **Task VEDESH-301: Tier 1 (Fast Verifier)**
  - Implement `backend/app/engine/tiers/fast_verifier.py`:
    - Pure deterministic Python check: schema validation, RBAC lookup, cached DB match.
    - **Latency Guarantee**: $\le 150\text{ms}$ at p95 (runs in ~30ms).
- [x] **Task VEDESH-302: Tier 2 (Strong Verifier)**
  - Implement `backend/app/engine/tiers/strong_verifier.py`:
    - Executes Tier 1 checks + live database query + fast semantic model (Gemini 1.5 Flash / GPT-4o-Mini).
    - Validates semantic intent (e.g. email draft matches user request).
    - **Latency Guarantee**: $\le 800\text{ms}$ at p95.
- [x] **Task VEDESH-303: Tier 3 (Deep Verifier)**
  - Implement `backend/app/engine/tiers/deep_verifier.py`:
    - Multi-source cross-referencing (Invoice DB + Purchase Order + Vendor status).
    - High-capacity reasoning model (Gemini 1.5 Pro / GPT-4o) checking for subtle fraud, adversarial payloads, and policy compliance.
    - **Latency Guarantee**: $\le 2000\text{ms}$ at p95.
- [x] **Task VEDESH-304: Vector Store & Semantic Policy Index**
  - Build `backend/app/engine/retrieval/vector_store.py`:
    - In-memory FAISS / Chroma store chunking the Corporate Procurement SOPs.
    - Provides semantic lookup for ambiguous policy questions.

#### Verification & Tests:
```bash
python -m pytest tests/integration/test_verification_tiers.py -v
```

---

## 📅 PHASE 4: Edge Cases, PDF Parser & Anti-Injection Hardening (Hours 32 – 42)

### Objectives
Expand ERP database with subtle edge cases; build PDF invoice extractor; harden defense against indirect prompt injection.

### Task Checklist
- [x] **Task VEDESH-401: Enterprise Edge Cases Seeding**
  - Add edge case records:
    - Cancelled invoice `INV-660` (₹28,000) $\to$ must block as cancelled.
    - Foreign currency invoice (USD $500) $\to$ requires exchange rate validation.
    - Vendor with pending KYC status $\to$ must escalate.
- [x] **Task VEDESH-402: PDF Invoice Parser Implementation**
  - Implement `backend/app/engine/ingestion/pdf_parser.py`:
    - Uses `pdfplumber` to extract vendor name, invoice number, line items, and totals from digital PDF invoices.
    - Validates line-item math: $\sum (\text{items}) + \text{tax} == \text{total}$.
- [x] **Task VEDESH-403: Adversarial Injection Stress Testing**
  - Test the sanitizer against 20 adversarial prompt injection payloads (e.g. hidden white text, markdown injection).
  - Verify that no prompt injection can override deterministic boolean checks.
- [x] **Task VEDESH-404: Ground Truth Explorer Endpoints**
  - Implement `GET /api/v1/ground-truth/invoices` and `GET /api/v1/ground-truth/vendors` for Aryan's compliance inspection UI.

#### Verification & Tests:
```bash
python -m pytest tests/security/test_prompt_injection.py -v
```

---

## 📅 PHASE 5: Seed Verification, Technical Defense & Q&A Prep (Hours 42 – 48)

### Objectives
Verify ground truth data integrity; prepare technical defense against judge skepticism; assist in presentation rehearsals.

### Task Checklist
- [x] **Task VEDESH-501: Data Integrity Audit**
  - Verify all 10 vendors and invoices in `veriact_enterprise.db`.
  - Ensure zero broken foreign keys or missing fields.
- [x] **Task VEDESH-502: Technical Defense Preparation for Judges**
  - Prepare bulletproof answers for common judge challenges:
    - *Q: "Why not just use an LLM-as-a-judge?"*  
      $\to$ **A:** "Because the judge LLM hallucinates too. We ground verification in deterministic database state—exact numerical equality and RBAC execute in Python code."
    - *Q: "Isn't this just NeMo Guardrails?"*  
      $\to$ **A:** "No. Guardrails checks prompts and conversational responses. VERIACT intercepts executable tool calls and validates concrete parameters against external enterprise state before execution."
    - *Q: "How do you handle prompt injection in retrieved documents?"*  
      $\to$ **A:** "Documents are treated strictly as passive data inside `<untrusted_evidence_data>` tags; deterministic arithmetic checks run in native Python and cannot be bypassed by prompt text."
- [x] **Task VEDESH-503: Code Freeze on Feature Branch**
  - Ready to merge feature branch into `main`.

#### Verification & Tests:
```bash
python -m app.mock_env.verify_seed --all
```
