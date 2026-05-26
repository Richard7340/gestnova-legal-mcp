"""Compliance tools: requirements by sector, legal templates."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import NoRuleApplicable, get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.types import DISCLAIMER


class GetLegalRequirementsTool(BaseTool):
    name = "getLegalRequirements"
    description = (
        "Dado pais + sector + headcount, devuelve requisitos legales obligatorios: "
        "licencias, registros, permisos, documentos de compliance."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "country": {"type": "string", "enum": ["ES", "MX"]},
            "sector": {"type": "string"},
            "workers": {"type": "integer"},
            "company_type": {"type": "string", "description": "SL, SA, autonomo, cooperativa..."},
        },
        "required": ["country", "sector", "workers"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        country = args["country"]
        sector = args["sector"]
        workers = int(args["workers"])
        today = date.today()
        lookup = get_lookup()
        try:
            rule = lookup.get(country, "legal_compliance_requirements", today)
        except NoRuleApplicable:
            return {"country": country, "error": "no_compliance_pack", "hint": f"No compliance pack for {country}.", "disclaimer": DISCLAIMER}
        applicable: list[str] = []
        reasoning: list[dict] = []
        for r in rule.data.get("rules", []):
            condition = r.get("if", {})
            if "workers_min" in condition and workers < condition["workers_min"]:
                continue
            if "sector_in" in condition and sector not in condition["sector_in"]:
                continue
            for doc in r.get("always_required", []) + r.get("adds", []):
                if doc not in applicable:
                    applicable.append(doc)
            reasoning.append({"matched": condition, "reason": r.get("reason", "")})
        return {
            "country": country, "sector": sector, "workers": workers,
            "applicable_documents": applicable, "reasoning": reasoning,
            "rules_applied": [{"rule": "legal_compliance_requirements", "effective_from": str(rule.effective_from), "source": rule.source}],
            "disclaimer": DISCLAIMER,
        }


class GetLegalTemplateTool(BaseTool):
    name = "getLegalTemplate"
    description = (
        "Obtiene plantilla de documento legal: politica privacidad, terminos servicio, "
        "NDA, contrato laboral. Con secciones obligatorias y base legal."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "country": {"type": "string", "enum": ["ES", "MX"]},
            "template_type": {"type": "string"},
            "date": {"type": "string", "format": "date"},
        },
        "required": ["country", "template_type"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        country = args["country"]
        template_type = args["template_type"]
        today = date.fromisoformat(args.get("date", date.today().isoformat()))
        lookup = get_lookup()
        candidates = lookup.get_all_for_area(country, "contract_checklist_", today)
        for rule in candidates:
            if rule.data.get("tipo_contrato") == template_type:
                return {
                    "country": country, "template_type": template_type, "template": rule.data,
                    "rules_applied": [{"rule": rule.rule, "effective_from": str(rule.effective_from), "source": rule.source}],
                    "disclaimer": DISCLAIMER,
                }
        return {"country": country, "template_type": template_type, "error": "template_not_found",
                "hint": f"No template for '{template_type}' in {country} packs.", "disclaimer": DISCLAIMER}
