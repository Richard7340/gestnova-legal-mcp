"""Donde estan los packs no puede depender de subir cuatro carpetas.

`get_lookup()` resolvia la carpeta de packs como
`Path(__file__).parent.parent.parent.parent / "packs"`, lo que solo es cierto
si el codigo corre desde el arbol del repo. Instalado en un contenedor
(`uv pip install --system .`), `__file__` cae en site-packages y esa cuenta de
cuatro niveles apunta a cualquier sitio menos a los packs: el servidor arranca,
responde /health, y devuelve CERO normas sin decir por que.

Con `LEGAL_PACKS_DIR` la ruta se declara, y si no existe se dice en voz alta.
"""
import os
from pathlib import Path

import pytest

from gestnova_legal.engine.rule_lookup import get_lookup, reset_lookup, packs_dir


@pytest.fixture(autouse=True)
def _limpia():
    reset_lookup()
    previo = os.environ.pop("LEGAL_PACKS_DIR", None)
    yield
    os.environ.pop("LEGAL_PACKS_DIR", None)
    if previo is not None:
        os.environ["LEGAL_PACKS_DIR"] = previo
    reset_lookup()


def test_sin_variable_usa_los_packs_del_repo():
    d = packs_dir()
    assert d.name == "packs"
    assert (d / "es").is_dir(), "los packs del repo deben seguir encontrandose"


def test_la_variable_manda(tmp_path):
    (tmp_path / "es").mkdir()
    os.environ["LEGAL_PACKS_DIR"] = str(tmp_path)
    assert packs_dir() == tmp_path


def test_una_ruta_que_no_existe_se_dice_no_se_traga(tmp_path):
    # Arrancar "bien" y devolver cero normas es el peor fallo posible aqui:
    # parece que no hay legislacion aplicable cuando lo que pasa es que no
    # encuentra el fichero.
    os.environ["LEGAL_PACKS_DIR"] = str(tmp_path / "no-existe")
    with pytest.raises(FileNotFoundError):
        packs_dir()


def test_el_lookup_usa_la_carpeta_declarada(tmp_path):
    (tmp_path / "es").mkdir()
    os.environ["LEGAL_PACKS_DIR"] = str(tmp_path)
    assert get_lookup().root == tmp_path
