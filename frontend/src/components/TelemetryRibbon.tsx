"use client";

import React from "react";
import { ShieldCheck, Zap, AlertTriangle, XOctagon, Clock, Activity, Layers } from "lucide-react";
import { AnalyticsStats } from "@/types";

interface TelemetryRibbonProps {
  stats: AnalyticsStats;
}

export const TelemetryRibbon: React.FC<TelemetryRibbonProps> = ({ stats }) => {
  const total = stats.total_actions_today || 1284;
  const executedPct = ((stats.verified_executed / total) * 100).toFixed(1);
  const escalatedPct = ((stats.escalated / total) * 100).toFixed(1);
  const blockedPct = ((stats.blocked / total) * 100).toFixed(1);

  return (
    <div className="w-full bg-[#0D1826]/90 border-b border-[#226192]/40 backdrop-blur-md px-6 py-4 shadow-xl">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        {/* Left: Shield Status Badge */}
        <div className="flex items-center space-x-3.5 bg-[#08111A] px-4 py-2.5 rounded-xl border border-[#226192]/50 shadow-inner">
          <div className="relative flex items-center justify-center w-3.5 h-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
          </div>
          <div className="flex flex-col">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-[#226192]" />
              <span className="font-display font-bold text-xs uppercase tracking-wider text-[#EAE6DE]">
                Agent Shield: <span className="text-emerald-400">Protected</span>
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-code mt-0.5">
              100% Pre-Execution • Fail-Closed Invariant
            </span>
          </div>
        </div>

        {/* Center: KPI Cards Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 flex-1 lg:max-w-3xl">
          {/* Total Intercepted */}
          <div className="bg-[#0F1C2A]/80 border border-[#226192]/35 rounded-xl p-2.5 px-3 flex flex-col justify-between hover:border-[#226192] transition-colors">
            <div className="flex items-center justify-between text-slate-400 text-[11px]">
              <span className="font-medium">Total Intercepted</span>
              <Activity className="w-3.5 h-3.5 text-[#226192]" />
            </div>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold font-code text-[#EAE6DE]">
                {total.toLocaleString()}
              </span>
              <span className="text-[10px] font-medium text-emerald-400 bg-emerald-950/60 px-1 rounded">
                +12% live
              </span>
            </div>
          </div>

          {/* Auto-Executed */}
          <div className="bg-[#0F1C2A]/80 border border-emerald-500/30 rounded-xl p-2.5 px-3 flex flex-col justify-between hover:border-emerald-500/60 transition-colors">
            <div className="flex items-center justify-between text-slate-400 text-[11px]">
              <span className="font-medium text-emerald-300">Verified & Acted</span>
              <Zap className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold font-code text-emerald-400">
                {stats.verified_executed.toLocaleString()}
              </span>
              <span className="text-[10px] font-medium text-emerald-400/90 font-code">
                ({executedPct}%)
              </span>
            </div>
          </div>

          {/* Escalated */}
          <div className="bg-[#0F1C2A]/80 border border-[#EF8557]/40 rounded-xl p-2.5 px-3 flex flex-col justify-between hover:border-[#EF8557] transition-colors">
            <div className="flex items-center justify-between text-slate-400 text-[11px]">
              <span className="font-medium text-[#EF8557]">Escalated</span>
              <AlertTriangle className="w-3.5 h-3.5 text-[#EF8557]" />
            </div>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold font-code text-[#EF8557]">
                {stats.escalated.toLocaleString()}
              </span>
              <span className="text-[10px] font-medium text-[#EF8557]/90 font-code">
                ({escalatedPct}%)
              </span>
            </div>
          </div>

          {/* Blocked High Risk */}
          <div className="bg-[#0F1C2A]/80 border border-rose-500/40 rounded-xl p-2.5 px-3 flex flex-col justify-between hover:border-rose-500 transition-colors">
            <div className="flex items-center justify-between text-slate-400 text-[11px]">
              <span className="font-medium text-rose-400">Blocked Unsafe</span>
              <XOctagon className="w-3.5 h-3.5 text-rose-400" />
            </div>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold font-code text-rose-400">
                {stats.blocked.toLocaleString()}
              </span>
              <span className="text-[10px] font-medium text-rose-400/90 font-code">
                ({blockedPct}%)
              </span>
            </div>
          </div>
        </div>

        {/* Right: Blended Latency & Tier Ratio */}
        <div className="bg-[#08111A] border border-[#226192]/40 rounded-xl p-2.5 px-3.5 flex items-center space-x-4">
          <div className="flex flex-col">
            <div className="flex items-center space-x-1.5 text-[11px] text-slate-400">
              <Clock className="w-3.5 h-3.5 text-[#226192]" />
              <span>Blended Latency</span>
            </div>
            <div className="flex items-baseline space-x-1.5 mt-0.5">
              <span className="text-base font-bold font-code text-[#EAE6DE]">
                {stats.average_latency_ms} <span className="text-xs font-normal text-slate-400">ms</span>
              </span>
              <span className="text-[10px] text-slate-400 font-code">
                (p95: {stats.p95_latency_ms}ms)
              </span>
            </div>
          </div>

          <div className="h-7 w-[1px] bg-[#226192]/40 hidden sm:block" />

          {/* Tier routing breakdown indicator */}
          <div className="hidden sm:flex flex-col text-[10px] font-code">
            <span className="text-slate-400 flex items-center space-x-1">
              <Layers className="w-3 h-3 text-[#226192]" />
              <span>Tier Distribution</span>
            </span>
            <div className="flex items-center space-x-1.5 mt-1">
              <span className="text-sky-300 font-semibold">Fast 69%</span>
              <span className="text-slate-600">•</span>
              <span className="text-purple-300 font-semibold">Strong 21%</span>
              <span className="text-slate-600">•</span>
              <span className="text-[#EF8557] font-semibold">Deep 10%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
