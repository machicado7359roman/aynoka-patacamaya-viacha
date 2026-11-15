"""Adaptadores de validación de contratos para datos NASA POWER (Iván) y telemetría (Nefi).

Verifica rigurosamente:
1. Fuente y URL de consulta.
2. Coordenadas geográficas.
3. Fecha inicial y final (formato ISO y orden cronológico).
4. Parámetros NASA consultados.
5. Unidades declaradas (rechaza unidades incompatibles sin conversión implícita silenciosa).
6. Frecuencia temporal.
7. Agregaciones realizadas.
8. Valores faltantes (None, NaN y centinelas NASA POWER como -999).
9. Calidad y cobertura de datos.
"""

from __future__ import annotations

import csv
from datetime import date
import math
from pathlib import Path
from typing import Any

from motor.configuracion import (
    LIMITES_VALIDACION,
    UNIDADES_ESPERADAS,
    VALORES_CENTINELA_NASA_POWER,
)
from motor.modelos import (
    DatosClimaticosNASA,
    DatosTelemetriaNefi,
    ErrorFechasInvalidas,
    ErrorRangoClimatico,
    ErrorUnidadesIncompatibles,
    ErrorValidacionContrato,
)


def _normalizar_fecha_yyyymmdd(cadena_fecha: str) -> str:
    """Convierte 'YYYYMMDD' o 'YYYY-MM-DD' al formato estándar ISO 'YYYY-MM-DD'."""
    limpia = cadena_fecha.strip()
    if len(limpia) == 8 and limpia.isdigit():
        return f"{limpia[:4]}-{limpia[4:6]}-{limpia[6:8]}"
    return limpia


