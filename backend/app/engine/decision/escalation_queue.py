"""
VERIACT — Human Review Escalation Queue (Task AMAN-302 & AMAN-303)
Holds high-risk and policy-alert transactions for human managerial review.
"""
from typing import List, Optional, Dict
from datetime import datetime
from uuid import uuid4
from app.models.schemas import EscalationItem, EscalationStatus, NormalizedAction, VerificationResult, GroundTruthEvidence
from app.core.crypto import generate_execution_token

class EscalationQueue:
    def __init__(self):
        self._items: Dict[str, EscalationItem] = {}

    def push(
        self,
        action: NormalizedAction,
        result: VerificationResult,
        evidence: Optional[GroundTruthEvidence] = None
    ) -> EscalationItem:
        item_id = f"esc_{uuid4().hex[:8]}"
        evidence_dict = evidence.data if evidence else None

        item = EscalationItem(
            item_id=item_id,
            action_id=action.action_id,
            trace_id=result.trace_id,
            agent_id=action.agent_id,
            tool_name=action.tool_name,
            action_type=action.action_type,
            target_entity=action.target_entity,
            proposed_params=action.parameters,
            retrieved_evidence=evidence_dict,
            risk_score=result.risk_assessment.total_risk_score,
            reason=result.reason,
            status=EscalationStatus.PENDING,
            created_at=datetime.utcnow()
        )
        self._items[item_id] = item
        return item

    def list_all(self, status: Optional[EscalationStatus] = None) -> List[EscalationItem]:
        items = list(self._items.values())
        if status:
            items = [i for i in items if i.status == status]
        return sorted(items, key=lambda x: x.created_at, reverse=True)

    def get_by_id(self, item_id: str) -> Optional[EscalationItem]:
        return self._items.get(item_id)

    def resolve(
        self,
        item_id: str,
        decision: str,
        reviewer_id: str = "mgr_vikram",
        notes: str = ""
    ) -> Optional[EscalationItem]:
        item = self._items.get(item_id)
        if not item:
            return None

        clean_dec = decision.strip().upper()
        item.reviewed_by = reviewer_id
        item.review_notes = notes
        item.resolved_at = datetime.utcnow()

        if clean_dec == "APPROVE":
            item.status = EscalationStatus.APPROVED
            # Generate valid override execution token
            item.execution_token = generate_execution_token(
                action_id=item.action_id,
                tool_name=item.tool_name,
                parameters=item.proposed_params
            )
        else:
            item.status = EscalationStatus.REJECTED
            item.execution_token = None

        return item

escalation_queue = EscalationQueue()
