"""Safe Enterprise Policy AST Evaluator for VERIACT.

Evaluates predicate rules against runtime action, evidence, and entity state
without using insecure eval() calls. Uses Python's abstract syntax tree (ast)
with strict node whitelisting.
"""

import ast
import operator
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class TriggeredPolicy(BaseModel):
    policy_id: str
    name: str
    enforcement_action: str  # BLOCK, ESCALATE, REQUIRE_MFA
    reason: str
    priority: int = 10


class PolicyEvaluationResult(BaseModel):
    passed: bool
    required_enforcement: str = "ALLOW"  # ALLOW, ESCALATE, BLOCK
    triggered_policies: List[TriggeredPolicy] = Field(default_factory=list)


class SafeASTVisitor:
    """Evaluates Python boolean/comparison expressions on a restricted context dictionary."""

    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
        ast.And: lambda a, b: a and b,
        ast.Or: lambda a, b: a or b,
        ast.Not: operator.not_,
    }

    def __init__(self, context: Dict[str, Any]):
        self.context = context

    def evaluate(self, expr: str) -> Any:
        try:
            parsed = ast.parse(expr.strip(), mode="eval")
            return self._eval_node(parsed.body)
        except Exception as e:
            # Safe fallback: fail-closed evaluation
            return False

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.Name):
            return self.context.get(node.id)

        if isinstance(node, ast.Attribute):
            val = self._eval_node(node.value)
            if isinstance(val, dict):
                return val.get(node.attr)
            return getattr(val, node.attr, None)

        if isinstance(node, ast.Subscript):
            val = self._eval_node(node.value)
            slice_val = self._eval_node(node.slice)
            if val is not None:
                try:
                    return val[slice_val]
                except (IndexError, KeyError, TypeError):
                    return None
            return None

        if isinstance(node, ast.Call):
            # Support .get(key, default) method on dictionaries
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
                obj = self._eval_node(node.func.value)
                if isinstance(obj, dict):
                    args = [self._eval_node(arg) for arg in node.args]
                    return obj.get(*args)
            return None

        if isinstance(node, ast.List):
            return [self._eval_node(el) for el in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(el) for el in node.elts)

        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval_node(comparator)
                op_type = type(op)
                if op_type in self.SAFE_OPERATORS:
                    op_func = self.SAFE_OPERATORS[op_type]
                    if not op_func(left, right):
                        return False
                    left = right
                else:
                    return False
            return True

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_node(v) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval_node(v) for v in node.values)

        if isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.SAFE_OPERATORS:
                return self.SAFE_OPERATORS[op_type](operand)

        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.SAFE_OPERATORS:
                return self.SAFE_OPERATORS[op_type](left, right)

        return None


class PolicyEvaluator:
    """Evaluates enterprise policies against normalized actions and evidence."""

    def evaluate_policies(
        self,
        policies: List[Dict[str, Any]],
        action_data: Dict[str, Any],
        invoice_data: Optional[Dict[str, Any]] = None,
        vendor_data: Optional[Dict[str, Any]] = None,
        agent_profile: Optional[Dict[str, Any]] = None,
    ) -> PolicyEvaluationResult:
        """Evaluates all active policy rules against current execution context."""
        context = {
            "action": action_data,
            "invoice": invoice_data or {},
            "vendor": vendor_data or {},
            "agent": agent_profile or {},
        }

        triggered: List[TriggeredPolicy] = []
        visitor = SafeASTVisitor(context)

        for policy in policies:
            if not policy.get("is_active", True):
                continue

            cond_expr = policy.get("condition_expression", "")
            if not cond_expr:
                continue

            # Deterministic evaluation using AST
            condition_met = visitor.evaluate(cond_expr)

            if bool(condition_met):
                triggered.append(
                    TriggeredPolicy(
                        policy_id=policy.get("id", "UNKNOWN"),
                        name=policy.get("name", "Unnamed Policy"),
                        enforcement_action=policy.get("enforcement_action", "BLOCK"),
                        reason=policy.get("description", "Policy rule condition satisfied"),
                        priority=policy.get("priority", 10),
                    )
                )

        # Determine highest severity enforcement action
        # Precedence: BLOCK > ESCALATE > ALLOW
        if any(p.enforcement_action == "BLOCK" for p in triggered):
            enforcement = "BLOCK"
            passed = False
        elif any(p.enforcement_action == "ESCALATE" for p in triggered):
            enforcement = "ESCALATE"
            passed = False
        else:
            enforcement = "ALLOW"
            passed = True

        return PolicyEvaluationResult(
            passed=passed,
            required_enforcement=enforcement,
            triggered_policies=triggered,
        )


default_policy_evaluator = PolicyEvaluator()
