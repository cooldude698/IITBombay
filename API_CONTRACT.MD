# REST API Contract & Interface Specification — VERIACT

> **Project:** VERIACT (*Risk-Adaptive Runtime Verification for AI Agents*)  
> **API Version:** `v1.0.0`  
> **Specification Standard:** OpenAPI 3.1  
> **Base URL:** `http://127.0.0.1:8000/api/v1`  

---

## 1. Authentication & Global Headers

All API requests must supply one of the following authentication headers:
- `X-API-Key: veriact_live_sec_991823ab49`
- `Authorization: Bearer <jwt_access_token>`

### Common Response Headers:
- `X-Veriact-Latency-Ms`: Integer (e.g., `42`)
- `X-Veriact-Tier`: String (`FAST`, `STRONG`, `DEEP`)
- `X-Veriact-Verdict`: String (`EXECUTE`, `ESCALATE`, `BLOCK`)

---

## 2. API Endpoints Summary

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| `POST` | `/intercept/action` | **Core Interceptor**: Evaluates agent tool call; issues execution token or blocks. | Agent Runtime |
| `POST` | `/verify/evaluate` | Standalone verification endpoint for testing and benchmark runs. | Developer / Tester |
| `GET` | `/actions/traces` | Retrieves paginated historical audit traces with risk scores and tier filters. | Dashboard |
| `GET` | `/actions/traces/{trace_id}` | Detailed trace breakdown with ground-truth evidence and parameter diff. | Dashboard |
| `GET` | `/escalation/queue` | Retrieves all pending actions awaiting human managerial review. | Human Reviewer |
| `POST` | `/escalation/{item_id}/decision` | Submits human review verdict (`APPROVE` or `REJECT`) for held action. | Manager |
| `GET` | `/ground-truth/invoices` | Queries mock ERP invoice directory. | Dashboard / Audit |
| `GET` | `/ground-truth/vendors` | Queries mock ERP vendor directory. | Dashboard / Audit |
| `POST` | `/benchmark/run` | Triggers test suite execution across all 4 baselines. | Benchmark Runner |
| `GET` | `/benchmark/results` | Fetches latest benchmark evaluation metrics and safety-cost curves. | Dashboard |
| `GET` | `/analytics/stats` | Returns real-time KPI counts (Total, Verified, Escalated, Blocked, Avg Latency). | Dashboard |

---

## 3. Endpoint Specifications

### 3.1 Intercept Proposed Action
`POST /api/v1/intercept/action`

**Description**: Intercepts an agent's proposed tool invocation *before* execution. Evaluates ground truth, runs deterministic policy checks, computes multi-factor risk, routes through adaptive tier, and returns verdict.

#### Request Body (`application/json`):
```json
{
  "agent_id": "agent_fin_sr",
  "tool_name": "make_payment",
  "raw_arguments": {
    "vendor": "ABC Technologies Pvt Ltd",
    "amount": 25000,
    "invoice": "INV-1921",
    "currency": "INR"
  },
  "user_request": "Pay the approved invoice INV-1921 for ABC Technologies",
  "session_id": "sess_882910"
}
```

#### Response 200 OK (Action Blocked - Contradiction Detected):
```json
{
  "action_id": "act_884920-a712-4e9b",
  "verdict": "BLOCK",
  "verification_tier": "DEEP",
  "risk_assessment": {
    "financial_impact": 0.25,
    "irreversibility": 1.0,
    "permission_risk": 0.5,
    "evidence_uncertainty": 0.0,
    "contradiction_severity": 1.0,
    "total_risk_score": 0.9375
  },
  "mismatches": [
    {
      "field_name": "amount",
      "proposed_value": 25000.0,
      "evidence_value": 18500.0,
      "severity": "CRITICAL",
      "message": "Proposed amount ₹25,000 exceeds approved invoice amount ₹18,500 by ₹6,500."
    }
  ],
  "policy_violations": [],
  "reason": "Parameter mismatch detected: Proposed amount ₹25,000 does not match approved invoice amount ₹18,500.",
  "execution_token": null,
  "latency_ms": 48,
  "trace_id": "trc_994821a8"
}
```

