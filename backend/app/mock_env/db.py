"""
VERIACT — Controlled Enterprise Ground Truth Store (Mock ERP Database)
Provides both SQLAlchemy SQLite persistence and resilient in-memory fallbacks.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.mock_env.models import (
    Base,
    Vendor,
    Invoice,
    AgentRegistry,
    PolicyRule,
    ActionTraceModel,
    EscalationQueueItem,
    BenchmarkScenarioModel,
)

# Resolve default DB path in backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "veriact_enterprise.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize all tables in database schema."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    """Context manager for scoped database sessions."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db():
    """FastAPI dependency generator for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# IN-MEMORY MASTER FIXTURES (DUAL-KEYED FOR AMAN & VEDESH COMPATIBILITY)
# ==============================================================================

MOCK_INVOICES: Dict[str, Dict[str, Any]] = {
    "INV-1921": {
        "id": "INV-1921",
        "invoice_id": "INV-1921",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 18500.00,
        "approved_amount": 18500.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-991",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-20",
    },
    "INV-1922": {
        "id": "INV-1922",
        "invoice_id": "INV-1922",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 42000.00,
        "approved_amount": 42000.00,
        "currency": "INR",
        "status": "PENDING_APPROVAL",
        "po_number": "PO-992",
        "approved_by": None,
        "due_date": "2026-10-25",
    },
    "INV-404": {
        "id": "INV-404",
        "invoice_id": "INV-404",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "amount": 9200.00,
        "approved_amount": 9200.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-812",
        "approved_by": "mgr_anita",
        "due_date": "2026-10-18",
    },
    "INV-405": {
        "id": "INV-405",
        "invoice_id": "INV-405",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "amount": 125000.00,
        "approved_amount": 125000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-813",
        "approved_by": "dir_rajesh",
        "due_date": "2026-11-01",
    },
    "INV-881": {
        "id": "INV-881",
        "invoice_id": "INV-881",
        "vendor_id": "VND-003",
        "vendor_name": "CloudScale Infrastructure",
        "amount": 64000.00,
        "approved_amount": 64000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-701",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-15",
    },
    "INV-102": {
        "id": "INV-102",
        "invoice_id": "INV-102",
        "vendor_id": "VND-004",
        "vendor_name": "Apex Office Supplies",
        "amount": 3400.00,
        "approved_amount": 3400.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-409",
        "approved_by": "mgr_anita",
        "due_date": "2026-10-30",
    },
    "INV-771": {
        "id": "INV-771",
        "invoice_id": "INV-771",
        "vendor_id": "VND-005",
        "vendor_name": "CyberShield Security",
        "amount": 50000.00,
        "approved_amount": 50000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-550",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-10",
    },
    "INV-900": {
        "id": "INV-900",
        "invoice_id": "INV-900",
        "vendor_id": "VND-006",
        "vendor_name": "Global Talent Solutions",
        "amount": 15000.00,
        "approved_amount": 15000.00,
        "currency": "INR",
        "status": "DRAFT",
        "po_number": None,
        "approved_by": None,
        "due_date": "2026-10-28",
    },
    "INV-312": {
        "id": "INV-312",
        "invoice_id": "INV-312",
        "vendor_id": "VND-007",
        "vendor_name": "QuickCourier Services",
        "amount": 1200.00,
        "approved_amount": 1200.00,
        "currency": "INR",
        "status": "PAID",
        "po_number": "PO-301",
        "approved_by": "mgr_anita",
        "due_date": "2026-09-30",
    },
    "INV-660": {
        "id": "INV-660",
        "invoice_id": "INV-660",
        "vendor_id": "VND-008",
        "vendor_name": "Quantum Analytics Lab",
        "amount": 28000.00,
        "approved_amount": 28000.00,
        "currency": "INR",
        "status": "CANCELLED",
        "po_number": "PO-602",
        "approved_by": None,
        "due_date": "2026-10-05",
    },
    "INV-550": {
        "id": "INV-550",
        "invoice_id": "INV-550",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 500.00,
        "approved_amount": 500.00,
        "currency": "USD",
        "status": "PENDING_APPROVAL",
        "po_number": "PO-995",
        "approved_by": None,
        "due_date": "2026-10-31",
    },
    "INV-711": {
        "id": "INV-711",
        "invoice_id": "INV-711",
        "vendor_id": "VND-011",
        "vendor_name": "Apex Global Freight",
        "amount": 12000.00,
        "approved_amount": 12000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-888",
        "approved_by": "mgr_vikram",
        "due_date": "2026-10-25",
    },
}

MOCK_VENDORS: Dict[str, Dict[str, Any]] = {
    "VND-001": {"id": "VND-001", "vendor_id": "VND-001", "name": "ABC Technologies Pvt Ltd", "status": "ACTIVE", "bank_account": "918239019283", "ifsc": "HDFC0000123", "ifsc_code": "HDFC0000123"},
    "VND-002": {"id": "VND-002", "vendor_id": "VND-002", "name": "XYZ Logistics India", "status": "ACTIVE", "bank_account": "812938192031", "ifsc": "ICIC0000456", "ifsc_code": "ICIC0000456"},
    "VND-003": {"id": "VND-003", "vendor_id": "VND-003", "name": "CloudScale Infrastructure", "status": "ACTIVE", "bank_account": "728192039182", "ifsc": "SBIN0001234", "ifsc_code": "SBIN0001234"},
    "VND-004": {"id": "VND-004", "vendor_id": "VND-004", "name": "Apex Office Supplies", "status": "ACTIVE", "bank_account": "619283019283", "ifsc": "KKBK0000789", "ifsc_code": "KKBK0000789"},
    "VND-005": {"id": "VND-005", "vendor_id": "VND-005", "name": "CyberShield Security", "status": "SUSPENDED", "bank_account": "519283910293", "ifsc": "UTIB0000321", "ifsc_code": "UTIB0000321"},
    "VND-006": {"id": "VND-006", "vendor_id": "VND-006", "name": "Global Talent Solutions", "status": "ACTIVE", "bank_account": "419283019201", "ifsc": "BARB0BOMBAY", "ifsc_code": "BARB0BOMBAY"},
    "VND-007": {"id": "VND-007", "vendor_id": "VND-007", "name": "QuickCourier Services", "status": "ACTIVE", "bank_account": "319203918203", "ifsc": "PUNB0000555", "ifsc_code": "PUNB0000555"},
    "VND-008": {"id": "VND-008", "vendor_id": "VND-008", "name": "Quantum Analytics Lab", "status": "ACTIVE", "bank_account": "219203918204", "ifsc": "YESB0000111", "ifsc_code": "YESB0000111"},
    "VND-009": {"id": "VND-009", "vendor_id": "VND-009", "name": "Delta Manufacturing Ltd", "status": "ACTIVE", "bank_account": "119203918205", "ifsc": "CBIN0000999", "ifsc_code": "CBIN0000999"},
    "VND-010": {"id": "VND-010", "vendor_id": "VND-010", "name": "FinEdge Advisory LLP", "status": "ACTIVE", "bank_account": "998203918206", "ifsc": "IDFB0000888", "ifsc_code": "IDFB0000888"},
    "VND-011": {"id": "VND-011", "vendor_id": "VND-011", "name": "Apex Global Freight", "status": "PENDING_KYC", "bank_account": "771122334455", "ifsc": "KKBK0000111", "ifsc_code": "KKBK0000111"},
}

MOCK_AGENTS: Dict[str, Dict[str, Any]] = {
    "agent_fin_jr": {"id": "agent_fin_jr", "name": "Junior Finance Bot", "role": "JUNIOR_ASSISTANT", "single_limit": 5000.0, "single_txn_limit": 5000.0, "daily_budget_limit": 20000.0, "allowed": ["read_invoice", "check_status"], "is_active": True},
    "agent_fin_sr": {"id": "agent_fin_sr", "name": "Senior Payment Agent", "role": "FINANCE_OPERATOR", "single_limit": 25000.0, "single_txn_limit": 25000.0, "daily_budget_limit": 100000.0, "allowed": ["read_invoice", "make_payment", "check_status"], "is_active": True},
    "agent_fin_mgr": {"id": "agent_fin_mgr", "name": "Executive Finance Agent", "role": "FINANCE_MANAGER", "single_limit": 250000.0, "single_txn_limit": 250000.0, "daily_budget_limit": 1000000.0, "allowed": ["*"], "is_active": True},
    "agent_ops_bot": {"id": "agent_ops_bot", "name": "General Operations Bot", "role": "OPS_BOT", "single_limit": 0.0, "single_txn_limit": 0.0, "daily_budget_limit": 0.0, "allowed": ["read_status", "send_notification"], "is_active": True},
}

MOCK_POLICIES: List[Dict[str, Any]] = [
    {
        "id": "POL-FIN-001",
        "name": "High Value Payment Signoff",
        "description": "Any single payment exceeding INR 10,000 INR requires human managerial approval.",
        "condition_expression": "action.parameters.get('amount', 0) > 10000",
        "action_type": "FINANCIAL",
        "enforcement_action": "ESCALATE",
        "priority": 1,
        "is_active": True,
    },
    {
        "id": "POL-FIN-002",
        "name": "Suspended Vendor Blacklist",
        "description": "Strictly prevent any transaction involving vendors marked as SUSPENDED or PENDING_KYC.",
        "condition_expression": "vendor.status in ['SUSPENDED', 'PENDING_KYC']",
        "action_type": "FINANCIAL",
        "enforcement_action": "BLOCK",
        "priority": 1,
        "is_active": True,
    },
    {
        "id": "POL-FIN-003",
        "name": "Duplicate Payment & Non-Approved Invoice Guard",
        "description": "Invoices can only be processed if their status is strictly 'APPROVED'. Invoices marked 'PAID', 'DRAFT', or 'CANCELLED' are blocked.",
        "condition_expression": "invoice.status != 'APPROVED'",
        "action_type": "FINANCIAL",
        "enforcement_action": "BLOCK",
        "priority": 1,
        "is_active": True,
    },
    {
        "id": "POL-SEC-001",
        "name": "Single Transaction Role Cap",
        "description": "An agent cannot initiate an action where amount exceeds its assigned single_txn_limit.",
        "condition_expression": "action.parameters.get('amount', 0) > agent.single_txn_limit",
        "action_type": "FINANCIAL",
        "enforcement_action": "BLOCK",
        "priority": 2,
        "is_active": True,
    },
    {
        "id": "POL-DATA-001",
        "name": "Destructive Table Drop Protection",
        "description": "Agents are unconditionally blocked from dropping or truncating database tables.",
        "condition_expression": "action.tool_name in ['drop_table', 'truncate_table', 'delete_all_records']",
        "action_type": "DATA_MUTATION",
        "enforcement_action": "BLOCK",
        "priority": 1,
        "is_active": True,
    },
]


# ==============================================================================
# REPOSITORY QUERY HELPERS (GROUND TRUTH LOOKUPS)
# ==============================================================================

def get_invoice(invoice_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve ground-truth invoice record by ID."""
    clean_id = invoice_id.strip().upper()
    try:
        with get_session() as session:
            inv = session.query(Invoice).filter(Invoice.id == clean_id).first()
            if inv:
                return inv.to_dict()
    except Exception:
        pass
    return MOCK_INVOICES.get(clean_id)