def transformar_geojson_nasa_power(raw_geojson: dict[str, Any]) -> dict[str, Any]:
    """Transforma una respuesta cruda NASA POWER (GeoJSON Feature con series diarias) al contrato interno.

    Extrae coordenadas de `geometry.coordinates`, metadatos de `header` y agrega las series
    diarias de `properties.parameter` (`PRECTOTCORR`, `T2M`, `T2M_MIN`, `RH2M`),
    filtrando valores centinela `-999` y contabilizando cobertura real.
    """
    header = raw_geojson.get("header", {}) if isinstance(raw_geojson.get("header"), dict) else {}
    geometry = raw_geojson.get("geometry", {}) if isinstance(raw_geojson.get("geometry"), dict) else {}
    props = raw_geojson.get("properties", {}) if isinstance(raw_geojson.get("properties"), dict) else {}
    parametros_dict = props.get("parameter", {})

    if not isinstance(parametros_dict, dict) or not parametros_dict:
        raise ErrorValidacionContrato(
            "Respuesta NASA POWER incompleta: falta 'properties.parameter' con series temporales."
        )

    coords = geometry.get("coordinates", [])
    if not isinstance(coords, list) or len(coords) < 2:
        raise ErrorValidacionContrato(
            "Respuesta NASA POWER incompleta: falta 'geometry.coordinates' [longitud, latitud]."
        )
    longitud = float(coords[0])
    latitud = float(coords[1])

    # Extraer conjunto de fechas diarias
    fechas_ordenadas: list[str] = sorted(
        {
            _normalizar_fecha_yyyymmdd(str(k))
            for serie in parametros_dict.values()
            if isinstance(serie, dict)
            for k in serie.keys()
        }
    )
    fecha_inicio = fechas_ordenadas[0] if fechas_ordenadas else None
    fecha_fin = fechas_ordenadas[-1] if fechas_ordenadas else None

    total_celdas = 0
    celdas_faltantes = 0

    def _extraer_serie_limpia(nombre_param: str) -> list[float]:
        nonlocal total_celdas, celdas_faltantes
        serie_raw = parametros_dict.get(nombre_param)
        if not isinstance(serie_raw, dict):
            return []
        valores_limpios: list[float] = []
        for v in serie_raw.values():
            total_celdas += 1
            val_limpio, fue_centinela = _validar_numero_opcional(v, nombre_param)
            if val_limpio is None or fue_centinela:
                celdas_faltantes += 1
            else:
                valores_limpios.append(float(val_limpio))
        return valores_limpios

    serie_p = _extraer_serie_limpia("PRECTOTCORR")
    serie_t2m = _extraer_serie_limpia("T2M")
    serie_tmin = _extraer_serie_limpia("T2M_MIN")
    serie_rh = _extraer_serie_limpia("RH2M")

    precipitacion_total = round(sum(serie_p), 3) if serie_p else None
    temperatura_media = round(sum(serie_t2m) / len(serie_t2m), 3) if serie_t2m else None
    temperatura_min_abs = round(min(serie_tmin), 3) if serie_tmin else None
    dias_helada = sum(1 for t in serie_tmin if t < 0.0) if serie_tmin else None
    humedad_media = round(sum(serie_rh) / len(serie_rh), 3) if serie_rh else None

    cobertura_pct = (
        round(100.0 * (total_celdas - celdas_faltantes) / total_celdas, 2)
        if total_celdas > 0
        else 0.0
    )

    # Extraer unidades desde header.parameter_information si existen
    unidades: dict[str, str] = {}
    info_params = raw_geojson.get("parameters", {})
    if isinstance(info_params, dict):
        mapa_campos = {
            "PRECTOTCORR": "precipitacion_total_mm",
            "T2M": "temperatura_media_c",
            "T2M_MIN": "temperatura_minima_absoluta_c",
            "RH2M": "humedad_relativa_pct",
        }
        for cod_nasa, campo_int in mapa_campos.items():
            meta_p = info_params.get(cod_nasa)
            if isinstance(meta_p, dict) and isinstance(meta_p.get("units"), str):
                u_raw = meta_p["units"].strip()
                if u_raw in {"mm/day", "mm"}:
                    unidades[campo_int] = "mm"
                elif u_raw in {"C", "°C", "degC"}:
                    unidades[campo_int] = "C"
                elif u_raw in {"%", "pct"}:
                    unidades[campo_int] = "%"
                else:
                    unidades[campo_int] = u_raw

    titulo_fuente = str(header.get("title", "NASA POWER Agroclimatology"))
    if "NASA" not in titulo_fuente.upper():
        titulo_fuente = f"NASA POWER - {titulo_fuente}"

    return {
        "fuente": titulo_fuente,
        "url_consulta": raw_geojson.get("url_consulta", "https://power.larc.nasa.gov/api/temporal/daily/point"),
        "latitud": latitud,
        "longitud": longitud,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "periodo": f"serie_diaria_{fecha_inicio}_a_{fecha_fin}" if fecha_inicio else "serie_diaria_nasa_power",
        "frecuencia_temporal": "diaria_agregada_desde_geojson",
        "parametros_nasa": list(parametros_dict.keys()),
        "unidades": unidades or None,
        "agregaciones": {
            "temperatura_media_c": "media_aritmetica_diaria",
            "temperatura_minima_absoluta_c": "minimo_absoluto_diario_T2M_MIN",
            "precipitacion_total_mm": "suma_acumulada_PRECTOTCORR",
            "dias_helada": "conteo_dias_T2M_MIN_menor_0C",
        },
        "temperatura_media_c": temperatura_media,
        "temperatura_minima_absoluta_c": temperatura_min_abs,
        "dias_helada": dias_helada,
        "precipitacion_total_mm": precipitacion_total,
        "humedad_relativa_pct": humedad_media,
        "calidad_cobertura": {
            "porcentaje_datos_validos": cobertura_pct,
            "valores_faltantes_detectados": celdas_faltantes,
            "es_simulacion_o_ejemplo": bool(raw_geojson.get("es_simulacion_o_ejemplo", False)),
        },
    }


