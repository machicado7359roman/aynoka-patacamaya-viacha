"""Cálculo determinista de criterios normalizados r_ij para cada estrategia de rotación.

Implementa las ecuaciones documentadas en `motor/configuracion.py` para:
1. `agua`: Disponibilidad y eficiencia de conservación hídrica.
2. `suelo`: Recuperación de fertilidad, cobertura protectora y fijación de N.
3. `produccion`: Estabilidad productiva ajustada por riesgo de heladas y déficit hídrico.

Restricción matemática estricta:
    0.0 <= r_ij <= 1.0 para toda alternativa i y criterio j.
"""

from __future__ import annotations

from motor.modelos import (
    DatosClimaticosNASA,
    DatosTelemetriaNefi,
    EstrategiaRotacion,
    PesosPrioridades,
    ResultadoCriterioRotacion,
)


def _clip(valor: float, minimo: float = 0.0, maximo: float = 1.0) -> float:
    """Acota un número real al intervalo cerrado [minimo, maximo]."""
    return max(minimo, min(maximo, float(valor)))


def evaluar_criterio_agua(
    estrategia: EstrategiaRotacion,
    datos_nasa: DatosClimaticosNASA,
    telemetria: DatosTelemetriaNefi,
    peso_w: float,
) -> ResultadoCriterioRotacion:
    """Evalúa r_{i,agua} en [0, 1] aplicando REGLA_AGUA_01."""
    favorables: list[str] = []
    desfavorables: list[str] = []
    incertidumbres: list[str] = []
    reglas = ["REGLA_AGUA_01"]

    precip = datos_nasa.precipitacion_total_mm
    if precip is None:
        incertidumbres.append(
            "Falta 'precipitacion_total_mm' (PRECTOTCORR); no es posible evaluar disponibilidad hídrica climática."
        )
        r_agua = _clip(estrategia.eficiencia_hidrica_base)
        return ResultadoCriterioRotacion(
            criterio="agua",
            evaluacion_normalizada_r_ij=round(r_agua, 6),
            peso_w_j=peso_w,
            contribucion_puntos=round(100.0 * peso_w * r_agua, 4),
            factores_favorables=tuple(favorables),
            factores_desfavorables=tuple(desfavorables),
            reglas_aplicadas=tuple(reglas),
            incertidumbres_criterio=tuple(incertidumbres),
        )

    # Factor de suficiencia hídrica respecto a los umbrales de la rotación
    rango_p = max(1.0, estrategia.precipitacion_optima_mm - estrategia.precipitacion_critica_min_mm)
    f_hidrico = _clip((precip - estrategia.precipitacion_critica_min_mm) / rango_p, 0.0, 1.0)

    # Ajuste opcional por telemetría in-situ de humedad de suelo (Nefi)
    ajuste_telemetria = 0.0
    if telemetria.disponible and telemetria.humedad_suelo_pct is not None:
        if telemetria.humedad_suelo_pct < 18.0:
            ajuste_telemetria = -0.04 * estrategia.sensibilidad_deficit_hidrico
            desfavorables.append(
                f"Telemetría reporta humedad edáfica baja ({telemetria.humedad_suelo_pct:.1f} %)."
            )
        elif telemetria.humedad_suelo_pct >= 25.0:
            ajuste_telemetria = 0.03 * (1.0 - estrategia.sensibilidad_deficit_hidrico)
            favorables.append(
                f"Telemetría confirma humedad edáfica favorable ({telemetria.humedad_suelo_pct:.1f} %)."
            )
        if telemetria.es_simulacion:
            incertidumbres.append(
                "El ajuste por humedad de suelo proviene de telemetría simulada (Nefi)."
            )

    # Bonificación de resiliencia en escenarios de déficit hídrico (< 280 mm, hipótesis de demostración)
    bonificacion_resiliencia = 0.0
    if precip < 280.0:
        if estrategia.sensibilidad_deficit_hidrico <= 0.25:
            bonificacion_resiliencia = 0.08 * (1.0 - f_hidrico)
            favorables.append(
                f"Alta eficiencia hídrica y tolerancia a déficit ({precip:.1f} mm acumulados; "
                f"umbral mínimo operativo {estrategia.precipitacion_critica_min_mm:.0f} mm)."
            )
        else:
            desfavorables.append(
                f"Déficit hídrico severo ({precip:.1f} mm frente a óptimo de "
                f"{estrategia.precipitacion_optima_mm:.0f} mm bajo hipótesis de trabajo)."
            )
    else:
        if f_hidrico >= 0.85:
            favorables.append(
                f"Precipitación acumulada ({precip:.1f} mm) cubre satisfactoriamente la demanda de la secuencia."
            )
        elif f_hidrico < 0.55:
            desfavorables.append(
                f"Precipitación subóptima ({precip:.1f} mm) para el requerimiento de {estrategia.precipitacion_optima_mm:.0f} mm."
            )

    penalizacion_deficit = estrategia.sensibilidad_deficit_hidrico * (1.0 - f_hidrico)
    r_agua = _clip(
        estrategia.eficiencia_hidrica_base * (1.0 - 0.65 * penalizacion_deficit)
        + bonificacion_resiliencia
        + ajuste_telemetria
    )

    if estrategia.eficiencia_hidrica_base >= 0.85 and not favorables:
        favorables.append("Baja demanda consuntiva de agua en la secuencia de cultivos.")

    return ResultadoCriterioRotacion(
        criterio="agua",
        evaluacion_normalizada_r_ij=round(r_agua, 6),
        peso_w_j=peso_w,
        contribucion_puntos=round(100.0 * peso_w * r_agua, 4),
        factores_favorables=tuple(favorables),
        factores_desfavorables=tuple(desfavorables),
        reglas_aplicadas=tuple(reglas),
        incertidumbres_criterio=tuple(incertidumbres),
    )