def get_vendor(vendor_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve ground-truth vendor master record by ID."""
    clean_id = vendor_id.strip().upper()
    try:
        with get_session() as session:
            vnd = session.query(Vendor).filter(Vendor.id == clean_id).first()
            if vnd:
                return vnd.to_dict()
    except Exception:
        pass
    return MOCK_VENDORS.get(clean_id)


def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
    """Alias for get_vendor."""
    return get_vendor(vendor_id)


def get_vendor_by_name(vendor_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve ground-truth vendor by legal entity name (case-insensitive)."""
    target = vendor_name.strip().lower()
    try:
        with get_session() as session:
            vnd = session.query(Vendor).filter(Vendor.name.ilike(f"%{target}%")).first()
            if vnd:
                return vnd.to_dict()
    except Exception:
        pass
    for v in MOCK_VENDORS.values():
        if target in v["name"].lower() or v["name"].lower() in target:
            return v
    return None


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve agent registry record by ID."""
    try:
        with get_session() as session:
            agt = session.query(AgentRegistry).filter(AgentRegistry.id == agent_id).first()
            if agt:
                return agt.to_dict()
    except Exception:
        pass
    return MOCK_AGENTS.get(agent_id, {
        "id": agent_id,
        "role": "FINANCE_OPERATOR",
        "single_limit": 25000.0,
        "single_txn_limit": 25000.0,
        "allowed": ["make_payment", "read_invoice"],
        "is_active": True,
    })


def get_policies(action_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve active enterprise policy rules, optionally filtered by action type."""
    try:
        with get_session() as session:
            query = session.query(PolicyRule).filter(PolicyRule.is_active == True)
            if action_type:
                query = query.filter(PolicyRule.action_type == action_type)
            policies = query.order_by(PolicyRule.priority.asc()).all()
            if policies:
                return [p.to_dict() for p in policies]
    except Exception:
        pass
    if action_type:
        return [p for p in MOCK_POLICIES if p["action_type"] == action_type and p["is_active"]]
    return [p for p in MOCK_POLICIES if p["is_active"]]


def get_all_invoices() -> List[Dict[str, Any]]:
    """Retrieve all ground-truth invoices for explorer UI."""
    try:
        with get_session() as session:
            invoices = session.query(Invoice).order_by(Invoice.id.asc()).all()
            if invoices:
                return [inv.to_dict() for inv in invoices]
    except Exception:
        pass
    return list(MOCK_INVOICES.values())


def get_all_vendors() -> List[Dict[str, Any]]:
    """Retrieve all ground-truth vendors for explorer UI."""
    try:
        with get_session() as session:
            vendors = session.query(Vendor).order_by(Vendor.id.asc()).all()
            if vendors:
                return [vnd.to_dict() for vnd in vendors]
    except Exception:
        pass
    return list(MOCK_VENDORS.values())


class GroundTruthRepository:
    """Class interface for ground truth ERP queries."""

    @staticmethod
    def get_invoice(invoice_id: str) -> Optional[Dict[str, Any]]:
        return get_invoice(invoice_id)

    @staticmethod
    def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
        return get_vendor(vendor_id)

    @staticmethod
    def get_vendor_by_name(vendor_name: str) -> Optional[Dict[str, Any]]:
        return get_vendor_by_name(vendor_name)

    @staticmethod
    def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
        return get_agent(agent_id)

    @staticmethod
    def list_invoices() -> List[Dict[str, Any]]:
        return get_all_invoices()

    @staticmethod
    def list_vendors() -> List[Dict[str, Any]]:
        return get_all_vendors()


ground_truth_repo = GroundTruthRepository()
