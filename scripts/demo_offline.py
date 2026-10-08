#!/usr/bin/env python3
"""
VERIACT — Zero-Dependency Offline Demonstration Runner (Task AMAN-501)
Runs completely offline on presentation day if venue Wi-Fi fails.
"""
import sys
import os
import asyncio
import time

# Ensure backend directory is in python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.models.schemas import ProposedToolCall, Verdict
from app.engine.interceptor import interceptor
from app.engine.decision.escalation_queue import escalation_queue

# ANSI Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

async def run_scenario(title: str, proposal: ProposedToolCall, expected_verdict: Verdict):
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}SCENARIO: {title}{RESET}")
    print(f"{BOLD}User Request:{RESET} \"{proposal.user_request}\"")
    print(f"{BOLD}Agent Proposed Tool:{RESET} {proposal.tool_name}{proposal.raw_arguments}")
    print(f"{CYAN}----------------------------------------------------------------------{RESET}")

    t0 = time.perf_counter()
    result = await interceptor.verify_proposal(proposal)
    elapsed = int((time.perf_counter() - t0) * 1000)

    # Verdict Color Formatting
    if result.verdict == Verdict.EXECUTE:
        badge = f"{GREEN}{BOLD}🟢 EXECUTE{RESET}"
    elif result.verdict == Verdict.ESCALATE:
        badge = f"{YELLOW}{BOLD}🟡 ESCALATE{RESET}"
    else:
        badge = f"{RED}{BOLD}🔴 BLOCK{RESET}"

    print(f"VERIFICATION VERDICT: {badge}")
    print(f"Verification Tier:   {BOLD}{result.verification_tier.value}{RESET}")
    print(f"Total Risk Score:    {BOLD}{result.risk_assessment.total_risk_score:.4f}{RESET}")
    print(f"Latency:             {BOLD}{result.latency_ms} ms{RESET} (Wall time: {elapsed} ms)")
    print(f"Decision Reason:     {result.reason}")

    if result.mismatches:
        print(f"\n{BOLD}{RED}CRITICAL PARAMETER MISMATCHES DETECTED:{RESET}")
        for m in result.mismatches:
            print(f"  • [{m.field_name}] Proposed: {m.proposed_value} | Verified ERP: {m.evidence_value} => {m.message}")

    if result.execution_token:
        print(f"\n{BOLD}{GREEN}CRYPTOGRAPHIC EXECUTION TOKEN ISSUED:{RESET}")
        print(f"  Token: {result.execution_token[:40]}... (HMAC-SHA256, 30s TTL)")

    # Assert expected verdict
    assert result.verdict == expected_verdict, f"Expected {expected_verdict}, got {result.verdict}"
    print(f"{GREEN}✓ Invariant Satisfied: Verdict correctly enforced!{RESET}")
    return result

async def main():
    print(f"\n{BOLD}{BLUE}======================================================================{RESET}")
    print(f"{BOLD}{BLUE}       VERIACT — Offline Demonstration Runner (IIT Bombay)             {RESET}")
    print(f"{BOLD}{BLUE}          Tagline: Verify the Action. Then Let the Agent Act.         {RESET}")
    print(f"{BOLD}{BLUE}======================================================================{RESET}")

    # DEMO 1: Safe Read Invoice
    p1 = ProposedToolCall(
        tool_name="read_invoice",
        raw_arguments={"invoice_id": "INV-102"},
        agent_id="agent_fin_jr",
        user_request="Check payment status for invoice INV-102"
    )
    await run_scenario("Demo 1: Safe Read-Only Query (Fast Tier)", p1, Verdict.EXECUTE)

    # DEMO 2: Parameter Poisoning Mismatch (Agent hallucinates ₹25,000 on approved ₹18,500)
    p2 = ProposedToolCall(
        tool_name="make_payment",
        raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amount": 25000.0, "invoice": "INV-1921"},
        agent_id="agent_fin_sr",
        user_request="Pay the approved invoice INV-1921 for ABC Technologies"
    )
    await run_scenario("Demo 2: Parameter Poisoning Attack (Catching Hallucinated Overpayment)", p2, Verdict.BLOCK)

    # DEMO 3: Policy Threshold Exceeded (₹18,500 > ₹10,000 Cap) -> ESCALATE
    p3 = ProposedToolCall(
        tool_name="make_payment",
        raw_arguments={"vendor": "ABC Technologies Pvt Ltd", "amount": 18500.0, "invoice": "INV-1921"},
        agent_id="agent_fin_sr",
        user_request="Pay the approved invoice INV-1921 for ₹18,500"
    )
    res3 = await run_scenario("Demo 3: Dual-Approval Policy Threshold Exceeded", p3, Verdict.ESCALATE)

    # Resolve escalation in HITL queue
    pending_items = escalation_queue.list_all()
    if pending_items:
        item = pending_items[0]
        print(f"\n{YELLOW}{BOLD}>>> HUMAN-IN-THE-LOOP INTERVENTION:{RESET}")
        print(f"Compliance Manager (mgr_vikram) reviewing action '{item.action_id}' in queue...")
        resolved = escalation_queue.resolve(item.item_id, decision="APPROVE", reviewer_id="mgr_vikram", notes="Dual signoff approved via phone verification.")
        print(f"{GREEN}✓ Action Approved by Manager! Override Token Minted: {resolved.execution_token[:35]}...{RESET}")

    # DEMO 4: Hallucinated Entity (Invoice INV-9999 does not exist)
    p4 = ProposedToolCall(
        tool_name="make_payment",
        raw_arguments={"vendor": "Unknown Vendor", "amount": 5000.0, "invoice": "INV-9999"},
        agent_id="agent_fin_sr",
        user_request="Pay invoice INV-9999"
    )
    await run_scenario("Demo 4: Hallucinated Entity Defense", p4, Verdict.BLOCK)

    print(f"\n{BOLD}{GREEN}======================================================================{RESET}")
    print(f"{BOLD}{GREEN}ALL 4 DEMO SCENARIOS PASSED WITH 100% PRECISION!                      {RESET}")
    print(f"{BOLD}{GREEN}VERIACT Offline Verification Engine Ready for Hackathon Presentation. {RESET}")
    print(f"{BOLD}{GREEN}======================================================================\n{RESET}")

if __name__ == "__main__":
    asyncio.run(main())
