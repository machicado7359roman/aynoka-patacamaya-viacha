"""Catálogo Botánico 3D y Evaluador de Viabilidad de Cultivos y Verduras (`app/catalogo_cultivos_3d.py`).

Módulo complementario (Nivel C / Extra Diferenciador) que:
1. Presenta un visor 3D interactivo (con rotación en 360°, zoom e iluminación) de los cultivos/verduras
   de las rotaciones del Altiplano boliviano y hortalizas seleccionables por el usuario.
2. Incluye fichas botánicas explicativas pensadas para jurados internacionales y usuarios de otros países
   que no conocen especies altoandinas como el Tarwi, la Cañahua, la Papa Luk'i o la Oca.
3. Permite al usuario seleccionar qué verduras/cultivos desea plantar y evalúa de forma transparente
   si es viable en la parcela seleccionada según los datos climáticos de NASA POWER (temperatura media,
   precipitación anual y días de helada), explicando el porqué agronómico específico de cada una.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

CATALOGO_CULTIVOS_VERDURAS: dict[str, dict[str, Any]] = {
    "quinua_real": {
        "id": "quinua_real",
        "nombre_comun": "Quinua Real Altiplánica",
        "nombre_internacional": "Royal Andean Quinoa (Amaranthaceae)",
        "nombre_cientifico": "Chenopodium quinoa Willd.",
        "categoria": "Grano / Hoja tierna comestible (Chiwa)",
        "presencia_rotaciones": "Presente en Rotación 1 (Año 2) y Rotación 2 (Año 1)",
        "forma_3d": "panoja_quinua",
        "color_primario": "#881337",
        "color_secundario": "#e11d48",
        "descripcion_internacional": (
            "Pseudocereal ancestral domesticado hace más de 5.000 años alrededor del Lago Titicaca y los salares "
            "bolivianos. Además de su grano rico en los 9 aminoácidos esenciales, sus hojas tiernas ('llipch'a' o 'chiwa') "
            "se consumen como verdura de hoja similar a la espinaca. Desarrolla una densa panoja de tonos carmesí, "
            "púrpura o dorado cubierta de saponina natural que la protege de aves y radiación UV extrema."
        ),
        "req_precip_min_mm": 250.0,
        "req_temp_min_c": 5.0,
        "tolera_heladas_dias": 150,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "Cultivo cabecera ideal en años secos: su raíz pivotante profunda aprovecha humedad residual a 30+ cm "
            "y deja estructura porosa en el suelo."
        ),
        "explicacion_especifica": (
            "Posee mecanismos fisiológicos halófitos y estomas que se cierran rápidamente ante la sequía del Altiplano, "
            "permitiendo producir grano y verdura foliar con apenas 250–400 mm de lluvia anual."
        ),
    },
    "tarwi_haba": {
        "id": "tarwi_haba",
        "nombre_comun": "Tarwi Andino / Haba de Altura",
        "nombre_internacional": "Andean Lupin Bean & Broad Bean (Fabaceae)",
        "nombre_cientifico": "Lupinus mutabilis / Vicia faba L.",
        "categoria": "Leguminosa / Vaina verde y grano proteico",
        "presencia_rotaciones": "Presente en Rotación 2 (Año 2 — Fijación biológica de N)",
        "forma_3d": "vaina_leguminosa",
        "color_primario": "#14532d",
        "color_secundario": "#22c55e",
        "descripcion_internacional": (
            "Para jurados fuera de los Andes: el Tarwi (Chocho) es una leguminosa de flores azul-violeta y vainas "
            "aterciopeladas cuyas semillas contienen más del 40% de proteína vegetal (comparable a la soya, pero "
            "adaptada a 3.800 m de altitud). Junto con el Haba andina (consumida fresca como verdura tierna en vaina "
            "o grano verde), constituye el motor biológico de fertilidad en las rotaciones del Altiplano."
        ),
        "req_precip_min_mm": 320.0,
        "req_temp_min_c": 6.0,
        "tolera_heladas_dias": 125,
        "fija_nitrogeno": True,
        "funcion_rotacion": (
            "Restaurador edáfico indispensable: mediante simbiosis con bacterias Rhizobium en sus nódulos radiculares, "
            "fija entre 60 y 140 kg de nitrógeno atmosférico por hectárea para el siguiente cultivo."
        ),
        "explicacion_especifica": (
            "Sin el Tarwi o el Haba en el Año 2, los suelos volcánicos/aluviales del Altiplano se agotan tras la quinua "
            "o la papa. Sus raíces profundas además solubilizan fósforo retenido en el suelo."
        ),
    },
    "papa_nativa": {
        "id": "papa_nativa",
        "nombre_comun": "Papa Nativa & Papa Amarga (Luk'i)",
        "nombre_internacional": "Andean Native & Frost-Resistant Bitter Potato (Solanaceae)",
        "nombre_cientifico": "Solanum tuberosum subsp. andigena / S. juzepczukii",
        "categoria": "Tubérculo altoandino de consumo fresco y deshidratado (Chuño)",
        "presencia_rotaciones": "Presente en Rotación 1 (Año 1), Rotación 2 (Año 4) y Rotación 3 (Año 4)",
        "forma_3d": "tuberculo_papa",
        "color_primario": "#78350f",
        "color_secundario": "#d97706",
        "descripcion_internacional": (
            "El Altiplano boliviano-peruano es el centro de origen mundial de la papa. A diferencia de la papa blanca "
            "comercial europea o norteamericana, aquí conviven variedades harinosas pigmentadas (ricas en antocianinas) "
            "y las 'papas amargas' (Luk'i), capaces de soportar heladas de hasta -5 °C en plena floración y que se "
            "deshidratan por congelación solar nocturna para producir 'Chuño' (alimento almacenable por décadas)."
        ),
        "req_precip_min_mm": 360.0,
        "req_temp_min_c": 5.5,
        "tolera_heladas_dias": 135,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "Cultivo de alta extracción de nutrientes y remoción de suelo; debe ubicarse preferentemente después de "
            "una leguminosa (Rotación 2) o un descanso manejado (Rotación 3) para cortar ciclos de nematodos."
        ),
        "explicacion_especifica": (
            "Demanda buena humedad en zona radicular (20–30 cm) durante la tuberización. La variedad Luk'i es viable "
            "incluso en llanuras con más de 130 días de helada al año."
        ),
    },
    "canahua_andina": {
        "id": "canahua_andina",
        "nombre_comun": "Cañahua (Qañawa)",
        "nombre_internacional": "Kañiwa — Extreme High-Altitude Supergrain & Leafy Green",
        "nombre_cientifico": "Chenopodium pallidicaule Aellen",
        "categoria": "Grano criotolerante y hoja tierna rica en calcio/hierro",
        "presencia_rotaciones": "Presente en Rotación 3 (Año 1 — Escenario de heladas severas)",
        "forma_3d": "planta_canahua",
        "color_primario": "#9a3412",
        "color_secundario": "#fb923c",
        "descripcion_internacional": (
            "Prácticamente desconocida fuera de Bolivia y Perú, la Cañahua es pariente cercana de la quinua pero de "
            "porte más bajo y ramificado. A diferencia de la quinua, NO contiene saponinas amargas (no requiere lavado "
            "intenso) y su arquitectura compacta crea un microclima térmico que le permite resistir heladas negras y "
            "granizadas a más de 4.000 metros sobre el nivel del mar."
        ),
        "req_precip_min_mm": 220.0,
        "req_temp_min_c": 3.5,
        "tolera_heladas_dias": 180,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "Seguro climático extremo en el Año 1 de la Rotación 3: garantiza cosecha alimentaria cuando las heladas "
            "radiativas o la sequía destruirían hortalizas convencionales."
        ),
        "explicacion_especifica": (
            "Es el cultivo agrícola más resistente al frío del hemisferio occidental: prospera con apenas 220 mm de "
            "precipitación y soporta hasta 180 días con temperaturas mínimas bajo cero."
        ),
    },
    "oca_isaño": {
        "id": "oca_isaño",
        "nombre_comun": "Oca Andina & Papalisa (Ulluco)",
        "nombre_internacional": "Andean Oca Tuber & Ulluco Vegetable (Oxalidaceae / Basellaceae)",
        "nombre_cientifico": "Oxalis tuberosa / Ullucus tuberosus",
        "categoria": "Verdura tuberosa dulce/cítrica altoandina",
        "presencia_rotaciones": "Verdura complementaria rotacional (Asociable en Año 2 o Año 4)",
        "forma_3d": "tuberculo_oca",
        "color_primario": "#b91c1c",
        "color_secundario": "#facc15",
        "descripcion_internacional": (
            "Para visitantes internacionales: la Oca es un tubérculo cilíndrico acanalado de colores brillantes "
            "(rojo, amarillo, rosado) que al exponerse al sol andino concentra azúcares hasta adquirir un sabor similar "
            "a una castaña o batata dulce con notas cítricas; la Papalisa (Ulluco) tiene textura crujiente incluso "
            "después de cocida y es base de la gastronomía tradicional boliviana."
        ),
        "req_precip_min_mm": 370.0,
        "req_temp_min_c": 6.5,
        "tolera_heladas_dias": 122,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "Diversifica la dieta familiar y rompe el ciclo del gorgojo de los Andes ('premnotrypes') cuando se "
            "intercala entre la papa y las leguminosas."
        ),
        "explicacion_especifica": (
            "Requiere suelos sueltos con materia orgánica y humedad moderada (>370 mm/año). Excelente opción para "
            "Viacha o parcelas con conservación de humedad."
        ),
    },
    "cebolla_zanahoria_altura": {
        "id": "cebolla_zanahoria_altura",
        "nombre_comun": "Cebolla & Zanahoria Criolla de Altura",
        "nombre_internacional": "High-Altitude Bulb Onion & Andean Root Carrot (Alliaceae / Apiaceae)",
        "nombre_cientifico": "Allium cepa / Daucus carota",
        "categoria": "Hortalizas de bulbo y raíz adaptadas al Altiplano",
        "presencia_rotaciones": "Hortalizas de ciclo corto seleccionables por el agricultor",
        "forma_3d": "bulbo_raiz",
        "color_primario": "#c2410c",
        "color_secundario": "#16a34a",
        "descripcion_internacional": (
            "Verduras universalmente conocidas pero cultivadas en el Altiplano bajo ecotipos criollos tolerantes al "
            "frío diurno/nocturno. La intensa radiación solar de La Paz (>3.700 m) favorece una alta concentración "
            "de carotenos y azúcares en la raíz, siempre que exista riego complementario o lluvia suficiente."
        ),
        "req_precip_min_mm": 410.0,
        "req_temp_min_c": 7.0,
        "tolera_heladas_dias": 125,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "Hortalizas comerciales de rápida rotación tras el cultivo de Haba/Tarwi, aprovechando el nitrógeno "
            "fijado en los primeros 20 cm del suelo."
        ),
        "explicacion_especifica": (
            "Su sistema radicular superficial (10–20 cm) exige al menos 410 mm anuales o microrriego; en años de "
            "sequía severa sin riego sufren estrés hídrico rápido."
        ),
    },
    "tomate_pimenton_campo": {
        "id": "tomate_pimenton_campo",
        "nombre_comun": "Tomate / Pimentón a Campo Abierto",
        "nombre_internacional": "Open-Field Tomato & Bell Pepper (Warm-Season Solanaceae)",
        "nombre_cientifico": "Solanum lycopersicum / Capsicum annuum",
        "categoria": "Hortaliza de fruto sensible a heladas (Contraste educativo)",
        "presencia_rotaciones": "No incluida en rotación a campo abierto (Requiere carpa solar/invernadero)",
        "forma_3d": "fruto_tomate",
        "color_primario": "#dc2626",
        "color_secundario": "#ef4444",
        "descripcion_internacional": (
            "Incluida como referencia comparativa para el usuario: aunque el tomate y el pimentón son hortalizas "
            "comunes a nivel global, son especies termófilas cuyos tejidos celulares colapsan a temperaturas "
            "inferiores a 0 °C."
        ),
        "req_precip_min_mm": 500.0,
        "req_temp_min_c": 14.0,
        "tolera_heladas_dias": 15,
        "fija_nitrogeno": False,
        "funcion_rotacion": (
            "No viable a cielo abierto en la puna altiplánica (>3.750 m); solo puede cultivarse dentro de "
            "'Walipinis' (invernaderos subterráneos andinos) o carpas solares."
        ),
        "explicacion_especifica": (
            "Demuestra por qué el sistema recomienda especies adaptadas (Quinua, Tarwi, Cañahua, Papa nativa) en "
            "lugar de hortalizas de clima templado/cálido a campo abierto."
        ),
    },
}


def evaluar_viabilidad_verdura(
    cultivo_id: str,
    datos_nasa: dict[str, Any],
    datos_sensor: dict[str, Any],
    escenario_id: str,
) -> dict[str, Any]:
    """Evalúa científicamente si es posible plantar la verdura/cultivo seleccionado y explica el porqué."""
    ficha = CATALOGO_CULTIVOS_VERDURAS.get(cultivo_id, CATALOGO_CULTIVOS_VERDURAS["quinua_real"])

    temp_nasa = datos_nasa.get("temperatura_media_c")
    precip_nasa = datos_nasa.get("precipitacion_total_mm")
    heladas_nasa = datos_nasa.get("heladas_dias_anio")
    hum_sensor = datos_sensor.get("humedad_suelo_pct")

    # Si los datos NASA son null (Contrato 9.2 sin validar), no inventamos viabilidad concluyente
    if temp_nasa is None or precip_nasa is None:
        return {
            "viable_codigo": "condicional_nulos",
            "veredicto_titulo": "Viabilidad condicionada (Datos climáticos NASA en estado `null`)",
            "color_estado": "orange",
            "puntaje_compatibilidad": 55,
            "razones": [
                "El archivo NASA POWER activo tiene `temperatura_media_c: null` o `precipitacion_total_mm: null` (Sección 9.2).",
                f"Por requisito botánico, **{ficha['nombre_comun']}** necesita al menos `{ficha['req_precip_min_mm']} mm/año` y temperatura media `>= {ficha['req_temp_min_c']} °C`.",
                f"**Por qué específico de este cultivo:** {ficha['explicacion_especifica']}",
            ],
        }

    razones: list[str] = []
    penalizaciones = 0

    # 1. Evaluación térmica y de heladas
    if float(temp_nasa) < ficha["req_temp_min_c"]:
        penalizaciones += 45
        razones.append(
            f"**Limitación térmica crítica:** La temperatura media de la parcela (`{temp_nasa} °C` según NASA POWER) "
            f"es inferior al umbral mínimo requerido por **{ficha['nombre_comun']}** (`{ficha['req_temp_min_c']} °C`)."
        )
    else:
        razones.append(
            f"**Régimen térmico favorable:** La temperatura media anual (`{temp_nasa} °C`) supera el mínimo fisiológico "
            f"del cultivo (`{ficha['req_temp_min_c']} °C`)."
        )

    if heladas_nasa is not None:
        if int(heladas_nasa) > ficha["tolera_heladas_dias"]:
            penalizaciones += 40
            razones.append(
                f"**Riesgo por heladas radiativas:** La parcela registra `{heladas_nasa} días de helada/año`, "
                f"superando la tolerancia máxima a campo abierto de esta especie (`{ficha['tolera_heladas_dias']} días`)."
            )
        else:
            razones.append(
                f"**Resistencia a heladas comprobada:** Tolera hasta `{ficha['tolera_heladas_dias']} días/año` bajo cero "
                f"(la parcela presenta `{heladas_nasa} días/año`)."
            )

    # 2. Evaluación hídrica (Precipitación NASA + Escenario)
    precip_efectiva = float(precip_nasa) * (0.78 if escenario_id == "sequia_altiplano" else 1.0)
    if precip_efectiva < ficha["req_precip_min_mm"]:
        deficit = round(ficha["req_precip_min_mm"] - precip_efectiva, 1)
        penalizaciones += 25
        razones.append(
            f"**Déficit hídrico estacional:** Requiere `{ficha['req_precip_min_mm']} mm/año` y la disponibilidad "
            f"estimada es de `{round(precip_efectiva, 1)} mm` (déficit de `{deficit} mm`; requeriría microrriego o cosecha de agua)."
        )
    else:
        razones.append(
            f"**Balance hídrico suficiente:** La precipitación disponible (`{round(precip_efectiva, 1)} mm/año`) "
            f"cubre la demanda mínima del cultivo (`{ficha['req_precip_min_mm']} mm/año`)."
        )

    # 3. Aporte edáfico y humedad local
    if ficha["fija_nitrogeno"]:
        razones.append(
            "**Sinergia edáfica positiva:** Al ser una leguminosa fijadora de nitrógeno (`Rhizobium`), regenera la "
            "fertilidad del suelo para los ciclos siguientes."
        )
    if hum_sensor is not None:
        razones.append(
            f"**Lectura local de referencia:** El nodo reporta `{hum_sensor}%` de humedad (rotulado explícitamente "
            f"según Contrato 9.1)."
        )

    razones.append(f"**Fundamento específico de la especie:** {ficha['explicacion_especifica']}")

    puntaje = max(10, min(98, 95 - penalizaciones))
    if penalizaciones >= 45:
        return {
            "viable_codigo": "no_viable_campo_abierto",
            "veredicto_titulo": "NO viable a campo abierto (Requiere carpa solar / Walipini)",
            "color_estado": "red",
            "puntaje_compatibilidad": puntaje,
            "razones": razones,
        }
    if penalizaciones >= 20:
        return {
            "viable_codigo": "viable_con_manejo",
            "veredicto_titulo": "SI es posible plantar con manejo suplementario (Microrriego / Cobertura)",
            "color_estado": "orange",
            "puntaje_compatibilidad": puntaje,
            "razones": razones,
        }
    return {
        "viable_codigo": "altamente_viable",
        "veredicto_titulo": "SI es altamente viable a campo abierto en esta parcela",
        "color_estado": "green",
        "puntaje_compatibilidad": puntaje,
        "razones": razones,
    }


# ==============================================================================
# COMPONENTE 3D DE ALTA DEFINICIÓN CON SOMBREADO POLIGONAL Y ANATOMÍA (CCv2)
# ==============================================================================
_VISOR_3D_VERDURA_HTML = """
<div class="crop3d-wrapper" id="crop3d-wrapper">
  <div class="crop3d-canvas-box" id="crop3d-canvas-box">
    <canvas id="crop3d-canvas"></canvas>
    <div class="crop3d-overlay-top">
      <span class="crop3d-tag" id="crop3d-tag">MODELO 3D BOTÁNICO SOMBREADO • 360°</span>
      <div class="crop3d-controls">
        <button class="c3d-btn" id="btn-wireframe" title="Alternar malla poligonal">Malla 3D</button>
        <button class="c3d-btn" id="btn-reset-cam" title="Centrar vista">Centrar</button>
      </div>
    </div>
    <div class="crop3d-overlay-bottom" id="crop3d-caption"></div>
  </div>

  <div class="crop3d-ficha">
    <div class="ficha-international-badge" id="ficha-intl"></div>
    <h3 class="ficha-title" id="ficha-title"></h3>
    <div class="ficha-scientific" id="ficha-sci"></div>
    <p class="ficha-desc" id="ficha-desc"></p>
    <div class="ficha-role-box" id="ficha-role"></div>
    <div class="ficha-Specs" id="ficha-specs"></div>
  </div>
