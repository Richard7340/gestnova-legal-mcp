"""Seed legal content tool — writes YAML pack files."""
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gestnova_legal.engine.rule_lookup import reset_lookup
from gestnova_legal.tools._base import BaseTool


class SeedLegalContentTool(BaseTool):
    name = "seedLegalContent"
    description = (
        "Crea o actualiza un pack YAML con reglas legales. "
        "Util para inyectar conocimiento juridico nuevo en el sistema."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
            "sector": {"type": "string", "description": "Sector: laboral, fiscal, mercantil..."},
            "entries": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rule": {"type": "string"},
                        "country": {"type": "string"},
                        "effective_from": {"type": "string", "format": "date"},
                        "effective_until": {"type": ["string", "null"], "format": "date"},
                        "source": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["rule", "country", "effective_from", "source", "data"],
                },
                "description": "Array of rule entries to write.",
            },
        },
        "required": ["jurisdiction", "sector", "entries"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        jurisdiction = args["jurisdiction"].lower()
        sector = args["sector"]
        entries = args["entries"]

        packs_root = Path(__file__).resolve().parent.parent.parent.parent / "packs"
        target_dir = packs_root / jurisdiction / sector
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "seed.yaml"

        yaml = YAML()
        yaml.default_flow_style = False

        existing: list[dict] = []
        if target_file.exists():
            loaded = yaml.load(target_file.read_text(encoding="utf-8"))
            if loaded:
                existing = list(loaded)

        existing.extend(entries)

        with open(target_file, "w", encoding="utf-8") as f:
            yaml.dump(existing, f)

        reset_lookup()

        return {
            "written": str(target_file),
            "entries_added": len(entries),
            "total_entries": len(existing),
        }
