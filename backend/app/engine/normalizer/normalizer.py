"""
VERIACT — Action Normalizer (Task AMAN-201)
Translates heterogeneous agent tool calls into standard NormalizedAction payloads.
"""
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from app.models.schemas import ProposedToolCall, NormalizedAction, ActionType

class ActionNormalizer:
    """Normalizes arbitrary LLM tool calls into standard verifiable schemas."""

    FINANCIAL_TOOLS = {
        "make_payment", "pay_invoice", "transfer_funds", "send_wire", 
        "refund_order", "process_payout", "disburse_loan"
    }
    
    DESTRUCTIVE_TOOLS = {
        "delete_record", "drop_table", "truncate_table", "purge_data",
        "remove_vendor", "delete_invoice"
    }

    COMMUNICATION_TOOLS = {
        "send_email", "notify_vendor", "dispatch_webhook", "send_slack_message"
    }

    READ_TOOLS = {
        "read_invoice", "get_vendor", "query_database", "check_status",
        "search_records", "fetch_po"
    }

    def infer_action_type(self, tool_name: str) -> ActionType:
        name = tool_name.lower()
        if name in self.FINANCIAL_TOOLS or "pay" in name or "transfer" in name:
            return ActionType.FINANCIAL
        if name in self.DESTRUCTIVE_TOOLS or "delete" in name or "drop" in name:
            return ActionType.DATA_MUTATION
        if name in self.COMMUNICATION_TOOLS or "email" in name or "notify" in name:
            return ActionType.EXTERNAL_COMMUNICATION
        if name in self.READ_TOOLS or "read" in name or "get" in name or "query" in name:
            return ActionType.READ_ONLY
        return ActionType.DATA_MUTATION

    def extract_target_entity(self, tool_name: str, args: Dict[str, Any]) -> str:
        for key in ["vendor", "vendor_name", "recipient", "payee", "to", "target", "table", "entity"]:
            if key in args and args[key]:
                return str(args[key])
        if "invoice" in args:
            return f"Invoice:{args['invoice']}"
        if "invoice_id" in args:
            return f"Invoice:{args['invoice_id']}"
        return tool_name

    def normalize(
        self,
        proposal: ProposedToolCall,
        agent_role: str = "FINANCE_OPERATOR"
    ) -> NormalizedAction:
        args = dict(proposal.raw_arguments)
        action_type = self.infer_action_type(proposal.tool_name)
        target = self.extract_target_entity(proposal.tool_name, args)

        # Canonicalize amount if present
        for amt_key in ["amount", "amt", "value", "payment_amount"]:
            if amt_key in args:
                try:
                    val = float(args[amt_key])
                    args["amount"] = val
                except (ValueError, TypeError):
                    pass

        # Canonicalize invoice ID
        for inv_key in ["invoice", "invoice_id", "inv_num", "inv_id"]:
            if inv_key in args:
                args["invoice"] = str(args[inv_key]).strip().upper()

        return NormalizedAction(
            action_id=f"act_{uuid4().hex[:12]}",
            timestamp=datetime.utcnow(),
            agent_id=proposal.agent_id,
            agent_role=agent_role,
            action_type=action_type,
            target_entity=target,
            tool_name=proposal.tool_name,
            parameters=args,
            user_context=proposal.user_request,
            session_id=proposal.session_id
        )

# Global singleton instance
normalizer = ActionNormalizer()