def cargar_datos_nasa_csv(ruta_csv: str | Path) -> dict[str, Any]:
    """Lee un archivo CSV procesado por Iván (serie diaria NASA POWER) y lo convierte al contrato."""
    ruta = Path(ruta_csv)
    if not ruta.exists() or not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo CSV de datos NASA: {ruta}")

    metadatos_cabecera: dict[str, str] = {}
    lineas_datos: list[str] = []

    with ruta.open("r", encoding="utf-8") as f:
        for linea in f:
            texto = linea.strip()
            if not texto:
                continue
            if texto.startswith("#"):
                contenido_meta = texto.lstrip("#").strip()
                if ":" in contenido_meta:
                    k, v = contenido_meta.split(":", 1)
                    metadatos_cabecera[k.strip().lower()] = v.strip()
            else:
                lineas_datos.append(texto)

    if not lineas_datos:
        raise ErrorValidacionContrato(f"El archivo CSV '{ruta}' no contiene filas de datos.")

    lector = csv.DictReader(lineas_datos)
    filas = list(lector)
    if not filas:
        raise ErrorValidacionContrato(f"El archivo CSV '{ruta}' tiene cabecera pero 0 registros.")

    fechas: list[str] = []
    valores_p: list[float] = []
    valores_t2m: list[float] = []
    valores_tmin: list[float] = []
    valores_rh: list[float] = []
    total_celdas = 0
    celdas_faltantes = 0

    latitud_csv: float | None = None
    longitud_csv: float | None = None

    for fila in filas:
        if "fecha" in fila and fila["fecha"]:
            fechas.append(_normalizar_fecha_yyyymmdd(fila["fecha"]))
        if latitud_csv is None and fila.get("latitud"):
            latitud_csv = float(fila["latitud"])
        if longitud_csv is None and fila.get("longitud"):
            longitud_csv = float(fila["longitud"])

        for col_nasa, lista_dest in (
            ("PRECTOTCORR", valores_p),
            ("T2M", valores_t2m),
            ("T2M_MIN", valores_tmin),
            ("RH2M", valores_rh),
        ):
            if col_nasa in fila:
                total_celdas += 1
                texto_val = (fila[col_nasa] or "").strip()
                if texto_val == "" or texto_val.lower() in {"null", "nan", "na"}:
                    celdas_faltantes += 1
                    continue
                val_num = float(texto_val)
                val_limpio, fue_centinela = _validar_numero_opcional(val_num, col_nasa)
                if val_limpio is None or fue_centinela:
                    celdas_faltantes += 1
                else:
                    lista_dest.append(float(val_limpio))

    fechas_ordenadas = sorted(fechas)
    fecha_ini = fechas_ordenadas[0] if fechas_ordenadas else metadatos_cabecera.get("fecha_inicio")
    fecha_fin = fechas_ordenadas[-1] if fechas_ordenadas else metadatos_cabecera.get("fecha_fin")

    if latitud_csv is None and "latitud" in metadatos_cabecera:
        latitud_csv = float(metadatos_cabecera["latitud"])
    if longitud_csv is None and "longitud" in metadatos_cabecera:
        longitud_csv = float(metadatos_cabecera["longitud"])

    cobertura = (
        round(100.0 * (total_celdas - celdas_faltantes) / total_celdas, 2)
        if total_celdas > 0
        else 0.0
    )
    es_sim = metadatos_cabecera.get("es_simulacion_o_ejemplo", "true").lower() in {"true", "1", "si", "sí"}

    return {
        "fuente": metadatos_cabecera.get("fuente", "NASA POWER"),
        "url_consulta": metadatos_cabecera.get(
            "url_consulta", "https://power.larc.nasa.gov/api/temporal/daily/point"
        ),
        "latitud": latitud_csv,
        "longitud": longitud_csv,
        "fecha_inicio": fecha_ini,
        "fecha_fin": fecha_fin,
        "periodo": metadatos_cabecera.get("periodo", f"csv_{fecha_ini}_a_{fecha_fin}"),
        "frecuencia_temporal": "diaria_agregada_desde_csv",
        "parametros_nasa": [
            c for c in ("PRECTOTCORR", "T2M", "T2M_MIN", "RH2M") if c in (lector.fieldnames or [])
        ],
        "agregaciones": {
            "temperatura_media_c": "media_aritmetica_diaria",
            "temperatura_minima_absoluta_c": "minimo_absoluto_diario_T2M_MIN",
            "precipitacion_total_mm": "suma_acumulada_PRECTOTCORR",
            "dias_helada": "conteo_dias_T2M_MIN_menor_0C",
        },
        "temperatura_media_c": round(sum(valores_t2m) / len(valores_t2m), 3) if valores_t2m else None,
        "temperatura_minima_absoluta_c": round(min(valores_tmin), 3) if valores_tmin else None,
        "dias_helada": sum(1 for t in valores_tmin if t < 0.0) if valores_tmin else None,
        "precipitacion_total_mm": round(sum(valores_p), 3) if valores_p else None,
        "humedad_relativa_pct": round(sum(valores_rh) / len(valores_rh), 3) if valores_rh else None,
        "calidad_cobertura": {
            "porcentaje_datos_validos": cobertura,
            "valores_faltantes_detectados": celdas_faltantes,
            "es_simulacion_o_ejemplo": es_sim,
        },
    }


