"use client";

import React, { useState } from "react";
import { ActionTrace, Verdict, VerificationTier } from "@/types";
import { Search, Filter, ShieldAlert, CheckCircle2, AlertTriangle, XCircle, ArrowUpRight } from "lucide-react";

interface ActionStreamTableProps {
  traces: ActionTrace[];
  selectedTrace: ActionTrace | null;
  onSelectTrace: (trace: ActionTrace) => void;
}

export const ActionStreamTable: React.FC<ActionStreamTableProps> = ({
  traces,
  selectedTrace,
  onSelectTrace,
}) => {
  const [filterVerdict, setFilterVerdict] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState<string>("");

  const filteredTraces = traces.filter((t) => {
    const matchesVerdict = filterVerdict === "ALL" || t.verdict === filterVerdict;
    const matchesSearch =
      t.agent_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.tool_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.target_entity.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.action_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesVerdict && matchesSearch;
  });

  const getVerdictBadge = (verdict: Verdict) => {
    switch (verdict) {
      case "EXECUTE":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-500/40">
            <CheckCircle2 className="w-3 h-3 mr-1" /> EXECUTE
          </span>
        );
      case "ESCALATE":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EF8557]/15 text-[#EF8557] border border-[#EF8557]/50">
            <AlertTriangle className="w-3 h-3 mr-1" /> ESCALATE
          </span>
        );
      case "BLOCK":
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-500/40">
            <XCircle className="w-3 h-3 mr-1" /> BLOCK
          </span>
        );
    }
  };

  const getTierBadge = (tier: VerificationTier) => {
    switch (tier) {
      case "FAST":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#226192]/20 text-[#226192] border border-[#226192]/40">
            FAST (&lt;150ms)
          </span>
        );
      case "STRONG":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-purple-950/40 text-purple-300 border border-purple-500/30">
            STRONG (&lt;800ms)
          </span>
        );
      case "DEEP":
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/40">
            DEEP (&lt;2000ms)
          </span>
        );
    }
  };

  const getRiskMeterColor = (score: number) => {
    if (score <= 0.35) return "bg-emerald-500";
    if (score <= 0.70) return "bg-[#EF8557]";
    return "bg-rose-500";
  };

  return (
    <div className="w-full bg-[#121E2B] rounded-xl border border-[#226192]/30 overflow-hidden shadow-xl">
      {/* Table Header Controls */}
      <div className="px-6 py-4 border-b border-[#226192]/30 flex flex-wrap items-center justify-between gap-4 bg-[#0F1A24]">
        <div className="flex items-center space-x-3">
          <ShieldAlert className="w-5 h-5 text-[#EF8557]" />
          <h2 className="text-base font-bold text-[#EAE6DE] tracking-wide">
            Live Action Telemetry Stream
          </h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-[#226192]/30 text-[#EAE6DE] border border-[#226192]/50 font-mono">
            {filteredTraces.length} events
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search agent, tool, entity..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#0B131B] border border-[#226192]/40 rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#EAE6DE] placeholder-slate-500 focus:outline-none focus:border-[#EF8557] w-64"
            />
          </div>

          {/* Verdict Filter */}
          <div className="flex items-center space-x-1 bg-[#0B131B] border border-[#226192]/40 rounded-lg p-0.5 text-xs">
            {["ALL", "EXECUTE", "ESCALATE", "BLOCK"].map((v) => (
              <button
                key={v}
                onClick={() => setFilterVerdict(v)}
                className={`px-2.5 py-1 rounded font-medium transition-colors ${
                  filterVerdict === v
                    ? "bg-[#226192] text-[#EAE6DE] shadow"
                    : "text-slate-400 hover:text-[#EAE6DE]"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table Grid */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-[#0F1A24]/60 text-slate-400 border-b border-[#226192]/20 font-mono uppercase text-[11px] tracking-wider">
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Agent ID</th>
              <th className="py-3 px-4">Tool Name</th>
              <th className="py-3 px-4">Target Entity</th>
              <th className="py-3 px-4">Risk Meter</th>
              <th className="py-3 px-4">Verification Tier</th>
              <th className="py-3 px-4">Verdict</th>
              <th className="py-3 px-4 text-right">Latency</th>
              <th className="py-3 px-2"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#226192]/15 text-[#EAE6DE]">
            {filteredTraces.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-12 text-center text-slate-500">
                  No action traces matching filter criteria.
                </td>
              </tr>
            ) : (
              filteredTraces.map((trace) => {
                const isSelected = selectedTrace?.trace_id === trace.trace_id;
                const formattedTime = new Date(trace.timestamp).toLocaleTimeString();

                return (
                  <tr
                    key={trace.trace_id}
                    onClick={() => onSelectTrace(trace)}
                    className={`cursor-pointer transition-colors duration-150 ${
                      isSelected
                        ? "bg-[#226192]/25 border-l-4 border-l-[#EF8557]"
                        : "hover:bg-[#1A2C3E]/50"
                    }`}
                  >
                    {/* Timestamp */}
                    <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                      {formattedTime}
                    </td>

                    {/* Agent ID */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span className="font-mono text-slate-300 font-medium">
                        {trace.agent_id}
                      </span>
                    </td>

                    {/* Tool Name */}
                    <td className="py-3 px-4 whitespace-nowrap font-mono text-[#EAE6DE]">
                      <span className="px-2 py-0.5 rounded bg-[#0B131B] border border-[#226192]/40 text-[#EAE6DE]">
                        {trace.tool_name}
                      </span>
                    </td>

                    {/* Target Entity */}
                    <td className="py-3 px-4 font-medium max-w-[200px] truncate text-slate-200">
                      {trace.target_entity}
                    </td>

                    {/* Risk Meter */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-[#0B131B] h-2 rounded-full overflow-hidden border border-slate-700">
                          <div
                            className={`h-full ${getRiskMeterColor(trace.risk_score)} transition-all duration-300`}
                            style={{ width: `${Math.min(100, trace.risk_score * 100)}%` }}
                          />
                        </div>
                        <span className="font-mono text-xs font-bold w-10 text-right">
                          {trace.risk_score.toFixed(2)}
                        </span>
                      </div>
                    </td>

                    {/* Tier Badge */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getTierBadge(trace.verification_tier)}
                    </td>

                    {/* Verdict */}
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getVerdictBadge(trace.verdict)}
                    </td>

                    {/* Latency */}
                    <td className="py-3 px-4 text-right font-mono font-medium whitespace-nowrap text-slate-300">
                      {trace.latency_ms} ms
                    </td>

                    {/* Action Arrow */}
                    <td className="py-3 px-2 text-slate-500 hover:text-[#EF8557]">
                      <ArrowUpRight className="w-4 h-4" />
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
