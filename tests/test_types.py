"""Tests for Pydantic types validation."""
from datetime import date

import pytest
from gestnova_legal.types import (
    DISCLAIMER,
    CaseLawRef,
    ConsultaContent,
    JurisprudenciaContent,
    LegalRef,
    LegalResult,
    NormaContent,
)


def test_legal_ref_required_fields():
    ref = LegalRef(
        norma="ET art. 56",
        jurisdiccion="ES",
        estado="vigente",
        effective_from=date(2015, 10, 24),
        source="BOE RDLeg 2/2015",
    )
    assert ref.norma == "ET art. 56"
    assert ref.fuente_url is None


def test_legal_ref_rejects_invalid_country():
    with pytest.raises(Exception):
        LegalRef(
            norma="X",
            jurisdiccion="FR",
            estado="vigente",
            effective_from=date(2020, 1, 1),
            source="test",
        )


def test_case_law_ref_defaults():
    ref = CaseLawRef(
        tribunal="TS",
        fecha=date(2025, 3, 15),
        doctrina="Test doctrine",
    )
    assert ref.divergencia is False
    assert ref.tribunales_divergentes == []


def test_legal_result_includes_disclaimer():
    result = LegalResult()
    assert result.disclaimer == DISCLAIMER
    assert result.confianza == "media"


def test_consulta_content_validates():
    c = ConsultaContent(
        pregunta="Test?",
        respuesta="Answer.",
        jurisdiccion="ES",
        sector="laboral",
        confianza="alta",
        normas_consultadas=["ET art. 14"],
        fuentes_verificadas=["https://boe.es/eli/..."],
    )
    assert c.jurisdiccion == "ES"


def test_norma_content_optional_fields():
    n = NormaContent(
        norma="RDLeg 2/2015",
        nombre_comun="Estatuto Trabajadores",
        tipo="real_decreto_legislativo",
        estado="vigente",
        fecha_publicacion=date(2015, 10, 24),
        fuente_url="https://www.boe.es/eli/es/rdlg/2015/10/23/2/con",
    )
    assert n.abreviatura is None
    assert n.texto_verbatim is None


def test_jurisprudencia_content():
    j = JurisprudenciaContent(
        tribunal="TS",
        fecha_sentencia=date(2025, 3, 15),
        tema="despido_improcedente",
        doctrina_fijada="Test doctrine",
        normas_interpretadas=["ET art. 56"],
    )
    assert j.divergencia is False


def test_confidence_rejects_invalid():
    with pytest.raises(Exception):
        LegalResult(confianza="muy_alta")
