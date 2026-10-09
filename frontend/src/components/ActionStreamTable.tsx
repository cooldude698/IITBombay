"use client";

import React, { useState, useEffect } from "react";
import { ActionTrace, Verdict, VerificationTier } from "@/types";
import {
  Search,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ArrowRight,
  Bot,
  Zap,
  RotateCcw,
  Sparkles,
} from "lucide-react";

interface ActionStreamTableProps {
  traces: ActionTrace[];
  selectedTrace: ActionTrace | null;
  onSelectTrace: (trace: ActionTrace) => void;
  onTriggerDemo?: () => void;
}

export const ActionStreamTable: React.FC<ActionStreamTableProps> = ({
  traces,
  selectedTrace,
  onSelectTrace,
  onTriggerDemo,
}) => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const [filterVerdict, setFilterVerdict] = useState<string>("ALL");
  const [filterTier, setFilterTier] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState<string>("");

  const formatTimestamp = (timestamp: string) => {
    if (!mounted) return "--:--:--";
    try {
      const d = new Date(timestamp);
      return isNaN(d.getTime())
        ? timestamp
        : d.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hour12: false,
          });
    } catch {
      return timestamp;
    }
  };

  const filteredTraces = traces.filter((t) => {
    const matchesVerdict = filterVerdict === "ALL" || t.verdict === filterVerdict;
    const matchesTier = filterTier === "ALL" || t.verification_tier === filterTier;
    const matchesSearch =
      t.agent_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.tool_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.target_entity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.action_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesVerdict && matchesTier && matchesSearch;
  });

  const getVerdictBadge = (verdict: Verdict) => {
    switch (verdict) {
      case "EXECUTE":
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-500/50 shadow-sm shadow-emerald-900/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>EXECUTE</span>
          </span>
        );
      case "ESCALATE":
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/60 shadow-sm shadow-[#EF8557]/20">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>ESCALATE</span>
          </span>
        );
      case "BLOCK":
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-950/80 text-rose-400 border border-rose-500/50 shadow-sm shadow-rose-900/30">
            <XCircle className="w-3.5 h-3.5" />
            <span>BLOCK</span>
          </span>
        );
    }
  };

  const getTierBadge = (tier: VerificationTier) => {
    switch (tier) {
      case "FAST":
        return (
          <span className="px-2.5 py-1 rounded-md text-[11px] font-code font-bold bg-[#226192]/25 text-sky-300 border border-[#226192]/60">
            FAST &bull; &lt;150ms
          </span>
        );
      case "STRONG":
        return (
          <span className="px-2.5 py-1 rounded-md text-[11px] font-code font-bold bg-purple-950/50 text-purple-300 border border-purple-500/40">
            STRONG &bull; &lt;800ms
          </span>
        );
      case "DEEP":
        return (
          <span className="px-2.5 py-1 rounded-md text-[11px] font-code font-bold bg-[#EF8557]/25 text-[#EF8557] border border-[#EF8557]/60">
            DEEP &bull; &lt;2000ms
          </span>
        );
    }
  };

  const getRiskMeterColor = (score: number) => {
    if (score <= 0.35) return "from-emerald-400 to-teal-400";
    if (score <= 0.70) return "from-amber-400 to-[#EF8557]";
    return "from-[#EF8557] to-rose-500";
  };

  return (
    <div className="w-full bg-[#0F1C2A]/90 backdrop-blur-xl rounded-2xl border border-[#226192]/40 overflow-hidden shadow-2xl">
      {/* Table Header Controls */}
      <div className="px-6 py-5 border-b border-[#226192]/40 bg-[#0B1522]/90 flex flex-wrap items-center justify-between gap-4">
        {/* Title & Live Status */}
        <div className="flex items-center space-x-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#226192]/30 border border-[#226192]/60 flex items-center justify-center text-[#EF8557]">
            <ShieldAlert className="w-5 h-5 text-[#EF8557]" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <h2 className="text-base font-display font-bold text-[#EAE6DE] tracking-wide">
                Live Action Telemetry Stream
              </h2>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#226192]/30 text-sky-200 border border-[#226192]/50 font-code font-semibold">
                {filteredTraces.length} events
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time pre-execution intercept log with continuous mathematical risk scoring
            </p>
          </div>
        </div>

        {/* Search & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Search Bar */}
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search agent, tool, entity..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-[#070E17] text-sm text-[#EAE6DE] pl-10 pr-4 py-2 rounded-xl border border-[#226192]/40 focus:border-[#EF8557] focus:outline-none transition-all placeholder:text-slate-500 font-sans"
            />
          </div>

          {/* Quick Demo Intercept Trigger */}
          {onTriggerDemo && (
            <button
              onClick={onTriggerDemo}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-[#EF8557] hover:bg-[#ff9468] text-[#0A121C] transition-all shadow-md shadow-[#EF8557]/20 active:scale-95"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Simulate Attack</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Tabs Bar */}
      <div className="px-6 py-3 bg-[#0B1522]/50 border-b border-[#226192]/30 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Verdict Filters */}
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-400 font-medium mr-1.5">Verdict:</span>
          {["ALL", "EXECUTE", "ESCALATE", "BLOCK"].map((v) => (
            <button
              key={v}
              onClick={() => setFilterVerdict(v)}
              className={`px-3 py-1.5 rounded-lg font-code font-semibold transition-all ${
                filterVerdict === v
                  ? "bg-[#226192] text-[#EAE6DE] shadow-md shadow-[#226192]/40 border border-sky-400/40"
                  : "bg-[#08111A] text-slate-400 hover:text-[#EAE6DE] hover:bg-[#142334] border border-[#226192]/30"
              }`}
            >
              {v}
            </button>
          ))}
        </div>

        {/* Tier Filters */}
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-400 font-medium mr-1.5">Tier:</span>
          {["ALL", "FAST", "STRONG", "DEEP"].map((t) => (
            <button
              key={t}
              onClick={() => setFilterTier(t)}
              className={`px-2.5 py-1.5 rounded-lg font-code font-semibold transition-all ${
                filterTier === t
                  ? "bg-[#226192] text-[#EAE6DE] border border-sky-400/40"
                  : "bg-[#08111A] text-slate-400 hover:text-[#EAE6DE] hover:bg-[#142334] border border-[#226192]/30"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-[11px] uppercase tracking-wider text-slate-300 bg-[#08111A]/90 border-b border-[#226192]/40 font-code font-bold">
            <tr>
              <th className="py-3.5 px-5">Timestamp</th>
              <th className="py-3.5 px-4">Agent ID</th>
              <th className="py-3.5 px-4">Tool Name</th>
              <th className="py-3.5 px-4">Target Entity</th>
              <th className="py-3.5 px-4">Risk Meter</th>
              <th className="py-3.5 px-4">Tier</th>
              <th className="py-3.5 px-4">Verdict</th>
              <th className="py-3.5 px-4 text-right">Latency</th>
              <th className="py-3.5 px-4 text-center">Inspect</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#226192]/20 font-sans">
            {filteredTraces.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-16 text-center">
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <div className="w-12 h-12 rounded-2xl bg-[#08111A] border border-[#226192]/50 flex items-center justify-center text-slate-500">
                      <RotateCcw className="w-6 h-6" />
                    </div>
                    <p className="text-base font-semibold text-[#EAE6DE]">
                      No events match your selected filters
                    </p>
                    <p className="text-xs text-slate-400 max-w-sm">
                      Try clearing search parameters or reset filter tabs to view live intercept telemetry.
                    </p>
                    <button
                      onClick={() => {
                        setFilterVerdict("ALL");
                        setFilterTier("ALL");
                        setSearchTerm("");
                      }}
                      className="mt-2 px-4 py-2 rounded-xl text-xs font-bold bg-[#226192] text-[#EAE6DE] hover:bg-[#2c77b0] transition-colors"
                    >
                      Reset All Filters
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              filteredTraces.map((trace) => {
                const isSelected = selectedTrace?.trace_id === trace.trace_id;
                const formattedTime = formatTimestamp(trace.timestamp);

                return (
                  <tr
                    key={trace.trace_id}
                    onClick={() => onSelectTrace(trace)}
                    className={`cursor-pointer transition-all duration-150 group ${
                      isSelected
                        ? "bg-[#226192]/30 border-l-4 border-l-[#EF8557]"
                        : "hover:bg-[#142538]/70"
                    }`}
                  >
                    {/* Timestamp */}
                    <td
                      suppressHydrationWarning
                      className="py-4 px-5 font-code text-xs text-slate-400 whitespace-nowrap"
                    >
                      {formattedTime}
                    </td>

                    {/* Agent ID */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 rounded-md bg-[#226192]/30 border border-[#226192]/50 flex items-center justify-center text-sky-300">
                          <Bot className="w-3.5 h-3.5" />
                        </div>
                        <span className="font-code text-xs text-[#EAE6DE] font-semibold">
                          {trace.agent_id}
                        </span>
                      </div>
                    </td>

                    {/* Tool Name */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      <span className="px-2.5 py-1 rounded-lg bg-[#08111A] border border-[#226192]/50 text-[#EAE6DE] font-code text-xs font-semibold shadow-inner">
                        {trace.tool_name}
                      </span>
                    </td>

                    {/* Target Entity */}
                    <td className="py-4 px-4 font-medium text-slate-200 max-w-[220px] truncate text-xs">
                      {trace.target_entity}
                    </td>

                    {/* Risk Meter */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-24 bg-[#08111A] h-2.5 rounded-full overflow-hidden border border-slate-700/60 p-[1px]">
                          <div
                            className={`h-full rounded-full bg-gradient-to-r ${getRiskMeterColor(
                              trace.risk_score
                            )} transition-all duration-300`}
                            style={{ width: `${Math.min(100, trace.risk_score * 100)}%` }}
                          />
                        </div>
                        <span className="font-code text-xs font-bold w-9 text-right text-[#EAE6DE]">
                          {trace.risk_score.toFixed(2)}
                        </span>
                      </div>
                    </td>

                    {/* Tier Badge */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      {getTierBadge(trace.verification_tier)}
                    </td>

                    {/* Verdict */}
                    <td className="py-4 px-4 whitespace-nowrap">
                      {getVerdictBadge(trace.verdict)}
                    </td>

                    {/* Latency */}
                    <td className="py-4 px-4 text-right font-code text-xs font-semibold whitespace-nowrap text-slate-300">
                      {trace.latency_ms} <span className="text-[10px] text-slate-500">ms</span>
                    </td>

                    {/* Inspect CTA */}
                    <td className="py-4 px-4 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectTrace(trace);
                        }}
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-[#226192]/30 text-sky-300 border border-[#226192]/50 group-hover:bg-[#EF8557] group-hover:text-[#0A121C] group-hover:border-[#EF8557] transition-all"
                      >
                        <span>Trace</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
