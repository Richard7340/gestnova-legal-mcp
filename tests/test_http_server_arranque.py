"""El servidor tiene que ser alcanzable desde OTRO contenedor.

Escuchaba en 127.0.0.1, que dentro de un contenedor significa "solo yo mismo":
docker lo daria por arrancado y la plataforma no podria hablarle nunca. Y su
puerto por defecto era el 8015, el mismo que finance-modeler.

Se comprueba con QUE ARGUMENTOS arranca, no leyendo el texto del fuente: la
primera version de este test miraba el codigo con inspect y fallaba porque mis
propios comentarios mencionaban "127.0.0.1". Un test que lee comentarios no
prueba nada.
"""
import os

import pytest

from gestnova_legal import http_server


@pytest.fixture
def arranque(monkeypatch):
    visto = {}
    monkeypatch.setattr(
        http_server, "uvicorn",
        type("FalsoUvicorn", (), {"run": staticmethod(lambda app, **kw: visto.update(kw))})(),
    )
    return visto


def test_escucha_en_toda_la_red_del_contenedor(arranque, monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    http_server.main()
    assert arranque["host"] == "0.0.0.0"


def test_el_puerto_por_defecto_no_pisa_a_finance_modeler(arranque, monkeypatch):
    monkeypatch.delenv("PORT", raising=False)
    http_server.main()
    assert arranque["port"] == 8019, "8015 ya es de finance-modeler"


def test_el_puerto_se_puede_declarar(arranque, monkeypatch):
    monkeypatch.setenv("PORT", "9100")
    http_server.main()
    assert arranque["port"] == 9100
