"""Labor-relation analysis tool."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.types import DISCLAIMER


class AnalyzeLaborRelationTool(BaseTool):
    name = "analyzeLaborRelation"
    description = (
        "Analiza un tema laboral (despido, vacaciones, jornada, etc.) "
        "buscando reglas labor_* en los packs de la jurisdiccion indicada."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "description": "Tema laboral: despido, vacaciones, jornada..."},
            "jurisdiction": {"type": "string", "enum": ["ES", "MX"]},
            "date": {"type": "string", "format": "date"},
        },
        "required": ["topic", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        topic = args["topic"].lower()
        country = args["jurisdiction"]
        on_date = date.fromisoformat(args.get("date", date.today().isoformat()))
        lookup = get_lookup()
        candidates = lookup.get_all_for_area(country, "labor_", on_date)
        matched = [
            r for r in candidates
            if topic in r.rule.lower() or topic in str(r.data).lower()
        ]
        if not matched:
            return {
                "topic": topic,
                "jurisdiction": country,
                "found": False,
                "hint": f"No labor rules matching '{topic}' in {country} packs.",
                "disclaimer": DISCLAIMER,
            }
        items = []
        for r in matched:
            items.append({
                "rule": r.rule,
                "source": r.source,
                "effective_from": str(r.effective_from),
                "data": r.data,
            })
        return {
            "topic": topic,
            "jurisdiction": country,
            "found": True,
            "results": items,
            "rules_applied": [
                {"rule": r.rule, "effective_from": str(r.effective_from), "source": r.source}
                for r in matched
            ],
            "disclaimer": DISCLAIMER,
        }
