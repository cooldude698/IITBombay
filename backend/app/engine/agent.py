"""
VERIACT — LangGraph Agent Loop & Mock Real Execution Tools (Task AMAN-103)
Simulates an autonomous agent generating tool proposals that pass through VERIACT.
"""
from typing import Dict, Any
from app.models.schemas import ProposedToolCall
from app.engine.interceptor import interceptor

# Real Mock Tools (These represent live banking APIs or production databases)
def real_make_payment_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates real banking payment gateway execution."""
    return {
        "transaction_id": "TXN_LIVE_994821",
        "vendor": params.get("vendor"),
        "amount_transferred": params.get("amount"),
        "invoice_settled": params.get("invoice"),
        "status": "SETTLED"
    }

def real_read_invoice_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates production invoice reader."""
    return {
        "invoice_id": params.get("invoice_id") or params.get("invoice"),
        "status": "FETCHED_FROM_ERP"
    }

def real_delete_record_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates production database deletion."""
    return {
        "table": params.get("table"),
        "record_id": params.get("record_id"),
        "status": "DELETED"
    }

TOOL_REGISTRY = {
    "make_payment": real_make_payment_tool,
    "read_invoice": real_read_invoice_tool,
    "delete_record": real_delete_record_tool
}

class AutonomousFinanceAgent:
    """Simulates an autonomous agent decomposing user goals into tool calls."""

    async def execute_user_request(
        self,
        user_request: str,
        simulated_hallucination: bool = False,
        agent_id: str = "agent_fin_sr"
    ) -> Dict[str, Any]:
        req_lower = user_request.lower()

        # Agent reasoning logic
        if "pay" in req_lower or "transfer" in req_lower:
            # Detect invoice reference
            inv_id = "INV-1921" if "1921" in req_lower else ("INV-102" if "102" in req_lower else "INV-404")
            vendor = "ABC Technologies Pvt Ltd" if "abc" in req_lower else "Apex Office Supplies"
            
            # If simulated_hallucination is True, hallucinate ₹25,000 instead of ₹18,500
            if simulated_hallucination:
                amount = 25000.0  # HALLUCINATION
            elif "102" in req_lower:
                amount = 3400.0
            else:
                amount = 18500.0  # Correct amount for INV-1921

            tool_name = "make_payment"
            raw_args = {"vendor": vendor, "amount": amount, "invoice": inv_id}

        elif "delete" in req_lower or "drop" in req_lower:
            tool_name = "delete_record"
            raw_args = {"table": "financial_records", "record_id": "all"}

        else:  # Read / check status
            tool_name = "read_invoice"
            inv_id = "INV-102" if "102" in req_lower else "INV-1921"
            raw_args = {"invoice_id": inv_id}

        proposal = ProposedToolCall(
            tool_name=tool_name,
            raw_arguments=raw_args,
            agent_id=agent_id,
            user_request=user_request
        )

        real_handler = TOOL_REGISTRY.get(tool_name, lambda p: {"status": "UNKNOWN_TOOL"})

        # Route through VERIACT Pre-Execution Interceptor!
        execution_report = await interceptor.execute_tool_with_interception(proposal, real_handler)
        return {
            "user_request": user_request,
            "proposed_tool": tool_name,
            "proposed_args": raw_args,
            "report": execution_report
        }

finance_agent = AutonomousFinanceAgent()
