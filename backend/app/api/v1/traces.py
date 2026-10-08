"""
VERIACT — Auditable Action Traces & Real-Time Telemetry Stream (Tasks AMAN-304 & AMAN-404)
Endpoints for compliance dashboards to inspect structured verification traces and stream live events via SSE.
"""
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List
from app.models.schemas import ActionTrace
from app.engine.trace_logger import trace_logger

router = APIRouter()

@router.get("/actions/traces", response_model=List[ActionTrace])
async def list_action_traces(limit: int = 50):
    """Returns chronological audit traces for the Live Action Stream."""
    return trace_logger.get_traces(limit=limit)

@router.get("/actions/traces/{trace_id}", response_model=ActionTrace)
async def get_action_trace_detail(trace_id: str):
    """Retrieves full parameter comparison matrix and evidence diff for a single trace."""
    trace = trace_logger.get_trace_by_id(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found.")
    return trace

@router.get("/telemetry/stream")
@router.get("/actions/stream")
async def stream_telemetry_events(request: Request):
    """
    Server-Sent Events (SSE) streaming endpoint for live action telemetry (Task AMAN-404).
    Pushes newly evaluated action traces in real-time to Aryan's Next.js UI table.
    """
    queue = trace_logger.subscribe()

    async def event_generator():
        try:
            # Yield initial connection ack
            yield "event: connected\ndata: {\"status\": \"connected\"}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    trace: ActionTrace = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: trace\ndata: {trace.model_dump_json()}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            trace_logger.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
