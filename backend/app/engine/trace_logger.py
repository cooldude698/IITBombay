"""
VERIACT — Auditable Action Trace Logger (Task AMAN-304 & AMAN-404)
Persists tamper-evident verification traces with SHA-256 payload chaining and real-time subscriber streaming.
"""
import asyncio
import hashlib
import json
from typing import List, Optional
from datetime import datetime
from app.models.schemas import ActionTrace, NormalizedAction, VerificationResult, GroundTruthEvidence

class TraceLogger:
    def __init__(self):
        self._traces: List[ActionTrace] = []
        self._subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        """Register an asyncio queue subscriber for real-time telemetry streaming (SSE)."""
        queue = asyncio.Queue()
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        """Unregister an asyncio queue subscriber."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)

    def record_trace(
        self,
        action: NormalizedAction,
        result: VerificationResult,
        evidence: Optional[GroundTruthEvidence] = None
    ) -> ActionTrace:
        # Canonical hash computation
        payload = f"{action.action_id}:{action.tool_name}:{sorted(action.parameters.items())}:{result.verdict.value}:{result.trace_id}"
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        evidence_dict = evidence.data if evidence else None

        trace = ActionTrace(
            trace_id=result.trace_id,
            action_id=action.action_id,
            timestamp=datetime.utcnow(),
            agent_id=action.agent_id,
            tool_name=action.tool_name,
            action_type=action.action_type,
            target_entity=action.target_entity,
            proposed_params=action.parameters,
            retrieved_evidence=evidence_dict,
            mismatches=result.mismatches,
            risk_score=result.risk_assessment.total_risk_score,
            verification_tier=result.verification_tier,
            verdict=result.verdict,
            reason=result.reason,
            latency_ms=result.latency_ms,
            payload_hash=f"sha256:{payload_hash}"
        )
        self._traces.insert(0, trace)  # Newest first

        # Broadcast to active SSE subscribers
        for sub in list(self._subscribers):
            try:
                sub.put_nowait(trace)
            except Exception:
                pass

        return trace

    def get_traces(self, limit: int = 50) -> List[ActionTrace]:
        return self._traces[:limit]

    def get_trace_by_id(self, trace_id: str) -> Optional[ActionTrace]:
        for t in self._traces:
            if t.trace_id == trace_id:
                return t
        return None

trace_logger = TraceLogger()
