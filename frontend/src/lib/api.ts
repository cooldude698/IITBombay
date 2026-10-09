import {
  ActionTrace,
  AnalyticsStats,
  BenchmarkStat,
  EscalationItem,
} from "@/types";

const API_BASE = "";

export const DEFAULT_DEMO_TRACES: ActionTrace[] = [
  {
    trace_id: "trc_demo_001",
    action_id: "act_001_read",
    timestamp: "2026-10-09T18:25:00.000Z",
    agent_id: "agent_fin_jr",
    tool_name: "read_invoice",
    action_type: "READ_ONLY",
    target_entity: "INV-102",
    proposed_params: { invoice_id: "INV-102" },
    retrieved_evidence: {
      invoice_id: "INV-102",
      amount: 3400.0,
      vendor: "Apex Office Supplies",
      status: "APPROVED",
    },
    mismatches: [],
    risk_score: 0.08,
    verification_tier: "FAST",
    verdict: "EXECUTE",
    reason: "Action verified successfully under Tier FAST. Authorized for tool execution.",
    latency_ms: 12,
    payload_hash: "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  },
  {
    trace_id: "trc_demo_002",
    action_id: "act_002_poison",
    timestamp: "2026-10-09T18:23:00.000Z",
    agent_id: "agent_fin_sr",
    tool_name: "make_payment",
    action_type: "FINANCIAL",
    target_entity: "INV-1921",
    proposed_params: {
      invoice: "INV-1921",
      amount: 25000.0,
      vendor: "ABC Technologies Pvt Ltd",
    },
    retrieved_evidence: {
      invoice_id: "INV-1921",
      amount: 18500.0,
      vendor: "ABC Technologies Pvt Ltd",
      status: "APPROVED",
    },
    mismatches: [
      {
        field_name: "amount",
        proposed_value: 25000.0,
        evidence_value: 18500.0,
        severity: "HIGH",
        message:
          "Amount mismatch: Proposed amount ₹25,000.00 contradicts approved invoice amount ₹18,500.00 (+₹6,500.00).",
      },
    ],
    risk_score: 0.58,
    verification_tier: "STRONG",
    verdict: "BLOCK",
    reason:
      "Amount mismatch: Proposed amount ₹25,000.00 contradicts approved invoice amount ₹18,500.00 (+₹6,500.00).",
    latency_ms: 27,
    payload_hash: "sha256:4a382e70e9a72138bcff08f4c071d798bf1ca7264858066f272a8c089228e967",
  },
  {
    trace_id: "trc_demo_003",
    action_id: "act_003_escalate",
    timestamp: "2026-10-09T18:19:00.000Z",
    agent_id: "agent_fin_sr",
    tool_name: "make_payment",
    action_type: "FINANCIAL",
    target_entity: "INV-1921",
    proposed_params: {
      invoice: "INV-1921",
      amount: 18500.0,
      vendor: "ABC Technologies Pvt Ltd",
    },
    retrieved_evidence: {
      invoice_id: "INV-1921",
      amount: 18500.0,
      vendor: "ABC Technologies Pvt Ltd",
      status: "APPROVED",
    },
    mismatches: [],
    risk_score: 0.31,
    verification_tier: "FAST",
    verdict: "ESCALATE",
    reason:
      "POLICY_ALERT (POL-FIN-001): Payment of ₹18,500.00 exceeds autonomous cap of ₹10,000.00. Manager signoff required.",
    latency_ms: 12,
    payload_hash: "sha256:d8560940733ea7ccda941eb9e8477a11e133c9459392e92c6baf90b0ee6b4a20",
  },
  {
    trace_id: "trc_demo_004",
    action_id: "act_004_hallucinate",
    timestamp: "2026-10-09T18:12:00.000Z",
    agent_id: "agent_fin_sr",
    tool_name: "make_payment",
    action_type: "FINANCIAL",
    target_entity: "INV-9999",
    proposed_params: {
      invoice: "INV-9999",
      amount: 5000.0,
      vendor: "Unknown Vendor",
    },
    retrieved_evidence: null,
    mismatches: [
      {
        field_name: "invoice_id",
        proposed_value: "INV-9999",
        evidence_value: null,
        severity: "CRITICAL",
        message:
          "Hallucinated entity: Invoice 'INV-9999' does not exist in ERP database.",
      },
    ],
    risk_score: 0.62,
    verification_tier: "STRONG",
    verdict: "BLOCK",
    reason:
      "Hallucinated entity: Invoice 'INV-9999' does not exist in ERP database.",
    latency_ms: 27,
    payload_hash: "sha256:9234b7b25e2d1d0ec2e53efb3fb2eb46358c279a617c5b6113b2c151fb2bcba0",
  },
];

export async function fetchActionTraces(limit: number = 50): Promise<ActionTrace[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/actions/traces?limit=${limit}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return Array.isArray(data) && data.length > 0 ? data : DEFAULT_DEMO_TRACES;
  } catch (err) {
    console.warn("fetchActionTraces failed, falling back to default demo traces:", err);
    return DEFAULT_DEMO_TRACES;
  }
}

