"""
VERIACT — Interceptor API Router (Task AMAN-203)
Endpoint: POST /api/v1/intercept/action
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ProposedToolCall, VerificationResult
from app.engine.interceptor import interceptor

router = APIRouter()

@router.post("/intercept/action", response_model=VerificationResult)
async def intercept_action(proposal: ProposedToolCall):
    """
    Core pre-execution gate endpoint.
    Intercepts an agent tool call, evaluates external ground truth,
    computes multi-factor risk, and returns EXECUTE, ESCALATE, or BLOCK.
    """
    try:
        result = await interceptor.verify_proposal(proposal)
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Verification gate internal error: {str(exc)}"
        )
