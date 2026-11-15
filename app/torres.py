"""Lecturas del simulador por región. Las vistas previas no representan recepciones."""
import json
import math
from uuid import uuid4
from streamlit.components.v1 import declare_component
from hashlib import sha256
from pathlib import Path

import streamlit as st
from app.seguimiento import registrar_red, panel

ROOT = Path(__file__).resolve().parents[1]
laboratorio = declare_component("adquisicion_astra", path=str(ROOT / "adquisicion"))
ZONAS = {"patacamaya_01", "viacha_01"}


def leer_red(raw):
    if len(raw) > 2_000_000:
        raise ValueError("El archivo supera 2 MB.")
    red = json.loads(raw)
    if not isinstance(red, dict) or red.get("schema") != "farmastra.adquisicion/1.1" or red.get("source") != "SIMULACION":
        raise ValueError("Selecciona el JSON de toda la red de Adquisición 1.1.")
    filas = red.get("stations")
    if not isinstance(filas, list) or not 1 <= len(filas) <= 12 or red.get("station_count") != len(filas):
        raise ValueError("La lista de estaciones no coincide con el número declarado.")
    torres = []
    ids = set()
    for fila in filas:
        if not isinstance(fila, dict):
            raise ValueError("Registro de torre inválido.")
        nodo, zona = fila.get("id"), fila.get("zona_id")
        if not isinstance(nodo, str) or not nodo or nodo in ids or (zona is not None and zona not in ZONAS):
            raise ValueError("Revisa el identificador y la zona de cada torre.")
        ids.add(nodo)
        torre = dict(id=nodo, zona=zona, lugar=fila.get("location") or "Ubicación pendiente",
                     direccion=fila.get("configured_address"), ip=fila.get("simulated_ipv4") or "—",
                     enlace=fila.get("link_available"), lectura=None, aviso="Sin paquete válido recibido.")
        torres.append(torre)
        paquete = fila.get("last_valid_received")
        if paquete is None:
            continue
        try:
            h = paquete["header"]
            origen = h["station"]
            if h["sources"] != ["SIMULACION"] or origen["id"] != nodo:
                raise ValueError("El origen del paquete no coincide con la torre.")
            if not zona or origen.get("zona_id") != zona:
                torre["aviso"] = "Pendiente de un paquete transmitido con la zona actual."
                continue
            dia = h["end"]
            v = paquete["properties"]["parameter"]["VWC_25CM"][dia]
            edad = fila["age_minutes"]
            if (paquete["parameters"]["VWC_25CM"]["units"] != "m3/m3" or type(v) not in (int,float)
                    or not 0 <= v <= 1 or type(edad) not in (int,float) or not math.isfinite(edad) or edad < 0):
                raise ValueError("Unidad, valor de humedad o antigüedad inválidos.")
            torre["lectura"] = dict(pct=v*100, fecha=fila["last_received_at_simulated"],
                                    edad=edad, direccion=origen.get("address"), lugar=origen.get("location"),
                                    geometria=paquete.get("geometry"))
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("El paquete recibido está incompleto.") from exc
    return torres


@st.cache_data
def simulador_portatil():
    carpeta = ROOT / "adquisicion"
    html = (carpeta/"index.html").read_text(encoding="utf8")
    css = (carpeta/"styles.css").read_text(encoding="utf8")
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+css+'</style>')
    for archivo in ("model.js","app.js"):
        codigo = (carpeta/archivo).read_text(encoding="utf8")
        html = html.replace(f'<script src="{archivo}"></script>', '<script>'+codigo+'</script>')
    return html.encode("utf8")


