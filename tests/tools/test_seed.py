"""Tests for the seed legal content tool."""
from pathlib import Path
from unittest.mock import patch

import pytest
from gestnova_legal.server import build_server
from gestnova_legal.engine.rule_lookup import reset_lookup


@pytest.mark.asyncio
async def test_seed_creates_pack(tmp_path):
    """Seed tool writes YAML and resets lookup."""
    fake_packs = tmp_path / "packs"
    fake_packs.mkdir()

    # The seed tool computes packs_root as:
    #   Path(__file__).resolve().parent.parent.parent.parent / "packs"
    # We need __file__ to resolve so that .parent^4 / "packs" == fake_packs
    fake_file = fake_packs / "a" / "b" / "c" / "seed.py"
    fake_file.parent.mkdir(parents=True, exist_ok=True)
    fake_file.touch()

    import gestnova_legal.tools.seed as seed_mod
    with patch.object(seed_mod, "__file__", str(fake_file)):
        server = build_server()
        entries = [
            {
                "rule": "test_rule_seed",
                "country": "ES",
                "effective_from": "2026-01-01",
                "effective_until": None,
                "source": "Test source",
                "data": {"titulo": "Test rule", "contenido": "Test content"},
            }
        ]
        res = await server.call_tool("seedLegalContent", {
            "jurisdiction": "ES",
            "sector": "test_sector",
            "entries": entries,
        })

    assert res["entries_added"] == 1
    assert res["total_entries"] == 1
    assert "written" in res

    written = Path(res["written"])
    assert written.exists()
    reset_lookup()
