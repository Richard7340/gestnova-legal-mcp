"""Meta tools: jurisdiction listing, sector listing, disclaimer."""
from typing import Any

from gestnova_legal.engine.rule_lookup import get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.types import DISCLAIMER


class ListJurisdictionsTool(BaseTool):
    name = "listJurisdictions"
    description = "List supported jurisdictions and their coverage in packs."
    input_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        lookup = get_lookup()
        countries = lookup.supported_countries()
        coverage: dict[str, Any] = {}
        for c in countries:
            rules = [k for (cc, k) in lookup._rules if cc == c]
            coverage[c] = {"rule_count": len(rules), "rules": sorted(set(rules))}
        return {"jurisdictions": countries, "coverage": coverage}


class ListLegalSectorsTool(BaseTool):
    name = "listLegalSectors"
    description = "List legal sectors with available packs per jurisdiction."
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
        },
        "required": ["jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        lookup = get_lookup()
        country = args["jurisdiction"]
        sectors: set[str] = set()
        for (c, k) in lookup._rules:
            if c == country:
                parts = k.split("_")
                if len(parts) >= 2:
                    sectors.add(parts[0])
        return {"jurisdiction": country, "sectors": sorted(sectors)}


class GetDisclaimerTool(BaseTool):
    name = "getDisclaimer"
    description = "Return the mandatory legal disclaimer text."
    input_schema: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        return {"disclaimer": DISCLAIMER}