</div>
"""

_VISOR_3D_VERDURA_CSS = """
:host {
  display: block;
  font-family: var(--st-font, 'Plus Jakarta Sans', sans-serif);
  color: #f8fafc;
}
.crop3d-wrapper {
  display: grid;
  grid-template-columns: 1.15fr 1.25fr;
  gap: 20px;
  background: linear-gradient(155deg, rgba(17, 22, 45, 0.96), rgba(9, 12, 26, 0.98));
  border: 1.5px solid rgba(124, 58, 237, 0.45);
  box-shadow: 0 12px 32px rgba(2, 6, 23, 0.65), inset 0 0 22px rgba(56, 189, 248, 0.06);
  border-radius: 16px;
  padding: 18px 20px;
  margin-bottom: 14px;
  align-items: stretch;
}
@media (max-width: 820px) {
  .crop3d-wrapper {
    grid-template-columns: 1fr;
  }
}
.crop3d-canvas-box {
  position: relative;
  min-height: 340px;
  background: radial-gradient(circle at 50% 42%, rgba(56, 189, 248, 0.14), rgba(6, 9, 22, 0.98) 76%);
  border-radius: 14px;
  border: 1.5px solid rgba(56, 189, 248, 0.38);
  box-shadow: inset 0 0 30px rgba(124, 58, 237, 0.18);
  overflow: hidden;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
}
.crop3d-canvas-box:active {
  cursor: grabbing;
}
#crop3d-canvas {
  width: 100%;
  height: 340px;
  display: block;
}
.crop3d-overlay-top {
  position: absolute;
  top: 10px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  pointer-events: none;
}
.crop3d-tag {
  font-family: var(--st-code-font, monospace);
  font-size: 0.68rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(56, 189, 248, 0.45);
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}
.crop3d-controls {
  display: flex;
  gap: 6px;
  pointer-events: auto;
}
.c3d-btn {
  font-family: var(--st-code-font, monospace);
  font-size: 0.68rem;
  color: #e2e8f0;
  background: rgba(17, 24, 48, 0.88);
  border: 1px solid rgba(139, 92, 246, 0.48);
  padding: 3px 9px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.c3d-btn:hover {
  border-color: #38bdf8;
  color: #38bdf8;
}
.crop3d-overlay-bottom {
  position: absolute;
  bottom: 10px;
  left: 12px;
  right: 12px;
  font-family: var(--st-code-font, monospace);
  font-size: 0.72rem;
  color: #cbd5e1;
  background: rgba(9, 13, 28, 0.84);
  border: 1px solid rgba(124, 58, 237, 0.32);
  padding: 5px 10px;
  border-radius: 8px;
  text-align: center;
  pointer-events: none;
}
.crop3d-ficha {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 8px;
}
.ficha-international-badge {
  display: inline-block;
  align-self: flex-start;
  font-family: var(--st-code-font, monospace);
  font-size: 0.73rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.42);
  padding: 4px 11px;
  border-radius: 999px;
}
.ficha-title {
  font-size: 1.38rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
}
.ficha-scientific {
  font-size: 0.84rem;
  font-style: italic;
  color: #94a3b8;
}
.ficha-desc {
  font-size: 0.87rem;
  line-height: 1.54;
  color: #e2e8f0;
  margin: 4px 0;
  background: rgba(15, 23, 42, 0.78);
  border-left: 4px solid #8b5cf6;
  padding: 10px 12px;
  border-radius: 0 8px 8px 0;
}
.ficha-role-box {
  font-size: 0.83rem;
  line-height: 1.46;
  color: #cbd5e1;
  padding: 9px 12px;
  border-radius: 8px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.35);
}
.ficha-Specs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
}
.spec-chip {
  font-family: var(--st-code-font, monospace);
  font-size: 0.73rem;
  color: #cbd5e1;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.28);
}
.spec-chip strong {
  color: #38bdf8;
}
"""

_VISOR_3D_VERDURA_JS = """
const viewerMap = new WeakMap();

