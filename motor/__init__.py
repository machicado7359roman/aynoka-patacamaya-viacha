"""Paquete del motor de evaluación multicriterio y recomendaciones explicables (Field Shift).

Responsable del módulo: Rudy Ramos.
"""

from __future__ import annotations

from typing import Any

from motor.configuracion import (
    CATALOGO_REGLAS_CIENTIFICAS,
    CRITERIOS_ORDENADOS,
    ESTRATEGIAS_ROTACION_PROVISIONALES,
    obtener_estrategias_configuradas,
)
from motor.modelos import (
    DatosClimaticosNASA,
    DatosTelemetriaNefi,
    ErrorFechasInvalidas,
    ErrorMotorEvaluacion,
    ErrorPonderacionesInvalidas,
    ErrorRangoClimatico,
    ErrorUnidadesIncompatibles,
    ErrorValidacionContrato,
    EstrategiaRotacion,
    EvaluacionRotacionInterna,
    PesosPrioridades,
    ReglaCientifica,
    ResultadoCriterioRotacion,
)

__all__ = [
    "CATALOGO_REGLAS_CIENTIFICAS",
    "CRITERIOS_ORDENADOS",
    "ESTRATEGIAS_ROTACION_PROVISIONALES",
    "DatosClimaticosNASA",
    "DatosTelemetriaNefi",
    "ErrorFechasInvalidas",
    "ErrorMotorEvaluacion",
    "ErrorPonderacionesInvalidas",
    "ErrorRangoClimatico",
    "ErrorUnidadesIncompatibles",
    "ErrorValidacionContrato",
    "EstrategiaRotacion",
    "EvaluacionRotacionInterna",
    "PesosPrioridades",
    "ReglaCientifica",
    "ResultadoCriterioRotacion",
    "cargar_datos_nasa_csv",
    "cargar_datos_nasa_locales",
    "evaluar_rotaciones",
    "evaluar_rotaciones_detallado",
    "obtener_estrategias_configuradas",
    "transformar_geojson_nasa_power",
]


def __getattr__(nombre: str) -> Any:
    """Carga diferida (PEP 562) de funciones de evaluación para evitar ciclos en ejecución CLI."""
    if nombre in {"evaluar_rotaciones", "evaluar_rotaciones_detallado", "cargar_datos_nasa_locales"}:
        from motor import evaluador

        return getattr(evaluador, nombre)
    if nombre in {"cargar_datos_nasa_csv", "transformar_geojson_nasa_power"}:
        from motor import validacion

        return getattr(validacion, nombre)
    raise AttributeError(f"El módulo 'motor' no tiene el atributo {nombre!r}.")
