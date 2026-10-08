"""
VERIACT — Ground Truth Explorer API Router
Endpoints to inspect controlled enterprise ERP state (invoices and vendors).
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from app.mock_env.db import ground_truth_repo

router = APIRouter()

@router.get("/ground-truth/invoices", response_model=List[Dict[str, Any]])
async def list_ground_truth_invoices():
    """Lists all 10 verified master invoices in the controlled ERP store."""
    return ground_truth_repo.list_invoices()

@router.get("/ground-truth/vendors", response_model=List[Dict[str, Any]])
async def list_ground_truth_vendors():
    """Lists all 10 verified master vendors in the controlled ERP store."""
    return ground_truth_repo.list_vendors()