def evaluar_criterio_suelo(
    estrategia: EstrategiaRotacion,
    datos_nasa: DatosClimaticosNASA,
    peso_w: float,
) -> ResultadoCriterioRotacion:
    """Evalúa r_{i,suelo} en [0, 1] aplicando REGLA_SUELO_01."""
    favorables: list[str] = []
    desfavorables: list[str] = []
    incertidumbres: list[str] = []
    reglas = ["REGLA_SUELO_01"]

    precip = datos_nasa.precipitacion_total_mm
    if precip is None:
        f_mineralizacion = 0.5
        incertidumbres.append(
            "Sin 'precipitacion_total_mm', el factor de humedad para mineralización edáfica se asume neutro (0.5)."
        )
    else:
        f_mineralizacion = _clip((precip - 140.0) / (380.0 - 140.0), 0.2, 1.0)
        if precip < 200.0:
            desfavorables.append(
                f"Baja precipitación ({precip:.1f} mm) ralentiza la descomposición y mineralización de biomasa en suelo."
            )

    r_suelo = _clip(
        0.65 * estrategia.recuperacion_suelo_base
        + 0.25 * estrategia.aporte_cobertura_y_fijacion_n
        + 0.10 * f_mineralizacion * estrategia.recuperacion_suelo_base
    )

    if estrategia.aporte_cobertura_y_fijacion_n >= 0.85:
        favorables.append(
            "Máximo aporte de fijación biológica de nitrógeno (leguminosas en asociación y rotación) y cobertura antierosiva."
        )
    elif estrategia.aporte_cobertura_y_fijacion_n >= 0.65:
        favorables.append(
            "Incluye leguminosa altoandina (tarwi/haba) que repone nitrógeno parcialmente en el tercer año."
        )
    else:
        desfavorables.append(
            "Secuencia extractiva sin leguminosa fijadora de nitrógeno ni descanso cubierto; mayor desgaste edáfico."
        )

    return ResultadoCriterioRotacion(
        criterio="suelo",
        evaluacion_normalizada_r_ij=round(r_suelo, 6),
        peso_w_j=peso_w,
        contribucion_puntos=round(100.0 * peso_w * r_suelo, 4),
        factores_favorables=tuple(favorables),
        factores_desfavorables=tuple(desfavorables),
        reglas_aplicadas=tuple(reglas),
        incertidumbres_criterio=tuple(incertidumbres),
    )


