"""Unit tests for Ground Truth Explorer API Endpoints (Task VEDESH-404)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_ground_truth_invoices_endpoint():
    """GET /api/v1/ground-truth/invoices returns verified ERP invoice master list."""
    response = client.get("/api/v1/ground-truth/invoices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10
    # Verify primary keys and schema presence
    first_invoice = data[0]
    assert "invoice_id" in first_invoice or "id" in first_invoice
    assert "vendor_name" in first_invoice
    assert "amount" in first_invoice or "approved_amount" in first_invoice
    assert "status" in first_invoice


def test_get_ground_truth_vendors_endpoint():
    """GET /api/v1/ground-truth/vendors returns verified ERP vendor directory."""
    response = client.get("/api/v1/ground-truth/vendors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10
    first_vendor = data[0]
    assert "vendor_id" in first_vendor or "id" in first_vendor
    assert "name" in first_vendor
    assert "bank_account" in first_vendor
    assert "status" in first_vendor
