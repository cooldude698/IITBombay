"""Role-Based Access Control (RBAC) Engine for AI Agent Capabilities.

Provides sub-5ms deterministic authorization checks validating agent role
permissions, allowed tool actions, and monetary caps before any execution.
"""

from typing import Any, Dict, List, Optional, Set, Tuple


class RBACPolicy:
    """Standard permission definitions for enterprise agent roles."""

    ROLE_PERMISSIONS: Dict[str, Set[str]] = {
        "JUNIOR_ASSISTANT": {
            "read_invoice",
            "read_vendor",
            "search_knowledge_base",
            "read_status",
            "draft_report",
            "draft_payment",
            "check_balance",
        },
        "FINANCE_OPERATOR": {
            "read_invoice",
            "read_vendor",
            "search_knowledge_base",
            "read_status",
            "draft_report",
            "draft_payment",
            "check_balance",
            "make_payment",
            "send_invoice",
            "update_invoice_status",
        },
        "FINANCE_MANAGER": {
            "read_invoice",
            "read_vendor",
            "search_knowledge_base",
            "read_status",
            "draft_report",
            "draft_payment",
            "check_balance",
            "make_payment",
            "send_invoice",
            "update_invoice_status",
            "approve_escalation",
            "reject_escalation",
            "modify_vendor",
            "export_financial_report",
        },
        "OPS_BOT": {
            "read_status",
            "send_notification",
            "read_log",
            "search_knowledge_base",
        },
    }

    ROLE_TXN_LIMITS: Dict[str, float] = {
        "JUNIOR_ASSISTANT": 5000.0,
        "FINANCE_OPERATOR": 25000.0,
        "FINANCE_MANAGER": 250000.0,
        "OPS_BOT": 0.0,
    }

    DESTRUCTIVE_TOOLS: Set[str] = {
        "drop_table",
        "drop_database",
        "truncate_table",
        "delete_all_records",
        "delete_database_table",
        "raw_sql_exec",
    }


class RBACValidator:
    """Evaluates agent role authorization against proposed tool actions."""

    def __init__(self, rbac_policy: Optional[RBACPolicy] = None):
        self.policy = rbac_policy or RBACPolicy()

    def check_permission(
        self,
        agent_role: str,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Determines if the agent's role allows invoking the target tool.

        Returns:
            (allowed: bool, violation_reason: Optional[str])
        """
        role_upper = (agent_role or "JUNIOR_ASSISTANT").upper()
        tool_clean = tool_name.strip().lower()

        # 1. Block destructive system operations for all autonomous agents
        if tool_clean in self.policy.DESTRUCTIVE_TOOLS:
            return False, f"ERR_RBAC_SECURITY: Tool '{tool_name}' is a destructive system action and is unconditionally blocked."

        # 2. Check Allowed Tool Set for Role
        allowed_tools = self.policy.ROLE_PERMISSIONS.get(role_upper)
        if allowed_tools is None:
            return False, f"ERR_RBAC_UNKNOWN_ROLE: Unrecognized agent role '{agent_role}'."

        if tool_clean not in allowed_tools:
            return False, (
                f"ERR_RBAC_UNAUTHORIZED_TOOL: Role '{role_upper}' lacks permission "
                f"to execute tool '{tool_name}'."
            )

        # 3. Monetary Single Transaction Cap Check
        params = parameters or {}
        proposed_amount = params.get("amount")
        if proposed_amount is not None:
            try:
                amt = float(proposed_amount)
                # Check against agent registry profile limit if available, otherwise role default
                role_limit = self.policy.ROLE_TXN_LIMITS.get(role_upper, 0.0)
                profile_limit = (
                    float(agent_profile["single_txn_limit"])
                    if agent_profile and "single_txn_limit" in agent_profile
                    else role_limit
                )
                effective_limit = min(role_limit, profile_limit)

                if amt > effective_limit:
                    return False, (
                        f"ERR_RBAC_LIMIT_EXCEEDED: Transaction amount INR {amt:,.2f} exceeds "
                        f"role single transaction limit INR {effective_limit:,.2f}."
                    )
            except (ValueError, TypeError):
                return False, f"ERR_RBAC_INVALID_AMOUNT: Invalid numeric amount parameter '{proposed_amount}'."

        return True, None


default_rbac = RBACValidator()
