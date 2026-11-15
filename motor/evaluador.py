"""Módulo principal de evaluación multicriterio de rotaciones de cultivos.

Implementa la función pública obligatoria:
    evaluar_rotaciones(entrada: dict) -> dict

Y la función de inspección científica interna:
    evaluar_rotaciones_detallado(entrada: dict) -> dict
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from motor.configuracion import (
    CATALOGO_REGLAS_CIENTIFICAS,
    CRITERIOS_ORDENADOS,
    obtener_estrategias_configuradas,
)
from motor.criterios import evaluar_todos_los_criterios
from motor.explicaciones import (
    generar_explicacion_datos_insuficientes,
    generar_explicacion_verificable,
)
from motor.modelos import (
    DatosClimaticosNASA,
    EstrategiaRotacion,
    ErrorValidacionContrato,
    EvaluacionRotacionInterna,
    PesosPrioridades,
    ResultadoCriterioRotacion,
)
from motor.ponderaciones import normalizar_ponderaciones
from motor.validacion import (
    adaptar_y_validar_datos_nasa,
    adaptar_y_validar_telemetria,
    cargar_datos_nasa_csv,
)


def cargar_datos_nasa_locales(ruta_archivo: str | Path) -> dict[str, Any]:
    """Carga un archivo local (JSON o CSV) de datos NASA POWER sin requerir conexión a internet."""
    ruta = Path(ruta_archivo)
    if not ruta.exists() or not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo climático local: {ruta}")
    if ruta.suffix.lower() == ".csv":
        return cargar_datos_nasa_csv(ruta)
    with ruta.open("r", encoding="utf-8") as archivo:
        contenido = json.load(archivo)
    if not isinstance(contenido, dict):
        raise ErrorValidacionContrato(
            f"El archivo climático local '{ruta}' debe contener un objeto JSON raíz."
        )
    return contenido


def _clave_desempate_determinista(
    id_rotacion: str,
    indice_orden: int,
    puntaje_entero: int,
    puntaje_exacto: float,
    criterios: dict[str, ResultadoCriterioRotacion],
    pesos: PesosPrioridades,
) -> tuple[int, float, float, float, float, int]:
    """Calcula la tupla de ordenamiento para desempates 100 % deterministas.

    Orden de prelación (de mayor a menor):
    1. Puntaje entero redondeado S_i (garantiza que la recomendada coincida con el puntaje máximo visible).
    2. Puntaje exacto en punto flotante (redondeado a 8 decimales).
    3. Evaluación normalizada r_{i, j*} en el criterio de mayor peso del agricultor.
    4. Evaluación normalizada en conservación de agua (r_{i, agua}).
    5. Evaluación normalizada en recuperación de suelo (r_{i, suelo}).
    6. Menor índice de configuración (-indice_orden: rotacion_1 antes que rotacion_2 antes que rotacion_3).
    """
    pesos_dict = pesos.como_diccionario()
    criterio_mayor_peso = max(CRITERIOS_ORDENADOS, key=lambda c: (pesos_dict[c], c == "agua", c == "suelo"))
    return (
        puntaje_entero,
        round(puntaje_exacto, 8),
        round(criterios[criterio_mayor_peso].evaluacion_normalizada_r_ij, 6),
        round(criterios["agua"].evaluacion_normalizada_r_ij, 6),
        round(criterios["suelo"].evaluacion_normalizada_r_ij, 6),
        -indice_orden,
    )


def _extraer_estructura_entrada(
    entrada: dict[str, Any],
) -> tuple[str, dict[str, Any] | None, dict[str, Any], dict[str, Any] | None, tuple[EstrategiaRotacion, ...] | None]:
    """Valida y extrae los bloques principales del diccionario de entrada."""
    if not isinstance(entrada, dict):
        raise ErrorValidacionContrato(
            f"La entrada a 'evaluar_rotaciones' debe ser un diccionario; se recibió {type(entrada).__name__}."
        )

    parcela_id = entrada.get("parcela_id", "piloto_01")
    if not isinstance(parcela_id, str) or not parcela_id.strip():
        raise ErrorValidacionContrato(
            "El campo 'parcela_id' debe ser una cadena de texto no vacía."
        )

    # Permite recibir tanto el contrato completo {"datos_nasa": {...}} como el bloque NASA directo
    if "datos_nasa" in entrada:
        datos_nasa_raw = entrada["datos_nasa"]
        if isinstance(datos_nasa_raw, (str, Path)):
            datos_nasa_raw = cargar_datos_nasa_locales(datos_nasa_raw)
    elif "fuente" in entrada and "latitud" in entrada and "longitud" in entrada:
        datos_nasa_raw = entrada
    else:
        raise ErrorValidacionContrato(
            "La entrada debe incluir el bloque 'datos_nasa' (o un objeto NASA POWER con 'fuente', 'latitud' y 'longitud')."
        )

    prioridades_raw = entrada.get("prioridades")
    telemetria_raw = entrada.get("telemetria")
    estrategias_personalizadas = entrada.get("estrategias_personalizadas")

    return (
        parcela_id.strip(),
        prioridades_raw,
        datos_nasa_raw,
        telemetria_raw,
        estrategias_personalizadas,
    )


def _determinar_estatus(datos_nasa: DatosClimaticosNASA, hay_puntajes: bool) -> str:
    """Determina el valor del campo `estatus` según la completitud y origen de los datos."""
    if not hay_puntajes:
        return "datos_insuficientes"
    if datos_nasa.es_simulacion_o_ejemplo or datos_nasa.variables_criticas_faltantes:
        return "demostracion"
    return "evaluado_datos_reales"


def evaluar_rotaciones_detallado(entrada: dict[str, Any]) -> dict[str, Any]:
    """Ejecuta la evaluación multicriterio devolviendo el contrato web y la auditoría interna.

    Conserva internamente toda la información de incertidumbre, desglose matemático r_ij,
    pesos normalizados w_j, reglas científicas y telemetría sin alterar el contrato
    principal consumido por la aplicación web de Jorge.
    """
    (
        parcela_id,
        prioridades_raw,
        datos_nasa_raw,
        telemetria_raw,
        estrategias_personalizadas,
    ) = _extraer_estructura_entrada(entrada)

    pesos = normalizar_ponderaciones(prioridades_raw)
    datos_nasa = adaptar_y_validar_datos_nasa(datos_nasa_raw)
    telemetria = adaptar_y_validar_telemetria(telemetria_raw)
    estrategias = obtener_estrategias_configuradas(estrategias_personalizadas)

    # Política de datos faltantes: si no hay precipitación NASA POWER ni humedad de telemetría,
    # no se fabrica un puntaje numérico arbitrario.
    datos_suficientes_para_puntaje = (
        datos_nasa.precipitacion_total_mm is not None or telemetria.humedad_suelo_pct is not None
    )

    if not datos_suficientes_para_puntaje:
        evaluaciones_internas: list[EvaluacionRotacionInterna] = []
        for estrategia in estrategias:
            motivo_insuficiente = generar_explicacion_datos_insuficientes(estrategia, datos_nasa)
            evaluaciones_internas.append(
                EvaluacionRotacionInterna(
                    id=estrategia.id,
                    nombre=estrategia.nombre,
                    puntaje=None,
                    puntaje_exacto=None,
                    motivo=motivo_insuficiente,
                    criterios={},
                    factores_favorables=(),
                    factores_desfavorables=(),
                    restricciones_identificadas=estrategia.restricciones_documentadas,
                    incertidumbres=datos_nasa.variables_criticas_faltantes + datos_nasa.advertencias_calidad,
                    supuestos=estrategia.supuestos,
                    limitaciones=estrategia.limitaciones,
                )
            )

        contrato_web = {
            "parcela_id": parcela_id,
            "recomendacion_id": None,
            "rotaciones": [ev.a_contrato_web() for ev in evaluaciones_internas],
            "estatus": _determinar_estatus(datos_nasa, hay_puntajes=False),
        }
        return {
            "contrato_web": contrato_web,
            "auditoria_interna": {
                "pesos_normalizados": pesos.como_diccionario(),
                "fueron_normalizados_automaticamente": pesos.fueron_normalizados_automaticamente,
                "datos_nasa_validados": datos_nasa,
                "telemetria_validada": telemetria,
                "evaluaciones_detalladas": evaluaciones_internas,
                "catalogo_reglas": CATALOGO_REGLAS_CIENTIFICAS,
            },
        }

    # Cálculo matemático real S_i = 100 * sum_{j=1..m} w_j * r_{ij}
    criterios_por_id: dict[str, dict[str, ResultadoCriterioRotacion]] = {}
    puntajes_exactos_por_id: dict[str, float] = {}
    puntajes_enteros_por_id: dict[str, int] = {}

    for estrategia in estrategias:
        criterios_rot = evaluar_todos_los_criterios(estrategia, datos_nasa, telemetria, pesos)
        criterios_por_id[estrategia.id] = criterios_rot

        suma_ponderada = sum(
            criterios_rot[c].peso_w_j * criterios_rot[c].evaluacion_normalizada_r_ij
            for c in CRITERIOS_ORDENADOS
        )
        puntaje_exacto = max(0.0, min(100.0, 100.0 * suma_ponderada))
        puntaje_entero = int(round(puntaje_exacto))

        puntajes_exactos_por_id[estrategia.id] = puntaje_exacto
        puntajes_enteros_por_id[estrategia.id] = puntaje_entero

    # Selección de la mejor alternativa con desempate determinista
    id_recomendada = max(
        range(len(estrategias)),
        key=lambda idx: _clave_desempate_determinista(
            id_rotacion=estrategias[idx].id,
            indice_orden=idx,
            puntaje_entero=puntajes_enteros_por_id[estrategias[idx].id],
            puntaje_exacto=puntajes_exactos_por_id[estrategias[idx].id],
            criterios=criterios_por_id[estrategias[idx].id],
            pesos=pesos,
        ),
    )
    recomendacion_id = estrategias[id_recomendada].id

    evaluaciones_completas: list[EvaluacionRotacionInterna] = []
    for estrategia in estrategias:
        rid = estrategia.id
        criterios_rot = criterios_por_id[rid]
        motivo = generar_explicacion_verificable(
            estrategia=estrategia,
            puntaje_entero=puntajes_enteros_por_id[rid],
            puntaje_exacto=puntajes_exactos_por_id[rid],
            criterios_propios=criterios_rot,
            todos_los_criterios_por_id=criterios_por_id,
            todos_los_puntajes_exactos=puntajes_exactos_por_id,
            id_recomendada=recomendacion_id,
            pesos=pesos,
            datos_nasa=datos_nasa,
        )

        favorables_acum = tuple(
            f for c in CRITERIOS_ORDENADOS for f in criterios_rot[c].factores_favorables
        )
        desfavorables_acum = tuple(
            d for c in CRITERIOS_ORDENADOS for d in criterios_rot[c].factores_desfavorables
        )
        incertidumbres_acum = tuple(
            dict.fromkeys(
                [
                    *(inc for c in CRITERIOS_ORDENADOS for inc in criterios_rot[c].incertidumbres_criterio),
                    *datos_nasa.advertencias_calidad,
                    *telemetria.advertencias_telemetria,
                ]
            )
        )

        evaluaciones_completas.append(
            EvaluacionRotacionInterna(
                id=rid,
                nombre=estrategia.nombre,
                puntaje=puntajes_enteros_por_id[rid],
                puntaje_exacto=round(puntajes_exactos_por_id[rid], 4),
                motivo=motivo,
                criterios=criterios_rot,
                factores_favorables=favorables_acum,
                factores_desfavorables=desfavorables_acum,
                restricciones_identificadas=estrategia.restricciones_documentadas,
                incertidumbres=incertidumbres_acum,
                supuestos=estrategia.supuestos,
                limitaciones=estrategia.limitaciones,
            )
        )

    contrato_web = {
        "parcela_id": parcela_id,
        "recomendacion_id": recomendacion_id,
        "rotaciones": [ev.a_contrato_web() for ev in evaluaciones_completas],
        "estatus": _determinar_estatus(datos_nasa, hay_puntajes=True),
    }

    return {
        "contrato_web": contrato_web,
        "auditoria_interna": {
            "pesos_normalizados": pesos.como_diccionario(),
            "fueron_normalizados_automaticamente": pesos.fueron_normalizados_automaticamente,
            "datos_nasa_validados": datos_nasa,
            "telemetria_validada": telemetria,
            "evaluaciones_detalladas": evaluaciones_completas,
            "catalogo_reglas": CATALOGO_REGLAS_CIENTIFICAS,
        },
    }


def evaluar_rotaciones(entrada: dict[str, Any]) -> dict[str, Any]:
    """Evalúa tres alternativas agrícolas y devuelve el JSON compatible con el contrato del equipo.

    Entradas:
        Parcela (`parcela_id`), prioridades (`prioridades`), datos NASA (`datos_nasa`) y
        telemetría opcional (`telemetria`).

    Salida:
        JSON compatible con el contrato aprobado por el equipo:
        {
            "parcela_id": str,
            "recomendacion_id": str | None,
            "rotaciones": [
                {"id": "rotacion_1", "puntaje": int | None, "motivo": str},
                {"id": "rotacion_2", "puntaje": int | None, "motivo": str},
                {"id": "rotacion_3", "puntaje": int | None, "motivo": str}
            ],
            "estatus": str
        }
    """
    resultado_completo = evaluar_rotaciones_detallado(entrada)
    return resultado_completo["contrato_web"]


def _resolver_ruta_datos_demo(raiz: Path, nombre_archivo: str) -> Path:
    """Busca primero en `datos_nasa/` (módulo de Iván) y como respaldo en `pruebas/motor/casos/`."""
    candidato_ivan = raiz / "datos_nasa" / nombre_archivo
    if candidato_ivan.exists():
        return candidato_ivan
    return raiz / "pruebas" / "motor" / "casos" / nombre_archivo


def _ejecutar_demostracion_cli() -> None:
    """Ejecuta los tres escenarios obligatorios con archivos locales (100 % offline)."""
    raiz = Path(__file__).resolve().parent.parent
    escenarios = [
        (
            "ESCENARIO A — SEQUÍA (DÉFICIT HÍDRICO)",
            {
                "parcela_id": "altiplano_sequia_01",
                "prioridades": {"agua": 0.50, "suelo": 0.25, "produccion": 0.25},
                "datos_nasa": cargar_datos_nasa_locales(
                    _resolver_ruta_datos_demo(raiz, "escenario_a_sequia_power.json")
                ),
            },
        ),
        (
            "ESCENARIO B — HELADAS SEVERAS",
            {
                "parcela_id": "altiplano_heladas_02",
                "prioridades": {"agua": 0.30, "suelo": 0.25, "produccion": 0.45},
                "datos_nasa": cargar_datos_nasa_locales(
                    _resolver_ruta_datos_demo(raiz, "escenario_b_heladas_power.json")
                ),
            },
        ),
        (
            "ESCENARIO C — PRIORIDAD DE RECUPERACIÓN DEL SUELO",
            {
                "parcela_id": "altiplano_suelo_03",
                "prioridades": {"agua": 0.15, "suelo": 0.70, "produccion": 0.15},
                "datos_nasa": cargar_datos_nasa_locales(
                    _resolver_ruta_datos_demo(raiz, "escenario_c_suelo_power.json")
                ),
            },
        ),
    ]

    for titulo, payload in escenarios:
        print("=" * 78)
        print(titulo)
        print("=" * 78)
        salida = evaluar_rotaciones(payload)
        print(json.dumps(salida, indent=2, ensure_ascii=False))
        print()


if __name__ == "__main__":
    _ejecutar_demostracion_cli()
