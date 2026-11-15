"""Historial experimental por torre. Solo transmisiones nuevas; sin mezclar parcelas."""
from datetime import datetime
from statistics import median
import json
import streamlit as st
import plotly.graph_objects as go
from aprendizaje.aprendiz import AprendizContinuo

MINIMO = 6
INTERVALO = 15 * 60

def incorporar(historial, modelos, torres):
    for torre in torres:
        dato = torre.get("lectura")
        if not dato or not torre.get("zona") or dato["edad"] > 15:
            continue
        clave = torre["zona"] + ":" + torre["id"] + ":" + str(torre["direccion"]) + ":" + str(dato.get("geometria"))
        fecha = datetime.fromisoformat(dato["fecha"])
        if fecha.utcoffset() is None:
            # Reloj del laboratorio: hora simulada de Bolivia.
            fecha = datetime.fromisoformat(dato["fecha"] + "-04:00")
        filas = historial.setdefault(clave, [])
        if filas and (fecha - datetime.fromisoformat(filas[-1]["fecha"])).total_seconds() < INTERVALO:
            continue
        modelo = modelos.setdefault(clave, AprendizContinuo())
        evento = {"flujo_id": clave[:120], "origen": "simulacion", "timestamp": fecha.isoformat(),
                  "valores": {"VWC_25CM": dato["pct"] / 100}, "unidades": {"VWC_25CM": "m3/m3"}}
        resultado = modelo.procesar(evento)
        filas.append({"fecha": fecha.isoformat(), "humedad_pct": dato["pct"], "estado": resultado["estado"],
                      "inusual": resultado["es_inusual"], "origen": "simulacion"})

def consolidar(filas):
    recientes = filas[-MINIMO:]
    if len(recientes) < MINIMO or any(f["inusual"] for f in recientes):
        return None
    fechas = [datetime.fromisoformat(f["fecha"]) for f in recientes]
    if (fechas[-1]-fechas[0]).total_seconds() < INTERVALO * (MINIMO-1):
        return None
    if (fechas[-1]-fechas[0]).total_seconds() > 86400:
        return None
    return {"origen": "simulado", "humedad_suelo_pct": median(f["humedad_pct"] for f in recientes)}

def registrar_red(torres):
    historial = st.session_state.setdefault("historial_torres", {})
    modelos = st.session_state.setdefault("modelos_torres", {})
    incorporar(historial, modelos, torres)

def panel(zona, seleccionar=False):
    historial = st.session_state.get("historial_torres", {})
    claves = [k for k in historial if k.startswith(zona+":") and historial[k]]
    st.subheader("Seguimiento de la parcela")
    st.caption("Experimento con transmisiones simuladas · 6 tomas separadas por al menos 15 minutos, dentro de 24 horas. Regla operativa de demostración.")
    if not claves:
        st.info("Transmite una lectura en el laboratorio y pulsa Aplicar red a ASTRA para comenzar.")
        return None
    clave = st.selectbox("Torre para esta comparación", claves, format_func=lambda k:k.split(":")[1], key="torre_seguimiento_"+str(seleccionar)+zona)
    filas = historial[clave]
    st.progress(min(len(filas), MINIMO)/MINIMO, text=f"{min(len(filas), MINIMO)} de {MINIMO} tomas para comparar")
    grafico = go.Figure(go.Scatter(x=[f["fecha"] for f in filas[-30:]], y=[f["humedad_pct"] for f in filas[-30:]], mode="lines+markers", line=dict(color="#32755a", width=3), name="Humedad a 25 cm"))
    grafico.update_layout(template="plotly_white", paper_bgcolor="#f7f1e4", plot_bgcolor="#fffcf4", font=dict(color="#193e34"), margin=dict(l=20,r=20,t=15,b=30), height=250, yaxis_title="Humedad (% vol.)", xaxis_title="Fecha de la toma simulada")
    st.plotly_chart(grafico, theme=None, use_container_width=True, key="historial_grafico_"+str(seleccionar)+zona)
    st.caption("Última toma simulada: "+filas[-1]["fecha"])
    modelo = st.session_state["modelos_torres"][clave]
    st.write(f"Aprendizaje de patrones: {len(filas)} observaciones · {filas[-1]['estado'].replace('_',' ')}")
    st.caption("El detector aprende humedad a 25 cm por torre. Comienza a clasificar desde la observación 351; mientras tanto, la comparación usa la regla experimental de seis tomas.")
    sensor = consolidar(filas)
    # La red activa debe seguir teniendo una lectura reciente del mismo nodo.
    vigentes = [t for t in st.session_state.get("red_torres", []) if t["zona"]==zona and t["id"]==clave.split(":")[1] and t.get("lectura") and t["zona"]+":"+t["id"]+":"+str(t["direccion"])+":"+str(t["lectura"].get("geometria"))==clave and t["lectura"]["edad"]<=15]
    if not vigentes:
        sensor = None
    if sensor:
        st.success(f"Mediana de las últimas 6 tomas: {sensor['humedad_suelo_pct']:.1f} % vol. Lista para comparar.")
    else:
        st.info("Se conserva la comparación NASA: falta evidencia reciente suficiente o hay una lectura inusual pendiente de revisión.")
    st.download_button("Descargar historial de esta torre", json.dumps(filas,ensure_ascii=False,indent=2), "historial_simulado.json", "application/json",key="descarga_historial_"+str(seleccionar)+zona)
    st.caption("Historial y aprendizaje conservados durante esta sesión del navegador. Descarga el historial antes de cerrarla.")
    return sensor
