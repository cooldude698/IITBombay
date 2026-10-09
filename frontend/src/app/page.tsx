"use client";

import React, { useEffect, useState } from "react";
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

  const [traces, setTraces] = useState<ActionTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<ActionTrace | null>(null);
  const [escalations, setEscalations] = useState<EscalationItem[]>([]);
  const [benchmarkStats, setBenchmarkStats] = useState<BenchmarkStat[]>([]);
  const [groundTruthOpen, setGroundTruthOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

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
      setTraces(t);
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
    // Live update interval
    const interval = setInterval(() => {
      fetchAnalyticsStats().then(setStats);
      fetchActionTraces(50).then(setTraces);
      fetchEscalationQueue().then(setEscalations);
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  const pendingEscalationsCount = escalations.filter((i) => i.status === "PENDING").length;

  return (
    <main className="min-h-screen bg-[#0B131B] text-[#EAE6DE] flex flex-col font-sans">
      {/* Top Brand Navigation Bar */}
      <header className="border-b border-[#226192]/40 bg-[#0F1A24] px-6 py-3.5 sticky top-0 z-40 shadow-xl">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          {/* Logo & Tagline */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-[#226192] flex items-center justify-center border border-[#EF8557] shadow-lg shadow-[#226192]/30">
              <Shield className="w-6 h-6 text-[#EAE6DE]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-extrabold tracking-wider text-[#EAE6DE] font-mono">
                  VERIACT
                </h1>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#EF8557] text-[#0B131B] font-mono">
                  v1.0.0
                </span>
                <span className="text-[10px] font-mono text-slate-400 border-l border-slate-700 pl-2">
                  IIT Bombay Techfest PS-9
                </span>
              </div>
              <p className="text-xs text-[#EF8557] font-medium tracking-wide">
                Verify the Action. Then Let the Agent Act.
              </p>
            </div>
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setGroundTruthOpen(true)}
              className="px-3 py-1.5 rounded-lg bg-[#121E2B] hover:bg-[#1A2C3E] border border-[#226192]/50 text-xs font-mono font-medium text-[#EAE6DE] flex items-center space-x-1.5 transition-colors shadow"
            >
              <Database className="w-3.5 h-3.5 text-[#EF8557]" />
              <span>ERP Ground Truth</span>
            </button>

            <button
              onClick={loadAllData}
              disabled={isRefreshing}
              className="p-1.5 rounded-lg bg-[#121E2B] hover:bg-[#1A2C3E] border border-[#226192]/50 text-slate-300 hover:text-[#EAE6DE] transition-colors"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin text-[#EF8557]" : ""}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Top Telemetry Ribbon */}
      <TelemetryRibbon stats={stats} />

      {/* Main Container */}
      <div className="max-w-7xl mx-auto w-full px-6 py-6 flex-1 flex flex-col space-y-6">
        {/* Navigation Tabs */}
        <div className="flex flex-wrap items-center border-b border-[#226192]/30 text-xs font-mono gap-1">
          <button
            onClick={() => setActiveTab("stream")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-all ${
              activeTab === "stream"
                ? "border-[#EF8557] text-[#EF8557] bg-[#121E2B]/50"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Live Action Stream</span>
          </button>

          <button
            onClick={() => setActiveTab("escalation")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-all relative ${
              activeTab === "escalation"
                ? "border-[#EF8557] text-[#EF8557] bg-[#121E2B]/50"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            <span>Human Review Queue</span>
            {pendingEscalationsCount > 0 && (
              <span className="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-[#EF8557] text-[#0B131B]">
                {pendingEscalationsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("benchmark")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-all ${
              activeTab === "benchmark"
                ? "border-[#EF8557] text-[#EF8557] bg-[#121E2B]/50"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>Pareto &amp; Benchmark</span>
          </button>

          <button
            onClick={() => setActiveTab("sandbox")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-all ${
              activeTab === "sandbox"
                ? "border-[#EF8557] text-[#EF8557] bg-[#121E2B]/50"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <Flame className="w-4 h-4" />
            <span>Attack Sandbox</span>
          </button>
        </div>

        {/* Tab View Content */}
        <div className="flex-1">
          {activeTab === "stream" && (
            <ActionStreamTable
              traces={traces}
              selectedTrace={selectedTrace}
              onSelectTrace={setSelectedTrace}
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

      {/* Inspectable Trace Drawer */}
      <TraceDrawer trace={selectedTrace} onClose={() => setSelectedTrace(null)} />

      {/* Ground Truth Explorer Modal */}
      <GroundTruthModal
        isOpen={groundTruthOpen}
        onClose={() => setGroundTruthOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-[#226192]/30 py-4 px-6 text-center text-xs text-slate-500 font-mono bg-[#0F1A24]">
        <span>VERIACT — Pre-Execution Runtime Verification Layer for Autonomous AI Agents</span>
        <span className="mx-2">|</span>
        <span className="text-[#EF8557]">IIT Bombay Techfest / Inter-IIT Hackathon</span>
      </footer>
    </main>
  );
}