function hexToRgb(hex) {
  const clean = (hex || "#38bdf8").replace("#", "");
  const num = parseInt(clean.length === 3 ? clean.split("").map((c) => c + c).join("") : clean, 16);
  return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
}

function shadeColor(rgb, light, spec) {
  const r = Math.min(255, Math.max(0, Math.round(rgb.r * light + spec * 255)));
  const g = Math.min(255, Math.max(0, Math.round(rgb.g * light + spec * 255)));
  const b = Math.min(255, Math.max(0, Math.round(rgb.b * light + spec * 255)));
  return `rgb(${r},${g},${b})`;
}

// Genera una superficie 3D cerrada de revolución / extrusión orgánica con caras poligonales
function addLatheSurface(faces, profileFn, rings, slices, colorHex, altColorHex) {
  const grid = [];
  for (let i = 0; i <= rings; i++) {
    const u = i / rings;
    const row = [];
    for (let j = 0; j < slices; j++) {
      const v = (j / slices) * Math.PI * 2;
      row.push(profileFn(u, v));
    }
    grid.push(row);
  }
  for (let i = 0; i < rings; i++) {
    for (let j = 0; j < slices; j++) {
      const jNext = (j + 1) % slices;
      const p00 = grid[i][j];
      const p10 = grid[i + 1][j];
      const p11 = grid[i + 1][jNext];
      const p01 = grid[i][jNext];
      const cHex = (altColorHex && (i + j) % 3 === 0) ? altColorHex : (p00.color || colorHex);
      faces.push({ pts: [p00, p10, p11, p01], rgb: hexToRgb(cHex), gloss: p00.gloss || 0.25 });
    }
  }
}

