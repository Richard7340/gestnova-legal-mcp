"""Contract clause analysis tool."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.types import DISCLAIMER


class AnalyzeClauseTool(BaseTool):
    name = "analyzeClause"
    description = (
        "Dado un tipo de contrato (laboral, mercantil, arrendamiento...) "
        "devuelve checklist de clausulas obligatorias y recomendadas."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "contract_type": {"type": "string", "description": "laboral, mercantil, arrendamiento..."},
            "jurisdiction": {"type": "string", "enum": ["ES", "MX"]},
            "date": {"type": "string", "format": "date"},
        },
        "required": ["contract_type", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        contract_type = args["contract_type"].lower()
        country = args["jurisdiction"]
        on_date = date.fromisoformat(args.get("date", date.today().isoformat()))
        lookup = get_lookup()
        candidates = lookup.get_all_for_area(country, "contract_checklist_", on_date)
        for rule in candidates:
            if rule.data.get("tipo_contrato", "").lower() == contract_type:
                return {
                    "contract_type": contract_type,
                    "jurisdiction": country,
                    "found": True,
                    "clausulas_obligatorias": rule.data.get("clausulas_obligatorias", []),
                    "clausulas_recomendadas": rule.data.get("clausulas_recomendadas", []),
                    "rules_applied": [
                        {"rule": rule.rule, "effective_from": str(rule.effective_from), "source": rule.source}
                    ],
                    "disclaimer": DISCLAIMER,
                }
        return {
            "contract_type": contract_type,
            "jurisdiction": country,
            "found": False,
            "hint": f"No contract checklist for '{contract_type}' in {country} packs.",
            "disclaimer": DISCLAIMER,
        }
