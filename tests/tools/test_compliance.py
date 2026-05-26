"""Tests for compliance tools."""
import pytest
from gestnova_legal.server import build_server


@pytest.mark.asyncio
async def test_legal_requirements_es_small():
    server = build_server()
    res = await server.call_tool("getLegalRequirements", {"country": "ES", "sector": "consultoria", "workers": 5})
    docs = res["applicable_documents"]
    assert "lopd-rgpd" in docs
    assert "prl-basico" in docs
    assert "plan-igualdad" not in docs


@pytest.mark.asyncio
async def test_legal_requirements_es_50plus():
    server = build_server()
    res = await server.call_tool("getLegalRequirements", {"country": "ES", "sector": "comercio", "workers": 60})
    docs = res["applicable_documents"]
    assert "plan-igualdad" in docs
    assert "canal-denuncias" in docs


@pytest.mark.asyncio
async def test_legal_requirements_es_regulated_sector():
    server = build_server()
    res = await server.call_tool("getLegalRequirements", {"country": "ES", "sector": "financiero", "workers": 10})
    docs = res["applicable_documents"]
    assert "compliance-penal" in docs


@pytest.mark.asyncio
async def test_legal_requirements_mx():
    server = build_server()
    res = await server.call_tool("getLegalRequirements", {"country": "MX", "sector": "servicios", "workers": 3})
    docs = res["applicable_documents"]
    assert "aviso-privacidad" in docs


@pytest.mark.asyncio
async def test_legal_template_laboral():
    server = build_server()
    res = await server.call_tool("getLegalTemplate", {"country": "ES", "template_type": "laboral"})
    assert "clausulas_obligatorias" in res.get("template", {})


@pytest.mark.asyncio
async def test_legal_template_not_found():
    server = build_server()
    res = await server.call_tool("getLegalTemplate", {"country": "ES", "template_type": "inexistente"})
    assert res.get("error") == "template_not_found"
