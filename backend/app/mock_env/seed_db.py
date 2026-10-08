"""Master Database Seeder for VERIACT Controlled Enterprise Mock Environment.

Populates 10 Vendors, 10 Invoices, 4 Agents (RBAC Matrix), and 5 Enterprise Policies.
"""

import sys
from datetime import date
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.mock_env.db import init_db, get_session
from app.mock_env.models import Vendor, Invoice, AgentRegistry, PolicyRule


# ==============================================================================
# SEED DEFINITIONS
# ==============================================================================

VENDORS_SEED = [
    {
        "id": "VND-001",
        "name": "ABC Technologies Pvt Ltd",
        "bank_account": "918239019283",
        "ifsc_code": "HDFC0000123",
        "category": "Cloud & Software",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-002",
        "name": "XYZ Logistics India",
        "bank_account": "812938192031",
        "ifsc_code": "ICIC0000456",
        "category": "Freight & Shipping",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-003",
        "name": "CloudScale Infrastructure",
        "bank_account": "728192039182",
        "ifsc_code": "SBIN0001234",
        "category": "Data Center",
        "risk_rating": "MEDIUM",
        "status": "ACTIVE",
    },
    {
        "id": "VND-004",
        "name": "Apex Office Supplies",
        "bank_account": "619283019283",
        "ifsc_code": "KKBK0000789",
        "category": "Facilities",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-005",
        "name": "CyberShield Security",
        "bank_account": "519283910293",
        "ifsc_code": "UTIB0000321",
        "category": "Cybersecurity",
        "risk_rating": "HIGH",
        "status": "SUSPENDED",
    },
    {
        "id": "VND-006",
        "name": "Global Talent Solutions",
        "bank_account": "419283019201",
        "ifsc_code": "BARB0BOMBAY",
        "category": "Staffing",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-007",
        "name": "QuickCourier Services",
        "bank_account": "319203918203",
        "ifsc_code": "PUNB0000555",
        "category": "Logistics",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-008",
        "name": "Quantum Analytics Lab",
        "bank_account": "219203918204",
        "ifsc_code": "YESB0000111",
        "category": "AI Research",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-009",
        "name": "Delta Manufacturing Ltd",
        "bank_account": "119203918205",
        "ifsc_code": "CBIN0000999",
        "category": "Hardware",
        "risk_rating": "MEDIUM",
        "status": "ACTIVE",
    },
    {
        "id": "VND-010",
        "name": "FinEdge Advisory LLP",
        "bank_account": "998203918206",
        "ifsc_code": "IDFB0000888",
        "category": "Audit & Legal",
        "risk_rating": "LOW",
        "status": "ACTIVE",
    },
    {
        "id": "VND-011",
        "name": "Apex Global Freight",
        "bank_account": "771122334455",
        "ifsc_code": "KKBK0000111",
        "category": "Logistics",
        "risk_rating": "MEDIUM",
        "status": "PENDING_KYC",
    },
]

INVOICES_SEED = [
    {
        "id": "INV-1921",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 18500.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-991",
        "approved_by": "mgr_vikram",
        "issue_date": date(2026, 10, 1),
        "due_date": date(2026, 10, 20),
    },
    {
        "id": "INV-1922",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 42000.00,
        "currency": "INR",
        "status": "PENDING_APPROVAL",
        "po_number": "PO-992",
        "approved_by": None,
        "issue_date": date(2026, 10, 2),
        "due_date": date(2026, 10, 25),
    },
    {
        "id": "INV-404",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "amount": 9200.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-812",
        "approved_by": "mgr_anita",
        "issue_date": date(2026, 9, 28),
        "due_date": date(2026, 10, 18),
    },
    {
        "id": "INV-405",
        "vendor_id": "VND-002",
        "vendor_name": "XYZ Logistics India",
        "amount": 125000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-813",
        "approved_by": "dir_rajesh",
        "issue_date": date(2026, 10, 1),
        "due_date": date(2026, 11, 1),
    },
    {
        "id": "INV-881",
        "vendor_id": "VND-003",
        "vendor_name": "CloudScale Infrastructure",
        "amount": 64000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-701",
        "approved_by": "mgr_vikram",
        "issue_date": date(2026, 9, 25),
        "due_date": date(2026, 10, 15),
    },
    {
        "id": "INV-102",
        "vendor_id": "VND-004",
        "vendor_name": "Apex Office Supplies",
        "amount": 3400.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-409",
        "approved_by": "mgr_anita",
        "issue_date": date(2026, 10, 1),
        "due_date": date(2026, 10, 30),
    },
    {
        "id": "INV-771",
        "vendor_id": "VND-005",
        "vendor_name": "CyberShield Security",
        "amount": 50000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-550",
        "approved_by": "mgr_vikram",
        "issue_date": date(2026, 9, 20),
        "due_date": date(2026, 10, 10),
    },
    {
        "id": "INV-900",
        "vendor_id": "VND-006",
        "vendor_name": "Global Talent Solutions",
        "amount": 15000.00,
        "currency": "INR",
        "status": "DRAFT",
        "po_number": None,
        "approved_by": None,
        "issue_date": date(2026, 10, 3),
        "due_date": date(2026, 10, 28),
    },
    {
        "id": "INV-312",
        "vendor_id": "VND-007",
        "vendor_name": "QuickCourier Services",
        "amount": 1200.00,
        "currency": "INR",
        "status": "PAID",
        "po_number": "PO-301",
        "approved_by": "mgr_anita",
        "issue_date": date(2026, 9, 10),
        "due_date": date(2026, 9, 30),
    },
    {
        "id": "INV-660",
        "vendor_id": "VND-008",
        "vendor_name": "Quantum Analytics Lab",
        "amount": 28000.00,
        "currency": "INR",
        "status": "CANCELLED",
        "po_number": "PO-602",
        "approved_by": None,
        "issue_date": date(2026, 9, 15),
        "due_date": date(2026, 10, 5),
    },
    {
        "id": "INV-550",
        "vendor_id": "VND-001",
        "vendor_name": "ABC Technologies Pvt Ltd",
        "amount": 500.00,
        "currency": "USD",
        "status": "PENDING_APPROVAL",
        "po_number": "PO-995",
        "approved_by": None,
        "issue_date": date(2026, 10, 4),
        "due_date": date(2026, 10, 31),
    },
    {
        "id": "INV-711",
        "vendor_id": "VND-011",
        "vendor_name": "Apex Global Freight",
        "amount": 12000.00,
        "currency": "INR",
        "status": "APPROVED",
        "po_number": "PO-888",
        "approved_by": "mgr_vikram",
        "issue_date": date(2026, 10, 5),
        "due_date": date(2026, 10, 25),
    },
]