#### Response 200 OK (Action Approved - Safe Execution):
```json
{
  "action_id": "act_102931-c421-4f11",
  "verdict": "EXECUTE",
  "verification_tier": "FAST",
  "risk_assessment": {
    "financial_impact": 0.034,
    "irreversibility": 0.1,
    "permission_risk": 0.1,
    "evidence_uncertainty": 0.0,
    "contradiction_severity": 0.0,
    "total_risk_score": 0.088
  },
  "mismatches": [],
  "policy_violations": [],
  "reason": "All parameters match ground truth invoice INV-102. Action authorized under Tier 1.",
  "execution_token": "veriact_tok_sha256_88e3a2b1c4d9e0f1...",
  "latency_ms": 32,
  "trace_id": "trc_102931bc"
}
```

#### Response 202 Accepted (Action Escalated to Human Review):
```json
{
  "action_id": "act_771829-f810-43aa",
  "verdict": "ESCALATE",
  "verification_tier": "DEEP",
  "risk_assessment": {
    "financial_impact": 0.185,
    "irreversibility": 1.0,
    "permission_risk": 0.5,
    "evidence_uncertainty": 0.0,
    "contradiction_severity": 0.0,
    "total_risk_score": 0.746
  },
  "mismatches": [],
  "policy_violations": [
    "POL-FIN-001: Payment ₹18,500 exceeds autonomous threshold of ₹10,000. Manager signoff required."
  ],
  "reason": "Policy threshold exceeded. Action routed to operations escalation queue.",
  "execution_token": null,
  "latency_ms": 112,
  "trace_id": "trc_771829aa"
}
```

---

### 3.2 Human Escalation Decision
`POST /api/v1/escalation/{item_id}/decision`

#### Request Body:
```json
{
  "decision": "APPROVE",
  "reviewer_id": "mgr_vikram",
  "notes": "Verified invoice with vendor POC via phone. Override authorized."
}
```

#### Response 200 OK:
```json
{
  "item_id": "esc_991823",
  "status": "APPROVED",
  "execution_token": "veriact_tok_override_991823_sha256...",
  "resolved_at": "2026-10-07T22:35:10Z"
}
```

---

### 3.3 Analytics & Live Metrics
`GET /api/v1/analytics/stats`

#### Response 200 OK:
```json
{
  "total_actions_today": 1284,
  "verified_executed": 1213,
  "escalated": 48,
  "blocked": 23,
  "fast_tier_count": 892,
  "strong_tier_count": 274,
  "deep_tier_count": 118,
  "average_latency_ms": 284,
  "p95_latency_ms": 780,
  "safety_recall_rate": 0.968
}
```

---

### 3.4 Benchmark Run Trigger
`POST /api/v1/benchmark/run`

#### Request Body:
```json
{
  "dataset_name": "VERIACT-ASB",
  "sample_size": 250,
  "baselines": ["NO_GUARDRAIL", "LLM_JUDGE", "ALWAYS_DEEP", "VERIACT_ADAPTIVE"]
}
```

#### Response 200 OK:
```json
{
  "run_id": "bmk_20261007_01",
  "status": "COMPLETED",
  "total_scenarios_evaluated": 250,
  "results": [
    {
      "system": "No Guardrail",
      "safety_recall": 0.142,
      "false_block_rate": 0.000,
      "avg_latency_ms": 18,
      "cost_per_1k": 0.00
    },
    {
      "system": "LLM-as-a-Judge",
      "safety_recall": 0.776,
      "false_block_rate": 0.138,
      "avg_latency_ms": 1120,
      "cost_per_1k": 4.80
    },
    {
      "system": "Always-Deep Verifier",
      "safety_recall": 0.984,
      "false_block_rate": 0.048,
      "avg_latency_ms": 2180,
      "cost_per_1k": 7.40
    },
    {
      "system": "VERIACT (Risk-Adaptive)",
      "safety_recall": 0.972,
      "false_block_rate": 0.028,
      "avg_latency_ms": 384,
      "cost_per_1k": 1.45
    }
  ]
}
```

---

## 4. Example Curl Invocations

### Test Invoice Mismatch Block:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/intercept/action \
  -H "Content-Type: application/json" \
  -H "X-API-Key: veriact_live_sec_991823ab49" \
  -d '{
    "agent_id": "agent_fin_sr",
    "tool_name": "make_payment",
    "raw_arguments": {
      "vendor": "ABC Technologies Pvt Ltd",
      "amount": 25000,
      "invoice": "INV-1921"
    },
    "user_request": "Pay invoice INV-1921"
  }'
```
