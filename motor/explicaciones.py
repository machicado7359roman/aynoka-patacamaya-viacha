"""Generador determinista de explicaciones verificables (XAI) para cada rotación.

Construye el campo `motivo` estrictamente a partir de los resultados numéricos
reales (r_ij, w_j, puntajes S_i, restricciones activas e incertidumbres).
Prohíbe emitir textos genéricos o afirmaciones que contradigan los cálculos.
"""

from __future__ import annotations

from motor.configuracion import CRITERIOS_ORDENADOS
from motor.modelos import (
    DatosClimaticosNASA,
    EstrategiaRotacion,
    PesosPrioridades,
    ResultadoCriterioRotacion,
)

NOMBRES_LEGIBLES_CRITERIO: dict[str, str] = {
    "agua": "conservación de agua",
    "suelo": "recuperación del suelo",
    "produccion": "producción agrícola/forrajera",
}


def generar_explicacion_datos_insuficientes(
    estrategia: EstrategiaRotacion,
    datos_nasa: DatosClimaticosNASA,
) -> str:
    """Genera una explicación transparente cuando faltan variables críticas para calcular S_i."""
    faltantes_txt = ", ".join(datos_nasa.variables_criticas_faltantes) or "variables climáticas críticas"
    return (
        f"[{estrategia.nombre}] Evaluación numérica no emitida (puntaje=null): "
        f"faltan variables críticas en el registro NASA POWER ({faltantes_txt}) para el periodo "
        f"'{datos_nasa.periodo}'. Conforme a la política científica del motor, no se inventan "
        f"precipitaciones ni se infieren heladas a partir de promedios térmicos."
    )


def generar_explicacion_verificable(
    estrategia: EstrategiaRotacion,
    puntaje_entero: int,
    puntaje_exacto: float,
    criterios_propios: dict[str, ResultadoCriterioRotacion],
     todos_los_criterios_por_id: dict[str, dict[str, ResultadoCriterioRotacion]],
    todos_los_puntajes_exactos: dict[str, float],
    id_recomendada: str,
    pesos: PesosPrioridades,
    datos_nasa: DatosClimaticosNASA,
) -> str:
    """Genera una explicación XAI trazable que responde por qué se recomienda o no la alternativa.

    Cada afirmación se verifica matemáticamente contra las evaluaciones reales:
    1. Posición relativa y puntaje exacto obtenido.
    2. Criterios que más favorecieron a la alternativa (comparación intra e inter-rotación).
    3. Criterios que redujeron su puntuación o donde fue superada.
    4. Influencia explícita de las prioridades del agricultor (pesos w_j).
    5. Restricciones climáticas/agronómicas e incertidumbres por datos incompletos o de demostración.
    """
    es_ganadora = estrategia.id == id_recomendada
    otras_ids = [rid for rid in todos_los_criterios_por_id if rid != estrategia.id]

    # 1. Identificar criterios donde esta rotación tiene el máximo estricto o compartido
    criterios_lider: list[str] = []
    criterios_rezagados: list[str] = []
    for crit in CRITERIOS_ORDENADOS:
        r_propio = criterios_propios[crit].evaluacion_normalizada_r_ij
        max_otros = max(
            todos_los_criterios_por_id[oid][crit].evaluacion_normalizada_r_ij
            for oid in otras_ids
        )
        if r_propio >= max_otros - 1e-6:
            criterios_lider.append(
                f"{NOMBRES_LEGIBLES_CRITERIO[crit]} (r={r_propio:.2f}, aporte={criterios_propios[crit].contribucion_puntos:.1f} pts)"
            )
        elif r_propio < max_otros - 0.05:
            criterios_rezagados.append(
                f"{NOMBRES_LEGIBLES_CRITERIO[crit]} (r={r_propio:.2f} vs {max_otros:.2f} de la mejor en ese criterio)"
            )

    # 2. Criterio de mayor peso del agricultor
    criterio_dominante = max(CRITERIOS_ORDENADOS, key=lambda c: pesos.como_diccionario()[c])
    peso_dom = pesos.como_diccionario()[criterio_dominante]
    r_en_dominante = criterios_propios[criterio_dominante].evaluacion_normalizada_r_ij

    partes: list[str] = []

    if es_ganadora:
        margen_segundo = min(
            puntaje_exacto - todos_los_puntajes_exactos[oid] for oid in otras_ids
        )
        partes.append(
            f"Alternativa recomendada ({estrategia.nombre}) con {puntaje_entero}/100 pts "
            f"(cálculo exacto {puntaje_exacto:.2f}, superando por +{margen_segundo:.2f} pts a la siguiente opción)."
        )
    else:
        diferencia_ganadora = todos_los_puntajes_exactos[id_recomendada] - puntaje_exacto
        partes.append(
            f"Alternativa no recomendada ({estrategia.nombre}) con {puntaje_entero}/100 pts "
            f"(cálculo exacto {puntaje_exacto:.2f}, a -{diferencia_ganadora:.2f} pts de {id_recomendada})."
        )

    if criterios_lider:
        partes.append(
            "Criterios favorables donde obtuvo la mayor evaluación: " + "; ".join(criterios_lider) + "."
        )
    else:
        mejor_interno = max(
            CRITERIOS_ORDENADOS,
            key=lambda c: criterios_propios[c].contribucion_puntos,
        )
        partes.append(
            f"Su mayor aporte interno provino de {NOMBRES_LEGIBLES_CRITERIO[mejor_interno]} "
            f"(r={criterios_propios[mejor_interno].evaluacion_normalizada_r_ij:.2f}, "
            f"aporte={criterios_propios[mejor_interno].contribucion_puntos:.1f} pts)."
        )

    if criterios_rezagados:
        partes.append(
            "Criterios que redujeron su puntuación relativa: " + "; ".join(criterios_rezagados) + "."
        )

    partes.append(
        f"Influencia de prioridades del agricultor (agua={pesos.agua:.2f}, suelo={pesos.suelo:.2f}, "
        f"produccion={pesos.produccion:.2f}): en el criterio prioritario de "
        f"{NOMBRES_LEGIBLES_CRITERIO[criterio_dominante]} (w={peso_dom:.2f}) alcanzó r={r_en_dominante:.2f}."
    )

    # 3. Factores climáticos / agronómicos específicos observados en el cálculo
    factores_destacados: list[str] = []
    for crit in CRITERIOS_ORDENADOS:
        if es_ganadora:
            factores_destacados.extend(criterios_propios[crit].factores_favorables[:1])
        else:
            factores_destacados.extend(criterios_propios[crit].factores_desfavorables[:1])

    if not factores_destacados:
        for crit in CRITERIOS_ORDENADOS:
            factores_destacados.extend(criterios_propios[crit].factores_favorables[:1])
            factores_destacados.extend(criterios_propios[crit].factores_desfavorables[:1])

    if factores_destacados:
        partes.append("Diagnóstico agroclimático: " + " ".join(factores_destacados[:2]))

    # 4. Incertidumbres y estado de validación
    incertidumbres_totales: list[str] = []
    for crit in CRITERIOS_ORDENADOS:
        for inc in criterios_propios[crit].incertidumbres_criterio:
            if inc not in incertidumbres_totales:
                incertidumbres_totales.append(inc)

    if incertidumbres_totales:
        partes.append("Incertidumbre registrada: " + " ".join(incertidumbres_totales))

    if datos_nasa.es_simulacion_o_ejemplo:
        partes.append(
            "Nota: evaluación calculada bajo perfil experimental de demostración (comparación interna del modelo, no garantía de rendimiento)."
        )

    return " ".join(partes)
