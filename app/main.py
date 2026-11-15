from pathlib import Path
import sys

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.contratos import cargar_catalogo_parcelas_nasa, CUATRO_LIMITES_CIENTIFICOS
from app.indicadores import explorar_indicadores
from app.recorrido import explorar
from app.torres import ficha_torres
from app.estilo import aplicar_estilo, linea
from app.seguimiento import panel
from app.portal_agricultor import mostrar_pacharota
from motor.configuracion import obtener_estrategias_configuradas
from motor.conector_motor import obtener_salida_motor

st.set_page_config(page_title="AYNOKA · Altiplano", layout="wide")
st.html("""<style>
[data-testid="stHeader"], [data-testid="stToolbar"] {display:none}
[data-testid="stMainBlockContainer"] {padding:0; max-width:none}
.st-key-mapa {position:fixed; inset:0; background:#eddbb9}
.st-key-mapa iframe {width:100%; height:100dvh!important; display:block}
/* Propagar el fondo activo de Streamlit hasta la ficha flotante. */
.stApp :has(.st-key-ficha), .stApp :has(.st-key-laboratorio) {background-color:inherit}
.st-key-ficha {position:fixed;right:1rem;top:1rem;bottom:1rem;width:min(38vw,485px)!important;min-width:310px;overflow:auto;padding:1.4rem;background-color:inherit;border:1px solid #ad9672;border-radius:18px;box-shadow:0 8px 40px #40362533;z-index:5}
.st-key-ficha:has(.st-key-lluvia) {bottom:auto;max-height:calc(100dvh - 2rem)}
@media(max-width:700px){.st-key-ficha{inset:auto 0 0;width:100%!important;min-width:0;height:52dvh;border-radius:18px 18px 0 0}.st-key-ficha:has(.st-key-lluvia){bottom:0;height:auto;max-height:52dvh}}
.st-key-laboratorio {position:fixed;inset:0;z-index:6;height:100dvh!important;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;background-color:inherit;padding:1rem max(1rem,3vw);color:inherit}
.st-key-laboratorio iframe {width:100%;box-sizing:content-box;max-width:calc(100% - 2px);border:1px solid #a99a78;border-radius:14px;display:block}
.st-key-ficha:has(.st-key-comparacion){width:min(760px,92vw)!important}
@media(max-width:700px){.st-key-ficha:has(.st-key-comparacion){width:100%!important;height:80dvh}}
</style>""")
aplicar_estilo()

def mostrar_campana(sitio, clima, clave):
    st.markdown(f"**{clima['ubicacion']}** · {clima['fecha_inicio']} a {clima['fecha_fin']}")
    lluvia, heladas = st.columns(2)
    lluvia.metric("Lluvia acumulada", f"{clima['precipitacion_total_mm']:.1f} mm")
    heladas.metric("Días con helada", clima["dias_helada"])
    columnas = {"PRECTOTCORR":"Lluvia (mm)", "T2M":"Temperatura media (°C)", "T2M_MIN":"Mínima (°C)",
                "T2M_MAX":"Máxima (°C)", "RH2M":"Humedad relativa (%)"}
    datos = pd.read_csv(ROOT/"datos_nasa/resultados/procesados/nasa_power_diario_dos_ubicaciones.csv",parse_dates=["fecha"])
    dias = datos.loc[(datos.parcela_id==sitio) & datos.fecha.between(clima["fecha_inicio"],clima["fecha_fin"])].set_index("fecha")[list(columnas)].rename(columns=columnas).sort_index()
    variable = st.selectbox("Ver evolución diaria", list(columnas.values()), key=clave)
    linea(dias[variable], y_label=variable)
    st.caption(f"NASA POWER · {len(dias)} días · Punto de referencia {clima['latitud']}°, {clima['longitud']}°")
    with st.expander("Ver tabla diaria y fuente original"):
        st.dataframe(dias.rename_axis("Fecha"),use_container_width=True)
        st.markdown(f"[Abrir respuesta técnica de NASA POWER (JSON)]({clima['url_consulta']})")

