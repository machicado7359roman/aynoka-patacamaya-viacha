"""Configuración agronómica, catálogo de reglas científicas y estrategias de rotación.

Separa explícitamente los parámetros de dominio, las referencias científicas y
el perfil experimental de demostración de la lógica de cálculo del motor.
Permite sustituir estrategias o coeficientes validados por Joel sin reescribir
el motor de evaluación.
"""

from __future__ import annotations

from motor.modelos import EstrategiaRotacion, ReglaCientifica

CRITERIOS_ORDENADOS: tuple[str, ...] = ("agua", "suelo", "produccion")

PESOS_POR_DEFECTO: dict[str, float] = {
    "agua": 1.0 / 3.0,
    "suelo": 1.0 / 3.0,
    "produccion": 1.0 / 3.0,
}

# Límites físicos y geográficos para validación de entradas
LIMITES_VALIDACION: dict[str, float | int] = {
    "latitud_min": -90.0,
    "latitud_max": 90.0,
    "longitud_min": -180.0,
    "longitud_max": 180.0,
    # Ventana geográfica de referencia del Altiplano boliviano (para advertencias de contexto)
    "altiplano_lat_min": -23.0,
    "altiplano_lat_max": -14.0,
    "altiplano_lon_min": -70.5,
    "altiplano_lon_max": -65.0,
    # Límites físicos terrestres admisibles
    "temperatura_min_posible_c": -50.0,
    "temperatura_max_posible_c": 55.0,
    "precipitacion_min_mm": 0.0,
    "precipitacion_max_campana_mm": 3000.0,
    "dias_helada_min": 0,
    "dias_helada_max": 366,
    "humedad_min_pct": 0.0,
    "humedad_max_pct": 100.0,
}

UNIDADES_ESPERADAS: dict[str, set[str]] = {
    "temperatura_media_c": {"C", "°C", "celsius", "degC"},
    "temperatura_minima_absoluta_c": {"C", "°C", "celsius", "degC"},
    "precipitacion_total_mm": {"mm", "milimetros", "millimeters"},
    "dias_helada": {"dias", "días", "days", "d"},
    "humedad_relativa_pct": {"%", "pct", "porcentaje", "percent"},
}

VALORES_CENTINELA_NASA_POWER: set[float] = {-999.0, -999, -99.0}


