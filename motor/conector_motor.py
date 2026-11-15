"""Adaptador entre los controles de Jorge y la API de Rudy."""

from __future__ import annotations

from typing import Any

from motor.evaluador import evaluar_rotaciones_detallado


def obtener_salida_motor(
    parcela_id: str,
    escenario_id: str = "contrato_base",
    prioridades: dict[str, int] | None = None,
    datos_nasa: dict[str, Any] | None = None,
    datos_sensor: dict[str, Any] | None = None,
    incluir_aportes: bool = False,
) -> dict[str, Any]:
    """Evalúa tres rotaciones con los datos activos, sin sustituir el motor por puntajes fijos."""
    pesos = prioridades or {}
    sensor = datos_sensor or {}
    telemetria = {
        "disponible": bool(sensor),
        "origen": (
            "medicion_real" if sensor.get("origen") == "sensor_real"
            else "simulacion" if sensor.get("origen") == "simulado"
            else "no_disponible"
        ),
        "humedad_suelo_pct": sensor.get("humedad_suelo_pct"),
        "temperatura_suelo_c": None,
    }
    entrada = {
        "parcela_id": parcela_id,
        "prioridades": {
            "agua": pesos.get("agua", 0),
            "suelo": pesos.get("suelo", 0),
            "produccion": pesos.get("produccion", pesos.get("forraje", 0)),
        },
        "datos_nasa": datos_nasa or {},
        "telemetria": telemetria,
    }
    try:
        resultado = evaluar_rotaciones_detallado(entrada)
        salida = resultado["contrato_web"]
        if incluir_aportes:
            salida["aportes"] = {
                ev.id: {k: 100*c.peso_w_j*c.evaluacion_normalizada_r_ij for k,c in ev.criterios.items()}
                for ev in resultado["auditoria_interna"]["evaluaciones_detalladas"]
            }
        return salida
    except Exception as exc:
        return {
            "parcela_id": parcela_id,
            "recomendacion_id": None,
            "rotaciones": [],
            "estatus": f"error_motor: {exc}",
        }
