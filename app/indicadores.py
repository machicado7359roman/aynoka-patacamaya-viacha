"""Explorador de las cinco familias del comprobador de Rudy."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

GRUPOS = {
    "Atmósfera y altitud": [
        ("Altitud de la celda","altitud_celda_msnm","m s. n. m."),
        ("Presión superficial","presion_superficial_ps_kpa","kPa"),
        ("Fracción relativa de gases estimada","fraccion_oxigeno_co2_relativa_nivel_mar_pct","%"),
        ("Punto de ebullición estimado","punto_ebullicion_agua_altitud_c","°C")],
    "Agua en suelo y aire": [
        ("Índice hídrico del modelo","indice_hidrogeno_hidrico_smap_0_100","/100"),
        ("Humedad relativa superficial · GWETTOP","humedad_suelo_superficial_gwettop_pct","%"),
        ("Humedad relativa radicular · GWETROOT","humedad_suelo_radicular_gwetroot_pct","%"),
        ("Humedad relativa del perfil · GWETPROF","humedad_suelo_perfil_profundo_gwetprof_pct","%"),
        ("Humedad específica · QV2M","humedad_especifica_aire_qv2m_g_kg","g/kg"),
        ("Punto de rocío · T2MDEW","punto_rocio_escarcha_t2mdew_c","°C")],
    "Química del suelo": [
        ("pH estimado","ph_suelo_estimado_lixiviacion","pH"),
        ("Concentración H⁺ estimada","concentracion_iones_hidrogeno_h_mas_umol_l","μmol/L"),
        ("Clasificación estimada","clasificacion_acidez_alcalinidad_suelo","")],
    "Radiación": [
        ("Onda corta","radiacion_solar_ceres_mj_m2_dia","MJ/m²/día"),
        ("Radiación fotosintética · PAR","radiacion_par_fotosintetica_mj_m2_dia","MJ/m²/día"),
        ("UVA","radiacion_uva_alta_montana_mj_m2_dia","MJ/m²/día"),
        ("UVB","radiacion_uvb_alta_montana_mj_m2_dia","MJ/m²/día"),
        ("Índice UV estimado","indice_uv_estimado_altiplano","")],
    "Clima y balance hídrico": [
        ("Lluvia acumulada","precipitacion_total_mm","mm"),
        ("Evapotranspiración de referencia estimada","evapotranspiracion_et0_fao_mm_campana","mm"),
        ("Temperatura media del aire","temperatura_media_c","°C"),
        ("Temperatura mínima del aire","temperatura_minima_absoluta_c","°C"),
        ("Temperatura mínima de superficie","temperatura_piel_suelo_min_ts_c","°C"),
        ("Días con helada","dias_helada","días"),
        ("Viento a 2 m","velocidad_viento_media_ws2m_ms","m/s")],
}
CAMPANA={"precipitacion_total_mm","temperatura_media_c","temperatura_minima_absoluta_c","dias_helada"}

def explorar_indicadores(sitio):
    datos=json.loads((Path(__file__).resolve().parents[1]/"datos_nasa/indicadores_rudy.json").read_text(encoding="utf8"))
    grupo=st.selectbox("Familia de indicadores",list(GRUPOS))
    opciones={nombre:(clave,unidad) for nombre,clave,unidad in GRUPOS[grupo]}
    nombre=st.selectbox("Indicador",list(opciones))
    clave,unidad=opciones[nombre]
    otro=next(k for k in datos if k!=sitio)
    st.caption("Campaña NASA POWER 2024–2025" if clave in CAMPANA else
               "Referencia geográfica de la celda" if clave=="altitud_celda_msnm" else
               "Resultado del modelo de Rudy sobre cinco campañas 2020–2025. El cálculo contempla estimaciones y valores de respaldo.")
    comparar=st.checkbox("Comparar con la otra región",value=True)
    ids=[sitio,otro] if comparar else [sitio]
    for col,k in zip(st.columns(len(ids)),ids):
        col.metric(datos[k]["ubicacion"],f"{datos[k][clave]} {unidad}")
    if comparar and isinstance(datos[sitio][clave],(float,int)):
        serie=pd.DataFrame({nombre:[datos[k][clave] for k in ids]},index=[datos[k]["ubicacion"] for k in ids])
        st.bar_chart(serie,y_label=unidad or nombre,color="#57856c")
    if grupo=="Química del suelo":
        st.info("El pH y la concentración de H⁺ se infieren del modelo de lixiviación. Su validación requiere muestras de suelo.")
    st.caption("Estos indicadores describen la región. Los aportes al puntaje de rotación se consultan en la gráfica de prioridades.")
