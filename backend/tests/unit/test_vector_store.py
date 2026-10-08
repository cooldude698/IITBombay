"""Unit tests for In-Memory Policy Vector Store & Semantic Retrieval."""

import pytest
from app.engine.retrieval.vector_store import default_vector_store, PolicyVectorStore


def test_vector_store_retrieval_payment_threshold():
    """Query about payment thresholds retrieves Clause 4.2."""
    results = default_vector_store.search("payment threshold dual control approval 10000", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc["doc_id"] == "SOP-PROC-4.2"
    assert top_doc["similarity_score"] > 0.0


def test_vector_store_retrieval_prompt_defense():
    """Query about adversarial prompt injection retrieves Clause 9.1."""
    results = default_vector_store.search("adversarial prompt injection quarantine payload", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc["doc_id"] == "SOP-SEC-9.1"
    assert top_doc["similarity_score"] > 0.0


def test_vector_store_retrieval_suspended_vendor():
    """Query about suspended vendor blacklist retrieves Clause 3.4."""
    results = default_vector_store.search("suspended vendor blacklist sanctions kyc", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc["doc_id"] == "SOP-VND-3.4"
    assert top_doc["similarity_score"] > 0.0


def test_vector_store_retrieval_rbac_caps():
    """Query about role caps and destructive actions retrieves Clause 2.1."""
    results = default_vector_store.search("junior assistant operator limit drop table", top_k=2)
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc["doc_id"] == "SOP-RBAC-2.1"
    assert top_doc["similarity_score"] > 0.0


def test_vector_store_empty_query():
    """Empty query gracefully returns top documents without error."""
    results = default_vector_store.search("", top_k=3)
    assert len(results) == 3
