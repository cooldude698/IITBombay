"""Ground Truth Verification Script for VERIACT Enterprise Mock Database.

Validates that all 10 vendors, 10 invoices, 4 agents, and 5 policies exist with correct values.
"""

import sys
import argparse
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.mock_env.db import (
    get_invoice,
    get_vendor,
    get_agent,
    get_policies,
    get_all_invoices,
    get_all_vendors,
)


def verify_all_seeds() -> bool:
    print("\n🔍 Running VERIACT Ground Truth Integrity Audit...")
    errors = []

    # 1. Verify Invoices
    expected_invoices = {
        "INV-1921": {"amount": 18500.0, "vendor_id": "VND-001", "status": "APPROVED"},
        "INV-1922": {"amount": 42000.0, "vendor_id": "VND-001", "status": "PENDING_APPROVAL"},
        "INV-404": {"amount": 9200.0, "vendor_id": "VND-002", "status": "APPROVED"},
        "INV-405": {"amount": 125000.0, "vendor_id": "VND-002", "status": "APPROVED"},
        "INV-881": {"amount": 64000.0, "vendor_id": "VND-003", "status": "APPROVED"},
        "INV-102": {"amount": 3400.0, "vendor_id": "VND-004", "status": "APPROVED"},
        "INV-771": {"amount": 50000.0, "vendor_id": "VND-005", "status": "APPROVED"},
        "INV-900": {"amount": 15000.0, "vendor_id": "VND-006", "status": "DRAFT"},
        "INV-312": {"amount": 1200.0, "vendor_id": "VND-007", "status": "PAID"},
        "INV-660": {"amount": 28000.0, "vendor_id": "VND-008", "status": "CANCELLED"},
        "INV-550": {"amount": 500.0, "vendor_id": "VND-001", "status": "PENDING_APPROVAL"},
        "INV-711": {"amount": 12000.0, "vendor_id": "VND-011", "status": "APPROVED"},
    }

    invoices = get_all_invoices()
    if len(invoices) != len(expected_invoices):
        errors.append(f"Expected {len(expected_invoices)} invoices, found {len(invoices)}")

    for inv_id, expected in expected_invoices.items():
        inv = get_invoice(inv_id)
        if not inv:
            errors.append(f"Missing invoice {inv_id}")
            continue
        if inv["amount"] != expected["amount"]:
            errors.append(f"{inv_id}: Expected amount {expected['amount']}, got {inv['amount']}")
        if inv["vendor_id"] != expected["vendor_id"]:
            errors.append(f"{inv_id}: Expected vendor {expected['vendor_id']}, got {inv['vendor_id']}")
        if inv["status"] != expected["status"]:
            errors.append(f"{inv_id}: Expected status {expected['status']}, got {inv['status']}")

    # 2. Verify Vendors
    expected_vendors = [
        ("VND-001", "ACTIVE", "LOW"),
        ("VND-002", "ACTIVE", "LOW"),
        ("VND-003", "ACTIVE", "MEDIUM"),
        ("VND-004", "ACTIVE", "LOW"),
        ("VND-005", "SUSPENDED", "HIGH"),
        ("VND-006", "ACTIVE", "LOW"),
        ("VND-007", "ACTIVE", "LOW"),
        ("VND-008", "ACTIVE", "LOW"),
        ("VND-009", "ACTIVE", "MEDIUM"),
        ("VND-010", "ACTIVE", "LOW"),
        ("VND-011", "PENDING_KYC", "MEDIUM"),
    ]

    vendors = get_all_vendors()
    if len(vendors) != len(expected_vendors):
        errors.append(f"Expected {len(expected_vendors)} vendors, found {len(vendors)}")

    for vnd_id, expected_status, expected_risk in expected_vendors:
        vnd = get_vendor(vnd_id)
        if not vnd:
            errors.append(f"Missing vendor {vnd_id}")
            continue
        if vnd["status"] != expected_status:
            errors.append(f"{vnd_id}: Expected status {expected_status}, got {vnd['status']}")
        if vnd["risk_rating"] != expected_risk:
            errors.append(f"{vnd_id}: Expected risk rating {expected_risk}, got {vnd['risk_rating']}")

    # 3. Verify Agents
    expected_agents = ["agent_fin_jr", "agent_fin_sr", "agent_fin_mgr", "agent_ops_bot"]
    for agt_id in expected_agents:
        agt = get_agent(agt_id)
        if not agt:
            errors.append(f"Missing agent {agt_id}")

    # 4. Verify Policies
    policies = get_policies()
    if len(policies) < 5:
        errors.append(f"Expected at least 5 policies, found {len(policies)}")

    if errors:
        print("❌ Verification Failed with errors:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("✅ All Ground Truth Fixtures Verified Successfully!")
    print(f"  - Invoices checked: {len(invoices)}/10 matching")
    print(f"  - Vendors checked:  {len(vendors)}/10 matching")
    print(f"  - Agents checked:   {len(expected_agents)}/4 matching")
    print(f"  - Policies checked: {len(policies)}/5 matching")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify VERIACT Ground Truth Seed Data")
    parser.add_argument("--all", action="store_true", help="Run complete audit across all tables")
    args = parser.parse_args()

    success = verify_all_seeds()
    sys.exit(0 if success else 1)
