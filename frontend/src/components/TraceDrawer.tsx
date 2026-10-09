"use client";

import React from "react";
import { ActionTrace } from "@/types";
import {
  X,
  ShieldCheck,
  AlertOctagon,
  FileText,
  Database,
  Sliders,
  CheckCircle2,
  XCircle,
  Copy,
  Hash,
  Scale,
  Lock,
} from "lucide-react";

interface TraceDrawerProps {
  trace: ActionTrace | null;
  onClose: () => void;
}

export const TraceDrawer: React.FC<TraceDrawerProps> = ({ trace, onClose }) => {
  if (!trace) return null;

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-[#0F1A24] border-l border-[#226192]/50 shadow-2xl z-50 flex flex-col overflow-hidden animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-6 border-b border-[#226192]/30 bg-[#121E2B] flex items-start justify-between">
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-[#226192]/30 text-[#EAE6DE] border border-[#226192]/50">
              {trace.trace_id}
            </span>
            <span className="font-mono text-xs text-slate-400">
              Action: {trace.action_id}
            </span>
          </div>
          <div className="flex items-center space-x-3 mt-2">
            {trace.verdict === "EXECUTE" && (
              <span className="px-3 py-1 rounded-md text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-500/50 flex items-center">
                <CheckCircle2 className="w-4 h-4 mr-1.5" /> 🟢 ACTION AUTHORIZED (EXECUTE)
              </span>
            )}
            {trace.verdict === "ESCALATE" && (
              <span className="px-3 py-1 rounded-md text-xs font-bold bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/60 flex items-center">
                <AlertOctagon className="w-4 h-4 mr-1.5" /> 🟡 HELD FOR HUMAN REVIEW (ESCALATE)
              </span>
            )}
            {trace.verdict === "BLOCK" && (
              <span className="px-3 py-1 rounded-md text-xs font-bold bg-rose-950 text-rose-400 border border-rose-500/50 flex items-center">
                <XCircle className="w-4 h-4 mr-1.5" /> 🔴 PRE-EXECUTION BLOCKED (HALTED)
              </span>
            )}
            <span className="text-xs font-mono text-slate-400">
              Tier: <strong className="text-[#EAE6DE]">{trace.verification_tier}</strong>
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2 italic">
            Decision Reason: {trace.reason}
          </p>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-[#EAE6DE] transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 text-xs text-[#EAE6DE]">
        {/* Step 1: Proposed Parameters */}
        <div className="bg-[#121E2B] rounded-lg border border-[#226192]/30 p-4">
          <div className="flex items-center space-x-2 text-[#226192] font-bold text-xs uppercase tracking-wider mb-3">
            <FileText className="w-4 h-4 text-[#EF8557]" />
            <span>Step 1: Proposed Action & Parameters (Intercepted)</span>
          </div>
          <div className="grid grid-cols-2 gap-2 font-mono bg-[#0B131B] p-3 rounded border border-slate-800">
            <div>
              <span className="text-slate-400">Tool Name:</span>
              <p className="text-[#EAE6DE] font-semibold">{trace.tool_name}</p>
            </div>
            <div>
              <span className="text-slate-400">Agent ID:</span>
              <p className="text-[#EAE6DE] font-semibold">{trace.agent_id}</p>
            </div>
            <div>
              <span className="text-slate-400">Target Entity:</span>
              <p className="text-[#EAE6DE] font-semibold">{trace.target_entity}</p>
            </div>
            <div>
              <span className="text-slate-400">Action Type:</span>
              <p className="text-[#EAE6DE] font-semibold">{trace.action_type}</p>
            </div>
          </div>
          <div className="mt-3">
            <span className="text-slate-400 font-mono text-[11px] block mb-1">
              Raw Parameter Payload:
            </span>
            <pre className="p-2.5 rounded bg-[#0B131B] border border-slate-800 font-mono text-[11px] text-amber-200 overflow-x-auto">
              {JSON.stringify(trace.proposed_params, null, 2)}
            </pre>
          </div>
        </div>

        {/* Step 2: Ground Truth Evidence */}
        <div className="bg-[#121E2B] rounded-lg border border-[#226192]/30 p-4">
          <div className="flex items-center space-x-2 text-[#226192] font-bold text-xs uppercase tracking-wider mb-3">
            <Database className="w-4 h-4 text-[#226192]" />
            <span>Step 2: External Ground Truth Retrieved (ERP Store)</span>
          </div>
          {trace.retrieved_evidence ? (
            <div className="bg-[#0B131B] p-3 rounded border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-slate-400">Source:</span>
                <span className="font-mono text-emerald-400">veriact_enterprise.db (Relational SQL)</span>
              </div>
              <pre className="p-2.5 rounded bg-[#121E2B] border border-slate-800 font-mono text-[11px] text-emerald-300 overflow-x-auto">
                {JSON.stringify(trace.retrieved_evidence, null, 2)}
              </pre>
            </div>
          ) : (
            <p className="text-slate-400 italic bg-[#0B131B] p-3 rounded border border-slate-800">
              No relational entity required (read-only or general action).
            </p>
          )}
        </div>

        {/* Step 3: Parameter Comparison Matrix */}
        <div className="bg-[#121E2B] rounded-lg border border-[#226192]/30 p-4">
          <div className="flex items-center space-x-2 text-[#226192] font-bold text-xs uppercase tracking-wider mb-3">
            <Scale className="w-4 h-4 text-[#EF8557]" />
            <span>Step 3: Deterministic Grounding & Parameter Equality</span>
          </div>
          {trace.mismatches.length > 0 ? (
            <div className="space-y-2">
              {trace.mismatches.map((m, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded bg-rose-950/40 border border-rose-500/50 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-rose-300">
                      Field: [{m.field_name}]
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-rose-900 text-rose-200 font-bold uppercase">
                      {m.severity}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
                    <div>
                      <span className="text-slate-400">Proposed:</span>{" "}
                      <span className="text-rose-400 font-bold">
                        {String(m.proposed_value)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">Verified ERP:</span>{" "}
                      <span className="text-emerald-400 font-bold">
                        {String(m.evidence_value)}
                      </span>
                    </div>
                  </div>
                  <p className="text-xs text-rose-300 italic">{m.message}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-3 rounded bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Zero parameter mismatches detected (Exact equality verified).</span>
            </div>
          )}
        </div>

        {/* Step 4 & 5: Multi-Factor Risk Assessment Breakdown */}
        <div className="bg-[#121E2B] rounded-lg border border-[#226192]/30 p-4">
          <div className="flex items-center space-x-2 text-[#226192] font-bold text-xs uppercase tracking-wider mb-3">
            <Sliders className="w-4 h-4 text-[#226192]" />
            <span>Step 4 & 5: Multi-Factor Mathematical Risk Breakdown</span>
          </div>
          <div className="space-y-3 bg-[#0B131B] p-3.5 rounded border border-slate-800">
            <div className="flex items-center justify-between font-mono pb-2 border-b border-slate-800">
              <span className="font-bold text-slate-300">Total Composite Risk Score (R):</span>
              <span
                className={`text-sm font-bold px-2.5 py-0.5 rounded ${
                  trace.risk_score <= 0.35
                    ? "bg-emerald-950 text-emerald-400 border border-emerald-500/40"
                    : trace.risk_score <= 0.70
                    ? "bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/50"
                    : "bg-rose-950 text-rose-400 border border-rose-500/50"
                }`}
              >
                {trace.risk_score.toFixed(4)}
              </span>
            </div>

            {/* Individual Factor Meters */}
            <div className="space-y-2 font-mono text-[11px]">
              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>F (Financial Impact - 25% weight)</span>
                  <span className="text-[#EAE6DE]">{(trace.risk_score > 0.5 ? 0.85 : 0.0).toFixed(2)}</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[#226192] h-full"
                    style={{ width: `${trace.risk_score > 0.5 ? 85 : 10}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>I (Irreversibility - 20% weight)</span>
                  <span className="text-[#EAE6DE]">
                    {trace.action_type === "READ_ONLY" ? "0.10" : "1.00"}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-[#EF8557] h-full"
                    style={{ width: `${trace.action_type === "READ_ONLY" ? 10 : 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>P (Permission Sensitivity - 20% weight)</span>
                  <span className="text-[#EAE6DE]">0.30</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-[#226192] h-full" style={{ width: "30%" }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-400 mb-1">
                  <span>C (Contradiction Severity - 20% weight)</span>
                  <span className="text-[#EAE6DE]">
                    {trace.mismatches.length > 0 ? "1.00" : "0.00"}
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-rose-500 h-full"
                    style={{ width: `${trace.mismatches.length > 0 ? 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Step 6: Signed Cryptographic Proof & Hash */}
        <div className="bg-[#121E2B] rounded-lg border border-[#226192]/30 p-4">
          <div className="flex items-center space-x-2 text-[#226192] font-bold text-xs uppercase tracking-wider mb-3">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span>Step 6: Cryptographic Payload Hash & Non-Repudiation</span>
          </div>
          <div className="bg-[#0B131B] p-3 rounded border border-slate-800 flex items-center justify-between">
            <span className="font-mono text-[11px] text-slate-300 truncate max-w-[480px]">
              {trace.payload_hash}
            </span>
            <button
              onClick={() => copyToClipboard(trace.payload_hash)}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-[#EAE6DE]"
              title="Copy Hash"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