def _validar_numero_opcional(
    valor: Any,
    nombre_campo: str,
    permitir_entero_solo: bool = False,
) -> tuple[float | int | None, bool]:
    """Valida un campo numérico opcional y detecta centinelas NASA POWER (-999).

    Devuelve (valor_limpio, fue_centinela_faltante).
    """
    if valor is None:
        return None, False

    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorValidacionContrato(
            f"El campo '{nombre_campo}' debe ser numérico o null; se recibió {type(valor).__name__} ({valor!r})."
        )

    valor_float = float(valor)
    if not math.isfinite(valor_float):
        return None, True

    if valor_float in VALORES_CENTINELA_NASA_POWER:
        return None, True

    if permitir_entero_solo:
        if not isinstance(valor, int) and not valor_float.is_integer():
            raise ErrorValidacionContrato(
                f"El campo '{nombre_campo}' debe ser un número entero; se recibió {valor!r}."
            )
        return int(valor_float), False

    return valor_float, False


def _validar_fechas_iso(fecha_inicio: Any, fecha_fin: Any) -> tuple[str | None, str | None]:
    """Comprueba formato ISO-8601 (YYYY-MM-DD) y coherencia cronológica fecha_inicio <= fecha_fin."""
    if fecha_inicio is None and fecha_fin is None:
        return None, None

    if (fecha_inicio is None) != (fecha_fin is None):
        raise ErrorFechasInvalidas(
            "Si se especifican fechas de consulta NASA, tanto 'fecha_inicio' como 'fecha_fin' deben estar presentes."
        )

    if not isinstance(fecha_inicio, str) or not isinstance(fecha_fin, str):
        raise ErrorFechasInvalidas(
            "'fecha_inicio' y 'fecha_fin' deben ser cadenas en formato ISO 'YYYY-MM-DD'."
        )

    try:
        d_ini = date.fromisoformat(fecha_inicio)
        d_fin = date.fromisoformat(fecha_fin)
    except ValueError as exc:
        raise ErrorFechasInvalidas(
            f"Formato de fecha inválido ({fecha_inicio!r} a {fecha_fin!r}). Use 'YYYY-MM-DD'."
        ) from exc

    if d_ini > d_fin:
        raise ErrorFechasInvalidas(
            f"'fecha_inicio' ({fecha_inicio}) no puede ser posterior a 'fecha_fin' ({fecha_fin})."
        )

    return fecha_inicio, fecha_fin


