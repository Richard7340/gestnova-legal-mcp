"""Tests for knowledge store — Pydantic validation layer."""
import pytest
from gestnova_legal.types import ConsultaContent, NormaContent, JurisprudenciaContent
from datetime import date


def test_consulta_content_validates():
    c = ConsultaContent(
        pregunta="Cuantos dias de vacaciones?",
        respuesta="30 dias naturales segun ET art. 38.",
        jurisdiccion="ES",
        sector="laboral",
        confianza="alta",
        normas_consultadas=["ET art. 38"],
        fuentes_verificadas=["https://boe.es/eli/es/rdlg/2015/10/23/2/con"],
    )
    assert c.jurisdiccion == "ES"


def test_consulta_content_rejects_bad_jurisdiction():
    with pytest.raises(Exception):
        ConsultaContent(
            pregunta="Test", respuesta="Test", jurisdiccion="FR",
            sector="laboral", confianza="alta",
            normas_consultadas=[], fuentes_verificadas=[],
        )


def test_norma_content_validates():
    n = NormaContent(
        norma="RDLeg 2/2015", nombre_comun="Estatuto de los Trabajadores",
        abreviatura="ET", tipo="real_decreto_legislativo", estado="vigente",
        fecha_publicacion=date(2015, 10, 24),
        fuente_url="https://boe.es/eli/es/rdlg/2015/10/23/2/con",
        texto_verbatim="Articulo 38. Vacaciones anuales...",
    )
    assert n.abreviatura == "ET"


def test_jurisprudencia_content_validates():
    j = JurisprudenciaContent(
        tribunal="TS", ecli="ECLI:ES:TS:2025:1234",
        fecha_sentencia=date(2025, 3, 15), tema="despido_improcedente",
        doctrina_fijada="Doctrina test", normas_interpretadas=["ET art. 56"],
        divergencia=True,
    )
    assert j.divergencia is True


def test_consulta_content_rejects_bad_confianza():
    with pytest.raises(Exception):
        ConsultaContent(
            pregunta="Test", respuesta="Test", jurisdiccion="ES",
            sector="laboral", confianza="muy_alta",
            normas_consultadas=[], fuentes_verificadas=[],
        )
