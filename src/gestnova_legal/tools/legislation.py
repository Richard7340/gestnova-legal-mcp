"""Legislation tools: search, vigencia check, source URL builder."""
from datetime import date
from typing import Any

from gestnova_legal.engine.rule_lookup import NoRuleApplicable, get_lookup
from gestnova_legal.tools._base import BaseTool
from gestnova_legal.types import DISCLAIMER

ELI_BASE = "https://www.boe.es"
EURLEX_BASE = "https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=CELEX:"

KNOWN_ELI: dict[str, str] = {
    "ET": "/eli/es/rdlg/2015/10/23/2/con",
    "CC": "/eli/es/rd/1889/07/24/(1)/con",
    "CP": "/eli/es/lo/1995/11/23/10/con",
    "LGT": "/eli/es/l/2003/12/17/58/con",
    "LIRPF": "/eli/es/l/2006/11/28/35/con",
    "LIVA": "/eli/es/l/1992/12/28/37/con",
    "LIS": "/eli/es/l/2014/11/27/27/con",
    "LSC": "/eli/es/rdlg/2010/07/02/1/con",
    "LPAC": "/eli/es/l/2015/10/01/39/con",
    "LOPDGDD": "/eli/es/lo/2018/12/05/3/con",
    "LSE": "/eli/es/l/2013/12/26/24/con",
    "LRJS": "/eli/es/l/2011/10/10/36/con",
    "LGSS": "/eli/es/rdlg/2015/10/30/8/con",
}


class SearchLegislationTool(BaseTool):
    name = "searchLegislation"
    description = "Busca legislacion en packs por keyword, sector y jurisdiccion."
    input_schema = {
        "type": "object",
        "properties": {
            "keyword": {"type": "string"},
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
            "sector": {"type": "string"},
        },
        "required": ["keyword", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        keyword = args["keyword"]
        country = args["jurisdiction"]
        today = date.today()
        lookup = get_lookup()
        results = lookup.search_by_keyword(country, keyword, today)
        items = []
        for r in results:
            items.append({
                "rule": r.rule,
                "source": r.source,
                "effective_from": str(r.effective_from),
                "data_summary": _summarize(r.data),
            })
        return {
            "keyword": keyword,
            "jurisdiction": country,
            "results": items,
            "count": len(items),
            "disclaimer": DISCLAIMER,
        }


class CheckNormVigenciaTool(BaseTool):
    name = "checkNormVigencia"
    description = (
        "Verifica si una norma esta vigente, derogada o modificada segun los packs. "
        "Devuelve estado + fecha ultima modificacion + fuente URL para verificacion."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "norma": {"type": "string", "description": "Nombre o abreviatura (ej: 'ET', 'GDPR', 'LFT')"},
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
            "date": {"type": "string", "format": "date"},
        },
        "required": ["norma", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        norma = args["norma"]
        country = args["jurisdiction"]
        on_date = date.fromisoformat(args.get("date", date.today().isoformat()))
        lookup = get_lookup()
        kw = norma.lower()
        found = lookup.search_by_keyword(country, kw, on_date)
        if not found:
            return {
                "norma": norma, "jurisdiction": country, "found": False,
                "hint": "Norma no encontrada en packs. Use buildSourceUrl para obtener URL oficial.",
                "disclaimer": DISCLAIMER,
            }
        rule = found[0]
        return {
            "norma": norma, "jurisdiction": country, "found": True,
            "estado": "vigente" if rule.effective_until is None else "con_vigencia_limitada",
            "effective_from": str(rule.effective_from),
            "effective_until": str(rule.effective_until) if rule.effective_until else None,
            "source": rule.source, "disclaimer": DISCLAIMER,
        }


class BuildSourceUrlTool(BaseTool):
    name = "buildSourceUrl"
    description = (
        "Construye la URL oficial correcta para una norma: ELI (BOE consolidado), "
        "EUR-Lex (CELEX), DOF, CENDOJ. El agente usa esta URL con WebFetch."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "norma": {"type": "string"},
            "jurisdiction": {"type": "string", "enum": ["ES", "EU", "MX"]},
            "article": {"type": "string", "description": "Articulo especifico si aplica"},
        },
        "required": ["norma", "jurisdiction"],
    }

    async def execute(self, args: dict[str, Any]) -> dict[str, Any]:
        norma = args["norma"].upper()
        country = args["jurisdiction"]
        urls: list[str] = []
        if country == "ES":
            eli = KNOWN_ELI.get(norma)
            if eli:
                urls.append(f"{ELI_BASE}{eli}")
            else:
                urls.append(f"https://www.boe.es/buscar/act.php?id=&q={args['norma']}")
            urls.append(f"https://noticias.juridicas.com/buscar?q={args['norma']}")
        elif country == "EU":
            lookup = get_lookup()
            found = lookup.search_by_keyword("EU", args["norma"].lower(), date.today())
            for r in found:
                celex = r.data.get("celex")
                if celex:
                    urls.append(f"{EURLEX_BASE}{celex}")
            if not urls:
                urls.append(f"https://eur-lex.europa.eu/search.html?text={args['norma']}&locale=es")
        elif country == "MX":
            urls.append("https://www.diputados.gob.mx/LeyesBiblio/index.htm")
            urls.append(f"https://www.dof.gob.mx/busqueda_detalle.php?textobusqueda={args['norma']}")
        return {
            "norma": args["norma"], "jurisdiction": country,
            "source_urls": urls, "note": "Use WebFetch on these URLs to obtain verbatim text.",
        }


def _summarize(data: Any) -> str:
    if isinstance(data, dict):
        if "contenido" in data:
            return str(data["contenido"])[:200]
        if "nombre_comun" in data:
            return str(data["nombre_comun"])
    return str(data)[:150]