CATALOGO_REGLAS_CIENTIFICAS: dict[str, ReglaCientifica] = {
    "REGLA_AGUA_01": ReglaCientifica(
        id_regla="REGLA_AGUA_01",
        nombre_regla="Respuesta normalizada de eficiencia y satisfacción hídrica en campaña",
        variable_utilizada="precipitacion_total_mm (NASA POWER PRECTOTCORR) y humedad_suelo_pct opcional",
        formula_transformacion=(
            "f_hidrico = clip((P - P_crit) / (P_opt - P_crit), 0, 1); "
            "r_i,agua = clip(base_agua_i * (1 - s_hid_i * (1 - f_hidrico)) + bonif_deficit_i, 0, 1)"
        ),
        unidad="mm/campaña (entrada) -> adimensional [0, 1] (salida)",
        fundamento_cientifico=(
            "Los cultivos altoandinos presentan requerimientos hídricos diferenciados: "
            "la quinua (Chenopodium quinoa) y la cañahua (Chenopodium pallidicaule) mantienen "
            "estabilidad fisiológica con 200-350 mm/campaña mediante regulación estomática y "
            "ajuste osmótico, mientras que la papa (Solanum tuberosum ssp. andigena) requiere "
            "400-550 mm para evitar merma severa de tuberización."
        ),
        referencia_verificable=(
            "Geerts et al. (2006), Agricultural Water Management 81(3): 339-355, "
            "https://doi.org/10.1016/j.agwat.2005.04.008; "
            "Allen et al. (1998), FAO Irrigation and Drainage Paper No. 56."
        ),
        condiciones_aplicabilidad=(
            "Parcelas de secano en el Altiplano boliviano (3.600-4.100 m s.n.m.) durante la "
            "campaña agrícola septiembre-abril con precipitación acumulada agregada de PRECTOTCORR."
        ),
        limitaciones=(
            "La suma acumulada de campaña no captura por sí sola veranillos intracamapaña "
            "de 15-20 días durante floración si no se desagrega por década fenológica."
        ),
        estado_validacion="hipotesis_trabajo",
    ),
    "REGLA_TERMICA_01": ReglaCientifica(
        id_regla="REGLA_TERMICA_01",
        nombre_regla="Penalización térmica por temperatura mínima absoluta y frecuencia de heladas",
        variable_utilizada="temperatura_minima_absoluta_c (NASA POWER T2M_MIN) y dias_helada (T2M_MIN < 0 °C)",
        formula_transformacion=(
            "exceso_frio = max(0, T_tol_i - T_min_abs); "
            "exceso_dias = max(0, dias_helada - D_tol_i) / 40.0; "
            "penalizacion_helada = clip(s_hel_i * (0.12 * exceso_frio + 0.35 * exceso_dias), 0, 0.75)"
        ),
        unidad="°C y días (entrada) -> adimensional [0, 0.75] (salida)",
        fundamento_cientifico=(
            "El daño celular por congelación apoplástica en cultivos altoandinos depende del "
            "umbral mínimo absoluto alcanzado (T2M_MIN) y de la recurrencia de noches bajo 0 °C. "
            "La cañahua y variedades amargas/resilientes de quinua toleran hasta -6 °C a -8 °C en "
            "fases vegetativas, mientras que variedades dulces de papa sufren necrosis foliar desde -2 °C a -3 °C."
        ),
        referencia_verificable=(
            "Jacobsen et al. (2005), European Journal of Agronomy 22(2): 131-143, "
            "https://doi.org/10.1016/j.eja.2004.01.003; "
            "NASA POWER Agroclimatology Parameters Guide (https://power.larc.nasa.gov/docs/methodology/)."
        ),
        condiciones_aplicabilidad=(
            "Exige temperatura mínima diaria absoluta (T2M_MIN) o conteo verificado de días con T2M_MIN < 0 °C. "
            "Prohibido evaluar esta regla usando únicamente temperatura media (T2M)."
        ),
        limitaciones=(
            "T2M_MIN de NASA POWER representa la temperatura del aire a 2 m en grilla (~0.5° x 0.625°); "
            "las heladas radiativas a nivel de dosel (5-10 cm del suelo) pueden ser 1-2 °C más frías."
        ),
        estado_validacion="validada_bibliograficamente",
    ),
    "REGLA_SUELO_01": ReglaCientifica(
        id_regla="REGLA_SUELO_01",
        nombre_regla="Índice de recuperación edáfica, cobertura protectora y fijación biológica de nitrógeno",
        variable_utilizada="aporte_cobertura_y_fijacion_n de la secuencia + factor hídrico de mineralización",
        formula_transformacion=(
            "r_i,suelo = clip(0.65 * recuperacion_suelo_base_i + 0.25 * aporte_n_cobertura_i "
            "+ 0.10 * f_humedad_mineralizacion, 0, 1)"
        ),
        unidad="adimensional [0, 1]",
        fundamento_cientifico=(
            "La incorporación de leguminosas altoandinas (Lupinus mutabilis - tarwi, Vicia faba - haba, "
            "Vicia sativa - vicia forrajera) aporta fijación biológica de nitrógeno (40-120 kg N/ha) y "
            "biomasa radicular que reduce la erosión eólica e hídrica frente a secuencias extractivas continuas."
        ),
        referencia_verificable=(
            "Tapia, M. E. & Fries, A. M. (2007), Guía de campo de los cultivos andinos, FAO / ANPE; "
            "Ortuño et al. (2013), Sustentabilidad de los suelos en el Altiplano boliviano, PROINPA / FAO."
        ),
        condiciones_aplicabilidad=(
            "Suelos del Altiplano con bajo contenido de materia orgánica (< 1.5 %) sometidos a rotación trienal."
        ),
        limitaciones=(
            "La mineralización efectiva de residuos vegetales se reduce en campañas con precipitación "
            "inferior a 200 mm debido a menor actividad microbiana edáfica."
        ),
        estado_validacion="hipotesis_trabajo",
    ),
    "REGLA_MCDA_01": ReglaCientifica(
        id_regla="REGLA_MCDA_01",
        nombre_regla="Agregación lineal ponderada multicriterio (Weighted Sum Model)",
        variable_utilizada="Pesos normalizados w_j y evaluaciones normalizadas r_ij",
        formula_transformacion="S_i = round(100 * sum_{j=1..3} (w_j * r_ij))",
        unidad="Puntos en escala [0, 100]",
        fundamento_cientifico=(
            "El modelo de suma ponderada (WSM) proporciona una función de utilidad aditiva, determinista "
            "y directamente auditable cuando todos los criterios están normalizados en el mismo intervalo [0, 1] "
            "y los pesos cumplen w_j >= 0 y sum(w_j) = 1."
        ),
        referencia_verificable=(
            "Fishburn, P. C. (1967), Additive Utilities with Incomplete Product Sets; "
            "Triantaphyllou, E. (2000), Multi-Criteria Decision Making Methods: A Comparative Study, Springer."
        ),
        condiciones_aplicabilidad=(
            "Comparación relativa entre tres alternativas predefinidas bajo preferencias explícitas del agricultor."
        ),
        limitaciones=(
            "Asume compensación lineal parcial entre criterios; por ello se complementa con advertencias "
            "explícitas de restricciones térmicas e hídricas en la explicación generada."
        ),
        estado_validacion="demostracion",
    ),
}


