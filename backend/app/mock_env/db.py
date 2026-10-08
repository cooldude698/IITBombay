"""
VERIACT — Controlled Enterprise Ground Truth Store (Mock ERP Database)
"""
from typing import Dict, Any, Optional, List

# Master Invoices Directory (10 Seed Invoices from DATA_SOURCES.MD)
MOCK_INVOICES: Dict[str, Dict[str, Any]] = {
    "INV-1921": {
        "invoice_id": "INV-1921",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "approved_amount": 18500.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-991",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-20"
    },
    "INV-1922": {
        "invoice_id": "INV-1922",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "approved_amount": 42000.00,
        "currency": "INR",
        "status": "PENDING_APPROVAL",
        "po_number": "PO-992",
        "approved_by": None,
        "due_date": "2026-10-25"
    },
    "INV-404": {
        "invoice_id": "INV-404",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "approved_amount": 9200.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-812",
        "approved_by": "mgr_anita",
        "due_date": "2026-10-18"
    },
    "INV-405": {
        "invoice_id": "INV-405",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "approved_amount": 125000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-813",
        "approved_by": "dir_rajesh",
        "due_date": "2026-11-01"
    },
    "INV-881": {
        "invoice_id": "INV-881",
        "vendor_id": "VND-003",
        "vendor_name": "CloudScale Infrastructure",
        "approved_amount": 64000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-701",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-15"
    },
    "INV-102": {
        "invoice_id": "INV-102",
        "vendor_id": "VND-004",
        "vendor_name": "Apex Office Supplies",
        "approved_amount": 3400.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-409",
        "approved_by": "mgr_anita",
        "due_date": "2026-10-30"
    },
    "INV-771": {
        "invoice_id": "INV-771",
        "vendor_id": "VND-005",
        "vendor_name": "CyberShield Security",
        "approved_amount": 50000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-550",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-10"
    },
    "INV-900": {
        "invoice_id": "INV-900",
        "vendor_id": "VND-006",
        "vendor_name": "Global Talent Solutions",
        "approved_amount": 15000.00,
        "currency": "INR",
        "status": "DRAFT",
        "po_number": None,
        "approved_by": None,
        "due_date": "2026-10-28"
    },
    "INV-312": {
        "invoice_id": "INV-312",
        "vendor_id": "VND-007",
        "vendor_name": "QuickCourier Services",
        "approved_amount": 1200.00,
        "currency": "INR",
        "status": "PAID",
        "po_number": "PO-301",
        "approved_by": "mgr_anita",
        "due_date": "2026-09-30"
    },
    "INV-660": {
        "invoice_id": "INV-660",
        "vendor_id": "VND-008",
        "vendor_name": "Quantum Analytics Lab",
        "approved_amount": 28000.00,
        "currency": "INR",
        "status": "CANCELLED",
        "po_number": "PO-602",
        "approved_by": None,
        "due_date": "2026-10-05"
    }
}

# Master Vendors Directory
MOCK_VENDORS: Dict[str, Dict[str, Any]] = {
    "VND-001": {"vendor_id": "VND-001", "name": "ABC Technologies Pvt Ltd", "status": "ACTIVE", "bank_account": "918239019283", "ifsc": "HDFC0000123"},
    "VND-002": {"vendor_id": "VND-002", "name": "XYZ Logistics India", "status": "ACTIVE", "bank_account": "812938192031", "ifsc": "ICIC0000456"},
    "VND-003": {"vendor_id": "VND-003", "name": "CloudScale Infrastructure", "status": "ACTIVE", "bank_account": "728192039182", "ifsc": "SBIN0001234"},
    "VND-004": {"vendor_id": "VND-004", "name": "Apex Office Supplies", "status": "ACTIVE", "bank_account": "619283019283", "ifsc": "KKBK0000789"},
    "VND-005": {"vendor_id": "VND-005", "name": "CyberShield Security", "status": "SUSPENDED", "bank_account": "519283910293", "ifsc": "UTIB0000321"},
    "VND-006": {"vendor_id": "VND-006", "name": "Global Talent Solutions", "status": "ACTIVE", "bank_account": "419283019201", "ifsc": "BARB0BOMBAY"},
    "VND-007": {"vendor_id": "VND-007", "name": "QuickCourier Services", "status": "ACTIVE", "bank_account": "319203918203", "ifsc": "PUNB0000555"},
    "VND-008": {"vendor_id": "VND-008", "name": "Quantum Analytics Lab", "status": "ACTIVE", "bank_account": "219203918204", "ifsc": "YESB0000111"},
    "VND-009": {"vendor_id": "VND-009", "name": "Delta Manufacturing Ltd", "status": "ACTIVE", "bank_account": "119203918205", "ifsc": "CBIN0000999"},
    "VND-010": {"vendor_id": "VND-010", "name": "FinEdge Advisory LLP", "status": "ACTIVE", "bank_account": "998203918206", "ifsc": "IDFB0000888"},
}

# Agent RBAC Profiles
MOCK_AGENTS: Dict[str, Dict[str, Any]] = {
    "agent_fin_jr": {"role": "JUNIOR_ASSISTANT", "single_limit": 5000.0, "allowed": ["read_invoice", "check_status"]},
    "agent_fin_sr": {"role": "FINANCE_OPERATOR", "single_limit": 25000.0, "allowed": ["read_invoice", "make_payment", "check_status"]},
    "agent_fin_mgr": {"role": "FINANCE_MANAGER", "single_limit": 250000.0, "allowed": ["*"]},
    "agent_ops_bot": {"role": "OPS_BOT", "single_limit": 0.0, "allowed": ["read_status", "send_notification"]},
}

class GroundTruthRepository:
    """Synchronous & Async Interface to query ground truth ERP state."""
    
    @staticmethod
    def get_invoice(invoice_id: str) -> Optional[Dict[str, Any]]:
        clean_id = invoice_id.strip().upper()
        return MOCK_INVOICES.get(clean_id)
        
    @staticmethod
    def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
        return MOCK_VENDORS.get(vendor_id)

    @staticmethod
    def get_vendor_by_name(vendor_name: str) -> Optional[Dict[str, Any]]:
        target = vendor_name.strip().lower()
        for v in MOCK_VENDORS.values():
            if target in v["name"].lower() or v["name"].lower() in target:
                return v
        return None

    @staticmethod
    def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
        return MOCK_AGENTS.get(agent_id, {
            "role": "FINANCE_OPERATOR",
            "single_limit": 25000.0,
            "allowed": ["make_payment", "read_invoice"]
        })
    
    @staticmethod
    def list_invoices() -> List[Dict[str, Any]]:
        return list(MOCK_INVOICES.values())

    @staticmethod
    def list_vendors() -> List[Dict[str, Any]]:
        return list(MOCK_VENDORS.values())

ground_truth_repo = GroundTruthRepository()
