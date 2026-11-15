"""Descarga NASA POWER y genera series diarias + agregados por campaña.

Contrato acordado con Rudy (motor):
- Ubicaciones independientes: Patacamaya y Viacha.
- Periodo diario: 2020-01-01 a 2025-12-31.
- Campaña agrícola: 1 de septiembre a 30 de abril.
- Variables: PRECTOTCORR, T2M, T2M_MIN, T2M_MAX, RH2M.
- El JSON principal por ubicación (patacamaya_power.json / viacha_power.json)
  corresponde a la última campaña completa disponible (2024-09-01 a 2025-04-30).
- También se guardan los cinco JSON históricos, uno por campaña.

Las coordenadas son las referencias acordadas por el equipo; confirmar si
corresponden al centro de las parcelas piloto y no solo a las localidades.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# CONFIGURACIÓN: modificar aquí solo si el equipo acuerda otros valores.
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "resultados" / "raw"
PROCESSED_DIR = BASE_DIR / "resultados" / "procesados"
CAMPAIGNS_DIR = PROCESSED_DIR / "campanas"

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
START_DATE = "2020-01-01"
END_DATE = "2025-12-31"
COMMUNITY = "AG"
# Rudy proporcionó una URL sin time-standard. NASA POWER usa LST por defecto.
# Se omite el parámetro en la consulta para reproducir ese comportamiento.
TIME_STANDARD = "LST (predeterminado de NASA POWER; parámetro omitido)"

LOCATIONS: dict[str, dict[str, Any]] = {
    "patacamaya": {
        "parcela_id": "patacamaya_01",
        "nombre": "Patacamaya",
        "latitud": -17.2333,
        "longitud": -67.9167,
        "tipo_punto": "coordenada_referencial_proporcionada_por_el_equipo",
    },
    "viacha": {
        "parcela_id": "viacha_01",
        "nombre": "Viacha",
        "latitud": -16.6533,
        "longitud": -68.3017,
        "tipo_punto": "coordenada_referencial_proporcionada_por_el_equipo",
    },
}

# Se usa el mismo conjunto y orden de variables que indicó Rudy.
PARAMETERS = ["PRECTOTCORR", "T2M", "T2M_MIN", "T2M_MAX", "RH2M"]
REQUIRED_PARAMETERS = ["PRECTOTCORR", "T2M_MIN"]

PARAMETER_DESCRIPTIONS = {
    "PRECTOTCORR": "Precipitación corregida diaria",
    "T2M": "Temperatura media diaria del aire a 2 metros",
    "T2M_MIN": "Temperatura mínima diaria del aire a 2 metros",
    "T2M_MAX": "Temperatura máxima diaria del aire a 2 metros",
    "RH2M": "Humedad relativa del aire a 2 metros",
}

# Centinelas mencionados por Rudy y el valor de relleno documentado/observado
# en NASA POWER. Se convierten en valores faltantes, nunca en cero.
MISSING_VALUES = {-999.0, -99.0, -9999.0, -99999.0}

CAMPAIGN_START_MONTH = 9
CAMPAIGN_START_DAY = 1
CAMPAIGN_END_MONTH = 4
CAMPAIGN_END_DAY = 30


def ensure_folders() -> None:
    for folder in (RAW_DIR, PROCESSED_DIR, CAMPAIGNS_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def build_request(location: dict[str, Any], start: str = START_DATE,
                  end: str = END_DATE) -> tuple[dict[str, str], str]:
    """Devuelve los parámetros y la URL efectiva de la consulta."""
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": COMMUNITY,
        "longitude": str(location["longitud"]),
        "latitude": str(location["latitud"]),
        "start": start.replace("-", ""),
        "end": end.replace("-", ""),
        "format": "JSON",
    }
    prepared = requests.Request("GET", API_URL, params=params).prepare()
    return params, prepared.url or API_URL


def extract_daily_table(payload: dict[str, Any], location: dict[str, Any]) -> pd.DataFrame:
    """Convierte properties.parameter de NASA POWER en una tabla diaria completa."""
    parameter_data = payload.get("properties", {}).get("parameter", {})
    if not isinstance(parameter_data, dict) or not parameter_data:
        messages = payload.get("messages", [])
        raise RuntimeError(f"NASA POWER no devolvió properties.parameter. Mensajes: {messages}")

    full_dates = pd.date_range(START_DATE, END_DATE, freq="D")
    table = pd.DataFrame(index=full_dates)
    table.index.name = "fecha"

    for parameter in PARAMETERS:
        values = parameter_data.get(parameter)
        if not isinstance(values, dict):
            raise RuntimeError(
                f"No se encontró {parameter} en properties.parameter. "
                "Revisa la disponibilidad de esa variable en NASA POWER."
            )
        series = pd.Series(values, dtype="object")
        series.index = pd.to_datetime(series.index, format="%Y%m%d", errors="coerce")
        series = pd.to_numeric(series, errors="coerce")
        series = series[~series.index.isna()]
        table[parameter] = series.reindex(full_dates)

    # Normalizar valores centinela y asegurar números o NaN.
    for parameter in PARAMETERS:
        table[parameter] = pd.to_numeric(table[parameter], errors="coerce")
        table[parameter] = table[parameter].where(~table[parameter].isin(MISSING_VALUES), pd.NA)
        table[parameter] = table[parameter].astype("Float64")

    table = table.reset_index()
    table.insert(0, "parcela_id", location["parcela_id"])
    table.insert(1, "ubicacion", location["nombre"])
    table.insert(2, "latitud", float(location["latitud"]))
    table.insert(3, "longitud", float(location["longitud"]))
    return table


def get_parameter_metadata(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extrae unidades y nombres oficiales que devuelve la API."""
    api_metadata = payload.get("parameters", {})
    result: dict[str, dict[str, Any]] = {}
    for parameter in PARAMETERS:
        item = api_metadata.get(parameter, {}) if isinstance(api_metadata, dict) else {}
        result[parameter] = {
            "descripcion": PARAMETER_DESCRIPTIONS[parameter],
            "unidad_api": item.get("units") if isinstance(item, dict) else None,
            "nombre_api": item.get("longname") if isinstance(item, dict) else None,
        }
    return result