AGENTS_SEED = [
    {
        "id": "agent_fin_jr",
        "name": "Junior Finance Bot",
        "role": "JUNIOR_ASSISTANT",
        "department": "Accounts Payable",
        "single_txn_limit": 5000.00,
        "daily_budget_limit": 20000.00,
        "is_active": True,
    },
    {
        "id": "agent_fin_sr",
        "name": "Senior Payment Agent",
        "role": "FINANCE_OPERATOR",
        "department": "Treasury",
        "single_txn_limit": 25000.00,
        "daily_budget_limit": 100000.00,
        "is_active": True,
    },
    {
        "id": "agent_fin_mgr",
        "name": "Executive Finance Agent",
        "role": "FINANCE_MANAGER",
        "department": "Executive",
        "single_txn_limit": 250000.00,
        "daily_budget_limit": 1000000.00,
        "is_active": True,
    },
    {
        "id": "agent_ops_bot",
        "name": "General Operations Bot",
        "role": "OPS_BOT",
        "department": "Logistics",
        "single_txn_limit": 0.00,
        "daily_budget_limit": 0.00,
        "is_active": True,
    },
]

POLICIES_SEED = [
    {
        "id": "POL-FIN-001",
        "name": "High Value Payment Signoff",
        "description": "Any single payment exceeding ₹10,000 INR requires human managerial approval.",
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


def seed_database(verbose: bool = True) -> None:
    """Initializes tables and seeds all enterprise fixtures."""
    init_db()

    with get_session() as session:
        # Seed Vendors
        for item in VENDORS_SEED:
            existing = session.query(Vendor).filter(Vendor.id == item["id"]).first()
            if not existing:
                session.add(Vendor(**item))
            else:
                for k, v in item.items():
                    setattr(existing, k, v)

        # Seed Invoices
        for item in INVOICES_SEED:
            existing = session.query(Invoice).filter(Invoice.id == item["id"]).first()
            if not existing:
                session.add(Invoice(**item))
            else:
                for k, v in item.items():
                    setattr(existing, k, v)

        # Seed Agents
        for item in AGENTS_SEED:
            existing = session.query(AgentRegistry).filter(AgentRegistry.id == item["id"]).first()
            if not existing:
                session.add(AgentRegistry(**item))
            else:
                for k, v in item.items():
                    setattr(existing, k, v)

        # Seed Policies
        for item in POLICIES_SEED:
            existing = session.query(PolicyRule).filter(PolicyRule.id == item["id"]).first()
            if not existing:
                session.add(PolicyRule(**item))
            else:
                for k, v in item.items():
                    setattr(existing, k, v)

    if verbose:
        print("=" * 60)
        print("VERIACT Ground Truth Database Seeded Successfully:")
        print(f"  - Vendors:  {len(VENDORS_SEED)} seeded (VND-001 to VND-010)")
        print(f"  - Invoices: {len(INVOICES_SEED)} seeded (INV-1921 to INV-660)")
        print(f"  - Agents:   {len(AGENTS_SEED)} seeded (RBAC Profiles)")
        print(f"  - Policies: {len(POLICIES_SEED)} seeded (POL-FIN, POL-SEC, POL-DATA)")
        print("=" * 60)


if __name__ == "__main__":
    seed_database(verbose=True)
