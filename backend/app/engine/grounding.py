"""
VERIACT — Grounding & Deterministic Validation Engine
Evaluates parameter equality, RBAC limits, and policy compliance against external ground truth.
"""
from typing import Tuple, List, Dict, Any, Optional
from app.models.schemas import NormalizedAction, ActionType, ParameterMismatch, GroundTruthEvidence
from app.mock_env.db import ground_truth_repo

class DeterministicGroundingEngine:
    """Executes native Python deterministic verification without LLM hallucination risk."""

    def evaluate(
        self,
        action: NormalizedAction
    ) -> Tuple[Optional[GroundTruthEvidence], List[ParameterMismatch], List[str], float, bool]:
        """
        Returns:
            (evidence, mismatches, policy_violations, contradiction_score, requires_escalation)
        """
        mismatches: List[ParameterMismatch] = []
        violations: List[str] = []
        contradiction_score = 0.0
        requires_escalation = False
        evidence_record: Optional[GroundTruthEvidence] = None

        # 1. Read-Only Actions
        if action.action_type == ActionType.READ_ONLY:
            inv_id = action.parameters.get("invoice") or action.parameters.get("invoice_id")
            if inv_id:
                raw_inv = ground_truth_repo.get_invoice(str(inv_id))
                if raw_inv:
                    evidence_record = GroundTruthEvidence(
                        evidence_id=f"evi_{raw_inv['invoice_id']}",
                        entity_key=raw_inv["invoice_id"],
                        data=raw_inv,
                        confidence_score=1.0
                    )
            return evidence_record, mismatches, violations, 0.0, False

        # 2. RBAC Privilege Check
        agent_profile = ground_truth_repo.get_agent(action.agent_id)
        if agent_profile:
            allowed_tools = agent_profile.get("allowed", [])
            if "*" not in allowed_tools and action.tool_name not in allowed_tools:
                violations.append(f"RBAC_VIOLATION: Agent role '{agent_profile['role']}' is not authorized to execute '{action.tool_name}'.")
                contradiction_score = 1.0

        # 3. Financial Actions Grounding
        if action.action_type == ActionType.FINANCIAL:
            inv_id = action.parameters.get("invoice")
            proposed_amount = action.parameters.get("amount")
            proposed_vendor = action.parameters.get("vendor")

            if not inv_id:
                violations.append("MISSING_EVIDENCE: Financial transfer requires valid invoice reference.")
                contradiction_score = 1.0
                return None, mismatches, violations, contradiction_score, False

            raw_inv = ground_truth_repo.get_invoice(str(inv_id))
            if not raw_inv:
                mismatches.append(ParameterMismatch(
                    field_name="invoice_id",
                    proposed_value=inv_id,
                    evidence_value=None,
                    severity="CRITICAL",
                    message=f"Hallucinated entity: Invoice '{inv_id}' does not exist in ERP database."
                ))
                contradiction_score = 1.0
                return None, mismatches, violations, contradiction_score, False

            evidence_record = GroundTruthEvidence(
                evidence_id=f"evi_{raw_inv['invoice_id']}",
                entity_key=raw_inv["invoice_id"],
                data=raw_inv,
                confidence_score=1.0
            )

            # Check Invoice Status
            if raw_inv["status"] != "APPROVED":
                violations.append(f"POLICY_VIOLATION (POL-FIN-003): Invoice '{inv_id}' status is '{raw_inv['status']}'. Only 'APPROVED' invoices can be paid.")
                contradiction_score = 1.0

            # Check Vendor Status
            vendor_rec = ground_truth_repo.get_vendor_by_id(raw_inv["vendor_id"])
            if vendor_rec and vendor_rec["status"] == "SUSPENDED":
                violations.append(f"POLICY_VIOLATION (POL-FIN-002): Vendor '{vendor_rec['name']}' is SUSPENDED. Payments strictly blocked.")
                contradiction_score = 1.0

            # Compare Amounts
            if proposed_amount is not None:
                approved_amount = raw_inv["approved_amount"]
                delta = abs(float(proposed_amount) - approved_amount)
                if delta > 0.01:
                    diff_sign = "+" if float(proposed_amount) > approved_amount else "-"
                    mismatches.append(ParameterMismatch(
                        field_name="amount",
                        proposed_value=proposed_amount,
                        evidence_value=approved_amount,
                        severity="CRITICAL",
                        message=f"Amount mismatch: Proposed amount ₹{proposed_amount:,.2f} contradicts approved invoice amount ₹{approved_amount:,.2f} ({diff_sign}₹{delta:,.2f})."
                    ))
                    contradiction_score = 1.0

            # Compare Vendor Names
            if proposed_vendor:
                exp_vendor = raw_inv["vendor_name"]
                if proposed_vendor.strip().lower() not in exp_vendor.lower() and exp_vendor.lower() not in proposed_vendor.strip().lower():
                    mismatches.append(ParameterMismatch(
                        field_name="vendor",
                        proposed_value=proposed_vendor,
                        evidence_value=exp_vendor,
                        severity="CRITICAL",
                        message=f"Recipient mismatch: Proposed vendor '{proposed_vendor}' does not match invoice recipient '{exp_vendor}'."
                    ))
                    contradiction_score = 1.0

            # Policy POL-FIN-001: Spending Cap > 10,000 requires manager signoff
            if proposed_amount and float(proposed_amount) > 10000.0:
                if contradiction_score == 0.0:  # If everything else matches
                    requires_escalation = True
                    violations.append(f"POLICY_ALERT (POL-FIN-001): Payment of ₹{proposed_amount:,.2f} exceeds autonomous cap of ₹10,000.00. Manager signoff required.")

        return evidence_record, mismatches, violations, contradiction_score, requires_escalation

grounding_engine = DeterministicGroundingEngine()
