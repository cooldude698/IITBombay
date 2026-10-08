"""
VERIACT — Human Escalation API Router (Task AMAN-302 & AMAN-303)
Endpoints for viewing pending actions and submitting managerial review decisions.
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.schemas import EscalationItem, EscalationDecisionRequest, EscalationStatus
from app.engine.decision.escalation_queue import escalation_queue

router = APIRouter()

@router.get("/escalation/queue", response_model=List[EscalationItem])
async def list_escalation_queue(status: Optional[EscalationStatus] = None):
    """Retrieves all pending or reviewed actions in the Human-in-the-Loop review queue."""
    return escalation_queue.list_all(status=status)

@router.post("/escalation/{item_id}/decision", response_model=EscalationItem)
async def submit_escalation_decision(item_id: str, payload: EscalationDecisionRequest):
    """
    Submits a managerial decision (APPROVE or REJECT).
    If approved, mints a valid cryptographic HMAC execution token.
    """
    resolved = escalation_queue.resolve(
        item_id=item_id,
        decision=payload.decision,
        reviewer_id=payload.reviewer_id,
        notes=payload.notes or ""
    )
    if not resolved:
        raise HTTPException(status_code=404, detail=f"Escalation item '{item_id}' not found.")
    return resolved