def evaluar_criterio_produccion(
    estrategia: EstrategiaRotacion,
    datos_nasa: DatosClimaticosNASA,
    peso_w: float,
) -> ResultadoCriterioRotacion:
    """Evalúa r_{i,produccion} en [0, 1] combinando potencial base, REGLA_TERMICA_01 y REGLA_AGUA_01."""
    favorables: list[str] = []
    desfavorables: list[str] = []
    incertidumbres: list[str] = []
    reglas = ["REGLA_TERMICA_01", "REGLA_AGUA_01"]

    t_min = datos_nasa.temperatura_minima_absoluta_c
    dias_helada = datos_nasa.dias_helada
    precip = datos_nasa.precipitacion_total_mm

    # 1. Evaluación estricta de riesgo térmico por heladas (PROHIBIDO usar temperatura_media_c)
    penalizacion_helada = 0.0
    if t_min is None and dias_helada is None:
        incertidumbres.append(
            "No se dispone de 'temperatura_minima_absoluta_c' (T2M_MIN) ni de 'dias_helada'; "
            "el motor NO diagnostica heladas con temperatura media (T2M)."
        )
    else:
        exceso_frio = 0.0
        if t_min is not None and t_min < estrategia.temperatura_minima_tolerable_c:
            exceso_frio = estrategia.temperatura_minima_tolerable_c - t_min

        exceso_dias = 0.0
        if dias_helada is not None and dias_helada > estrategia.dias_helada_tolerables:
            exceso_dias = (dias_helada - estrategia.dias_helada_tolerables) / 40.0

        penalizacion_helada = _clip(
            estrategia.sensibilidad_heladas * (0.14 * exceso_frio + 0.38 * exceso_dias),
            0.0,
            0.75,
        )

        if penalizacion_helada > 0.12:
            detalle_t = f"T2M_MIN={t_min:.1f} °C" if t_min is not None else "T2M_MIN no reportada"
            detalle_d = f"{dias_helada} días de helada" if dias_helada is not None else "días no reportados"
            desfavorables.append(
                f"Penalización productiva por riesgo de heladas ({detalle_t}, {detalle_d}) "
                f"que supera la tolerancia térmica de la secuencia ({estrategia.temperatura_minima_tolerable_c:.1f} °C)."
            )
        else:
            if t_min is not None and t_min <= -4.0:
                favorables.append(
                    f"Alta tolerancia fisiológica a heladas severas (T2M_MIN={t_min:.1f} °C dentro de umbral tolerable "
                    f"de {estrategia.temperatura_minima_tolerable_c:.1f} °C)."
                )
            elif t_min is not None:
                favorables.append(
                    f"Régimen térmico mínimo (T2M_MIN={t_min:.1f} °C) compatible con el ciclo productivo."
                )

    # 2. Penalización hídrica sobre el rendimiento productivo
    penalizacion_hidrica_prod = 0.0
    if precip is not None:
        rango_p = max(1.0, estrategia.precipitacion_optima_mm - estrategia.precipitacion_critica_min_mm)
        f_hidrico = _clip((precip - estrategia.precipitacion_critica_min_mm) / rango_p, 0.0, 1.0)
        penalizacion_hidrica_prod = _clip(
            0.45 * estrategia.sensibilidad_deficit_hidrico * (1.0 - f_hidrico),
            0.0,
            0.55,
        )
        if penalizacion_hidrica_prod > 0.12:
            desfavorables.append(
                f"Merma productiva estimada por precipitación limitada ({precip:.1f} mm)."
            )

    # 3. Estabilidad productiva combinada
    bonificacion_estabilidad = 0.0
    if (t_min is not None and t_min <= -5.0) or (precip is not None and precip <= 230.0):
        # En condiciones abióticas extremas, las especies rústicas conservan mayor estabilidad relativa
        if estrategia.sensibilidad_heladas <= 0.25 and estrategia.sensibilidad_deficit_hidrico <= 0.25:
            bonificacion_estabilidad = 0.06
            favorables.append(
                "Estabilidad de cosecha superior bajo estrés abiótico altoandino (quinua y cañahua)."
            )

    r_produccion = _clip(
        estrategia.potencial_productivo_base * (1.0 - penalizacion_helada - penalizacion_hidrica_prod)
        + bonificacion_estabilidad
    )

    if estrategia.potencial_productivo_base >= 0.88 and penalizacion_helada <= 0.08 and penalizacion_hidrica_prod <= 0.08:
        favorables.append("Alto potencial de rendimiento comercial bajo condiciones hídricas y térmicas benignas.")

    return ResultadoCriterioRotacion(
        criterio="produccion",
        evaluacion_normalizada_r_ij=round(r_produccion, 6),
        peso_w_j=peso_w,
        contribucion_puntos=round(100.0 * peso_w * r_produccion, 4),
        factores_favorables=tuple(favorables),
        factores_desfavorables=tuple(desfavorables),
        reglas_aplicadas=tuple(reglas),
        incertidumbres_criterio=tuple(incertidumbres),
    )


def evaluar_todos_los_criterios(
    estrategia: EstrategiaRotacion,
    datos_nasa: DatosClimaticosNASA,
    telemetria: DatosTelemetriaNefi,
    pesos: PesosPrioridades,
) -> dict[str, ResultadoCriterioRotacion]:
    """Calcula los tres criterios normalizados para una estrategia de rotación."""
    return {
        "agua": evaluar_criterio_agua(estrategia, datos_nasa, telemetria, pesos.agua),
        "suelo": evaluar_criterio_suelo(estrategia, datos_nasa, pesos.suelo),
        "produccion": evaluar_criterio_produccion(estrategia, datos_nasa, pesos.produccion),
    }