// Genera una hoja 3D curvada con nervadura central
function addLeaf3D(faces, baseX, baseY, baseZ, yaw, pitch, length, width, hexColor) {
  const steps = 6;
  const rgb = hexToRgb(hexColor);
  for (let i = 0; i < steps; i++) {
    const t0 = i / steps;
    const t1 = (i + 1) / steps;
    const w0 = Math.sin(t0 * Math.PI) * width;
    const w1 = Math.sin(t1 * Math.PI) * width;
    const arch0 = Math.sin(t0 * Math.PI) * (length * 0.22);
    const arch1 = Math.sin(t1 * Math.PI) * (length * 0.22);

    const localQuad = [
      { lx: -w0, ly: arch0, lz: t0 * length },
      { lx: w0,  ly: arch0, lz: t0 * length },
      { lx: w1,  ly: arch1, lz: t1 * length },
      { lx: -w1, ly: arch1, lz: t1 * length }
    ].map((p) => {
      const cy = Math.cos(pitch), sy = Math.sin(pitch);
      const y1 = p.ly * cy - p.lz * sy;
      const z1 = p.lz * cy + p.ly * sy;
      const cz = Math.cos(yaw), sz = Math.sin(yaw);
      return {
        x: baseX + p.lx * cz - z1 * sz,
        y: baseY - y1,
        z: baseZ + z1 * cz + p.lx * sz
      };
    });
    faces.push({ pts: localQuad, rgb: rgb, gloss: 0.2 });
  }
}

