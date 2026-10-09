"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  ActionTrace,
  AnalyticsStats,
  BenchmarkStat,
  EscalationItem,
} from "@/types";
import {
  fetchActionTraces,
  fetchAnalyticsStats,
  fetchBenchmarkResults,
  fetchEscalationQueue,
  DEFAULT_DEMO_TRACES,
} from "@/lib/api";
import { TelemetryRibbon } from "@/components/TelemetryRibbon";
import { ActionStreamTable } from "@/components/ActionStreamTable";
import { TraceDrawer } from "@/components/TraceDrawer";
import { EscalationQueue } from "@/components/EscalationQueue";
import { ParetoChart } from "@/components/ParetoChart";
import { AttackSandbox } from "@/components/AttackSandbox";
import { GroundTruthModal } from "@/components/GroundTruthModal";
import {
  Shield,
  Activity,
  AlertTriangle,
  TrendingUp,
  Flame,
  Database,
  RefreshCw,
  Zap,
  Radio,
  Sliders,
  Sparkles,
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<
    "stream" | "escalation" | "benchmark" | "sandbox"
  >("stream");

  const [stats, setStats] = useState<AnalyticsStats>({
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
  });

  const [traces, setTraces] = useState<ActionTrace[]>(DEFAULT_DEMO_TRACES);
  const [selectedTrace, setSelectedTrace] = useState<ActionTrace | null>(null);
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [benchmarkStats, setBenchmarkStats] = useState<BenchmarkStat[]>([]);
  const [groundTruthOpen, setGroundTruthOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLiveStreaming, setIsLiveStreaming] = useState(true);

  const loadAllData = async () => {
    try {
      setIsRefreshing(true);
      const [s, t, e, b] = await Promise.all([
        fetchAnalyticsStats(),
        fetchActionTraces(50),
        fetchEscalationQueue(),
        fetchBenchmarkResults(),
      ]);
      setStats(s);
      if (t && t.length > 0) {
        setTraces(t);
      }
      setEscalations(e);
      setBenchmarkStats(b);
    } catch (err) {
      console.error("Data loading error:", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  // Live Traffic Simulation Engine: Emits realistic agent events when enabled
  useEffect(() => {
    if (!isLiveStreaming) return;

    const SIMULATED_ACTIONS: Partial<ActionTrace>[] = [
      {
        agent_id: "agent_fin_jr",
        tool_name: "read_invoice",
        action_type: "READ_ONLY",
        target_entity: "INV-101",
        proposed_params: { invoice_id: "INV-101" },
        retrieved_evidence: { invoice_id: "INV-101", amount: 5000.0, status: "APPROVED" },
        mismatches: [],
        risk_score: 0.06,
        verification_tier: "FAST",
        verdict: "EXECUTE",
        reason: "Read action verified within Fast Tier limits. Direct execution approved.",
        latency_ms: 16,
      },
      {
        agent_id: "agent_ops_bot",
        tool_name: "query_inventory",
        action_type: "READ_ONLY",
        target_entity: "SKU-PRO-402",
        proposed_params: { sku_id: "SKU-PRO-402" },
        retrieved_evidence: { sku_id: "SKU-PRO-402", stock: 140 },
        mismatches: [],
        risk_score: 0.04,
        verification_tier: "FAST",
        verdict: "EXECUTE",
        reason: "Low risk inventory query authorized.",
        latency_ms: 12,
      },
      {
        agent_id: "agent_fin_sr",
        tool_name: "make_payment",
        action_type: "FINANCIAL",
        target_entity: "Prime Supplies Ltd",
        proposed_params: { vendor: "Prime Supplies Ltd", amount: 3400.0, invoice: "INV-102" },
        retrieved_evidence: { invoice_id: "INV-102", amount: 3400.0, status: "APPROVED" },
        mismatches: [],
        risk_score: 0.28,
        verification_tier: "FAST",
        verdict: "EXECUTE",
        reason: "Invoice payment matches verified ERP parameters (< ₹10,000 threshold).",
        latency_ms: 19,
      },
      {
        agent_id: "agent_fin_mgr",
        tool_name: "make_payment",
        action_type: "FINANCIAL",
        target_entity: "Global Logistics Corp",
        proposed_params: { vendor: "Global Logistics Corp", amount: 32000.0, invoice: "INV-992" },
        retrieved_evidence: { invoice_id: "INV-992", amount: 32000.0, status: "APPROVED" },
        mismatches: [],
        risk_score: 0.68,
        verification_tier: "STRONG",
        verdict: "ESCALATE",
        reason: "Rule POL-FIN-001: Amount exceeds ₹10,000 policy threshold. Held for dual-approval.",
        latency_ms: 280,
      },
    ];

    let actionIndex = 0;
    const interval = setInterval(() => {
      const template = SIMULATED_ACTIONS[actionIndex % SIMULATED_ACTIONS.length];
      actionIndex++;

      const newTrace: ActionTrace = {
        trace_id: `trc_${Math.random().toString(36).substring(2, 10)}`,
        action_id: `act_${Math.floor(100000 + Math.random() * 900000)}`,
        timestamp: new Date().toISOString(),
        agent_id: template.agent_id || "agent_fin_sr",
        tool_name: template.tool_name || "read_invoice",
        action_type: template.action_type || "READ_ONLY",
        target_entity: template.target_entity || "ERP System",
        proposed_params: template.proposed_params || {},
        retrieved_evidence: template.retrieved_evidence || null,
        mismatches: template.mismatches || [],
        risk_score: template.risk_score || 0.15,
        verification_tier: template.verification_tier || "FAST",
        verdict: template.verdict || "EXECUTE",
        reason: template.reason || "Action authorized.",
        latency_ms: template.latency_ms || 24,
        payload_hash: `sha256:${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`,
      };

      setTraces((prev) => [newTrace, ...prev.slice(0, 49)]);
      setStats((prev) => ({
        ...prev,
        total_actions_today: prev.total_actions_today + 1,
        verified_executed: template.verdict === "EXECUTE" ? prev.verified_executed + 1 : prev.verified_executed,
        escalated: template.verdict === "ESCALATE" ? prev.escalated + 1 : prev.escalated,
        blocked: template.verdict === "BLOCK" ? prev.blocked + 1 : prev.blocked,
      }));
    }, 4500);

    return () => clearInterval(interval);
  }, [isLiveStreaming]);

  // Quick Attack Injection: Adds a blocked high-risk attack and pops open the Trace Drawer!
  const triggerSimulatedAttack = () => {
    const attackTrace: ActionTrace = {
      trace_id: `trc_atk_${Math.random().toString(36).substring(2, 8)}`,
      action_id: `act_${Math.floor(100000 + Math.random() * 900000)}`,
      timestamp: new Date().toISOString(),
      agent_id: "agent_compromised_01",
      tool_name: "make_payment",
      action_type: "FINANCIAL",
      target_entity: "ABC Technologies Pvt Ltd",
      proposed_params: {
        vendor: "ABC Technologies Pvt Ltd",
        amount: 25000.0, // Parameter mismatch attack
        invoice: "INV-1921",
      },
      retrieved_evidence: {
        invoice_id: "INV-1921",
        amount: 18500.0,
        status: "APPROVED",
        vendor_id: "VND-001",
      },
      mismatches: [
        {
          field_name: "amount",
          proposed_value: 25000.0,
          evidence_value: 18500.0,
          severity: "CRITICAL",
          message: "Proposed amount INR 25,000.00 contradicts verified ERP invoice amount INR 18,500.00 (Delta: +INR 6,500.00)",
        },
      ],
      risk_score: 0.95,
      verification_tier: "DEEP",
      verdict: "BLOCK",
      reason: "Critical parameter tampering detected: Amount INR 25,000 exceeds verified ERP record INR 18,500. Pre-execution token withheld.",
      latency_ms: 46,
      payload_hash: `sha256:attack_${Math.random().toString(36).substring(2, 12)}`,
    };

    setTraces((prev) => [attackTrace, ...prev]);
    setSelectedTrace(attackTrace);
    setActiveTab("stream");
    setStats((prev) => ({
      ...prev,
      total_actions_today: prev.total_actions_today + 1,
      blocked: prev.blocked + 1,
    }));
  };

  const pendingEscalationsCount = escalations.filter((i) => i.status === "PENDING").length;

  return (
    <main className="min-h-screen bg-[#0A121C] text-[#EAE6DE] flex flex-col font-sans selection:bg-[#EF8557]/30 selection:text-[#EAE6DE]">
      {/* Top Brand Navigation Bar */}
      <header className="border-b border-[#226192]/40 bg-[#0B1522]/95 backdrop-blur-xl px-6 py-4 sticky top-0 z-40 shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-[#226192] to-[#123652] flex items-center justify-center border-2 border-[#EF8557] shadow-lg shadow-[#226192]/40">
              <Shield className="w-6 h-6 text-[#EAE6DE]" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <h1 className="text-2xl font-black tracking-wider text-[#EAE6DE] font-display">
                  VERIACT
                </h1>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[#EF8557] text-[#0A121C] font-code">
                  v1.0.0
                </span>
                <span className="text-xs font-code text-sky-200/70 border-l border-[#226192]/60 pl-2.5 hidden sm:inline">
                  IIT Bombay Techfest PS-9
                </span>
              </div>
              <p className="text-xs text-[#EF8557] font-semibold tracking-wide flex items-center space-x-1.5 mt-0.5">
                <span>Verify the Action. Then Let the Agent Act.</span>
              </p>
            </div>
          </div>

          {/* Quick Action Controls */}
          <div className="flex items-center space-x-3">
            {/* Live Traffic Toggle */}
            <button
              onClick={() => setIsLiveStreaming(!isLiveStreaming)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-code font-bold flex items-center space-x-2 transition-all shadow-sm ${
                isLiveStreaming
                  ? "bg-emerald-950/60 border-emerald-500/50 text-emerald-400"
                  : "bg-[#08111A] border-slate-700 text-slate-400"
              }`}
            >
              <Radio className={`w-3.5 h-3.5 ${isLiveStreaming ? "animate-pulse text-emerald-400" : ""}`} />
              <span>{isLiveStreaming ? "Live Feed: ON" : "Live Feed: PAUSED"}</span>
            </button>

            {/* Test Attack Injection Button */}
            <button
              onClick={triggerSimulatedAttack}
              className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#EF8557] to-[#f09a74] hover:from-[#f09a74] hover:to-[#EF8557] text-[#0A121C] text-xs font-bold font-display flex items-center space-x-1.5 transition-all shadow-lg shadow-[#EF8557]/25 active:scale-95"
            >
              <Zap className="w-3.5 h-3.5 text-[#0A121C]" />
              <span>Trigger Test Attack</span>
            </button>

            {/* ERP Ground Truth Modal Trigger */}
            <button
              onClick={() => setGroundTruthOpen(true)}
              className="px-3 py-1.5 rounded-xl bg-[#0F1C2A] hover:bg-[#162a3f] border border-[#226192]/60 text-xs font-code font-semibold text-[#EAE6DE] flex items-center space-x-1.5 transition-colors shadow"
            >
              <Database className="w-3.5 h-3.5 text-sky-300" />
              <span className="hidden sm:inline">ERP Ground Truth</span>
            </button>

            {/* Refresh Button */}
            <button
              onClick={loadAllData}
              disabled={isRefreshing}
              className="p-2 rounded-xl bg-[#0F1C2A] hover:bg-[#162a3f] border border-[#226192]/60 text-slate-300 hover:text-[#EAE6DE] transition-colors"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-[#EF8557]" : ""}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Top Telemetry Ribbon */}
      <TelemetryRibbon stats={stats} />

      {/* Main Command Center Container */}
      <div className="max-w-7xl mx-auto w-full px-6 py-6 flex-1 flex flex-col space-y-6">
        {/* Navigation Tabs Bar */}
        <div className="flex flex-wrap items-center bg-[#0B1522]/80 p-1.5 rounded-2xl border border-[#226192]/40 gap-1.5 shadow-lg">
          <button
            onClick={() => setActiveTab("stream")}
            className={`py-2.5 px-4 rounded-xl font-bold font-display text-xs flex items-center space-x-2 transition-all ${
              activeTab === "stream"
                ? "bg-[#226192] text-[#EAE6DE] shadow-md shadow-[#226192]/40 border border-sky-400/30"
                : "text-slate-400 hover:text-[#EAE6DE] hover:bg-[#122335]"
            }`}
          >
            <Activity className="w-4 h-4 text-sky-300" />
            <span>Live Action Stream</span>
            <span className="ml-1 px-2 py-0.5 rounded-full text-[10px] font-code bg-[#08111A] text-sky-200 border border-[#226192]/60">
              {traces.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab("escalation")}
            className={`py-2.5 px-4 rounded-xl font-bold font-display text-xs flex items-center space-x-2 transition-all relative ${
              activeTab === "escalation"
                ? "bg-[#226192] text-[#EAE6DE] shadow-md shadow-[#226192]/40 border border-sky-400/30"
                : "text-slate-400 hover:text-[#EAE6DE] hover:bg-[#122335]"
            }`}
          >
            <AlertTriangle className="w-4 h-4 text-[#EF8557]" />
            <span>Human Review Queue</span>
            {pendingEscalationsCount > 0 && (
              <span className="ml-1 px-2 py-0.5 rounded-full text-[10px] font-code font-bold bg-[#EF8557] text-[#0A121C]">
                {pendingEscalationsCount} Pending
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("benchmark")}
            className={`py-2.5 px-4 rounded-xl font-bold font-display text-xs flex items-center space-x-2 transition-all ${
              activeTab === "benchmark"
                ? "bg-[#226192] text-[#EAE6DE] shadow-md shadow-[#226192]/40 border border-sky-400/30"
                : "text-slate-400 hover:text-[#EAE6DE] hover:bg-[#122335]"
            }`}
          >
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Pareto &amp; Benchmark</span>
            <span className="ml-1 px-2 py-0.5 rounded-full text-[10px] font-code bg-[#08111A] text-slate-300 border border-[#226192]/40">
              250 Cases
            </span>
          </button>

          <button
            onClick={() => setActiveTab("sandbox")}
            className={`py-2.5 px-4 rounded-xl font-bold font-display text-xs flex items-center space-x-2 transition-all ${
              activeTab === "sandbox"
                ? "bg-[#226192] text-[#EAE6DE] shadow-md shadow-[#226192]/40 border border-sky-400/30"
                : "text-slate-400 hover:text-[#EAE6DE] hover:bg-[#122335]"
            }`}
          >
            <Flame className="w-4 h-4 text-[#EF8557]" />
            <span>Attack Sandbox</span>
            <span className="ml-1 px-2 py-0.5 rounded-full text-[10px] font-code bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/40">
              4 Presets
            </span>
          </button>
        </div>

        {/* Tab View Content */}
        <div className="flex-1">
          {activeTab === "stream" && (
            <ActionStreamTable
              traces={traces}
              selectedTrace={selectedTrace}
              onSelectTrace={setSelectedTrace}
              onTriggerDemo={triggerSimulatedAttack}
            />
          )}

          {activeTab === "escalation" && (
            <EscalationQueue items={escalations} onRefresh={loadAllData} />
          )}

          {activeTab === "benchmark" && (
            <ParetoChart stats={benchmarkStats} onRefresh={loadAllData} />
          )}

          {activeTab === "sandbox" && (
            <AttackSandbox onActionSimulated={loadAllData} />
          )}
        </div>
      </div>

      {/* Inspectable Trace Drawer (Strictly without raw CoT) */}
      <TraceDrawer trace={selectedTrace} onClose={() => setSelectedTrace(null)} />

      {/* Ground Truth Explorer Modal */}
      <GroundTruthModal
        isOpen={groundTruthOpen}
        onClose={() => setGroundTruthOpen(false)}
      />

      {/* Brand Footer */}
      <footer className="border-t border-[#226192]/40 py-5 px-6 text-center text-xs text-slate-400 font-code bg-[#0B1522]/90">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            VERIACT &bull; Pre-Execution Verification Invariant for Autonomous Agents
          </span>
          <span className="text-[#EF8557] font-semibold">
            Strict Palette: #EAE6DE &bull; #226192 &bull; #EF8557
          </span>
          <span className="text-slate-500">
            IIT Bombay Techfest / Inter-IIT Hackathon
          </span>
        </div>
      </footer>
    </main>
  );
}