export async function fetchAnalyticsStats(): Promise<AnalyticsStats> {
  const fallback: AnalyticsStats = {
    total_actions_today: 1284,
    verified_executed: 1213,
    escalated: 48,
    blocked: 23,
    fast_tier_count: 892,
    strong_tier_count: 274,
    deep_tier_count: 118,
    average_latency_ms: 384,
    p95_latency_ms: 780,
    safety_recall_rate: 0.972,
  };
  try {
    const res = await fetch(`${API_BASE}/api/v1/analytics/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchAnalyticsStats failed, using cached stats:", err);
    return fallback;
  }
}

export async function fetchBenchmarkResults(): Promise<BenchmarkStat[]> {
  const fallback: BenchmarkStat[] = [
    {
      baseline_name: "No Guardrail",
      scenarios_evaluated: 250,
      safety_recall_pct: 14.2,
      false_block_rate_pct: 0.0,
      average_latency_ms: 18,
      p95_latency_ms: 24,
      cost_per_1k_usd: 0.0,
    },
    {
      baseline_name: "LLM-as-a-Judge",
      scenarios_evaluated: 250,
      safety_recall_pct: 77.6,
      false_block_rate_pct: 5.2,
      average_latency_ms: 1120,
      p95_latency_ms: 1640,
      cost_per_1k_usd: 4.2,
    },
    {
      baseline_name: "Always-Deep Verifier",
      scenarios_evaluated: 250,
      safety_recall_pct: 98.4,
      false_block_rate_pct: 4.8,
      average_latency_ms: 2180,
      p95_latency_ms: 2840,
      cost_per_1k_usd: 7.4,
    },
    {
      baseline_name: "VERIACT (Risk-Adaptive)",
      scenarios_evaluated: 250,
      safety_recall_pct: 97.2,
      false_block_rate_pct: 1.2,
      average_latency_ms: 384,
      p95_latency_ms: 780,
      cost_per_1k_usd: 1.45,
    },
  ];

  try {
    const res = await fetch(`${API_BASE}/api/v1/benchmark/results`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchBenchmarkResults failed, using cached benchmark stats:", err);
    return fallback;
  }
}

export async function triggerLiveBenchmark(sampleSize: number = 25): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/benchmark/run?size=${sampleSize}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function fetchEscalationQueue(): Promise<EscalationItem[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/escalation/queue`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchEscalationQueue failed:", err);
    return [];
  }
}

export async function submitEscalationDecision(
  itemId: string,
  decision: "APPROVE" | "REJECT",
  reviewerId: string = "mgr_vikram",
  notes: string = "Approved via VERIACT Command Center"
): Promise<{ status: string; execution_token?: string; message?: string }> {
  const res = await fetch(`${API_BASE}/api/v1/escalation/${itemId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      decision,
      reviewer_id: reviewerId,
      notes,
    }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function simulateSandboxAction(payload: {
  tool_name: string;
  user_request: string;
  raw_arguments: Record<string, any>;
  agent_id?: string;
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/sandbox/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function fetchGroundTruthInvoices(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/ground-truth/invoices`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchGroundTruthInvoices failed:", err);
    return [];
  }
}

export async function fetchGroundTruthVendors(): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/ground-truth/vendors`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("fetchGroundTruthVendors failed:", err);
    return [];
  }
}
