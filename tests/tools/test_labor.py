"""Tests for labor analysis tool."""
import pytest
from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_labor_despido_es():
    server = build_server()
    res = await server.call_tool("analyzeLaborRelation", {"topic": "despido", "jurisdiction": "ES"})
    assert res["found"] is True
    assert any("despido" in r["rule"] for r in res["results"])
    assert "rules_applied" in res
    assert "disclaimer" in res


@pytest.mark.asyncio
async def test_labor_vacaciones_es():
    server = build_server()
    res = await server.call_tool("analyzeLaborRelation", {"topic": "vacaciones", "jurisdiction": "ES"})
    assert res["found"] is True
    assert any("vacaciones" in r["rule"] for r in res["results"])


@pytest.mark.asyncio
async def test_labor_vacaciones_mx():
    server = build_server()
    res = await server.call_tool("analyzeLaborRelation", {"topic": "vacaciones", "jurisdiction": "MX"})
    assert res["found"] is True
    assert any("vacaciones" in r["rule"] for r in res["results"])


@pytest.mark.asyncio
async def test_labor_unknown_topic():
    server = build_server()
    res = await server.call_tool("analyzeLaborRelation", {"topic": "xyznonexistent", "jurisdiction": "ES"})
    assert res["found"] is False
    assert "hint" in res
