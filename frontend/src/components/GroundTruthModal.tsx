"use client";

import React, { useEffect, useState } from "react";
import { fetchGroundTruthInvoices, fetchGroundTruthVendors } from "@/lib/api";
import { X, Database, Building, FileCheck } from "lucide-react";

interface GroundTruthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GroundTruthModal: React.FC<GroundTruthModalProps> = ({ isOpen, onClose }) => {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [vendors, setVendors] = useState<any[]>([]);
  const [tab, setTab] = useState<"invoices" | "vendors">("invoices");

  useEffect(() => {
    if (isOpen) {
      fetchGroundTruthInvoices().then(setInvoices);
      fetchGroundTruthVendors().then(setVendors);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-[#121E2B] border border-[#226192]/50 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-[#226192]/30 flex items-center justify-between bg-[#0F1A24]">
          <div className="flex items-center space-x-3">
            <Database className="w-5 h-5 text-[#EF8557]" />
            <div>
              <h3 className="font-bold text-sm text-[#EAE6DE]">
                Enterprise Ground Truth Explorer (veriact_enterprise.db)
              </h3>
              <p className="text-[11px] text-slate-400">
                Authoritative SQL Master Invoices &amp; Vendor Directory
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-[#EAE6DE]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-[#226192]/20 px-6 bg-[#0B131B] text-xs font-mono">
          <button
            onClick={() => setTab("invoices")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-colors ${
              tab === "invoices"
                ? "border-[#EF8557] text-[#EF8557]"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <FileCheck className="w-4 h-4" />
            <span>Verified Invoices ({invoices.length || 12})</span>
          </button>

          <button
            onClick={() => setTab("vendors")}
            className={`py-3 px-4 font-bold border-b-2 flex items-center space-x-2 transition-colors ${
              tab === "vendors"
                ? "border-[#226192] text-[#226192]"
                : "border-transparent text-slate-400 hover:text-[#EAE6DE]"
            }`}
          >
            <Building className="w-4 h-4" />
            <span>Master Vendors ({vendors.length || 11})</span>
          </button>
        </div>

        {/* Content Table */}
        <div className="p-6 overflow-y-auto flex-1 text-xs">
          {tab === "invoices" ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono">
                <thead>
                  <tr className="bg-[#0B131B] text-slate-400 border-b border-slate-800 uppercase text-[11px]">
                    <th className="py-2.5 px-3">Invoice ID</th>
                    <th className="py-2.5 px-3">Vendor</th>
                    <th className="py-2.5 px-3 text-right">Approved Amount</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">PO Reference</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#226192]/15 text-[#EAE6DE]">
                  {invoices.map((inv, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="py-2.5 px-3 font-bold text-[#EF8557]">
                        {inv.invoice_id || inv.id}
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {inv.vendor_name || inv.vendor_id}
                      </td>
                      <td suppressHydrationWarning className="py-2.5 px-3 text-right font-bold text-emerald-400">
                        INR {(inv.amount || inv.approved_amount || 0).toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            inv.status === "APPROVED"
                              ? "bg-emerald-950 text-emerald-400"
                              : inv.status === "PAID"
                              ? "bg-blue-950 text-blue-400"
                              : "bg-amber-950 text-amber-400"
                          }`}
                        >
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">{inv.po_number || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono">
                <thead>
                  <tr className="bg-[#0B131B] text-slate-400 border-b border-slate-800 uppercase text-[11px]">
                    <th className="py-2.5 px-3">Vendor ID</th>
                    <th className="py-2.5 px-3">Name</th>
                    <th className="py-2.5 px-3">Bank Account</th>
                    <th className="py-2.5 px-3">Risk Rating</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#226192]/15 text-[#EAE6DE]">
                  {vendors.map((vnd, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40">
                      <td className="py-2.5 px-3 font-bold text-[#226192]">
                        {vnd.vendor_id || vnd.id}
                      </td>
                      <td className="py-2.5 px-3 text-slate-200">{vnd.name}</td>
                      <td className="py-2.5 px-3 text-slate-400">{vnd.bank_account || "—"}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-slate-300">{vnd.risk_rating || "LOW"}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            vnd.status === "ACTIVE"
                              ? "bg-emerald-950 text-emerald-400"
                              : "bg-rose-950 text-rose-400"
                          }`}
                        >
                          {vnd.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
