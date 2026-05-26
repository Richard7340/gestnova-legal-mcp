"""Tests for legislation tools."""
import pytest
from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_search_legislation_vacaciones():
    server = build_server()
    res = await server.call_tool("searchLegislation", {"keyword": "vacaciones", "jurisdiction": "ES"})
    assert res["count"] >= 1
    assert any("vacaciones" in r["rule"] for r in res["results"])
    assert "disclaimer" in res


@pytest.mark.asyncio
async def test_search_legislation_gdpr():
    server = build_server()
    res = await server.call_tool("searchLegislation", {"keyword": "gdpr", "jurisdiction": "EU"})
    assert res["count"] >= 1


@pytest.mark.asyncio
async def test_check_vigencia_found():
    server = build_server()
    res = await server.call_tool("checkNormVigencia", {"norma": "vacaciones", "jurisdiction": "ES"})
    assert res["found"] is True
    assert res["estado"] == "vigente"


@pytest.mark.asyncio
async def test_check_vigencia_not_found():
    server = build_server()
    res = await server.call_tool("checkNormVigencia", {"norma": "ley_inexistente", "jurisdiction": "ES"})
    assert res["found"] is False


@pytest.mark.asyncio
async def test_build_source_url_es():
    server = build_server()
    res = await server.call_tool("buildSourceUrl", {"norma": "ET", "jurisdiction": "ES"})
    assert any("boe.es" in u for u in res["source_urls"])


@pytest.mark.asyncio
async def test_build_source_url_eu():
    server = build_server()
    res = await server.call_tool("buildSourceUrl", {"norma": "GDPR", "jurisdiction": "EU"})
    assert any("eur-lex" in u for u in res["source_urls"])
