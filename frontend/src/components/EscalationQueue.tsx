"use client";

import React, { useState, useEffect } from "react";
import { EscalationItem } from "@/types";
import { submitEscalationDecision } from "@/lib/api";
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  UserCheck,
  Shield,
  Key,
} from "lucide-react";

interface EscalationQueueProps {
  items: EscalationItem[];
  onRefresh: () => void;
}

export const EscalationQueue: React.FC<EscalationQueueProps> = ({ items, onRefresh }) => {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [resolvedToken, setResolvedToken] = useState<string | null>(null);

  const handleDecision = async (itemId: string, decision: "APPROVE" | "REJECT") => {
    try {
      setSubmittingId(itemId);
      const res = await submitEscalationDecision(itemId, decision);
      if (decision === "APPROVE" && res.execution_token) {
        setResolvedToken(res.execution_token);
      }
      onRefresh();
    } catch (err) {
      console.error("Decision submission error:", err);
    } finally {
      setSubmittingId(null);
    }
  };

  const pendingItems = items.filter((i) => i.status === "PENDING");

  return (
    <div className="w-full space-y-6">
      {/* Header Banner */}
      <div className="bg-[#121E2B] p-6 rounded-xl border border-[#EF8557]/40 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-[#EF8557]/15 rounded-lg border border-[#EF8557]/30 text-[#EF8557]">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#EAE6DE]">
              Human-in-the-Loop Review Queue (HITL)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Actions held by Dual-Control policy rules awaiting compliance manager authorization.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="text-xs px-3 py-1.5 rounded-lg bg-[#0B131B] border border-[#226192]/40 text-[#EAE6DE] font-mono font-bold">
            {pendingItems.length} PENDING REVIEW
          </span>
        </div>
      </div>

      {/* Minted Execution Token Notification */}
      {resolvedToken && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/50 flex items-start space-x-3 text-xs">
          <Key className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-emerald-400">
              Manager Authorization Granted — Signed HMAC Execution Token Issued:
            </span>
            <p className="font-mono text-emerald-200 text-[11px] break-all bg-emerald-900/40 p-2 rounded border border-emerald-500/30">
              {resolvedToken}
            </p>
            <p className="text-[10px] text-emerald-400/80">
              Valid for 30 seconds. Dispatched to real tool adapter.
            </p>
          </div>
        </div>
      )}

      {/* Pending Items List */}
      <div className="grid grid-cols-1 gap-4">
        {pendingItems.length === 0 ? (
          <div className="p-12 text-center bg-[#121E2B] rounded-xl border border-[#226192]/30 text-slate-400 space-y-2">
            <UserCheck className="w-8 h-8 text-emerald-400 mx-auto" />
            <p className="font-medium text-sm text-[#EAE6DE]">
              All escalated actions have been reviewed!
            </p>
            <p className="text-xs text-slate-500">
              New high-value or threshold exceptions will automatically queue here.
            </p>
          </div>
        ) : (
          pendingItems.map((item) => (
            <div
              key={item.item_id}
              className="bg-[#121E2B] rounded-xl border border-[#226192]/30 p-5 space-y-4 shadow-lg hover:border-[#EF8557]/50 transition-colors"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#226192]/20 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-[#EF8557] bg-[#EF8557]/10 px-2 py-0.5 rounded border border-[#EF8557]/30">
                    {item.item_id}
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    Agent: <strong className="text-[#EAE6DE]">{item.agent_id}</strong>
                  </span>
                  <span className="font-mono text-xs text-slate-400">
                    Tool: <strong className="text-[#EAE6DE]">{item.tool_name}</strong>
                  </span>
                </div>

                <div className="flex items-center space-x-2">
                  <span suppressHydrationWarning className="text-xs font-mono text-slate-400 flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1" />
                    {mounted ? new Date(item.created_at).toLocaleTimeString() : "--:--:--"}
                  </span>
                  <span className="px-2 py-0.5 rounded text-xs font-bold font-mono bg-[#EF8557]/20 text-[#EF8557] border border-[#EF8557]/40">
                    Risk: {item.risk_score.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Action Details & Reason */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="space-y-2 bg-[#0B131B] p-3 rounded-lg border border-slate-800">
                  <span className="font-bold text-[#226192] uppercase tracking-wider text-[10px] block">
                    Proposed Parameters
                  </span>
                  <pre className="text-[11px] font-mono text-[#EAE6DE] overflow-x-auto">
                    {JSON.stringify(item.proposed_params, null, 2)}
                  </pre>
                </div>

                <div className="space-y-2 bg-[#0B131B] p-3 rounded-lg border border-slate-800">
                  <span className="font-bold text-[#EF8557] uppercase tracking-wider text-[10px] block">
                    Escalation Trigger Reason
                  </span>
                  <p className="text-slate-300 italic text-xs leading-relaxed">
                    {item.reason}
                  </p>
                  {item.retrieved_evidence && (
                    <div className="mt-2 pt-2 border-t border-slate-800">
                      <span className="text-[10px] text-slate-500 font-mono">
                        Verified ERP Status: {item.retrieved_evidence.status || "APPROVED"}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Controls */}
              <div className="flex items-center justify-end space-x-3 pt-2">
                <button
                  disabled={submittingId === item.item_id}
                  onClick={() => handleDecision(item.item_id, "REJECT")}
                  className="px-4 py-2 rounded-lg bg-rose-950/60 hover:bg-rose-900 border border-rose-500/50 text-rose-300 font-medium text-xs flex items-center transition-colors disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4 mr-1.5" /> Reject Action
                </button>

                <button
                  disabled={submittingId === item.item_id}
                  onClick={() => handleDecision(item.item_id, "APPROVE")}
                  className="px-5 py-2 rounded-lg bg-[#226192] hover:bg-[#2b79b5] text-[#EAE6DE] font-bold text-xs flex items-center transition-colors shadow-md disabled:opacity-50 border border-[#226192]"
                >
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-400" />
                  Approve & Issue HMAC Token
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
