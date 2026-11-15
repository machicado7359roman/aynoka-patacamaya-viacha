"""Modelos de dominio y excepciones del motor de evaluación multicriterio.

Define estructuras inmutables (dataclasses) con tipado estricto en Python estándar
para representar reglas científicas, estrategias de rotación, datos NASA POWER,
telemetría opcional de sensores, ponderaciones y resultados de evaluación.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ErrorMotorEvaluacion(ValueError):
    """Excepción base para errores de validación y contrato en el motor."""


class ErrorValidacionContrato(ErrorMotorEvaluacion):
    """La estructura o los tipos de datos de entrada violan el contrato acordado."""


class ErrorUnidadesIncompatibles(ErrorMotorEvaluacion):
    """Las unidades declaradas en los datos climáticos o de telemetría son incompatibles."""


class ErrorRangoClimatico(ErrorMotorEvaluacion):
    """Valores climáticos o geográficos fuera de rangos físicamente posibles."""


class ErrorFechasInvalidas(ErrorMotorEvaluacion):
    """Fechas ausentes, mal formadas o con fecha inicial posterior a la final."""


class ErrorPonderacionesInvalidas(ErrorMotorEvaluacion):
    """Prioridades del agricultor negativas, vacías, no numéricas o de suma nula."""


@dataclass(frozen=True)
class ReglaCientifica:
    """Documentación trazable de una regla agronómica o climática (Sección 12)."""

    id_regla: str
    nombre_regla: str
    variable_utilizada: str
    formula_transformacion: str
    unidad: str
    fundamento_cientifico: str
    referencia_verificable: str
    condiciones_aplicabilidad: str
    limitaciones: str
    estado_validacion: str  # "validada_bibliograficamente" | "hipotesis_trabajo" | "demostracion"


@dataclass(frozen=True)
class EstrategiaRotacion:
    """Definición parametrizada de una alternativa de rotación de cultivos (Sección 6)."""

    id: str
    nombre: str
    descripcion: str
    cultivos_secuencia: tuple[str, ...]
    requisitos_documentados: tuple[str, ...]
    restricciones_documentadas: tuple[str, ...]
    # Factores intrínsecos de línea base en [0, 1] bajo condiciones de referencia
    eficiencia_hidrica_base: float
    recuperacion_suelo_base: float
    potencial_productivo_base: float
    # Parámetros de respuesta agroclimática (perfil experimental documentado)
    precipitacion_optima_mm: float
    precipitacion_critica_min_mm: float
    temperatura_minima_tolerable_c: float
    dias_helada_tolerables: int
    sensibilidad_deficit_hidrico: float
    sensibilidad_heladas: float
    aporte_cobertura_y_fijacion_n: float
    supuestos: tuple[str, ...]
    limitaciones: tuple[str, ...]
    estado_definicion: str  # "provisional_experimental" | "aprobada_campo"
    referencias_agronomicas: tuple[str, ...]


@dataclass(frozen=True)
class DatosClimaticosNASA:
    """Modelo interno verificado de datos climáticos NASA POWER (Sección 4)."""

    fuente: str
    url_consulta: str | None
    latitud: float
    longitud: float
    fecha_inicio: str | None
    fecha_fin: str | None
    periodo: str
    frecuencia_temporal: str
    parametros_nasa: tuple[str, ...]
    unidades: dict[str, str]
    agregaciones: dict[str, str]
    temperatura_media_c: float | None
    temperatura_minima_absoluta_c: float | None
    dias_helada: int | None
    precipitacion_total_mm: float | None
    humedad_relativa_pct: float | None
    porcentaje_datos_validos: float
    valores_faltantes_detectados: int
    es_simulacion_o_ejemplo: bool
    variables_criticas_faltantes: tuple[str, ...] = field(default_factory=tuple)
    advertencias_calidad: tuple[str, ...] = field(default_factory=tuple)
    etiqueta_escenario: str | None = None


@dataclass(frozen=True)
class DatosTelemetriaNefi:
    """Modelo interno del adaptador opcional de telemetría de sensores (Sección 13)."""

    disponible: bool
    origen: str  # "medicion_real" | "simulacion" | "no_disponible"
    humedad_suelo_pct: float | None
    temperatura_suelo_c: float | None
    timestamp: str | None
    es_simulacion: bool
    advertencias_telemetria: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PesosPrioridades:
    """Ponderaciones normalizadas de los criterios del agricultor (Sección 5)."""

    agua: float
    suelo: float
    produccion: float
    fueron_normalizados_automaticamente: bool
    pesos_originales: dict[str, float]

    def como_diccionario(self) -> dict[str, float]:
        """Devuelve los pesos normalizados por nombre de criterio."""
        return {
            "agua": self.agua,
            "suelo": self.suelo,
            "produccion": self.produccion,
        }


@dataclass(frozen=True)
class ResultadoCriterioRotacion:
    """Evaluación normalizada r_ij y contribución ponderada de un criterio j."""

    criterio: str
    evaluacion_normalizada_r_ij: float
    peso_w_j: float
    contribucion_puntos: float
    factores_favorables: tuple[str, ...]
    factores_desfavorables: tuple[str, ...]
    reglas_aplicadas: tuple[str, ...]
    incertidumbres_criterio: tuple[str, ...]


@dataclass(frozen=True)
class EvaluacionRotacionInterna:
    """Resultado completo y trazable de una alternativa de rotación."""

    id: str
    nombre: str
    puntaje: int | None
    puntaje_exacto: float | None
    motivo: str
    criterios: dict[str, ResultadoCriterioRotacion]
    factores_favorables: tuple[str, ...]
    factores_desfavorables: tuple[str, ...]
    restricciones_identificadas: tuple[str, ...]
    incertidumbres: tuple[str, ...]
    supuestos: tuple[str, ...]
    limitaciones: tuple[str, ...]

    def a_contrato_web(self) -> dict[str, Any]:
        """Serializa exclusivamente los campos aprobados en el contrato web de Jorge."""
        return {
            "id": self.id,
            "puntaje": self.puntaje,
            "motivo": self.motivo,
        }
