"""Componente local del recorrido, servido por Streamlit incluso sin Internet."""
from pathlib import Path

from streamlit.components.v1 import declare_component

_recorrido = declare_component("recorrido_altiplano", path=str(Path(__file__).resolve().parents[1] / "mundo"))


def explorar(localidad, parada, destino_id, destino_nombre):
    return _recorrido(localidad=localidad, parada=parada, destino_id=destino_id, destino_nombre=destino_nombre, key="mundo_altiplano", default=None)
