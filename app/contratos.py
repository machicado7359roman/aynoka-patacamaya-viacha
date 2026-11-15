"""Validación y carga de contratos de datos para la interfaz web de Jorge (`app/`).

Cumple con las secciones 4 (Jorge), 9.1, 9.2, 9.3, 17 y 19 del Plan Operativo NASA Space Apps 2026:
- Valida estructura, tipos y nulos de:
  1. Sensor o simulación -> aplicación (Nefi -> Jorge/Rudy)
  2. NASA POWER -> motor/web (Iván -> Rudy/Jorge)
  3. Motor -> página web (Rudy -> Jorge)
- Nunca inventa mediciones ni reemplaza nulos sin declararlo.
- Proporciona mensajes de error y advertencia comprensibles para el agricultor y el jurado.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent

DEFAULT_SENSOR_PATH = ROOT_DIR / "hardware" / "telemetria" / "lectura_sensor.json"
DEFAULT_NASA_PILOTO_PATH = ROOT_DIR / "datos_nasa" / "nasa_power_piloto.json"
DEFAULT_NASA_CATALOGO_PATH = ROOT_DIR / "datos_nasa" / "catalogo_parcelas_nasa.json"
DEFAULT_MOTOR_SALIDA_PATH = ROOT_DIR / "motor" / "salida_motor.json"

CUATRO_LIMITES_CIENTIFICOS: list[dict[str, str]] = [
    {
        "id": "limite_smap",
        "titulo": "Escala satelital vs. zona radicular (SMAP)",
        "descripcion": (
            "SMAP informa humedad superficial a escala satelital; no equivale sin modelo "
            "a una lectura de zona radicular de 20–30 cm."
        ),
        "icono": ":material/satellite_alt:",
    },
    {
        "id": "limite_ndvi",
        "titulo": "Alcance del índice espectral NDVI",
        "descripcion": (
            "NDVI por sí solo no permite diagnosticar deficiencia de nitrógeno de forma concluyente."
        ),
        "icono": ":material/grass:",
    },
    {
        "id": "limite_literatura",
        "titulo": "Herramienta exploratoria basada en literatura",
        "descripcion": (
            "Una comparación basada en literatura es una herramienta exploratoria; sin validación "
            "en campo no se afirma que mejore rendimientos."
        ),
        "icono": ":material/menu_book:",
    },
    {
        "id": "limite_simulacion",
        "titulo": "Rotulado explícito de valores simulados",
        "descripcion": (
            "Los valores simulados y las pruebas de mesa deben aparecer rotulados como simulación "
            "o demostración experimental."
        ),
        "icono": ":material/sensors:",
    },
]

from motor.configuracion import obtener_estrategias_configuradas

NOMBRES_ROTACIONES_CATALOGO = {
    e.id: {"nombre_corto": e.nombre, "secuencia": " | ".join(e.cultivos_secuencia)}
    for e in obtener_estrategias_configuradas()
}


@dataclass
class ResultadoValidacion:
    """Resultado trazable al validar un contrato de datos."""

    valido: bool
    datos: dict[str, Any]
    advertencias: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)
    origen_archivo: str = ""


def validar_contrato_sensor(payload: Any, origen_archivo: str = "memoria") -> ResultadoValidacion:
    """Valida el Contrato 9.1 (Sensor o simulación -> aplicación)."""
    errores: list[str] = []
    advertencias: list[str] = []

    if not isinstance(payload, dict):
        return ResultadoValidacion(
            valido=False,
            datos={},
            errores=["El mensaje de telemetría no es un objeto JSON válido."],
            origen_archivo=origen_archivo,
        )

    campos_requeridos = [
        "parcela_id",
        "origen",
        "temperatura_aire_c",
        "humedad_suelo_pct",
        "fecha_hora",
    ]
    for campo in campos_requeridos:
        if campo not in payload:
            errores.append(f"Falta el campo obligatorio `{campo}` en el contrato de sensor (Sección 9.1).")

    parcela_id = payload.get("parcela_id")
    if not isinstance(parcela_id, str) or not parcela_id.strip():
        errores.append("`parcela_id` debe ser un texto no vacío.")

    origen = payload.get("origen")
    if origen not in ("simulado", "sensor_real"):
        errores.append("`origen` debe ser exactamente `'simulado'` o `'sensor_real'`.")
    elif origen == "simulado":
        advertencias.append(
            "Lectura con `origen: simulado`. Se muestra como demostración experimental de protocolo, "
            "no como medición física de campo."
        )

    temp = payload.get("temperatura_aire_c")
    if temp is None:
        advertencias.append("`temperatura_aire_c` es `null` (lectura de temperatura no disponible).")
    elif not isinstance(temp, (int, float)) or isinstance(temp, bool):
        errores.append("`temperatura_aire_c` debe ser un número en °C o `null`.")
    elif temp < -35 or temp > 45:
        advertencias.append(
            f"`temperatura_aire_c` ({temp} °C) está fuera del rango habitual del Altiplano (-35 °C a 45 °C)."
        )

    hum = payload.get("humedad_suelo_pct")
    if hum is None:
        advertencias.append(
            "`humedad_suelo_pct` es `null` (sensor sin calibración válida o no conectado; no se adivina el valor)."
        )
    elif not isinstance(hum, (int, float)) or isinstance(hum, bool):
        errores.append("`humedad_suelo_pct` debe ser un número entre 0 y 100 o `null`.")
    elif hum < 0 or hum > 100:
        errores.append(f"`humedad_suelo_pct` ({hum}) vulnera la regla 0–100 del Contrato 9.1.")

    fecha_hora = payload.get("fecha_hora")
    if not isinstance(fecha_hora, str) or "T" not in fecha_hora:
        errores.append("`fecha_hora` debe estar en formato ISO 8601 con fecha y hora (ej. `2026-11-14T15:30:00-04:00`).")

    return ResultadoValidacion(
        valido=len(errores) == 0,
        datos=dict(payload),
        advertencias=advertencias,
        errores=errores,
        origen_archivo=origen_archivo,
    )


def validar_contrato_nasa(payload: Any, origen_archivo: str = "memoria") -> ResultadoValidacion:
    """Valida el Contrato 9.2 (NASA POWER -> motor/web) aplicando la skill `verificar-datos-nasa`."""
    errores: list[str] = []
    advertencias: list[str] = []

    if not isinstance(payload, dict):
        return ResultadoValidacion(
            valido=False,
            datos={},
            errores=["El archivo de datos NASA no es un objeto JSON válido."],
            origen_archivo=origen_archivo,
        )

    campos_requeridos = [
        "fuente",
        "latitud",
        "longitud",
        "periodo",
        "temperatura_media_c",
        "precipitacion_total_mm",
    ]
    for campo in campos_requeridos:
        if campo not in payload:
            errores.append(f"Falta el campo obligatorio `{campo}` en el contrato NASA (Sección 9.2).")

    fuente = payload.get("fuente")
    if not isinstance(fuente, str) or not fuente.strip():
        errores.append("`fuente` debe ser un texto no vacío (ej. `'NASA POWER'`).")

    lat = payload.get("latitud")
    lon = payload.get("longitud")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        errores.append("`latitud` debe ser un número decimal.")
    elif not (-23.5 <= float(lat) <= -9.5):
        advertencias.append(f"La `latitud` ({lat}) parece estar fuera del territorio boliviano.")

    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        errores.append("`longitud` debe ser un número decimal.")
    elif not (-71.0 <= float(lon) <= -57.0):
        advertencias.append(f"La `longitud` ({lon}) parece estar fuera del territorio boliviano.")

    periodo = payload.get("periodo")
    if not isinstance(periodo, str) or not periodo.strip():
        errores.append("`periodo` debe ser un texto descriptivo del rango de fechas.")
    elif periodo == "ejemplo_no_validado":
        advertencias.append(
            "El campo `periodo` indica `'ejemplo_no_validado'` (Plantilla didáctica 9.2). "
            "Pendiente sustituir por descarga validada de Iván."
        )

    temp_media = payload.get("temperatura_media_c")
    if temp_media is None:
        advertencias.append(
            "`temperatura_media_c` es `null` (dato climático aún no disponible; no se inventa ni interpola)."
        )
    elif not isinstance(temp_media, (int, float)) or isinstance(temp_media, bool):
        errores.append("`temperatura_media_c` debe ser un número en °C o `null`.")

    precip = payload.get("precipitacion_total_mm")
    if precip is None:
        advertencias.append(
            "`precipitacion_total_mm` es `null` (dato de precipitación aún no disponible; no se inventa)."
        )
    elif not isinstance(precip, (int, float)) or isinstance(precip, bool) or precip < 0:
        errores.append("`precipitacion_total_mm` debe ser un número >= 0 en mm o `null`.")

    return ResultadoValidacion(
        valido=len(errores) == 0,
        datos=dict(payload),
        advertencias=advertencias,
        errores=errores,
        origen_archivo=origen_archivo,
    )


def validar_contrato_motor(payload: Any, origen_archivo: str = "memoria") -> ResultadoValidacion:
    """Valida el Contrato 9.3 (Motor -> página web: Rudy -> Jorge)."""
    errores: list[str] = []
    advertencias: list[str] = []

    if not isinstance(payload, dict):
        return ResultadoValidacion(
            valido=False,
            datos={},
            errores=["La respuesta del motor no es un objeto JSON válido."],
            origen_archivo=origen_archivo,
        )

    for campo in ("parcela_id", "recomendacion_id", "rotaciones", "estatus"):
        if campo not in payload:
            errores.append(f"Falta el campo obligatorio `{campo}` en el contrato del motor (Sección 9.3).")

    parcela_id = payload.get("parcela_id")
    if not isinstance(parcela_id, str) or not parcela_id.strip():
        errores.append("`parcela_id` en la respuesta del motor debe ser un texto no vacío.")

    rotaciones = payload.get("rotaciones")
    ids_encontrados: list[str] = []
    if not isinstance(rotaciones, list) or len(rotaciones) != 3:
        errores.append("`rotaciones` debe ser una lista con exactamente las 3 estrategias evaluadas.")
    else:
        for idx, item in enumerate(rotaciones, start=1):
            if not isinstance(item, dict):
                errores.append(f"La rotación en posición {idx} no es un objeto JSON.")
                continue
            rot_id = item.get("id")
            puntaje = item.get("puntaje")
            motivo = item.get("motivo")
            if not isinstance(rot_id, str) or not rot_id.strip():
                errores.append(f"La rotación #{idx} no tiene un `id` válido.")
            else:
                ids_encontrados.append(rot_id)
            if not isinstance(puntaje, (int, float)) or isinstance(puntaje, bool):
                errores.append(f"La rotación `{rot_id}` debe tener un `puntaje` numérico.")
            elif not (0 <= float(puntaje) <= 100):
                advertencias.append(f"El `puntaje` ({puntaje}) de `{rot_id}` está fuera de la escala 0–100.")
            if not isinstance(motivo, str) or not motivo.strip():
                errores.append(f"La rotación `{rot_id}` debe incluir un `motivo` explicativo no vacío.")

    recomendacion_id = payload.get("recomendacion_id")
    if not isinstance(recomendacion_id, str) or not recomendacion_id.strip():
        errores.append("`recomendacion_id` debe ser un texto no vacío.")
    elif ids_encontrados and recomendacion_id not in ids_encontrados:
        errores.append(
            f"`recomendacion_id` (`'{recomendacion_id}'`) no coincide con ninguno de los IDs en `rotaciones` ({ids_encontrados})."
        )

    estatus = payload.get("estatus")
    if estatus == "demostracion":
        advertencias.append(
            "El motor reporta `estatus: demostracion`. Los puntajes provienen del escenario de referencia de Rudy "
            "y deben presentarse como apoyo exploratorio."
        )
    elif isinstance(estatus, str) and estatus.startswith("error"):
        errores.append(f"El motor reportó un estado de error: `{estatus}`.")

    return ResultadoValidacion(
        valido=len(errores) == 0,
        datos=dict(payload),
        advertencias=advertencias,
        errores=errores,
        origen_archivo=origen_archivo,
    )


def cargar_catalogo_parcelas_nasa(path: Path = DEFAULT_NASA_CATALOGO_PATH) -> dict[str, dict[str, Any]]:
    """Carga el catálogo local de parcelas NASA POWER preparado para operación offline."""
    if path.exists():
        try:
            contenido = json.loads(path.read_text(encoding="utf-8"))
            parcelas = contenido.get("parcelas", {})
            if isinstance(parcelas, dict) and parcelas:
                return parcelas
        except Exception:
            pass

    if DEFAULT_NASA_PILOTO_PATH.exists():
        try:
            piloto = json.loads(DEFAULT_NASA_PILOTO_PATH.read_text(encoding="utf-8"))
            return {"piloto_01": piloto}
        except Exception:
            pass

    return {
        "piloto_01": {
            "fuente": "NASA POWER",
            "latitud": -17.2,
            "longitud": -67.9,
            "periodo": "ejemplo_no_validado",
            "temperatura_media_c": None,
            "precipitacion_total_mm": None,
            "parcela_id": "piloto_01",
            "nombre_parcela": "Parcela Piloto (Respaldo Mínimo)",
        }
    }


def cargar_sensor_respaldo(path: Path = DEFAULT_SENSOR_PATH) -> ResultadoValidacion:
    """Lee y valida el archivo JSON del sensor/simulador (Nefi -> Jorge)."""
    if not path.exists():
        return ResultadoValidacion(
            valido=False,
            datos={},
            errores=[f"No se encontró el archivo de telemetría en `{path.relative_to(ROOT_DIR)}`."],
            origen_archivo=str(path),
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return validar_contrato_sensor(raw, origen_archivo=str(path.relative_to(ROOT_DIR)))
    except Exception as exc:
        return ResultadoValidacion(
            valido=False,
            datos={},
            errores=[f"Error al leer JSON de sensor en `{path.name}`: {exc}"],
            origen_archivo=str(path),
        )