catalogo = cargar_catalogo_parcelas_nasa()
paradas = ["Rotaciones", "Estación climática", "Sensor de suelo", "Aplicación del agricultor"]
sitio_actual = st.session_state.get("sitio_actual", next(iter(catalogo)))
destino = next(k for k in catalogo if k != sitio_actual)
with st.container(key="mapa"):
    evento = explorar(catalogo[sitio_actual]["ubicacion"], st.session_state.get("estacion"), destino, catalogo[destino]["ubicacion"])

def cerrar():
    st.session_state.pop("estacion", None)

if isinstance(evento, dict) and evento.get("token") != st.session_state.get("ultima_visita"):
    if evento.get("tipo") == "viaje" and evento.get("destino") == destino:
        st.session_state["ultima_visita"] = evento["token"]
        st.session_state["sitio_actual"] = destino
        st.session_state.pop("localidad_ficha", None)
        cerrar()
        st.rerun()
if isinstance(evento, dict) and evento.get("name") in paradas and evento.get("token") != st.session_state.get("ultima_visita"):
    st.session_state["ultima_visita"] = evento["token"]
    st.session_state["estacion"] = evento["name"]
    st.rerun()

parada = st.session_state.get("estacion")
if parada in paradas:
    with st.container(key="laboratorio" if parada in ("Sensor de suelo","Aplicación del agricultor") else "ficha"):
        st.button("Volver al mapa", on_click=cerrar, key="volver_mapa")
        st.html("""<script>
        if (!window.__astraEscapeMapa) {
          window.__astraEscapeMapa = true;
          document.addEventListener('keydown', function (event) {
            if (event.key !== 'Escape') return;
            const volver = document.querySelector('.st-key-volver_mapa button');
            if (!volver) return;
            event.preventDefault();
            event.stopImmediatePropagation();
            volver.click();
          }, true);
        }
        </script>""", unsafe_allow_javascript=True)
        if parada != "Sensor de suelo":
            st.header(parada)
        if parada == "Aplicación del agricultor":
            mostrar_pacharota(sitio_actual, catalogo)
            st.stop()
        sitio = st.selectbox("Localidad de referencia", list(catalogo),
                             key="localidad_ficha", index=list(catalogo).index(sitio_actual),
                             format_func=lambda k: catalogo[k]["ubicacion"])
        if sitio != sitio_actual:
            st.session_state["sitio_actual"] = sitio
            st.rerun()
        clima = catalogo[sitio]
        if parada == "Rotaciones":
            st.caption(f"Paisaje ilustrativo · Punto de referencia {clima['latitud']}°, {clima['longitud']}° · Campaña del {clima['fecha_inicio']} al {clima['fecha_fin']}")
        if parada == "Sensor de suelo":
            ficha_torres(sitio, clima["ubicacion"])
            st.divider()
            st.subheader("Diseño del prototipo electrónico")
            st.write("Este diagrama elaborado por el equipo en Fritzing muestra un nodo transmisor con una Raspberry Pi Pico W, sensores ambientales y una sonda capacitiva de humedad del suelo, además de una central receptora. Algunas señales analógicas requieren conversión analógico-digital antes de que el microcontrolador procese los datos; el esquema representa esa etapa con módulos ADC.")
            st.image(str(ROOT / "referencias/prototipo_sensores_fritzing.jpeg"),
                     caption="Diseño de conexiones del prototipo: transmisor y central receptora. Imagen del equipo en Fritzing.",
                     use_container_width=True)
            st.caption("Es una referencia de diseño. Algunos sensores no cuentan con símbolo esquemático específico en Fritzing, por lo que sus conexiones se indican de forma ilustrativa. La simulación de esta página no acredita mediciones físicas ni valida por sí sola el cableado o la calibración del circuito.")
            for limite in CUATRO_LIMITES_CIENTIFICOS:
                with st.expander(limite["titulo"]):
                    st.write(limite["descripcion"])
        if parada == "Estación climática":
            st.caption(f"NASA POWER · Campaña del {clima['fecha_inicio']} al {clima['fecha_fin']}")
            with st.container(key="lluvia"):
                for campo, etiqueta, unidad in [
                    ("precipitacion_total_mm", "Lluvia acumulada", "mm"),
                    ("temperatura_media_c", "Temperatura media", "°C"),
                    ("dias_helada", "Días con heladas", "días"),
                ]:
                    valor = clima.get(campo)
                    st.metric(etiqueta, (f"{valor:.1f} {unidad}" if unidad != "días" else f"{valor:g} {unidad}") if valor is not None else "Sin dato")
            with st.expander("Ver campaña"):
                st.caption(f"Punto de referencia · {clima['latitud']}°, {clima['longitud']}°")
                serie = pd.read_csv(ROOT / "datos_nasa/resultados/procesados/nasa_power_diario_dos_ubicaciones.csv")
                serie = serie.loc[(serie.parcela_id == sitio) & serie.fecha.between(clima["fecha_inicio"], clima["fecha_fin"])].set_index("fecha")
                if not serie.empty:
                    linea(serie.T2M, y_label="Temperatura media diaria (°C)", color="#657946")
                st.markdown(f"[Consultar fuente NASA POWER]({clima['url_consulta']})")
        if parada == "Rotaciones":
            st.subheader("Rotaciones según tus prioridades")
            if sitio == "patacamaya_01":
                with st.expander("Ejemplo guiado · Patacamaya"):
                    st.write("Una familia quiere elegir una secuencia de tres años. ¿Elegiría la misma si su prioridad pasara de ahorrar agua a recuperar el suelo?")
                    st.write(f"En esta campaña NASA POWER registra {clima['precipitacion_total_mm']:.2f} mm de lluvia y {clima['dias_helada']} días con mínima bajo cero en el punto de referencia.")
                    if st.toggle("Consultar la campaña NASA POWER en AYNOKA"):
                        mostrar_campana(sitio, clima, "variable_ejemplo")
                    st.caption("Prueba los dos casos con el mismo clima. Cada botón da todo el peso a un criterio para que puedas ver su efecto en las tres secuencias de abajo.")
                    def aplicar_prioridad(criterio):
                        for k in ("agua", "suelo", "produccion"):
                            st.session_state["peso_"+k] = 100 if k == criterio else 0
                    st.button("1 · Priorizar agua", on_click=aplicar_prioridad, args=("agua",))
                    st.button("2 · Priorizar suelo", on_click=aplicar_prioridad, args=("suelo",))
                    st.caption("Los puntajes comparan estrategias según las reglas experimentales. El ahorro de agua y la recuperación del suelo aún requieren mediciones en parcela.")
            with st.expander("Explorar indicadores de la localidad", expanded=True):
                explorar_indicadores(sitio)
            columnas = st.columns(3)
            pesos = {}
            for columna, (clave, etiqueta, inicial) in zip(columnas, [
                ("agua", "Ahorrar agua", 45), ("suelo", "Recuperar el suelo", 35), ("produccion", "Favorecer la producción", 20)
            ]):
                if "peso_"+clave not in st.session_state:
                    st.session_state["peso_"+clave]=st.session_state.get("prioridades_guardadas", {}).get(clave, inicial)
                pesos[clave] = columna.slider(etiqueta, 0, 100, step=5, key="peso_"+clave)
            st.session_state.prioridades_guardadas = pesos.copy()
            st.caption("Comparación experimental · Los puntajes expresan el ajuste al modelo. La validación en campo está pendiente.")
            if not sum(pesos.values()):
                st.info("Asigna peso a una prioridad para comparar.")
            else:
                sensor = panel(sitio, seleccionar=True)
                base=obtener_salida_motor(sitio,prioridades=pesos,datos_nasa=clima,datos_sensor=None,incluir_aportes=True)
                salida=obtener_salida_motor(sitio,prioridades=pesos,datos_nasa=clima,datos_sensor=sensor,incluir_aportes=True) if sensor else base
                if sensor:
                    st.warning("Escenario experimental: NASA 2024–2025 como referencia histórica + humedad simulada posterior. No representa una campaña observada conjunta. Umbrales de humedad del motor pendientes de validación agronómica.")
                    tabla = [{"Rotación": r["id"], "Solo NASA": r["puntaje"], "NASA + sensores (experimental)": next(x["puntaje"] for x in salida["rotaciones"] if x["id"]==r["id"])} for r in base["rotaciones"]]
                    st.dataframe(tabla, hide_index=True, use_container_width=True)
                    st.write("Sugerencia experimental actualizada" if salida["recomendacion_id"] != base["recomendacion_id"] else "Las lecturas ajustan la evaluación; la rotación preferida se mantiene.")
                perfiles={e.id:e for e in obtener_estrategias_configuradas()}
                if not salida.get("recomendacion_id"):
                    st.info("Con los datos disponibles no se puede recomendar una rotación.")
                else:
                    orden = sorted(salida["rotaciones"], key=lambda r: (r["id"] != salida["recomendacion_id"], -r["puntaje"]))
                    etiquetas = {r["id"]: perfiles[r["id"]].nombre.split("(")[0].strip() for r in orden}
                    with st.container(key="comparacion"):
                        st.subheader("¿Qué aporta cada prioridad?")
                        grafico = go.Figure()
                        for clave, nombre, color in [("agua","Agua","#378da1"),("suelo","Suelo","#aa7542"),("produccion","Producción","#698b4a")]:
                            grafico.add_bar(name=nombre, y=[etiquetas[r["id"]] for r in orden],
                                            x=[salida["aportes"][r["id"]][clave] for r in orden],
                                            orientation="h", marker_color=color, hovertemplate="%{y}<br>"+nombre+": %{x:.1f} puntos<extra></extra>")
                        grafico.update_layout(template="plotly_white",paper_bgcolor="#f7f1e4",plot_bgcolor="#fffcf4",font=dict(color="#193e34"),barmode="stack",height=290,margin=dict(l=4,r=8,t=5,b=10),
                                              legend=dict(orientation="h"),xaxis=dict(range=[0,100],title="Puntos del modelo"),
                                              yaxis=dict(autorange="reversed",automargin=True))
                        st.plotly_chart(grafico,theme=None,use_container_width=True,config={"displayModeBar":False})
                        ganadora=orden[0]
                        st.success(f"Recomendación · {etiquetas[ganadora['id']]} · {ganadora['puntaje']}/100")
                        plan, evidencia = st.tabs(["Explorar plan trienal","Datos de la campaña"])
                        with plan:
                            rid=st.selectbox("Elegir secuencia", [r["id"] for r in orden],format_func=lambda k: etiquetas[k])
                            for indice, paso in enumerate(perfiles[rid].cultivos_secuencia, 1):
                                cultivo = paso.split(": ",1)[-1]
                                comun, _, cientifico = cultivo.partition(" (")
                                with st.container(border=True):
                                    st.caption(f"AÑO {indice} DE 3")
                                    st.markdown(f"**{comun}**")
                                    if cientifico:
                                        st.caption(cientifico.rstrip(")"))
                            fila=next(r for r in orden if r["id"]==rid)
                            aportes=salida["aportes"][rid]
                            etiquetas_criterio={"agua":"conservación de agua","suelo":"recuperación del suelo","produccion":"producción"}
                            principal=max(aportes,key=aportes.get)
                            st.metric("Ajuste a tus prioridades", f"{fila['puntaje']} / 100")
                            st.write(f"El mayor aporte viene de **{etiquetas_criterio[principal]}**: {aportes[principal]:.1f} puntos con los pesos elegidos.")
                            with st.expander("Cómo calculó el motor este resultado"):
                                for criterio, aporte in aportes.items():
                                    st.write(f"**{etiquetas_criterio[criterio].capitalize()}** · {aporte:.1f} puntos")
                                st.caption(fila["motivo"])
                        with evidencia:
                            mostrar_campana(sitio, clima, "variable_evidencia")
