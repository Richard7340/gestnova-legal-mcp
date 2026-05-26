"""Smoke test: ensure build_server can list and call all registered tools."""
import pytest

from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_all_tools_callable():
    server = build_server()
    tools = await server.list_tools()
    assert len(tools) >= 4
    for tool in tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "input_schema")


@pytest.mark.asyncio
async def test_smoke_ping():
    server = build_server()
    res = await server.call_tool("ping", {})
    assert res["status"] == "ok"
