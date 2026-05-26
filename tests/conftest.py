"""Shared pytest fixtures."""
from datetime import date
from pathlib import Path

import pytest

from gestnova_legal.engine.rule_lookup import init_lookup, reset_lookup


@pytest.fixture
def today() -> date:
    return date(2026, 5, 15)


@pytest.fixture
def sample_pack_dir(tmp_path: Path) -> Path:
    es = tmp_path / "packs" / "es"
    (es / "compliance").mkdir(parents=True)
    (es / "laboral").mkdir(parents=True)

    (es / "compliance" / "applicability.yaml").write_text(
        """\
- rule: legal_compliance_requirements
  country: ES
  effective_from: 2026-01-01
  effective_until: null
  source: "RGPD 2016/679 + LOPDGDD 3/2018 + Ley 31/1995 PRL"
  data:
    rules:
      - if:
          workers_min: 1
        always_required:
          - lopd-rgpd
          - prl-basico
          - registro-horario
        reason: "RGPD + PRL + Registro horario (RDL 8/2019)."
      - if:
          workers_min: 50
        adds:
          - plan-igualdad
          - canal-denuncias
        reason: "Plan Igualdad (RD 901/2020). Canal denuncias (Ley 2/2023)."
      - if:
          workers_min: 250
        adds:
          - compliance-penal
        reason: "Art. 31 bis CP."
""",
        encoding="utf-8",
    )

    (es / "laboral" / "basics.yaml").write_text(
        """\
- rule: labor_vacaciones
  country: ES
  effective_from: 2026-01-01
  effective_until: null
  source: "ET art. 38 (RDLeg 2/2015)"
  data:
    articulo: "38"
    norma: "Estatuto de los Trabajadores"
    abreviatura: "ET"
    eli: "/eli/es/rdlg/2015/10/23/2/con"
    contenido: "30 dias naturales de vacaciones anuales retribuidas."
    detalles:
      - "No sustituibles por compensacion economica"
      - "Periodo disfrute pactado en convenio colectivo"
      - "Derecho proporcional al tiempo trabajado"
- rule: labor_periodo_prueba
  country: ES
  effective_from: 2026-01-01
  effective_until: null
  source: "ET art. 14 (RDLeg 2/2015)"
  data:
    articulo: "14"
    norma: "Estatuto de los Trabajadores"
    abreviatura: "ET"
    eli: "/eli/es/rdlg/2015/10/23/2/con"
    contenido: "Duracion maxima segun convenio. Limites legales: 6 meses tecnicos titulados, 2 meses demas."
    detalles:
      - "Resolucion libre por cualquier parte durante el periodo"
      - "Computa a efectos de antiguedad"
      - "Nulo si ya desempeno mismas funciones en la empresa"
""",
        encoding="utf-8",
    )

    eu = tmp_path / "packs" / "eu"
    eu.mkdir(parents=True)
    (eu / "regulations.yaml").write_text(
        """\
- rule: eu_regulation_gdpr
  country: EU
  effective_from: 2018-05-25
  effective_until: null
  source: "DOUE L 119/2016"
  data:
    norma: "Reglamento (UE) 2016/679"
    celex: "32016R0679"
    nombre_comun: "GDPR"
    eli: "http://data.europa.eu/eli/reg/2016/679/oj"
""",
        encoding="utf-8",
    )

    mx = tmp_path / "packs" / "mx"
    (mx / "laboral").mkdir(parents=True)
    (mx / "laboral" / "basics.yaml").write_text(
        """\
- rule: labor_vacaciones_mx
  country: MX
  effective_from: 2023-01-01
  effective_until: null
  source: "LFT art. 76 (reforma 2022)"
  data:
    articulo: "76"
    norma: "Ley Federal del Trabajo"
    abreviatura: "LFT"
    contenido: "12 dias de vacaciones el primer ano, incremento de 2 dias por ano hasta 20, luego 2 dias por cada 5 anos."
""",
        encoding="utf-8",
    )

    return tmp_path / "packs"


@pytest.fixture
def lookup(sample_pack_dir):
    lk = init_lookup(sample_pack_dir)
    yield lk
    reset_lookup()