function buildBotanical3DModel(shapeType, primaryHex, secondaryHex) {
  const faces = [];
  const labels = [];

  if (shapeType === "panoja_quinua") {
    // Tallo leñoso central
    addLatheSurface(faces, (u, v) => {
      const y = 85 - u * 165;
      const r = 4.5 * (1 - u * 0.35);
      return { x: Math.cos(v) * r, y, z: Math.sin(v) * r, color: "#15803d" };
    }, 10, 10, "#15803d");

    // Racimos glomerulares densos de la panoja real con relieve 3D
    addLatheSurface(faces, (u, v) => {
      const y = 45 - u * 128;
      const env = Math.sin(u * Math.PI);
      const lobe = 1 + 0.28 * Math.sin(u * Math.PI * 9) * Math.cos(v * 6);
      const r = Math.max(4, 44 * Math.pow(env, 0.72) * lobe);
      return {
        x: Math.cos(v) * r,
        y,
        z: Math.sin(v) * r,
        color: Math.sin(u * 18 + v * 3) > 0.15 ? secondaryHex : primaryHex,
        gloss: 0.32
      };
    }, 26, 20, primaryHex, secondaryHex);

    // Hojas inferiores comestibles (Chiwa / Llipch'a)
    for (let k = 0; k < 6; k++) {
      const ang = (k / 6) * Math.PI * 2;
      addLeaf3D(faces, Math.cos(ang) * 6, 48 + (k % 2) * 12, Math.sin(ang) * 6, ang, 0.45, 42, 12, "#22c55e");
    }
    labels.push(
      { x: 38, y: -35, z: 0, text: "Panoja glomerular (Saponina + Grano)" },
      { x: -36, y: 52, z: 12, text: "Hojas tiernas comestibles (Chiwa)" }
    );
  } else if (shapeType === "vaina_leguminosa") {
    // Vaina 3D esculpida de Tarwi / Haba con curvatura orgánica y semillas abultadas
    addLatheSurface(faces, (u, v) => {
      const y = 78 - u * 156;
      const seedBump = 1 + 0.24 * Math.pow(Math.sin(u * Math.PI * 4), 2);
      const env = Math.sin(u * Math.PI);
      const rx = 26 * env * seedBump;
      const rz = 16 * env * seedBump;
      const curveX = Math.sin(u * Math.PI) * 16;
      return {
        x: curveX + Math.cos(v) * rx,
        y,
        z: Math.sin(v) * rz,
        color: Math.cos(v) > 0.7 ? "#4ade80" : primaryHex,
        gloss: 0.38
      };
    }, 28, 18, primaryHex, secondaryHex);

    // Raíz inferior con nódulos fijadores de nitrógeno (Rhizobium)
    for (let n = 0; n < 5; n++) {
      const ang = (n / 5) * Math.PI * 2;
      const nx = Math.cos(ang) * 18;
      const nz = Math.sin(ang) * 18;
      const ny = 76 + (n % 2) * 8;
      addLatheSurface(faces, (u, v) => {
        const phi = u * Math.PI;
        const r = 6.5;
        return {
          x: nx + Math.sin(phi) * Math.cos(v) * r,
          y: ny + Math.cos(phi) * r,
          z: nz + Math.sin(phi) * Math.sin(v) * r,
          color: "#facc15",
          gloss: 0.45
        };
      }, 6, 8, "#facc15");
    }
    labels.push(
      { x: 34, y: -15, z: 0, text: "Vaina proteica (>40% proteína)" },
      { x: -28, y: 78, z: 0, text: "Nódulos Rhizobium (+N al suelo)" }
    );
  } else if (shapeType === "tuberculo_papa") {
    // Tubérculo 3D de Papa Nativa / Luk'i con hendiduras ("ojos" meristemáticos)
    addLatheSurface(faces, (u, v) => {
      const phi = u * Math.PI;
      const eyeIndent = 1 - 0.14 * Math.pow(Math.sin(phi * 4) * Math.cos(v * 3), 2);
      const asym = 1 + 0.12 * Math.sin(phi * 2 + v);
      const rx = 56 * eyeIndent * asym;
      const ry = 44 * eyeIndent;
      const rz = 46 * eyeIndent * asym;
      const isEye = Math.sin(phi * 4) * Math.cos(v * 3) > 0.75;
      return {
        x: Math.sin(phi) * Math.cos(v) * rx,
        y: Math.cos(phi) * ry,
        z: Math.sin(phi) * Math.sin(v) * rz,
        color: isEye ? "#fde047" : primaryHex,
        gloss: 0.22
      };
    }, 24, 22, primaryHex, secondaryHex);
    labels.push(
      { x: 48, y: -18, z: 0, text: "Peridermis rica en antocianinas" },
      { x: -42, y: 24, z: 15, text: "Yemas / Ojos meristemáticos" }
    );
  } else if (shapeType === "planta_canahua") {
    // Arbusto hemisférico ramificado de Cañahua con follaje denso resistente a heladas
    addLatheSurface(faces, (u, v) => {
      const phi = u * Math.PI * 0.85;
      const crown = 1 + 0.22 * Math.sin(u * 16) * Math.cos(v * 7);
      const r = 52 * Math.sin(phi) * crown;
      const y = 40 - Math.cos(phi) * 58;
      return {
        x: Math.cos(v) * r,
        y,
        z: Math.sin(v) * r,
        color: u < 0.45 ? secondaryHex : (u < 0.75 ? primaryHex : "#16a34a"),
        gloss: 0.28
      };
    }, 22, 20, primaryHex, secondaryHex);
    labels.push(
      { x: 44, y: -25, z: 0, text: "Grano sin saponina (Cañahua)" },
      { x: -40, y: 30, z: 0, text: "Arquitectura térmica anti-helada (-8 °C)" }
    );
  } else if (shapeType === "tuberculo_oca") {
    // Tubérculo cilíndrico anillado de Oca Andina con segmentos acanalados reales
    addLatheSurface(faces, (u, v) => {
      const y = 70 - u * 140;
      const env = Math.pow(Math.sin(u * Math.PI), 0.65);
      const ringWave = 1 + 0.22 * Math.sin(u * Math.PI * 8);
      const r = Math.max(5, 32 * env * ringWave);
      const curveX = Math.cos(u * Math.PI * 1.2) * 10;
      const isScale = Math.sin(u * Math.PI * 8) < -0.55;
      return {
        x: curveX + Math.cos(v) * r,
        y,
        z: Math.sin(v) * r,
        color: isScale ? secondaryHex : primaryHex,
        gloss: 0.42
      };
    }, 30, 18, primaryHex, secondaryHex);
    labels.push(
      { x: 35, y: -20, z: 0, text: "Anillos tuberosos dulces (Oxalis)" },
      { x: -32, y: 32, z: 0, text: "Escamas meristemáticas bicolores" }
    );
  } else if (shapeType === "bulbo_raiz") {
    // Raíz cónica anaranjada + bulbo + penacho de hojas verdes 3D
    addLatheSurface(faces, (u, v) => {
      const y = -12 + u * 98;
      const r = Math.max(3, 30 * Math.pow(1 - u, 0.78) * (1 + 0.06 * Math.sin(u * 25)));
      return {
        x: Math.cos(v) * r,
        y,
        z: Math.sin(v) * r,
        color: primaryHex,
        gloss: 0.3
      };
    }, 20, 18, primaryHex);

    for (let k = 0; k < 8; k++) {
      const ang = (k / 8) * Math.PI * 2;
      addLeaf3D(faces, Math.cos(ang) * 6, -12, Math.sin(ang) * 6, ang, 1.05, 58, 9, "#22c55e");
    }
    labels.push(
      { x: 36, y: -48, z: 0, text: "Follaje fotosintético de altura" },
      { x: -34, y: 38, z: 0, text: "Raíz reservante rica en carotenos" }
    );
  } else {
    // Fruto lobulado brillante en 3D (Tomate / Pimentón) con cáliz verde estrellado
    addLatheSurface(faces, (u, v) => {
      const phi = u * Math.PI;
      const lobe = 1 + 0.14 * Math.cos(v * 6) * Math.sin(phi);
      const rx = 50 * Math.sin(phi) * lobe;
      const ry = 40 * Math.cos(phi);
      const rz = 50 * Math.sin(phi) * lobe;
      return {
        x: Math.cos(v) * rx,
        y: ry + 8,
        z: Math.sin(v) * rz,
        color: u < 0.16 ? "#16a34a" : primaryHex,
        gloss: 0.58
      };
    }, 22, 24, primaryHex, secondaryHex);

    for (let k = 0; k < 6; k++) {
      const ang = (k / 6) * Math.PI * 2;
      addLeaf3D(faces, Math.cos(ang) * 5, -32, Math.sin(ang) * 5, ang, 0.25, 28, 7, "#16a34a");
    }
    labels.push(
      { x: 42, y: -32, z: 0, text: "Cáliz y pedúnculo herbáceo" },
      { x: -44, y: 18, z: 0, text: "Pericarpio sensible a heladas (<0 °C)" }
    );
  }

  return { faces, labels };
}