ESTRATEGIAS_ROTACION_PROVISIONALES: tuple[EstrategiaRotacion, ...] = (
    EstrategiaRotacion(
        id="rotacion_1",
        nombre="Secuencia Intensiva Tradicional (Papa -> Quinua -> Cebada)",
        descripcion=(
            "Rotación comercial tradicional del Altiplano: inicia con papa como cultivo "
            "de cabecera de alta demanda hídrica y nutricional, seguido de quinua y cierre "
            "con cebada para grano/forraje."
        ),
        cultivos_secuencia=(
            "Año 1: Papa (Solanum tuberosum ssp. andigena)",
            "Año 2: Quinua (Chenopodium quinoa)",
            "Año 3: Cebada (Hordeum vulgare)",
        ),
        requisitos_documentados=(
            "Precipitación acumulada ideal >= 420 mm/campaña para tuberización óptima de papa.",
            "Temperaturas mínimas superiores a -2.5 °C durante brotación y floración del Año 1.",
            "Reposición orgánica inicial para compensar extracción consecutiva de tubérculo y grano.",
        ),
        restricciones_documentadas=(
            "Alta vulnerabilidad al estrés hídrico severo (< 250 mm).",
            "Susceptibilidad elevada a heladas negras o radiativas intensas (<-4.0 °C).",
            "Ausencia de leguminosa fijadora de nitrógeno en la secuencia trienal.",
        ),
        eficiencia_hidrica_base=0.62,
        recuperacion_suelo_base=0.42,
        potencial_productivo_base=0.92,
        precipitacion_optima_mm=460.0,
        precipitacion_critica_min_mm=220.0,
        temperatura_minima_tolerable_c=-2.5,
        dias_helada_tolerables=18,
        sensibilidad_deficit_hidrico=0.58,
        sensibilidad_heladas=0.72,
        aporte_cobertura_y_fijacion_n=0.30,
        supuestos=(
            "Perfil experimental de demostración pendiente de calibración varietal con Joel.",
            "Se asume manejo convencional sin riego suplementario (secano estricto).",
        ),
        limitaciones=(
            "No diferencia entre variedades de papa amarga (Luk'i, más tolerante a heladas) e Imilla.",
        ),
        estado_definicion="provisional_experimental",
        referencias_agronomicas=(
            "Geerts et al. (2006) - Déficit hídrico en el Altiplano",
            "Tapia & Fries (2007) - Sistemas de rotación andinos (FAO)",
        ),
    ),
    EstrategiaRotacion(
        id="rotacion_2",
        nombre="Secuencia Conservacionista Resiliente (Quinua -> Cañahua -> Tarwi/Haba)",
        descripcion=(
            "Rotación adaptativa orientada a resiliencia climática frente a sequía y heladas: "
            "combina dos quenopodiáceas altoandinas de alta tolerancia abiótica (quinua y cañahua) "
            "con cierre de leguminosa fijadora de nitrógeno (tarwi o haba)."
        ),
        cultivos_secuencia=(
            "Año 1: Quinua (Chenopodium quinoa)",
            "Año 2: Cañahua (Chenopodium pallidicaule)",
            "Año 3: Tarwi / Haba (Lupinus mutabilis / Vicia faba)",
        ),
        requisitos_documentados=(
            "Precipitación mínima operativa de 200-350 mm/campaña gracias a la plasticidad de cañahua y quinua.",
            "Suelos con drenaje moderado para evitar asfixia radicular en quinua.",
        ),
        restricciones_documentadas=(
            "Menor volumen total de biomasa forrajera verde respecto a asociaciones gramínea-vicia dedicadas.",
            "El cierre con leguminosa en Año 3 requiere humedad residual mínima en floración.",
        ),
        eficiencia_hidrica_base=0.91,
        recuperacion_suelo_base=0.74,
        potencial_productivo_base=0.81,
        precipitacion_optima_mm=340.0,
        precipitacion_critica_min_mm=150.0,
        temperatura_minima_tolerable_c=-6.5,
        dias_helada_tolerables=45,
        sensibilidad_deficit_hidrico=0.20,
        sensibilidad_heladas=0.22,
        aporte_cobertura_y_fijacion_n=0.72,
        supuestos=(
            "Perfil experimental de demostración basado en tolerancia reportada de Chenopodium pallidicaule.",
            "Se asume que los rastrojos de cañahua y tarwi se reincorporan parcialmente al suelo.",
        ),
        limitaciones=(
            "La tolerancia a heladas de la quinua disminuye durante la antesis (floración) respecto al estado ramificado.",
        ),
        estado_definicion="provisional_experimental",
        referencias_agronomicas=(
            "Jacobsen et al. (2005) - Resistencia a heladas y sequía en quinua y cañahua",
            "Geerts et al. (2006) - Requerimientos hídricos en el Altiplano boliviano",
        ),
    ),
    EstrategiaRotacion(
        id="rotacion_3",
        nombre="Secuencia Regenerativa Suelo-Forraje (Cebada+Vicia -> Tarwi -> Cobertura/Descanso Mejorado)",
        descripcion=(
            "Rotación diseñada para restaurar fertilidad edáfica, incrementar materia orgánica y "
            "proteger contra la erosión: asocia gramínea con leguminosa forrajera (vicia), continúa "
            "con leguminosa de raíz pivotante profunda (tarwi) y culmina en cobertura protectora."
        ),
        cultivos_secuencia=(
            "Año 1: Asociación Cebada + Vicia forrajera (Hordeum vulgare + Vicia sativa)",
            "Año 2: Tarwi (Lupinus mutabilis)",
            "Año 3: Cobertura vegetal protectora / Descanso mejorado con leguminosa",
        ),
        requisitos_documentados=(
            "Precipitación moderada (280-420 mm) para maximizar fijación simbiótica de N y biomasa de cobertura.",
            "Manejo de corte o incorporación de abono verde antes de la lignificación completa.",
        ),
        restricciones_documentadas=(
            "Menor producción de grano comercial directo para venta inmediata en el Año 3 (enfocado en suelo/forraje).",
            "Sensibilidad moderada del tarwi a heladas extremas tempranas si se atrasa la siembra.",
        ),
        eficiencia_hidrica_base=0.76,
        recuperacion_suelo_base=0.95,
        potencial_productivo_base=0.68,
        precipitacion_optima_mm=380.0,
        precipitacion_critica_min_mm=180.0,
        temperatura_minima_tolerable_c=-4.5,
        dias_helada_tolerables=32,
        sensibilidad_deficit_hidrico=0.32,
        sensibilidad_heladas=0.38,
        aporte_cobertura_y_fijacion_n=0.96,
        supuestos=(
            "Perfil experimental de demostración orientado a conservación y restauración edáfica.",
            "Se asume nodulación efectiva de Rhizobium/Bradyrhizobium en vicia y tarwi.",
        ),
        limitaciones=(
            "El beneficio sobre el carbono orgánico del suelo se consolida a lo largo del ciclo trienal completo.",
        ),
        estado_definicion="provisional_experimental",
        referencias_agronomicas=(
            "Tapia & Fries (2007) - Fijación de nitrógeno en Lupinus mutabilis y rotaciones altoandinas",
            "Ortuño et al. (2013) - Conservación de suelos y abonos verdes en el Altiplano",
        ),
    ),
)


def obtener_estrategias_configuradas(
    estrategias_personalizadas: tuple[EstrategiaRotacion, ...] | None = None,
) -> tuple[EstrategiaRotacion, ...]:
    """Devuelve las tres estrategias de rotación activas para evaluación.

    Permite inyectar una configuración validada por Joel sin alterar la lógica
    del motor, verificando que siempre existan exactamente 3 estrategias con
    identificadores únicos.
    """
    estrategias = (
        estrategias_personalizadas
        if estrategias_personalizadas is not None
        else ESTRATEGIAS_ROTACION_PROVISIONALES
    )
    if len(estrategias) != 3:
        raise ValueError(
            f"El sistema requiere exactamente 3 estrategias configuradas; se recibieron {len(estrategias)}."
        )
    ids = [e.id for e in estrategias]
    if len(set(ids)) != 3:
        raise ValueError(f"Los identificadores de las estrategias deben ser únicos: {ids}")
    return estrategias
