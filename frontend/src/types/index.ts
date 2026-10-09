export type ActionType =
  | "FINANCIAL"
  | "DATA_MUTATION"
  | "EXTERNAL_COMMUNICATION"
  | "SYSTEM_CONFIG"
  | "READ_ONLY";

export type VerificationTier = "FAST" | "STRONG" | "DEEP";

export type Verdict = "EXECUTE" | "ESCALATE" | "BLOCK";

export type EscalationStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface ParameterMismatch {
  field_name: string;
  proposed_value: any;
  evidence_value: any;
  severity: string;
  message: string;
}

export interface RiskBreakdown {
  financial_impact: number;
  irreversibility: number;
  permission_risk: number;
  evidence_uncertainty: number;
  contradiction_severity: number;
  total_risk_score: number;
}

export interface ActionTrace {
  trace_id: string;
  action_id: string;
  timestamp: string;
  agent_id: string;
  tool_name: string;
  action_type: ActionType;
  target_entity: string;
  proposed_params: Record<string, any>;
  retrieved_evidence?: Record<string, any> | null;
  mismatches: ParameterMismatch[];
  risk_score: number;
  verification_tier: VerificationTier;
  verdict: Verdict;
  reason: string;
  latency_ms: number;
  payload_hash: string;
}

export interface EscalationItem {
  item_id: string;
  action_id: string;
  trace_id: string;
  agent_id: string;
  tool_name: string;
  action_type: ActionType;
  target_entity: string;
  proposed_params: Record<string, any>;
  retrieved_evidence?: Record<string, any> | null;
  risk_score: number;
  reason: string;
  status: EscalationStatus;
  created_at: string;
  resolved_at?: string | null;
  reviewed_by?: string | null;
  review_notes?: string | null;
  execution_token?: string | null;
}

export interface AnalyticsStats {
  total_actions_today: number;
  verified_executed: number;
  escalated: number;
  blocked: number;
  fast_tier_count: number;
  strong_tier_count: number;
  deep_tier_count: number;
  average_latency_ms: number;
  p95_latency_ms: number;
  safety_recall_rate: number;
}

export interface BenchmarkStat {
  baseline_name: string;
  scenarios_evaluated: number;
  safety_recall_pct: number;
  false_block_rate_pct: number;
  average_latency_ms: number;
  p95_latency_ms: number;
  cost_per_1k_usd: number;
}