export default function (component) {
  const { data, parentElement } = component;
  if (!data) return;

  const ficha = data.ficha || {};
  parentElement.querySelector("#ficha-intl").textContent = `Guía internacional: ${ficha.nombre_internacional || ""}`;
  parentElement.querySelector("#ficha-title").textContent = ficha.nombre_comun || "";
  parentElement.querySelector("#ficha-sci").textContent = `${ficha.nombre_cientifico || ""} • ${ficha.categoria || ""}`;
  parentElement.querySelector("#ficha-desc").textContent = ficha.descripcion_internacional || "";
  parentElement.querySelector("#ficha-role").innerHTML = `<strong>Rol en rotación del Altiplano:</strong> ${ficha.funcion_rotacion || ""}`;
  parentElement.querySelector("#crop3d-caption").textContent = `${ficha.presencia_rotaciones || ""}`;

  const specsEl = parentElement.querySelector("#ficha-specs");
  if (specsEl) {
    specsEl.innerHTML = `
      <span class="spec-chip">Lluvia mín.: <strong>${ficha.req_precip_min_mm} mm/año</strong></span>
      <span class="spec-chip">Temp. media mín.: <strong>${ficha.req_temp_min_c} °C</strong></span>
      <span class="spec-chip">Tolera heladas: <strong>hasta ${ficha.tolera_heladas_dias} días/año</strong></span>
      <span class="spec-chip">Fija Nitrógeno: <strong>${ficha.fija_nitrogeno ? "Sí (Rhizobium)" : "No"}</strong></span>
    `;
  }

  const canvas = parentElement.querySelector("#crop3d-canvas");
  const box = parentElement.querySelector("#crop3d-canvas-box");
  if (!canvas || !box) return;

  const model3D = buildBotanical3DModel(
    ficha.forma_3d || "panoja_quinua",
    ficha.color_primario || "#881337",
    ficha.color_secundario || "#e11d48"
  );

  let st = viewerMap.get(parentElement);
  if (!st) {
    st = {
      rafId: null,
      model: model3D,
      rotY: 0.45,
      rotX: 0.24,
      zoom: 1.08,
      wireframe: false,
      dragging: false,
      lastX: 0,
      lastY: 0
    };
    viewerMap.set(parentElement, st);

    const btnWire = parentElement.querySelector("#btn-wireframe");
    if (btnWire) {
      btnWire.onclick = (e) => {
        e.stopPropagation();
        st.wireframe = !st.wireframe;
      };
    }
    const btnReset = parentElement.querySelector("#btn-reset-cam");
    if (btnReset) {
      btnReset.onclick = (e) => {
        e.stopPropagation();
        st.rotY = 0.45;
        st.rotX = 0.24;
        st.zoom = 1.08;
      };
    }

    box.onpointerdown = (e) => {
      st.dragging = true;
      st.lastX = e.clientX;
      st.lastY = e.clientY;
    };
    window.addEventListener("pointerup", () => {
      st.dragging = false;
    });
    box.onpointermove = (e) => {
      if (!st.dragging) return;
      const dx = e.clientX - st.lastX;
      const dy = e.clientY - st.lastY;
      st.lastX = e.clientX;
      st.lastY = e.clientY;
      st.rotY += dx * 0.012;
      st.rotX = Math.max(-1.05, Math.min(1.05, st.rotX + dy * 0.012));
    };
    box.onwheel = (e) => {
      e.preventDefault();
      st.zoom = Math.max(0.75, Math.min(1.55, st.zoom - e.deltaY * 0.0008));
    };

    const ctx = canvas.getContext("2d");
    const lightDir = { x: -0.45, y: -0.58, z: 0.68 };

    const transformPt = (p, cosY, sinY, cosX, sinX, cx, cy, zoom) => {
      const x1 = p.x * cosY - p.z * sinY;
      const z1 = p.z * cosY + p.x * sinY;
      const y2 = p.y * cosX - z1 * sinX;
      const z2 = z1 * cosX + p.y * sinX;
      const scale = (310 * zoom) / (310 + z2 + 110);
      return {
        x: x1,
        y: y2,
        z: z2,
        sx: cx + x1 * scale,
        sy: cy + y2 * scale
      };
    };

    const renderLoop = () => {
      if (!canvas.isConnected) return;
      const w = canvas.clientWidth || 380;
      const h = canvas.clientHeight || 340;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }

      if (!st.dragging) {
        st.rotY += 0.009;
      }

      ctx.clearRect(0, 0, w, h);
      const cx = w / 2;
      const cy = h / 2 - 4;

      // Pedestal holográfico 3D en la base
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(cx, h - 42, 78 * st.zoom, 16 * st.zoom, 0, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(56, 189, 248, 0.12)";
      ctx.fill();
      ctx.lineWidth = 1.3;
      ctx.strokeStyle = "rgba(56, 189, 248, 0.45)";
      ctx.stroke();

      ctx.beginPath();
      ctx.ellipse(cx, h - 42, 52 * st.zoom, 10 * st.zoom, 0, 0, Math.PI * 2);
      ctx.strokeStyle = "rgba(139, 92, 246, 0.45)";
      ctx.stroke();
      ctx.restore();

      const cosY = Math.cos(st.rotY);
      const sinY = Math.sin(st.rotY);
      const cosX = Math.cos(st.rotX);
      const sinX = Math.sin(st.rotX);

      // Proyectar y sombrear caras poligonales con iluminación direccional + especular
      const drawList = st.model.faces.map((f) => {
        const tPts = f.pts.map((pt) => transformPt(pt, cosY, sinY, cosX, sinX, cx, cy, st.zoom));
        const ux = tPts[1].x - tPts[0].x;
        const uy = tPts[1].y - tPts[0].y;
        const uz = tPts[1].z - tPts[0].z;
        const vx = tPts[2].x - tPts[0].x;
        const vy = tPts[2].y - tPts[0].y;
        const vz = tPts[2].z - tPts[0].z;

        let nx = uy * vz - uz * vy;
        let ny = uz * vx - ux * vz;
        let nz = ux * vy - uy * vx;
        const len = Math.hypot(nx, ny, nz) || 1;
        nx /= len; ny /= len; nz /= len;

        if (nz < 0) {
          nx = -nx; ny = -ny; nz = -nz;
        }

        const dot = Math.max(0, nx * lightDir.x + ny * lightDir.y + nz * lightDir.z);
        const light = 0.34 + dot * 0.72;
        const spec = Math.pow(dot, 12) * (f.gloss || 0.25);
        const avgZ = (tPts[0].z + tPts[1].z + tPts[2].z + tPts[3].z) * 0.25;

        return {
          tPts,
          avgZ,
          fill: shadeColor(f.rgb, light, spec)
        };
      });

      // Ordenar de atrás hacia adelante (algoritmo del pintor)
      drawList.sort((a, b) => b.avgZ - a.avgZ);

      drawList.forEach((d) => {
        ctx.beginPath();
        ctx.moveTo(d.tPts[0].sx, d.tPts[0].sy);
        for (let i = 1; i < d.tPts.length; i++) {
          ctx.lineTo(d.tPts[i].sx, d.tPts[i].sy);
        }
        ctx.closePath();
        ctx.fillStyle = d.fill;
        ctx.fill();
        ctx.lineWidth = st.wireframe ? 0.95 : 0.45;
        ctx.strokeStyle = st.wireframe ? "rgba(56, 189, 248, 0.65)" : d.fill;
        ctx.stroke();
      });

      // Etiquetas anatómicas flotantes en 3D
      ctx.font = "600 10.5px monospace";
      (st.model.labels || []).forEach((lb) => {
        const tp = transformPt(lb, cosY, sinY, cosX, sinX, cx, cy, st.zoom);
        ctx.beginPath();
        ctx.arc(tp.sx, tp.sy, 3.2, 0, Math.PI * 2);
        ctx.fillStyle = "#38bdf8";
        ctx.fill();

        const boxW = ctx.measureText(lb.text).width + 12;
        const bx = tp.sx > cx ? Math.min(w - boxW - 6, tp.sx + 8) : Math.max(6, tp.sx - boxW - 8);
        const by = tp.sy - 10;
        ctx.fillStyle = "rgba(9, 13, 28, 0.86)";
        ctx.strokeStyle = "rgba(56, 189, 248, 0.55)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(bx, by, boxW, 19, 4);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "#e2e8f0";
        ctx.fillText(lb.text, bx + 6, by + 13);
      });

      st.rafId = requestAnimationFrame(renderLoop);
    };
    st.rafId = requestAnimationFrame(renderLoop);
  } else {
    st.model = model3D;
  }

  return () => {
    const s = viewerMap.get(parentElement);
    if (s && s.rafId) cancelAnimationFrame(s.rafId);
  };
}
"""

_COMPONENTE_VISOR_3D_CCV2 = st.components.v2.component(
    "visor_botanico_3d_altiplano_v3",
    html=_VISOR_3D_VERDURA_HTML,
    css=_VISOR_3D_VERDURA_CSS,
    js=_VISOR_3D_VERDURA_JS,
)


def renderizar_explorador_verduras_3d(
    parcela_id: str,
    datos_nasa: dict[str, Any],
    datos_sensor: dict[str, Any],
    escenario_id: str,
    cultivo_sincronizado_id: str | None = None,
) -> None:
    """Renderiza el módulo complementario de exploración 3D y simulador de viabilidad de verduras/cultivos."""
    with st.container(border=True):
        st.header(
            "3.1 Visor botánico 3D y simulador de viabilidad de verduras y cultivos (Contexto internacional)",
            icon=":material/view_in_ar:",
        )
        st.caption(
            "Integrado con las 3 rotaciones: haz clic en cualquier cultivo de las tarjetas de rotación de arriba "
            "o elige uno aquí para inspeccionar su estructura en 3D (360°), conocer su descripción para otros países "
            "y evaluar qué verduras puedes plantar en tu parcela y el porqué agronómico específico."
        )

        opciones_ids = list(CATALOGO_CULTIVOS_VERDURAS.keys())
        indice_default = 0
        if cultivo_sincronizado_id in opciones_ids:
            indice_default = opciones_ids.index(cultivo_sincronizado_id)
            if st.session_state.get("ultimo_cultivo_sincronizado") != cultivo_sincronizado_id:
                st.session_state["ultimo_cultivo_sincronizado"] = cultivo_sincronizado_id
                st.session_state["selector_cultivo_visor_3d"] = cultivo_sincronizado_id

        col_sel_3d, col_multi = st.columns([2, 3])
        with col_sel_3d:
            cultivo_activo_id = st.selectbox(
                "Inspeccionar verdura / cultivo en el visor 3D (360°)",
                options=opciones_ids,
                index=indice_default,
                format_func=lambda cid: (
                    f"{CATALOGO_CULTIVOS_VERDURAS[cid]['nombre_comun']} — "
                    f"({CATALOGO_CULTIVOS_VERDURAS[cid]['nombre_internacional'].split('(')[0].strip()})"
                ),
                key="selector_cultivo_visor_3d",
            )

        with col_multi:
            verduras_elegidas = st.multiselect(
                "Selecciona qué verduras y cultivos deseas plantar en tu parcela para verificar si es posible",
                options=opciones_ids,
                default=["quinua_real", "tarwi_haba", "oca_isaño", "cebolla_zanahoria_altura", "tomate_pimenton_campo"],
                format_func=lambda cid: CATALOGO_CULTIVOS_VERDURAS[cid]["nombre_comun"],
                key="multiselect_verduras_usuario",
            )

        ficha_activa = CATALOGO_CULTIVOS_VERDURAS[cultivo_activo_id]
        _COMPONENTE_VISOR_3D_CCV2(
            key="visor_3d_verdura_instancia",
            data={"ficha": ficha_activa},
        )

        st.subheader(
            f"Dictamen de viabilidad de siembra en `{parcela_id}` para tus verduras seleccionadas",
            icon=":material/fact_check:",
        )

        if not verduras_elegidas:
            st.info(
                "Selecciona al menos una verdura o cultivo en el selector múltiple de arriba para evaluar si es posible plantarla.",
                title="Ninguna verdura seleccionada",
                icon=":material/touch_app:",
            )
            return

        cols_eval = st.columns(min(len(verduras_elegidas), 2), border=True)
        for idx, cid in enumerate(verduras_elegidas):
            ficha = CATALOGO_CULTIVOS_VERDURAS[cid]
            dictamen = evaluar_viabilidad_verdura(
                cultivo_id=cid,
                datos_nasa=datos_nasa,
                datos_sensor=datos_sensor,
                escenario_id=escenario_id,
            )
            with cols_eval[idx % len(cols_eval)]:
                st.badge(
                    dictamen["veredicto_titulo"],
                    icon=":material/check_circle:" if dictamen["color_estado"] == "green" else (
                        ":material/warning:" if dictamen["color_estado"] == "orange" else ":material/cancel:"
                    ),
                    color=dictamen["color_estado"],
                )
                st.subheader(f"{ficha['nombre_comun']}")
                st.caption(f"*{ficha['nombre_cientifico']}* • Equivalencia internacional: **{ficha['nombre_internacional']}**")
                st.progress(
                    dictamen["puntaje_compatibilidad"],
                    text=f"Índice de viabilidad agroclimática: {dictamen['puntaje_compatibilidad']}%",
                )
                for razon in dictamen["razones"]:
                    st.markdown(f"- {razon}")
