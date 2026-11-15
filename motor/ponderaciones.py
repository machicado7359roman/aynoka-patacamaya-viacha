"""Módulo de validación y normalización de ponderaciones multicriterio.

Garantiza las restricciones matemáticas del modelo:
- w_j >= 0 para todo criterio j en {agua, suelo, produccion}
- sum_{j=1..m} w_j = 1.0
"""

from __future__ import annotations

import math
from typing import Any

from motor.configuracion import CRITERIOS_ORDENADOS, PESOS_POR_DEFECTO
from motor.modelos import ErrorPonderacionesInvalidas, PesosPrioridades


def _es_numero_real_valido(valor: Any) -> bool:
    """Comprueba que el valor sea int o float (excluyendo bool, NaN e infinito)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    return math.isfinite(float(valor))


def normalizar_ponderaciones(prioridades_raw: dict[str, Any] | None) -> PesosPrioridades:
    """Valida y normaliza las prioridades del agricultor para que sumen exactamente 1.0.

    Si `prioridades_raw` es None, aplica pesos equilibrados (1/3, 1/3, 1/3)
    registrando que fueron asignados/normalizados por defecto.
    """
    if prioridades_raw is None:
        return PesosPrioridades(
            agua=PESOS_POR_DEFECTO["agua"],
            suelo=PESOS_POR_DEFECTO["suelo"],
            produccion=PESOS_POR_DEFECTO["produccion"],
            fueron_normalizados_automaticamente=True,
            pesos_originales=dict(PESOS_POR_DEFECTO),
        )

    if not isinstance(prioridades_raw, dict):
        raise ErrorPonderacionesInvalidas(
            f"'prioridades' debe ser un diccionario; se recibió {type(prioridades_raw).__name__}."
        )

    claves_desconocidas = set(prioridades_raw.keys()) - set(CRITERIOS_ORDENADOS)
    if claves_desconocidas:
        raise ErrorPonderacionesInvalidas(
            f"Criterios de prioridad no reconocidos: {sorted(claves_desconocidas)}. "
            f"Criterios permitidos: {list(CRITERIOS_ORDENADOS)}."
        )

    claves_faltantes = set(CRITERIOS_ORDENADOS) - set(prioridades_raw.keys())
    if claves_faltantes:
        raise ErrorPonderacionesInvalidas(
            f"Faltan criterios obligatorios en 'prioridades': {sorted(claves_faltantes)}."
        )

    pesos_brutos: dict[str, float] = {}
    for criterio in CRITERIOS_ORDENADOS:
        valor = prioridades_raw[criterio]
        if not _es_numero_real_valido(valor):
            raise ErrorPonderacionesInvalidas(
                f"El peso del criterio '{criterio}' debe ser un número real finito; se recibió {valor!r}."
            )
        peso_float = float(valor)
        if peso_float < 0.0:
            raise ErrorPonderacionesInvalidas(
                f"El peso del criterio '{criterio}' no puede ser negativo ({peso_float}). "
                "Restricción del modelo: w_j >= 0."
            )
        pesos_brutos[criterio] = peso_float

    suma_total = sum(pesos_brutos.values())
    if suma_total <= 0.0:
        raise ErrorPonderacionesInvalidas(
            "La suma de las prioridades del agricultor debe ser estrictamente mayor que cero."
        )

    ya_normalizado = math.isclose(suma_total, 1.0, rel_tol=1e-6, abs_tol=1e-6)
    agua_norm = pesos_brutos["agua"] / suma_total
    suelo_norm = pesos_brutos["suelo"] / suma_total
    # Asegurar cierre exacto de punto flotante en el tercer término
    produccion_norm = max(0.0, 1.0 - (agua_norm + suelo_norm))
    if not math.isclose(produccion_norm, pesos_brutos["produccion"] / suma_total, abs_tol=1e-9):
        produccion_norm = pesos_brutos["produccion"] / suma_total

    return PesosPrioridades(
        agua=agua_norm,
        suelo=suelo_norm,
        produccion=produccion_norm,
        fueron_normalizados_automaticamente=not ya_normalizado,
        pesos_originales=pesos_brutos,
    )
