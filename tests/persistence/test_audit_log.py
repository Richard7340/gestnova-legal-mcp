"""Tests for audit log — structure validation (no DB)."""
import json


def test_audit_entry_structure():
    entry = {
        "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
        "tool_name": "queryLegalTopic",
        "input_args": {"question": "vacaciones", "jurisdiction": "ES"},
        "confianza": "alta",
    }
    serialized = json.dumps(entry, default=str)
    parsed = json.loads(serialized)
    assert parsed["tool_name"] == "queryLegalTopic"
    assert parsed["confianza"] == "alta"
