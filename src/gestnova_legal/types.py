"""Shared Pydantic types for the legal engine."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field

Country = Literal["ES", "EU", "MX"]
Confidence = Literal["alta", "media", "baja"]

DISCLAIMER = (
    "Esta informacion tiene caracter orientativo. "
    "Para decisiones con implicaciones legales significativas, "
    "consulte con un profesional colegiado."
)


class LegalRef(BaseModel):
    norma: str
    jurisdiccion: Country
    estado: str
    fuente_url: Optional[str] = None
    effective_from: date
    effective_until: Optional[date] = None
    source: str


class CaseLawRef(BaseModel):
    tribunal: str
    ecli: Optional[str] = None
    numero_recurso: Optional[str] = None
    fecha: date
    doctrina: str
    divergencia: bool = False
    tribunales_divergentes: list[str] = Field(default_factory=list)


class LegalResult(BaseModel):
    rules_applied: list[LegalRef] = Field(default_factory=list)
    case_law: list[CaseLawRef] = Field(default_factory=list)
    confianza: Confidence = "media"
    disclaimer: str = DISCLAIMER
    warnings: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)


class ConsultaContent(BaseModel):
    pregunta: str
    respuesta: str
    jurisdiccion: Country
    sector: str
    confianza: Confidence
    normas_consultadas: list[str]
    fuentes_verificadas: list[str]


class NormaContent(BaseModel):
    norma: str
    nombre_comun: str
    abreviatura: Optional[str] = None
    tipo: str
    estado: str
    fecha_publicacion: date
    ultima_modificacion: Optional[date] = None
    fuente_url: str
    texto_verbatim: Optional[str] = None
    articulos_relevantes: list[str] = Field(default_factory=list)


class JurisprudenciaContent(BaseModel):
    tribunal: str
    ecli: Optional[str] = None
    fecha_sentencia: date
    tema: str
    doctrina_fijada: str
    normas_interpretadas: list[str]
    divergencia: bool = False
