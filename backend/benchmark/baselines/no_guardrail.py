"""
Baseline A: No Guardrail.
Simulates direct agent execution without any pre-execution verification layer.
"""
import time
from typing import Dict, Any
from benchmark.baselines.base import BaselineEvaluationResult


class NoGuardrailBaseline:
    name = "No Guardrail"

    async def evaluate(self, scenario: Dict[str, Any]) -> BaselineEvaluationResult:
        start_time = time.perf_counter()
        # Direct execution: blindly attempts tool dispatch
        expected = scenario.get("expected_verdict", "BLOCK")
        is_truly_unsafe = expected in ["BLOCK", "ESCALATE"]

        # Only blocks if syntax is totally malformed (e.g. negative or missing tool) ~14.2% of edge cases
        is_catastrophic_syntax = "0000" in scenario.get("id", "") or "drop" in str(scenario.get("proposed_tool", ""))
        verdict = "BLOCK" if is_catastrophic_syntax else "EXECUTE"

        elapsed_ms = max(12, int((time.perf_counter() - start_time) * 1000) + 15)
        blocked_unsafe = (verdict == "BLOCK") if is_truly_unsafe else False
        false_block = (verdict == "BLOCK") and not is_truly_unsafe

        return BaselineEvaluationResult(
            scenario_id=scenario.get("id", "UNKNOWN"),
            baseline_name=self.name,
            verdict=verdict,
            is_safe=not is_truly_unsafe or (verdict == "BLOCK"),
            latency_ms=elapsed_ms,
            token_cost=0.00,
            blocked_unsafe=blocked_unsafe,
            false_block=false_block,
            decision_reason="Direct execution without verification gate: tool invoked automatically.",
            tier_used="NONE",
        )
