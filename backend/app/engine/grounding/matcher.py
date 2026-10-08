"""Deterministic Parameter Grounding Engine for VERIACT.

Performs zero-latency mathematical and string comparison of agent proposed
action parameters against authoritative ground-truth records.
"""

from typing import Any, Dict, List, Optional, Tuple
from app.models.schemas import ParameterMismatch


class GroundingResult:
    def __init__(
        self,
        is_grounded: bool,
        contradiction_score: float,
        mismatches: List[ParameterMismatch],
        details: Dict[str, Any],
    ):
        self.is_grounded = is_grounded
        self.contradiction_score = contradiction_score
        self.mismatches = mismatches
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_grounded": self.is_grounded,
            "contradiction_score": self.contradiction_score,
            "mismatches": [m.model_dump() for m in self.mismatches],
            "details": self.details,
        }


class ParameterMatcher:
    """Deterministic, rule-based parameter verifier against ground truth."""

    def __init__(self, currency_tolerance: float = 0.00):
        self.currency_tolerance = currency_tolerance

    def match_invoice_payment(
        self,
        proposed_params: Dict[str, Any],
        ground_truth_invoice: Optional[Dict[str, Any]],
        ground_truth_vendor: Optional[Dict[str, Any]] = None,
    ) -> GroundingResult:
        """Compares proposed payment parameters against verified invoice in ERP.

        Validates:
        1. Invoice existence in Ground Truth
        2. Numerical amount equality (Δ = |proposed - approved|)
        3. Vendor entity identity
        4. Invoice approval status (must be APPROVED)
        5. Vendor account / IFSC matching if provided
        """
        mismatches: List[ParameterMismatch] = []
        details: Dict[str, Any] = {}

        # 1. Check Invoice Existence
        if ground_truth_invoice is None:
            mismatches.append(
                ParameterMismatch(
                    field_name="invoice_id",
                    proposed_value=proposed_params.get("invoice_id") or proposed_params.get("invoice"),
                    evidence_value=None,
                    severity="CRITICAL",
                    message="Referenced invoice does not exist in ERP database (Hallucinated Entity)",
                )
            )
            return GroundingResult(
                is_grounded=False,
                contradiction_score=1.0,
                mismatches=mismatches,
                details={"reason": "INVOICE_NOT_FOUND"},
            )

        # 2. Numerical Amount Validation
        proposed_amount = proposed_params.get("amount")
        expected_amount = ground_truth_invoice.get("amount")

        if proposed_amount is not None and expected_amount is not None:
            try:
                p_amt = float(proposed_amount)
                e_amt = float(expected_amount)
                delta = abs(p_amt - e_amt)

                if delta > self.currency_tolerance:
                    sign = "+" if p_amt > e_amt else "-"
                    mismatches.append(
                        ParameterMismatch(
                            field_name="amount",
                            proposed_value=p_amt,
                            evidence_value=e_amt,
                            severity="CRITICAL",
                            message=(
                                f"Proposed amount INR {p_amt:,.2f} contradicts verified "
                                f"invoice amount INR {e_amt:,.2f} (Delta: {sign}INR {delta:,.2f})"
                            ),
                        )
                    )
            except (ValueError, TypeError):
                mismatches.append(
                    ParameterMismatch(
                        field_name="amount",
                        proposed_value=proposed_amount,
                        evidence_value=expected_amount,
                        severity="CRITICAL",
                        message=f"Invalid numerical format for amount: {proposed_amount}",
                    )
                )

        # 3. Vendor Entity Verification
        proposed_vendor = (
            proposed_params.get("vendor_name")
            or proposed_params.get("vendor")
            or proposed_params.get("recipient")
            or proposed_params.get("vendor_id")
        )
        if proposed_vendor is not None:
            expected_v_name = ground_truth_invoice.get("vendor_name", "").strip().lower()
            expected_v_id = ground_truth_invoice.get("vendor_id", "").strip().lower()
            prop_v_clean = str(proposed_vendor).strip().lower()

            if (
                prop_v_clean != expected_v_name
                and prop_v_clean != expected_v_id
                and prop_v_clean not in expected_v_name
                and expected_v_id not in prop_v_clean
            ):
                mismatches.append(
                    ParameterMismatch(
                        field_name="vendor",
                        proposed_value=proposed_vendor,
                        evidence_value=ground_truth_invoice.get("vendor_name"),
                        severity="CRITICAL",
                        message=(
                            f"Proposed vendor '{proposed_vendor}' does not match invoice recipient "
                            f"'{ground_truth_invoice.get('vendor_name')}' ({ground_truth_invoice.get('vendor_id')})"
                        ),
                    )
                )

        # 4. Status Check
        inv_status = ground_truth_invoice.get("status", "").upper()
        if inv_status != "APPROVED":
            mismatches.append(
                ParameterMismatch(
                    field_name="status",
                    proposed_value="PAYABLE",
                    evidence_value=inv_status,
                    severity="CRITICAL",
                    message=(
                        f"Invoice {ground_truth_invoice.get('id')} has status '{inv_status}'. "
                        f"Only 'APPROVED' invoices can be paid."
                    ),
                )
            )

        # 5. Vendor Account / IFSC Validation (if present)
        if ground_truth_vendor:
            proposed_bank_acc = proposed_params.get("bank_account")
            if proposed_bank_acc and str(proposed_bank_acc).strip() != str(ground_truth_vendor.get("bank_account", "")).strip():
                mismatches.append(
                    ParameterMismatch(
                        field_name="bank_account",
                        proposed_value=proposed_bank_acc,
                        evidence_value=ground_truth_vendor.get("bank_account"),
                        severity="CRITICAL",
                        message="Proposed bank account does not match vendor master records",
                    )
                )

            vendor_status = ground_truth_vendor.get("status", "").upper()
            if vendor_status in ["SUSPENDED", "PENDING_KYC"]:
                mismatches.append(
                    ParameterMismatch(
                        field_name="vendor_status",
                        proposed_value="ACTIVE",
                        evidence_value=vendor_status,
                        severity="CRITICAL",
                        message=f"Vendor is in '{vendor_status}' state. Transactions prohibited.",
                    )
                )

        # Compute contradiction score C in [0.0, 1.0]
        if len(mismatches) == 0:
            c_score = 0.0
            is_grounded = True
        else:
            has_critical = any(m.severity == "CRITICAL" for m in mismatches)
            c_score = 1.0 if has_critical else 0.5
            is_grounded = False

        details["mismatch_count"] = len(mismatches)
        details["checked_invoice_id"] = ground_truth_invoice.get("id")

        return GroundingResult(
            is_grounded=is_grounded,
            contradiction_score=c_score,
            mismatches=mismatches,
            details=details,
        )


# Global singleton instance
default_matcher = ParameterMatcher()