def ficha_torres(zona, nombre):
    st.caption("Adquisición · Telemetría simulada · "+nombre)
    if "red_torres" not in st.session_state:
        st.session_state.red_torres = leer_red((ROOT/"adquisicion/demo.json").read_bytes())
        st.session_state.nombre_red = "Ejemplo de demostración"
    clave = st.session_state.setdefault("sesion_laboratorio", uuid4().hex)
    evento = laboratorio(zona=zona, nombre=nombre, sesion=clave, confirmacion=st.session_state.get("confirmacion_red", ""), key="laboratorio_interactivo", default=None)
    if isinstance(evento, dict) and evento.get("token") != st.session_state.get("ultimo_envio_lab"):
        try:
            red_activa = leer_red(json.dumps(evento["red"]).encode())
        except (ValueError, TypeError, KeyError) as exc:
            st.session_state.confirmacion_red = f"No se pudo aplicar: {exc}"
            st.session_state.ultimo_envio_lab = evento.get("token")
            st.rerun()
        else:
            st.session_state.red_torres = red_activa
            st.session_state.nombre_red = "Laboratorio de Adquisición"
            antes = sum(len(f) for f in st.session_state.get("historial_torres", {}).values())
            registrar_red(red_activa)
            despues = sum(len(f) for f in st.session_state.get("historial_torres", {}).values())
            nuevas = despues - antes
            locales_hist = [len(f) for k,f in st.session_state.get("historial_torres", {}).items() if k.startswith(zona+":")]
            progreso = min(max(locales_hist, default=0), 6)
            st.session_state.confirmacion_red = (
                f"Red recibida por ASTRA. {nuevas} toma(s) nueva(s). Progreso regional: {progreso}/6. "
                + ("Puedes abrir Rotaciones para consultar la comparación." if progreso >= 6 else "Avanza +15 min, transmite la torre y vuelve a aplicar.")
                + (" La misma transmisión no cuenta otra vez; revisa también zona, enlace y antigüedad." if nuevas == 0 else "")
            )
            st.session_state.ultimo_envio_lab = evento["token"]
            st.rerun()
    st.subheader("Lecturas recibidas · "+nombre)
    with st.expander("Importar archivo o descargar el simulador") :
        st.write("En el simulador, elige la zona de cada torre, transmite y descarga el JSON de toda la red.")
        st.download_button("Descargar simulador para abrir en el navegador",simulador_portatil(),
                           "Adquisicion-ASTRA.html","text/html")
        archivo = st.file_uploader("Importar JSON de la red",type="json")
        if archivo:
            raw = archivo.getvalue()
            firma = sha256(raw).hexdigest()
            if firma != st.session_state.get("firma_red"):
                try:
                    torres = leer_red(raw)
                except (ValueError, UnicodeError, RecursionError) as exc:
                    st.error(f"Archivo rechazado. Sigue activa la red anterior. {exc}")
                else:
                    st.session_state.red_torres = torres
                    st.session_state.nombre_red = archivo.name
                    st.session_state.firma_red = firma
                    registrar_red(torres)
    red = st.session_state.red_torres
    st.caption("Red activa: "+st.session_state.nombre_red)
    pendientes = sum(t["zona"] is None for t in red)
    if pendientes:
        st.caption(f"Torres sin zona en la red: {pendientes}. Asigna la zona en el simulador para mostrarlas en el mapa.")
    locales = [t for t in red if t["zona"] == zona]
    if not locales:
        st.info("Sin torres asignadas a "+nombre+".")
    for t in locales:
        with st.container(border=True):
            st.subheader(t["id"])
            st.text(str(t["lugar"]))
            st.caption(f"Dirección {t['direccion']} · IP simulada {t['ip']}")
            if t["enlace"] is False:
                st.warning("Enlace interrumpido en el momento de exportar.")
            dato = t["lectura"]
            if dato is None:
                st.info(t["aviso"])
                continue
            st.metric("Humedad del suelo a 25 cm", f"{dato['pct']:.1f} % vol.")
            st.caption(f"Recepción simulada {dato['fecha']} · {dato['edad']:g} min antes de la exportación · Dirección de origen {dato['direccion']}")
            if dato["edad"] > 15:
                st.warning("Lectura antigua al exportar (más de 15 minutos).")
            with st.expander("Ubicación de la última lectura"):
                st.text(str(dato["lugar"] or "Referencia pendiente"))
                if dato["geometria"]:
                    st.json(dato["geometria"])

    panel(zona)