def _validar_unidades(unidades_raw: Any) -> dict[str, str]:
    """Comprueba que las unidades declaradas sean compatibles con el modelo interno."""
    unidades_por_defecto = {
        "temperatura_media_c": "C",
        "temperatura_minima_absoluta_c": "C",
        "precipitacion_total_mm": "mm",
        "dias_helada": "dias",
        "humedad_relativa_pct": "%",
    }
    if unidades_raw is None:
        return unidades_por_defecto

    if not isinstance(unidades_raw, dict):
        raise ErrorValidacionContrato(
            f"'unidades' debe ser un diccionario; se recibió {type(unidades_raw).__name__}."
        )

    unidades_validadas = dict(unidades_por_defecto)
    for campo, unidad in unidades_raw.items():
        if not isinstance(unidad, str):
            raise ErrorUnidadesIncompatibles(
                f"La unidad del campo '{campo}' debe ser texto; se recibió {unidad!r}."
            )
        if campo in UNIDADES_ESPERADAS:
            if unidad.strip() not in UNIDADES_ESPERADAS[campo]:
                raise ErrorUnidadesIncompatibles(
                    f"Unidad incompatible para '{campo}': se recibió '{unidad}', "
                    f"pero el motor exige una de {sorted(UNIDADES_ESPERADAS[campo])}."
                )
        unidades_validadas[campo] = unidad.strip()

    return unidades_validadas


