"""Main legal-topic query tool (orchestrator)."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.tools.legislation import KNOWN_ELI
from gestnova_legal.types import DISCLAIMER

SECTOR_KEYWORDS: dict[str, list[str]] = {
    "laboral": ["despido", "vacaciones", "jornada", "contrato laboral", "salario", "nomina", "permiso", "baja", "convenio", "trabajador", "empleado", "ERE", "ERTE"],
    "fiscal": ["impuesto", "iva", "irpf", "is", "hacienda", "tributario", "declaracion", "modelo", "factura", "retencion"],
    "mercantil": ["sociedad", "estatutos", "junta", "administrador", "capital", "dividendo", "disolucion"],
    "proteccion_datos": ["gdpr", "rgpd", "lopd", "datos", "privacidad", "consentimiento", "dpo", "cookies"],
    "compliance": ["blanqueo", "penal", "canal", "denuncias", "prevencion"],
    "energetico": ["solar", "fotovoltaic", "renovable", "electrica", "autoconsumo", "generacion", "eolica", "bateria", "BESS"],
    "inmobiliario": ["alquiler", "arrendamiento", "vivienda", "compraventa", "hipoteca", "fianza", "inquilino"],
    "tecnologico": ["software", "saas", "ia ", "inteligencia artificial", "digital", "plataforma", "app"],
    "contratos": ["clausula", "nda", "confidencialidad", "contrato obra", "arrendamiento", "servicios"],
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
        learning_instructions: dict[str, Any] | None = None

        if confianza == "baja":
            if country == "ES":
                source_urls = [
                    f"https://www.boe.es/buscar/act.php?q={question}",
                    "https://noticias.juridicas.com",
                    "https://www.poderjudicial.es/search/",
                ]
            elif country == "EU":
                source_urls = [
                    f"https://eur-lex.europa.eu/search.html?text={question}&locale=es",
                    "https://curia.europa.eu",
                ]
            elif country == "MX":
                source_urls = [
                    "https://www.diputados.gob.mx/LeyesBiblio/index.htm",
                    f"https://www.dof.gob.mx/busqueda_detalle.php?textobusqueda={question}",
                ]

            learning_instructions = {
                "action": "El agente DEBE buscar en las source_urls usando WebSearch/WebFetch",
                "steps": [
                    "1. Busca en las URLs proporcionadas usando WebSearch o WebFetch",
                    "2. Lee el texto de la norma relevante — extrae artículos verbatim",
                    "3. Identifica: nombre norma, abreviatura, artículos, estado vigencia",
                    f"4. Llama seedLegalContent con jurisdiction='{country}', sector='{sector or 'general'}' y los datos encontrados",
                    "5. Responde al usuario con citación verbatim + disclaimer",
                ],
                "seed_template": {
                    "tool": "seedLegalContent",
                    "args": {
                        "jurisdiction": country,
                        "sector": sector or "general",
                        "entries": [
                            {
                                "norma": "(nombre completo de la norma encontrada)",
                                "abreviatura": "(abreviatura si existe)",
                                "tipo": "(ley|real_decreto|reglamento|directiva|...)",
                                "estado": "vigente",
                                "fuente_url": "(URL exacta de donde se leyó)",
                                "texto_verbatim": "(texto literal del artículo relevante)",
                                "articulos": ["(lista de artículos consultados)"],
                            }
                        ],
                    },
                },
            }
        elif confianza == "media":
            if country == "ES":
                source_urls.append(f"https://www.boe.es/buscar/act.php?q={question}")
            elif country == "EU":
                source_urls.append(f"https://eur-lex.europa.eu/search.html?text={question}&locale=es")

        return {
            "question": question,
            "jurisdiction": country,
            "sector_detected": sector,
            "results": results,
            "count": len(results),
            "confianza": confianza,
            "source_urls": source_urls,
            "learning_instructions": learning_instructions,
            "disclaimer": DISCLAIMER,
        }