def download_location(key: str, location: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    params, request_url = build_request(location)
    print(f"\nConsultando NASA POWER para {location['nombre']}...")
    print(f"Coordenadas: latitud {location['latitud']}, longitud {location['longitud']}")
    print(f"Periodo diario: {START_DATE} a {END_DATE}")

    try:
        response = requests.get(API_URL, params=params, timeout=(20, 180))
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Error de conexión/HTTP con NASA POWER: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("NASA POWER no devolvió un JSON válido.") from exc

    table = extract_daily_table(payload, location)
    raw_path = RAW_DIR / f"nasa_power_{key}_{START_DATE}_{END_DATE}.json"
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    parameter_data = payload.get("properties", {}).get("parameter", {})
    returned_date_keys: set[str] = set()
    if isinstance(parameter_data, dict):
        for values in parameter_data.values():
            if isinstance(values, dict):
                returned_date_keys.update(str(k) for k in values.keys())
    start_key = START_DATE.replace("-", "")
    end_key = END_DATE.replace("-", "")
    returned_dates_in_range = [k for k in returned_date_keys if start_key <= k <= end_key]

    metadata = {
        "clave": key,
        "parcela_id": location["parcela_id"],
        "nombre": location["nombre"],
        "latitud": location["latitud"],
        "longitud": location["longitud"],
        "tipo_punto": location["tipo_punto"],
        "periodo_descargado": {"inicio": START_DATE, "fin": END_DATE},
        "url_consulta": response.url or request_url,
        "estandar_tiempo": TIME_STANDARD,
        "archivo_respuesta_original": str(raw_path.relative_to(BASE_DIR)),
        "registros_esperados": int(len(table)),
        "fechas_devuelta_por_api_en_rango": int(len(returned_dates_in_range)),
        "variables": get_parameter_metadata(payload),
        "mensajes_api": payload.get("messages", []),
    }
    print(f"Registros diarios preparados: {len(table)}")
    return table, metadata


def clean_float(value: Any, digits: int = 3) -> float | None:
    if pd.isna(value):
        return None
    return round(float(value), digits)


def make_campaign_windows() -> list[tuple[str, str, str]]:
    """Campañas completas septiembre-abril contenidas en el periodo solicitado."""
    start_bound = date.fromisoformat(START_DATE)
    end_bound = date.fromisoformat(END_DATE)
    windows: list[tuple[str, str, str]] = []
    for start_year in range(start_bound.year, end_bound.year):
        start = date(start_year, CAMPAIGN_START_MONTH, CAMPAIGN_START_DAY)
        end = date(start_year + 1, CAMPAIGN_END_MONTH, CAMPAIGN_END_DAY)
        if start >= start_bound and end <= end_bound:
            campaign_id = f"{start_year}_{start_year + 1}"
            windows.append((campaign_id, start.isoformat(), end.isoformat()))
    return windows


def aggregate_campaign(key: str, location: dict[str, Any], table: pd.DataFrame,
                       location_metadata: dict[str, Any], campaign_id: str,
                       campaign_start: str, campaign_end: str) -> dict[str, Any]:
    subset = table[
        (table["fecha"] >= pd.Timestamp(campaign_start)) &
        (table["fecha"] <= pd.Timestamp(campaign_end))
    ].copy()
    expected_days = len(pd.date_range(campaign_start, campaign_end, freq="D"))
    if len(subset) != expected_days:
        raise RuntimeError(
            f"La campaña {campaign_id} de {location['nombre']} tiene "
            f"{len(subset)} filas; se esperaban {expected_days}."
        )

    missing_cells = int(subset[PARAMETERS].isna().sum().sum())
    total_cells = expected_days * len(PARAMETERS)
    valid_cells = total_cells - missing_cells
    valid_percent = round((valid_cells / total_cells) * 100, 2) if total_cells else 0.0

    precip = subset["PRECTOTCORR"]
    tmin = subset["T2M_MIN"]
    tmean = subset["T2M"]
    rh = subset["RH2M"]

    # Un total de precipitación y un conteo de heladas solo son exactos si
    # hay cobertura completa de su variable durante toda la campaña.
    precipitation_total = (
        clean_float(precip.sum()) if precip.notna().all() else None
    )
    tmin_absolute = clean_float(tmin.min()) if tmin.notna().all() else None
    frost_days = int((tmin < 0).sum()) if tmin.notna().all() else None

    # JSON plano y compatible con el contrato que indicó Rudy.
    return {
        "ubicacion": location["nombre"],
        "fuente": "NASA POWER",
        # URL reproducible para la ventana exacta de esta campaña.
        "url_consulta": build_request(location, campaign_start, campaign_end)[1],
        "latitud": float(location["latitud"]),
        "longitud": float(location["longitud"]),
        "fecha_inicio": campaign_start,
        "fecha_fin": campaign_end,
        "periodo": f"campana_agricola_{campaign_id}_{key}",
        "frecuencia_temporal": "diaria_agregada_campana",
        "parametros_nasa": PARAMETERS,
        "unidades": {
            "temperatura_media_c": "C",
            "temperatura_minima_absoluta_c": "C",
            "precipitacion_total_mm": "mm",
            "dias_helada": "dias",
            "humedad_relativa_pct": "%",
        },
        "agregaciones": {
            "temperatura_media_c": "media_aritmetica_diaria",
            "temperatura_minima_absoluta_c": "minimo_absoluto_diario_T2M_MIN",
            "precipitacion_total_mm": "suma_acumulada_PRECTOTCORR",
            "dias_helada": "conteo_dias_T2M_MIN_menor_0C",
        },
        "temperatura_media_c": clean_float(tmean.mean()),
        "temperatura_minima_absoluta_c": tmin_absolute,
        "dias_helada": frost_days,
        "precipitacion_total_mm": precipitation_total,
        "humedad_relativa_pct": clean_float(rh.mean()),
        "calidad_cobertura": {
            "porcentaje_datos_validos": valid_percent,
            "valores_faltantes_detectados": missing_cells,
            "es_simulacion_o_ejemplo": False,
        },
    }


def write_json(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def make_quality_report(all_daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for place in all_daily["ubicacion"].drop_duplicates():
        part = all_daily[all_daily["ubicacion"] == place]
        for parameter in PARAMETERS:
            series = part[parameter].astype("Float64")
            rows.append({
                "ubicacion": place,
                "variable": parameter,
                "registros_esperados": int(len(series)),
                "registros_validos": int(series.notna().sum()),
                "valores_faltantes": int(series.isna().sum()),
                "porcentaje_valido": round(float(series.notna().mean() * 100), 2),
                "minimo": clean_float(series.min()),
                "maximo": clean_float(series.max()),
                "promedio": clean_float(series.mean()),
            })
    return pd.DataFrame(rows)


def main() -> int:
    ensure_folders()
    if date.fromisoformat(END_DATE) < date.fromisoformat(START_DATE):
        print("ERROR: END_DATE es anterior a START_DATE.", file=sys.stderr)
        return 1

    all_frames: list[pd.DataFrame] = []
    all_metadata: list[dict[str, Any]] = []
    all_campaign_rows: list[dict[str, Any]] = []
    windows = make_campaign_windows()

    for key, location in LOCATIONS.items():
        try:
            daily, metadata = download_location(key, location)
        except Exception as exc:
            print(f"\nERROR en {location['nombre']}: {exc}", file=sys.stderr)
            print("No se considera completa la entrega. Corrige el problema y vuelve a ejecutar.", file=sys.stderr)
            return 1

        all_frames.append(daily)
        all_metadata.append(metadata)

        daily_csv = PROCESSED_DIR / f"nasa_power_diario_{key}.csv"
        daily_export = daily.copy()
        daily_export["fecha"] = daily_export["fecha"].dt.strftime("%Y-%m-%d")
        daily_export.to_csv(daily_csv, index=False, encoding="utf-8-sig")
        print(f"CSV diario guardado: {daily_csv.relative_to(BASE_DIR)}")

        campaign_objects: list[dict[str, Any]] = []
        for campaign_id, campaign_start, campaign_end in windows:
            campaign_json = aggregate_campaign(
                key, location, daily, metadata,
                campaign_id, campaign_start, campaign_end,
            )
            campaign_objects.append(campaign_json)
            all_campaign_rows.append(campaign_json)
            safe_name = f"{key}_{campaign_id}.json"
            write_json(CAMPAIGNS_DIR / safe_name, campaign_json)

        if not campaign_objects:
            print(f"No hay campañas completas dentro del periodo para {location['nombre']}.", file=sys.stderr)
            return 1

        # Archivo principal compatible con el ejemplo de Rudy: campaña 2024-2025.
        latest = next(
            (item for item in campaign_objects if item["fecha_inicio"] == "2024-09-01"),
            campaign_objects[-1],
        )
        write_json(PROCESSED_DIR / f"{key}_power.json", latest)

        # Historial de campañas: contiene una lista de objetos con el mismo contrato.
        history = {
            "fuente": "NASA POWER",
            "ubicacion": location["nombre"],
            "nota": "Cada elemento de campanas cumple el contrato de agregación acordado con el motor.",
            "campanas": campaign_objects,
        }
        write_json(PROCESSED_DIR / f"{key}_power_campanas.json", history)

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["ubicacion", "fecha"]).reset_index(drop=True)
    combined["fecha"] = combined["fecha"].dt.strftime("%Y-%m-%d")
    combined.to_csv(
        PROCESSED_DIR / "nasa_power_diario_dos_ubicaciones.csv",
        index=False, encoding="utf-8-sig",
    )

    quality = make_quality_report(pd.concat(all_frames, ignore_index=True))
    quality.to_csv(
        PROCESSED_DIR / "control_calidad_datos.csv",
        index=False, encoding="utf-8-sig",
    )

    campaign_summary = pd.DataFrame(all_campaign_rows)
    campaign_summary.to_csv(
        PROCESSED_DIR / "resumen_campanas_dos_ubicaciones.csv",
        index=False, encoding="utf-8-sig",
    )

    metadata_document = {
        "fuente": "NASA POWER",
        "endpoint": API_URL,
        "comunidad": COMMUNITY,
        "periodo_diario_solicitado": {"inicio": START_DATE, "fin": END_DATE},
        "estandar_tiempo": TIME_STANDARD,
        "variables_solicitadas": PARAMETERS,
        "campanas_completas_generadas": [
            {"periodo": campaign_id, "inicio": s, "fin": e}
            for (campaign_id, s, e) in windows
        ],
        "ubicaciones": all_metadata,
        "valores_centinela_convertidos_a_nulo": sorted(MISSING_VALUES),
        "fecha_generacion_local": pd.Timestamp.now().isoformat(timespec="seconds"),
        "advertencias": [
            "Las coordenadas son referencias proporcionadas por el equipo; confirmar que correspondan a las parcelas piloto.",
            "NASA POWER entrega datos de productos/grillas y no sustituye una estación meteorológica dentro de la parcela.",
            "RH2M representa humedad relativa del aire, no humedad del suelo.",
            "Si falta al menos un día de PRECTOTCORR, la precipitación total de la campaña se entrega como null.",
            "Si falta al menos un día de T2M_MIN, la temperatura mínima absoluta y el conteo de heladas se entregan como null.",
            "El porcentaje de cobertura se calcula sobre todas las celdas diarias de las cinco variables.",
        ],
    }
    write_json(PROCESSED_DIR / "metadata_nasa_power.json", metadata_document)

    print("\nDESCARGA Y PROCESAMIENTO FINALIZADOS")
    print(f"Ubicaciones: {len(LOCATIONS)}")
    print(f"Días por ubicación: {len(pd.date_range(START_DATE, END_DATE, freq='D'))}")
    print(f"Campañas completas por ubicación: {len(windows)}")
    print(f"Carpeta de resultados: {PROCESSED_DIR}")
    print("Archivos principales para Rudy:")
    print("  resultados/procesados/patacamaya_power.json")
    print("  resultados/procesados/viacha_power.json")
    print("Revisa control_calidad_datos.csv antes de entregar los resultados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
