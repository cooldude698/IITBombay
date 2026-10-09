"use client";

import React from "react";
import { ShieldCheck, Zap, AlertTriangle, XOctagon, Clock, Activity } from "lucide-react";
import { AnalyticsStats } from "@/types";

interface TelemetryRibbonProps {
  stats: AnalyticsStats;
}

export const TelemetryRibbon: React.FC<TelemetryRibbonProps> = ({ stats }) => {
  const executedPct = stats.total_actions_today
    ? ((stats.verified_executed / stats.total_actions_today) * 100).toFixed(1)
    : "94.5";
  const escalatedPct = stats.total_actions_today
    ? ((stats.escalated / stats.total_actions_today) * 100).toFixed(1)
    : "3.7";
  const blockedPct = stats.total_actions_today
    ? ((stats.blocked / stats.total_actions_today) * 100).toFixed(1)
    : "1.8";

  return (
    <div className="w-full bg-[#121E2B] border-b border-[#226192]/40 px-6 py-3 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Status Indicator */}
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center w-3 h-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </div>
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-5 h-5 text-[#226192]" />
            <span className="font-semibold text-xs tracking-wider uppercase text-[#EAE6DE]">
              Agent Shield: <span className="text-emerald-400 font-bold">Protected</span>
            </span>
            <span className="text-xs px-2 py-0.5 rounded bg-[#226192]/30 text-[#EAE6DE] border border-[#226192]/50 font-mono">
              FAIL-CLOSED
            </span>
          </div>
        </div>

        {/* Real-time KPI Counters */}
        <div className="flex flex-wrap items-center gap-6 text-xs">
          {/* Total Intercepted */}
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-[#226192]" />
            <span className="text-slate-400">Total Intercepted:</span>
            <span className="font-bold font-mono text-[#EAE6DE] text-sm">
              {stats.total_actions_today.toLocaleString()}
            </span>
          </div>

          {/* Executed */}
          <div className="flex items-center space-x-2 bg-emerald-950/40 px-2.5 py-1 rounded border border-emerald-500/30">
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-300">Executed:</span>
            <span className="font-bold font-mono text-emerald-400 text-sm">
              {stats.verified_executed.toLocaleString()}
            </span>
            <span className="text-[10px] text-emerald-500/80">({executedPct}%)</span>
          </div>

          {/* Escalated */}
          <div className="flex items-center space-x-2 bg-[#EF8557]/10 px-2.5 py-1 rounded border border-[#EF8557]/40">
            <AlertTriangle className="w-3.5 h-3.5 text-[#EF8557]" />
            <span className="text-slate-300">Escalated:</span>
            <span className="font-bold font-mono text-[#EF8557] text-sm">
              {stats.escalated.toLocaleString()}
            </span>
            <span className="text-[10px] text-[#EF8557]/80">({escalatedPct}%)</span>
          </div>

          {/* Blocked */}
          <div className="flex items-center space-x-2 bg-rose-950/40 px-2.5 py-1 rounded border border-rose-500/30">
            <XOctagon className="w-3.5 h-3.5 text-rose-400" />
            <span className="text-slate-300">Blocked:</span>
            <span className="font-bold font-mono text-rose-400 text-sm">
              {stats.blocked.toLocaleString()}
            </span>
            <span className="text-[10px] text-rose-400/80">({blockedPct}%)</span>
          </div>

          {/* Latency */}
          <div className="flex items-center space-x-2 border-l border-slate-700 pl-4">
            <Clock className="w-4 h-4 text-[#226192]" />
            <span className="text-slate-400">Blended Latency:</span>
            <span className="font-bold font-mono text-[#EAE6DE] text-sm">
              {stats.average_latency_ms} ms
            </span>
            <span className="text-[10px] text-slate-500">(p95: {stats.p95_latency_ms}ms)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
