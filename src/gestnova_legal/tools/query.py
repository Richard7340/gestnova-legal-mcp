"""Main legal-topic query tool (orchestrator)."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.tools.legislation import KNOWN_ELI
from gestnova_legal.types import DISCLAIMER

SECTOR_KEYWORDS: dict[str, list[str]] = {
    "laboral": ["despido", "vacaciones", "jornada", "contrato", "salario", "nomina", "permiso", "baja", "convenio"],
    "fiscal": ["impuesto", "iva", "irpf", "is", "hacienda", "tributario", "declaracion", "modelo"],
    "mercantil": ["sociedad", "estatutos", "junta", "administrador", "capital", "dividendo"],
    "proteccion_datos": ["gdpr", "rgpd", "lopd", "datos", "privacidad", "consentimiento", "dpo"],
    "compliance": ["blanqueo", "penal", "canal", "denuncias", "prevencion"],
}


def _detect_sector(question: str) -> str | None:
    q = question.lower()
    for sector, kws in SECTOR_KEYWORDS.items():
        if any(kw in q for kw in kws):
            return sector
    return None


class QueryLegalTopicTool(BaseTool):
    name = "queryLegalTopic"
    description = (
        "Consulta principal: dada una pregunta en lenguaje natural y jurisdiccion, "
        "busca en todos los packs, auto-detecta sector, y devuelve resultados "
        "con nivel de confianza y fuentes para verificacion."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "question": {"type": "string"},
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
            "sector": {"type": "string", "description": "Sector (auto-detectado si se omite)"},
        },
        "required": ["question", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        question = args["question"]
        country = args["jurisdiction"]
        sector = args.get("sector") or _detect_sector(question)
        on_date = date.today()
        lookup = get_lookup()

        words = question.lower().split()
        seen: set[str] = set()
        results: list[dict[str, Any]] = []
        for word in words:
            if len(word) < 3:
                continue
            for rule in lookup.search_by_keyword(country, word, on_date):
                if rule.rule not in seen:
                    seen.add(rule.rule)
                    results.append({
                        "rule": rule.rule,
                        "source": rule.source,
                        "effective_from": str(rule.effective_from),
                        "data_summary": str(rule.data)[:300],
                    })

        confianza = "alta" if len(results) >= 3 else ("media" if results else "baja")

        source_urls: list[str] = []
        if not results:
            if country == "ES":
                source_urls.append(f"https://www.boe.es/buscar/act.php?q={question}")
            elif country == "EU":
                source_urls.append(f"https://eur-lex.europa.eu/search.html?text={question}&locale=es")
            elif country == "MX":
                source_urls.append(f"https://www.diputados.gob.mx/LeyesBiblio/index.htm")

        return {
            "question": question,
            "jurisdiction": country,
            "sector_detected": sector,
            "results": results,
            "count": len(results),
            "confianza": confianza,
            "source_urls": source_urls,
            "disclaimer": DISCLAIMER,
        }