def adaptar_y_validar_datos_nasa(datos_raw: dict[str, Any]) -> DatosClimaticosNASA:
    """Transforma y verifica el diccionario de datos NASA de Iván al modelo interno.

    Soporta tanto el esquema pre-agregado del contrato como respuestas crudas
    GeoJSON (`Feature`) de la API NASA POWER (`properties.parameter`).
    """
    if not isinstance(datos_raw, dict):
        raise ErrorValidacionContrato(
            f"'datos_nasa' debe ser un diccionario JSON; se recibió {type(datos_raw).__name__}."
        )

    if "properties" in datos_raw and "geometry" in datos_raw and "fuente" not in datos_raw:
        datos_raw = transformar_geojson_nasa_power(datos_raw)

    fuente = datos_raw.get("fuente")
    if not isinstance(fuente, str) or not fuente.strip():
        raise ErrorValidacionContrato(
            "El campo 'fuente' en 'datos_nasa' es obligatorio y debe ser una cadena no vacía (ej. 'NASA POWER')."
        )
    if "NASA" not in fuente.upper():
        raise ErrorValidacionContrato(
            f"Fuente climática no reconocida ({fuente!r}). Se requiere procedencia 'NASA POWER' o producto NASA documentado."
        )

    url_consulta = datos_raw.get("url_consulta")
    if url_consulta is not None and (not isinstance(url_consulta, str) or not url_consulta.strip()):
        raise ErrorValidacionContrato("'url_consulta' debe ser una cadena válida o null.")

    # Coordenadas
    lat_val, _ = _validar_numero_opcional(datos_raw.get("latitud"), "latitud")
    lon_val, _ = _validar_numero_opcional(datos_raw.get("longitud"), "longitud")
    if lat_val is None or lon_val is None:
        raise ErrorValidacionContrato(
            "Los campos 'latitud' y 'longitud' son obligatorios en 'datos_nasa'."
        )
    latitud = float(lat_val)
    longitud = float(lon_val)

    if not (LIMITES_VALIDACION["latitud_min"] <= latitud <= LIMITES_VALIDACION["latitud_max"]):
        raise ErrorRangoClimatico(
            f"Latitud fuera del rango terrestre [-90, 90]: {latitud}."
        )
    if not (LIMITES_VALIDACION["longitud_min"] <= longitud <= LIMITES_VALIDACION["longitud_max"]):
        raise ErrorRangoClimatico(
            f"Longitud fuera del rango terrestre [-180, 180]: {longitud}."
        )

    advertencias: list[str] = []
    if not (
        LIMITES_VALIDACION["altiplano_lat_min"] <= latitud <= LIMITES_VALIDACION["altiplano_lat_max"]
        and LIMITES_VALIDACION["altiplano_lon_min"] <= longitud <= LIMITES_VALIDACION["altiplano_lon_max"]
    ):
        advertencias.append(
            f"Coordenadas ({latitud}, {longitud}) fuera de la ventana de referencia del Altiplano boliviano."
        )

    if url_consulta is None:
        advertencias.append("No se especificó 'url_consulta'; registro tratado como extracto local o ejemplo.")

    # Fechas y periodo
    fecha_inicio, fecha_fin = _validar_fechas_iso(
        datos_raw.get("fecha_inicio"),
        datos_raw.get("fecha_fin"),
    )
    periodo = datos_raw.get("periodo", "no_especificado")
    if not isinstance(periodo, str) or not periodo.strip():
        raise ErrorValidacionContrato("El campo 'periodo' debe ser una cadena no vacía.")

    frecuencia_temporal = datos_raw.get("frecuencia_temporal", "no_especificada")
    if not isinstance(frecuencia_temporal, str):
        raise ErrorValidacionContrato("'frecuencia_temporal' debe ser una cadena.")

    parametros_raw = datos_raw.get("parametros_nasa", [])
    if not isinstance(parametros_raw, list) or not all(isinstance(p, str) for p in parametros_raw):
        raise ErrorValidacionContrato("'parametros_nasa' debe ser una lista de cadenas.")
    parametros_nasa = tuple(parametros_raw)

    unidades = _validar_unidades(datos_raw.get("unidades"))

    agregaciones_raw = datos_raw.get("agregaciones", {})
    if not isinstance(agregaciones_raw, dict):
        raise ErrorValidacionContrato("'agregaciones' debe ser un diccionario.")
    agregaciones = {str(k): str(v) for k, v in agregaciones_raw.items()}

    # Variables climáticas y detección de valores centinela (-999)
    centinelas_detectados = 0

    t_media_raw, c1 = _validar_numero_opcional(datos_raw.get("temperatura_media_c"), "temperatura_media_c")
    t_min_raw, c2 = _validar_numero_opcional(
        datos_raw.get("temperatura_minima_absoluta_c"), "temperatura_minima_absoluta_c"
    )
    dias_helada_raw, c3 = _validar_numero_opcional(
        datos_raw.get("dias_helada"), "dias_helada", permitir_entero_solo=True
    )
    precip_raw, c4 = _validar_numero_opcional(
        datos_raw.get("precipitacion_total_mm"), "precipitacion_total_mm"
    )
    humedad_raw, c5 = _validar_numero_opcional(
        datos_raw.get("humedad_relativa_pct"), "humedad_relativa_pct"
    )
    centinelas_detectados += sum(1 for c in (c1, c2, c3, c4, c5) if c)

    temperatura_media_c = float(t_media_raw) if t_media_raw is not None else None
    temperatura_minima_absoluta_c = float(t_min_raw) if t_min_raw is not None else None
    dias_helada = int(dias_helada_raw) if dias_helada_raw is not None else None
    precipitacion_total_mm = float(precip_raw) if precip_raw is not None else None
    humedad_relativa_pct = float(humedad_raw) if humedad_raw is not None else None

    # Validación de rangos físicos
    for nombre_t, val_t in (
        ("temperatura_media_c", temperatura_media_c),
        ("temperatura_minima_absoluta_c", temperatura_minima_absoluta_c),
    ):
        if val_t is not None and not (
            LIMITES_VALIDACION["temperatura_min_posible_c"]
            <= val_t
            <= LIMITES_VALIDACION["temperatura_max_posible_c"]
        ):
            raise ErrorRangoClimatico(
                f"'{nombre_t}' ({val_t} °C) fuera de límites físicos admisibles "
                f"[{LIMITES_VALIDACION['temperatura_min_posible_c']}, {LIMITES_VALIDACION['temperatura_max_posible_c']}]."
            )

    if (
        temperatura_minima_absoluta_c is not None
        and temperatura_media_c is not None
        and temperatura_minima_absoluta_c > temperatura_media_c
    ):
        raise ErrorRangoClimatico(
            f"Inconsistencia termodinámica: 'temperatura_minima_absoluta_c' ({temperatura_minima_absoluta_c} °C) "
            f"no puede ser mayor que 'temperatura_media_c' ({temperatura_media_c} °C)."
        )

    if precipitacion_total_mm is not None and not (
        LIMITES_VALIDACION["precipitacion_min_mm"]
        <= precipitacion_total_mm
        <= LIMITES_VALIDACION["precipitacion_max_campana_mm"]
    ):
        raise ErrorRangoClimatico(
            f"'precipitacion_total_mm' ({precipitacion_total_mm} mm) fuera de rango válido "
            f"[{LIMITES_VALIDACION['precipitacion_min_mm']}, {LIMITES_VALIDACION['precipitacion_max_campana_mm']}]."
        )

    if dias_helada is not None and not (
        LIMITES_VALIDACION["dias_helada_min"]
        <= dias_helada
        <= LIMITES_VALIDACION["dias_helada_max"]
    ):
        raise ErrorRangoClimatico(
            f"'dias_helada' ({dias_helada}) fuera de rango válido [0, 366]."
        )

    if (
        dias_helada is not None
        and dias_helada > 0
        and temperatura_minima_absoluta_c is not None
        and temperatura_minima_absoluta_c >= 0.0
    ):
        raise ErrorRangoClimatico(
            f"Inconsistencia térmica: se reportan {dias_helada} días de helada, pero "
            f"'temperatura_minima_absoluta_c' es {temperatura_minima_absoluta_c} °C (>= 0 °C)."
        )

    if humedad_relativa_pct is not None and not (
        LIMITES_VALIDACION["humedad_min_pct"]
        <= humedad_relativa_pct
        <= LIMITES_VALIDACION["humedad_max_pct"]
    ):
        raise ErrorRangoClimatico(
            f"'humedad_relativa_pct' ({humedad_relativa_pct} %) fuera de rango [0, 100]."
        )

    # Identificación de variables críticas faltantes
    faltantes: list[str] = []
    if precipitacion_total_mm is None:
        faltantes.append("precipitacion_total_mm")
    if temperatura_minima_absoluta_c is None and dias_helada is None:
        faltantes.append("temperatura_minima_absoluta_c_o_dias_helada")
        if temperatura_media_c is not None:
            advertencias.append(
                "Existe 'temperatura_media_c', pero falta 'temperatura_minima_absoluta_c' (T2M_MIN) "
                "y 'dias_helada'. Por regla científica estricta, NO se infieren heladas a partir de la temperatura media."
            )

    if centinelas_detectados > 0:
        advertencias.append(
            f"Se detectaron {centinelas_detectados} valores centinela NASA POWER (-999) y se convirtieron a faltantes (null)."
        )

    # Calidad y cobertura
    calidad_raw = datos_raw.get("calidad_cobertura", {})
    if calidad_raw is not None and not isinstance(calidad_raw, dict):
        raise ErrorValidacionContrato("'calidad_cobertura' debe ser un diccionario.")
    calidad = calidad_raw or {}

    porcentaje_validos = float(calidad.get("porcentaje_datos_validos", 100.0 if not faltantes else 50.0))
    if not (0.0 <= porcentaje_validos <= 100.0):
        raise ErrorRangoClimatico(
            f"'porcentaje_datos_validos' ({porcentaje_validos}) debe estar entre 0 y 100."
        )

    faltantes_declarados = int(calidad.get("valores_faltantes_detectados", len(faltantes) + centinelas_detectados))
    es_ejemplo_periodo = any(
        token in periodo.lower()
        for token in ("ejemplo", "sintetico", "demostracion", "no_validado", "prueba")
    )
    es_simulacion = bool(calidad.get("es_simulacion_o_ejemplo", es_ejemplo_periodo or url_consulta is None))
    etiqueta_escenario = calidad.get("etiqueta_escenario")

    return DatosClimaticosNASA(
        fuente=fuente.strip(),
        url_consulta=url_consulta,
        latitud=latitud,
        longitud=longitud,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        periodo=periodo.strip(),
        frecuencia_temporal=frecuencia_temporal.strip(),
        parametros_nasa=parametros_nasa,
        unidades=unidades,
        agregaciones=agregaciones,
        temperatura_media_c=temperatura_media_c,
        temperatura_minima_absoluta_c=temperatura_minima_absoluta_c,
        dias_helada=dias_helada,
        precipitacion_total_mm=precipitacion_total_mm,
        humedad_relativa_pct=humedad_relativa_pct,
        porcentaje_datos_validos=porcentaje_validos,
        valores_faltantes_detectados=max(faltantes_declarados, len(faltantes) + centinelas_detectados),
        es_simulacion_o_ejemplo=es_simulacion,
        variables_criticas_faltantes=tuple(faltantes),
        advertencias_calidad=tuple(advertencias),
        etiqueta_escenario=str(etiqueta_escenario) if etiqueta_escenario is not None else None,
    )


