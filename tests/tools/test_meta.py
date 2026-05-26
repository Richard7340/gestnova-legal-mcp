"""Tests for meta tools."""
import pytest

from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_ping():
    server = build_server()
    res = await server.call_tool("ping", {})
    assert res["status"] == "ok"
    assert "version" in res


@pytest.mark.asyncio
async def test_list_jurisdictions(lookup):
    server = build_server()
    res = await server.call_tool("listJurisdictions", {})
    assert "jurisdictions" in res
    assert isinstance(res["jurisdictions"], list)


@pytest.mark.asyncio
async def test_list_legal_sectors(lookup):
    server = build_server()
    res = await server.call_tool("listLegalSectors", {"jurisdiction": "ES"})
    assert res["jurisdiction"] == "ES"
    assert isinstance(res["sectors"], list)


@pytest.mark.asyncio
async def test_get_disclaimer():
    server = build_server()
    res = await server.call_tool("getDisclaimer", {})
    assert "orientativo" in res["disclaimer"]


@pytest.mark.asyncio
async def test_unknown_tool():
    server = build_server()
    with pytest.raises(ValueError, match="Unknown tool"):
        await server.call_tool("nonexistent", {})
