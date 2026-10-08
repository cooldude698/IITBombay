"""SQLAlchemy ORM models for VERIACT Controlled Enterprise Mock ERP and Audit Store."""

from datetime import datetime, date
import json
from typing import Any, Dict, Optional
from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Integer,
    Text,
    DateTime,
    Date,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    bank_account = Column(String(64), nullable=False)
    ifsc_code = Column(String(32), nullable=False)
    category = Column(String(64), nullable=False, default="General")
    risk_rating = Column(String(16), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH
    status = Column(String(32), nullable=False, default="ACTIVE")  # ACTIVE, SUSPENDED, PENDING_KYC
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="vendor", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vendor_id": self.id,
            "name": self.name,
            "bank_account": self.bank_account,
            "ifsc_code": self.ifsc_code,
            "ifsc": self.ifsc_code,
            "category": self.category,
            "risk_rating": self.risk_rating,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(64), primary_key=True)  # e.g. 'INV-1921'
    vendor_id = Column(String(64), ForeignKey("vendors.id"), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="INR")
    status = Column(String(32), nullable=False)  # DRAFT, PENDING_APPROVAL, APPROVED, PAID, CANCELLED
    po_number = Column(String(64), nullable=True)
    approved_by = Column(String(64), nullable=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="invoices")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "invoice_id": self.id,
            "vendor_id": self.vendor_id,
            "vendor_name": self.vendor_name,
            "amount": float(self.amount),
            "approved_amount": float(self.amount),
            "currency": self.currency,
            "status": self.status,
            "po_number": self.po_number,
            "approved_by": self.approved_by,
            "issue_date": str(self.issue_date),
            "due_date": str(self.due_date),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AgentRegistry(Base):
    __tablename__ = "agents"

    id = Column(String(64), primary_key=True)  # e.g. 'agent_fin_jr'
    name = Column(String(255), nullable=False)
    role = Column(String(64), nullable=False)  # JUNIOR_ASSISTANT, FINANCE_OPERATOR, FINANCE_MANAGER, OPS_BOT
    department = Column(String(64), nullable=False)
    daily_budget_limit = Column(Float, nullable=False, default=50000.00)
    single_txn_limit = Column(Float, nullable=False, default=10000.00)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        allowed_map = {
            "JUNIOR_ASSISTANT": ["read_invoice", "check_status"],
            "FINANCE_OPERATOR": ["read_invoice", "make_payment", "check_status"],
            "FINANCE_MANAGER": ["*"],
            "OPS_BOT": ["read_status", "send_notification"],
        }
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "daily_budget_limit": float(self.daily_budget_limit),
            "single_txn_limit": float(self.single_txn_limit),
            "single_limit": float(self.single_txn_limit),
            "allowed": allowed_map.get(self.role, ["read_invoice"]),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Alias Agent to AgentRegistry for developer convenience
Agent = AgentRegistry


class PolicyRule(Base):
    __tablename__ = "policies"

    id = Column(String(64), primary_key=True)  # e.g. 'POL-FIN-001'
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    condition_expression = Column(Text, nullable=False)
    action_type = Column(String(64), nullable=False)  # FINANCIAL, DATA_MUTATION, etc.
    enforcement_action = Column(String(32), nullable=False)  # BLOCK, ESCALATE, REQUIRE_MFA
    priority = Column(Integer, nullable=False, default=10)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "condition_expression": self.condition_expression,
            "action_type": self.action_type,
            "enforcement_action": self.enforcement_action,
            "priority": self.priority,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Alias Policy to PolicyRule
Policy = PolicyRule


class ActionTraceModel(Base):
    __tablename__ = "action_traces"

    id = Column(String(64), primary_key=True)  # e.g. 'trc_482910'
    action_id = Column(String(64), nullable=False)
    agent_id = Column(String(64), nullable=False)
    tool_name = Column(String(64), nullable=False)
    action_type = Column(String(64), nullable=False)
    target_entity = Column(String(255), nullable=False)
    proposed_params = Column(JSON, nullable=False)
    retrieved_evidence = Column(JSON, nullable=True)
    mismatches = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=False)
    verification_tier = Column(String(16), nullable=False)
    verdict = Column(String(16), nullable=False)
    reason = Column(Text, nullable=False)
    latency_ms = Column(Integer, nullable=False)
    payload_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_id": self.action_id,
            "agent_id": self.agent_id,
            "tool_name": self.tool_name,
            "action_type": self.action_type,
            "target_entity": self.target_entity,
            "proposed_params": self.proposed_params,
            "retrieved_evidence": self.retrieved_evidence,
            "mismatches": self.mismatches,
            "risk_score": float(self.risk_score),
            "verification_tier": self.verification_tier,
            "verdict": self.verdict,
            "reason": self.reason,
            "latency_ms": self.latency_ms,
            "payload_hash": self.payload_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EscalationQueueItem(Base):
    __tablename__ = "escalation_queue"

    id = Column(String(64), primary_key=True)  # e.g. 'esc_991823'
    trace_id = Column(String(64), nullable=False)
    agent_id = Column(String(64), nullable=False)
    action_type = Column(String(64), nullable=False)
    risk_score = Column(Float, nullable=False)
    details = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED
    reviewed_by = Column(String(64), nullable=True)
    review_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "agent_id": self.agent_id,
            "action_type": self.action_type,
            "risk_score": float(self.risk_score),
            "details": self.details,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "review_notes": self.review_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class BenchmarkScenarioModel(Base):
    __tablename__ = "benchmark_scenarios"

    id = Column(String(64), primary_key=True)  # e.g. 'SC-042'
    category = Column(String(64), nullable=False)
    user_request = Column(Text, nullable=False)
    proposed_tool = Column(String(64), nullable=False)
    proposed_params = Column(JSON, nullable=False)
    ground_truth_evidence = Column(JSON, nullable=False)
    expected_verdict = Column(String(16), nullable=False)
    difficulty = Column(String(16), nullable=False, default="MEDIUM")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "user_request": self.user_request,
            "proposed_tool": self.proposed_tool,
            "proposed_params": self.proposed_params,
            "ground_truth_evidence": self.ground_truth_evidence,
            "expected_verdict": self.expected_verdict,
            "difficulty": self.difficulty,
        }
