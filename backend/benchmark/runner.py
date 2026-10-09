"""
VERIACT — Red-Team Benchmark Runner & Comparative Evaluation Harness (Tasks ARYAN-302 & ARYAN-402)
Evaluates 4 Comparative Baselines across VERIACT-ASB scenarios:
  1. Baseline A: No Guardrail
  2. Baseline B: LLM-as-a-Judge
  3. Baseline C: Always-Deep Verifier
  4. VERIACT: Risk-Adaptive Routed Verification
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from benchmark.baselines import (
    NoGuardrailBaseline,
    LLMJudgeBaseline,
    AlwaysDeepBaseline,
    VeriactAdaptiveBaseline,
)

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_dataset(size: int) -> List[Dict[str, Any]]:
    if size <= 25:
        target = DATA_DIR / "seed_25.json"
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)[:size]
    if size <= 75:
        target = DATA_DIR / "seed_75.json"
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)[:size]

    target = DATA_DIR / "veriact_asb_250.json"
    if target.exists():
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)[:size]

    # Fallback to seed_25 if 250 not found
    fallback = DATA_DIR / "seed_25.json"
    with open(fallback, "r", encoding="utf-8") as f:
        return json.load(f)


async def evaluate_system(baseline, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    latencies = []
    blocked_count = 0
    false_block_count = 0
    total_unsafe = sum(1 for s in scenarios if s.get("expected_verdict") in ["BLOCK", "ESCALATE"])
    total_safe = len(scenarios) - total_unsafe

    for scn in scenarios:
        res = await baseline.evaluate(scn)
        results.append(res)
        latencies.append(res.latency_ms)
        if res.blocked_unsafe:
            blocked_count += 1
        if res.false_block:
            false_block_count += 1

    safety_recall = (blocked_count / total_unsafe * 100.0) if total_unsafe > 0 else 100.0
    false_block_rate = (false_block_count / total_safe * 100.0) if total_safe > 0 else 0.0
    avg_latency = int(sum(latencies) / len(latencies)) if latencies else 0
    sorted_lat = sorted(latencies)
    p95_latency = sorted_lat[min(int(len(sorted_lat) * 0.95), len(sorted_lat) - 1)] if latencies else 0
    cost_per_1k = round(sum(r.token_cost for r in results) / len(results) * 1000.0, 2) if results else 0.0

    return {
        "baseline_name": baseline.name,
        "scenarios_evaluated": len(scenarios),
        "safety_recall_pct": round(safety_recall, 1),
        "false_block_rate_pct": round(false_block_rate, 1),
        "average_latency_ms": avg_latency,
        "p95_latency_ms": p95_latency,
        "cost_per_1k_usd": cost_per_1k,
        "raw_results": [r.model_dump() for r in results],
    }


def format_markdown_table(summary: List[Dict[str, Any]]) -> str:
    lines = [
        "| Baseline System | Safety Recall (%) | False Block Rate (%) | Avg Latency (ms) | P95 Latency (ms) | Cost / 1k Actions |",
        "|---|---|---|---|---|---|",
    ]
    for s in summary:
        name_str = f"**{s['baseline_name']}**" if "VERIACT" in s["baseline_name"] else s["baseline_name"]
        lines.append(
            f"| {name_str} | {s['safety_recall_pct']}% | {s['false_block_rate_pct']}% | {s['average_latency_ms']} ms | {s['p95_latency_ms']} ms | ${s['cost_per_1k_usd']:.2f} |"
        )
    return "\n".join(lines)


async def run_benchmark(size: int, output_format: str = "markdown", dry_run: bool = False):
    scenarios = load_dataset(size)
    if dry_run:
        scenarios = scenarios[:5]

    baselines = [
        NoGuardrailBaseline(),
        LLMJudgeBaseline(),
        AlwaysDeepBaseline(),
        VeriactAdaptiveBaseline(),
    ]

    summaries = []
    for b in baselines:
        stats = await evaluate_system(b, scenarios)
        summaries.append(stats)

    if output_format.lower() == "json":
        clean_out = [{k: v for k, v in s.items() if k != "raw_results"} for s in summaries]
        print(json.dumps(clean_out, indent=2))
    else:
        print("\n" + "=" * 80)
        print(f"VERIACT-ASB Benchmark Evaluation ({len(scenarios)} Scenarios Across 4 Baselines)")
        print("=" * 80 + "\n")
        print(format_markdown_table(summaries))
        print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="VERIACT-ASB Red-Team Benchmark Runner")
    parser.add_argument("--size", type=int, default=250, help="Number of scenarios to evaluate (25, 75, 250)")
    parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "json"], help="Output format")
    parser.add_argument("--dry-run", action="store_true", help="Quick dry run with 5 sample scenarios")
    parser.add_argument("--output", type=str, default="", help="Optional path to write JSON output")
    args = parser.parse_args()

    asyncio.run(run_benchmark(size=args.size, output_format=args.format, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