def adaptar_y_validar_telemetria(telemetria_raw: dict[str, Any] | None) -> DatosTelemetriaNefi:
    """Transforma y valida los datos opcionales del sensor de Nefi.

    La ausencia del hardware o del bloque `telemetria` nunca impide ejecutar el motor.
    Distingue explícitamente mediciones reales de simulaciones.
    """
    if telemetria_raw is None:
        return DatosTelemetriaNefi(
            disponible=False,
            origen="no_disponible",
            humedad_suelo_pct=None,
            temperatura_suelo_c=None,
            timestamp=None,
            es_simulacion=False,
            advertencias_telemetria=("Sin telemetria in-situ conectada; evaluación basada en NASA POWER.",),
        )

    if not isinstance(telemetria_raw, dict):
        raise ErrorValidacionContrato(
            f"'telemetria' debe ser un diccionario o null; se recibió {type(telemetria_raw).__name__}."
        )

    disponible = bool(telemetria_raw.get("disponible", False))
    origen = str(telemetria_raw.get("origen", "no_disponible" if not disponible else "simulacion"))
    if origen not in {"medicion_real", "simulacion", "no_disponible"}:
        raise ErrorValidacionContrato(
            f"Origen de telemetría inválido ({origen!r}). Valores permitidos: 'medicion_real', 'simulacion', 'no_disponible'."
        )

    humedad_val, _ = _validar_numero_opcional(
        telemetria_raw.get("humedad_suelo_pct"), "telemetria.humedad_suelo_pct"
    )
    temp_suelo_val, _ = _validar_numero_opcional(
        telemetria_raw.get("temperatura_suelo_c"), "telemetria.temperatura_suelo_c"
    )

    humedad_suelo = float(humedad_val) if humedad_val is not None else None
    temperatura_suelo = float(temp_suelo_val) if temp_suelo_val is not None else None

    if humedad_suelo is not None and not (0.0 <= humedad_suelo <= 100.0):
        raise ErrorRangoClimatico(
            f"'telemetria.humedad_suelo_pct' ({humedad_suelo} %) fuera del rango [0, 100]."
        )
    if temperatura_suelo is not None and not (-40.0 <= temperatura_suelo <= 60.0):
        raise ErrorRangoClimatico(
            f"'telemetria.temperatura_suelo_c' ({temperatura_suelo} °C) fuera de rango [-40, 60]."
        )

    advertencias: list[str] = []
    es_simulacion = origen == "simulacion"
    if disponible and es_simulacion:
        advertencias.append("Telemetría de suelo proviene de simulación de Nefi (no hardware físico).")

    return DatosTelemetriaNefi(
        disponible=disponible,
        origen=origen,
        humedad_suelo_pct=humedad_suelo,
        temperatura_suelo_c=temperatura_suelo,
        timestamp=str(telemetria_raw["timestamp"]) if telemetria_raw.get("timestamp") else None,
        es_simulacion=es_simulacion,
        advertencias_telemetria=tuple(advertencias),
    )
