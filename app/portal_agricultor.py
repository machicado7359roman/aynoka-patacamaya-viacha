"""Entrega móvil y guía de alta. La cuenta se crea en el portal ASTABLES."""
import json
import os
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st
from app.cuentas_demo import mostrar_cuentas_demo
import streamlit.components.v1 as components

from motor.configuracion import obtener_estrategias_configuradas
from motor.conector_motor import obtener_salida_motor

ASSETS = Path(__file__).resolve().parents[1] / "pacharota"


def version_movil(sitio, catalogo, prioridades):
    if not sum(prioridades.values()):
        prioridades = dict(agua=45, suelo=35, produccion=20)
    estrategias = {e.id: e for e in obtener_estrategias_configuradas()}
    datos = {"inicial": sitio, "regiones": {}, "catalogo_rudy_27":
             json.loads((ASSETS / "cultivos.json").read_text(encoding="utf8"))}
    for key, clima in catalogo.items():
        casos = {}
        for opcion, pesos in [("agua", prioridades), ("suelo", dict(agua=0,suelo=100,produccion=0)),
                               ("produccion", dict(agua=0,suelo=0,produccion=100))]:
            salida = obtener_salida_motor(key, prioridades=pesos, datos_nasa=clima, datos_sensor=None)
            filas = salida["rotaciones"]
            ganador = next((r for r in filas if r["id"] == salida.get("recomendacion_id")), None)
            if ganador is None:
                raise ValueError("Para preparar la descarga, asigna peso a una prioridad en Rotaciones.")
            estrategia = estrategias[ganador["id"]]
            casos[opcion] = dict(id=ganador["id"], nombre=estrategia.nombre, puntaje=ganador["puntaje"],
                                 pasos=estrategia.cultivos_secuencia, motivo=ganador["motivo"],
                                 pesos=[pesos[k] for k in ("agua","suelo","produccion")],
                                 alternativas=[f"{estrategias[r['id']].nombre} · {r['puntaje']}/100"
                                               for r in filas if r != ganador])
        datos["regiones"][key] = dict(nombre=clima["ubicacion"], casos=casos,
            periodo=f"{clima['fecha_inicio']} — {clima['fecha_fin']}", lluvia=clima["precipitacion_total_mm"],
            heladas=clima["dias_helada"], fuente=clima["url_consulta"])
    return (ASSETS / "movil.html").read_text(encoding="utf8").replace(
        "__ASTRA_DB__", json.dumps(datos, ensure_ascii=True).replace("<", r"\u003c"))


def mostrar_pacharota(sitio, catalogo):
    portal = os.environ.get("ASTRA_PORTAL_CUENTAS", "").strip()
    pesos = st.session_state.get("prioridades_guardadas", dict(agua=45,suelo=35,produccion=20))
    guia, telefono = st.columns([1, 1.15], gap="large")
    with guia:
        st.subheader("Tu cuenta ASTABLES")
        if urlsplit(portal).scheme in {"https", "http"} and urlsplit(portal).hostname:
            st.write("Crea tu cuenta en el portal ASTABLES y verifica tu correo para iniciar sesión.")
            st.link_button("Abrir portal de cuentas", portal)
        else:
            mostrar_cuentas_demo()
        st.subheader("Lleva PachaRota a tu parcela")
        st.write("Abre el archivo en GitHub y pulsa **Download raw** para guardar el APK. "
                 "Después podrás instalarlo en tu teléfono Android.")
        try:
            app = version_movil(sitio, catalogo, pesos)
        except ValueError as exc:
            st.warning(str(exc))
            return
        st.link_button(
            "Ver APK en GitHub",
            "https://github.com/machicado7359roman/astra-altiplano-demo/blob/"
            "main/descargas/PachaRota-1.3-prueba.apk",
            type="primary",
        )
    with telefono:
        # La vista y el archivo descargado usan exactamente el mismo documento.
        components.html(f"""<style>*{{box-sizing:border-box}}body{{margin:0}}
        .phone{{margin:4px auto;width:min(414px,98%);height:min(824px,200vw);background:#172921;
        border:6px solid #23382e;border-radius:34px;padding:11px 5px 12px;box-shadow:0 3px 8px #0004}}
        .speaker{{width:48px;height:4px;background:#799183;margin:0 auto 8px;border-radius:8px}}
        iframe{{width:100%;height:calc(100% - 14px);border:0;border-radius:20px}}</style>
        <div class="phone"><div class="speaker"></div><iframe sandbox="allow-scripts" title="Pantalla inicial de PachaRota"
        srcdoc="{escape(app, quote=True)}"></iframe></div>""", height=836)
        st.caption("Vista previa de PachaRota · Puedes probarla aquí.")


