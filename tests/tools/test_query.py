"""Tests for the main query legal topic tool."""
import pytest
from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_query_vacaciones_es():
    server = build_server()
    res = await server.call_tool("queryLegalTopic", {"question": "vacaciones", "jurisdiction": "ES"})
    assert res["count"] >= 1
    assert res["confianza"] in ("alta", "media")
    assert res["sector_detected"] == "laboral"
    assert "disclaimer" in res


@pytest.mark.asyncio
async def test_query_gdpr_eu():
    server = build_server()
    res = await server.call_tool("queryLegalTopic", {"question": "gdpr proteccion datos", "jurisdiction": "EU"})
    assert res["count"] >= 1
    assert any("gdpr" in r["rule"].lower() for r in res["results"])


@pytest.mark.asyncio
async def test_query_unknown_returns_source_urls():
    server = build_server()
    res = await server.call_tool("queryLegalTopic", {"question": "xyznonexistent", "jurisdiction": "ES"})
    assert res["count"] == 0
    assert res["confianza"] == "baja"
    assert len(res["source_urls"]) > 0


@pytest.mark.asyncio
async def test_query_sector_autodetect():
    server = build_server()
    res = await server.call_tool("queryLegalTopic", {"question": "impuesto sobre sociedades", "jurisdiction": "ES"})
    assert res["sector_detected"] == "fiscal"
