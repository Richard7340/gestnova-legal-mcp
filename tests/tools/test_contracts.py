"""Tests for contract clause analysis tool."""
import pytest
from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_clause_laboral():
    server = build_server()
    res = await server.call_tool("analyzeClause", {"contract_type": "laboral", "jurisdiction": "ES"})
    assert res["found"] is True
    assert len(res["clausulas_obligatorias"]) > 0
    assert len(res["clausulas_recomendadas"]) > 0
    assert "rules_applied" in res
    assert "disclaimer" in res


@pytest.mark.asyncio
async def test_clause_mercantil():
    server = build_server()
    res = await server.call_tool("analyzeClause", {"contract_type": "mercantil", "jurisdiction": "ES"})
    assert res["found"] is True
    assert len(res["clausulas_obligatorias"]) > 0


@pytest.mark.asyncio
async def test_clause_unknown_type():
    server = build_server()
    res = await server.call_tool("analyzeClause", {"contract_type": "inexistente", "jurisdiction": "ES"})
    assert res["found"] is False
    assert "hint" in res
