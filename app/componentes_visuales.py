"""Componentes visuales e interactivos inspirados en la imagen de referencia NASA Space Apps La Paz 2026 (`app/componentes_visuales.py`).

Implementa:
1. Consola Interactiva Principal (fiel a la imagen de referencia):
   - Banner superior con emblema agrícola verde neón, título "Consola de parcela y escenarios", paisaje andino al atardecer con tractor e indicador "Sistema listo".
   - Tarjeta "Selección de parcela piloto" con miniatura satelital, polígono cian brillante y selectores de localidad/parcela.
   - Tarjeta "Vista previa" con terreno 3D en perspectiva del Altiplano, polígono holográfico de parcela, brújula N, Área (12.5 ha) y Altitud (3.640 m / 3.799 m).
   - Tarjeta "Escenario del motor (Rudy)" con holograma azul del motor y selector de Contrato 9.3.
   - Tarjeta "Prioridades del productor andino" con sliders de colores neón (azul agua, verde suelo, naranja forraje) e ilustración holográfica de ganadería sostenible en los Andes.
   - Barra "Estado del nodo Pico W (Nefi / Joel)" con chip electrónico, estado "Conectado" y barras de intensidad de señal.
   - Botones "Restablecer" y "Aplicar configuración >" con sincronización bidireccional a Python (`st.components.v2`).
2. Tablero 3D de las 3 Rotaciones (Rudy -> Jorge).
3. Prisma 3D de Horizontes del Suelo (SMAP 0-5cm vs Zona radicular 20-30cm).
4. Gráficos Apache ECharts en tema oscuro espacial.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

# ==============================================================================
# 1. PANEL LATERAL ESPACIAL NASA SPACE APPS LA PAZ 2026
# ==============================================================================
def renderizar_decoracion_sidebar_nasa() -> None:
    """Renderiza el emblema NASA Space Apps La Paz 2026 y la ilustración satelital en la barra lateral."""
    st.html(
        """
        <div style="
            background: linear-gradient(180deg, #0d1229 0%, #070a18 100%);
            border: 1px solid rgba(124, 58, 237, 0.38);
            border-radius: 16px;
            padding: 16px 14px;
            text-align: center;
            box-shadow: 0 0 28px rgba(124, 58, 237, 0.18);
            margin-bottom: 10px;
            position: relative;
            overflow: hidden;
        ">
            <!-- Emblema circular estilo NASA Meatball -->
            <div style="
                width: 78px;
                height: 78px;
                margin: 0 auto 10px auto;
                border-radius: 50%;
                background: radial-gradient(circle at 35% 30%, #1d4ed8, #0a194e 75%);
                border: 2px solid rgba(56, 189, 248, 0.55);
                box-shadow: 0 0 22px rgba(37, 99, 235, 0.55);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            ">
                <svg viewBox="0 0 100 100" width="70" height="70">
                    <circle cx="25" cy="25" r="1.4" fill="#fff"/>
                    <circle cx="75" cy="22" r="1.2" fill="#fff"/>
                    <circle cx="68" cy="75" r="1.5" fill="#fff"/>
                    <ellipse cx="50" cy="52" rx="40" ry="14" fill="none" stroke="#f8fafc" stroke-width="2" transform="rotate(-22 50 52)"/>
                    <path d="M 16 62 Q 52 20 86 34 Q 52 40 16 62 Z" fill="#ef4444"/>
                    <text x="50" y="57" text-anchor="middle" fill="#ffffff" font-family="Georgia, serif" font-weight="900" font-size="22" letter-spacing="1">NASA</text>
                </svg>
            </div>
            <div style="font-weight: 800; font-size: 1.08rem; color: #f8fafc; letter-spacing: 0.01em;">
                Space Apps
            </div>
            <div style="font-size: 0.82rem; font-weight: 600; color: #cbd5e1; margin-bottom: 10px;">
                La Paz 2026
            </div>
            <!-- Silueta de cordillera iluminada -->
            <svg viewBox="0 0 260 48" width="100%" height="40" style="display:block; opacity:0.85;">
                <defs>
                    <linearGradient id="mtnGlow" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.7"/>
                        <stop offset="100%" stop-color="#070a18" stop-opacity="0.0"/>
                    </linearGradient>
                </defs>
                <path d="M0,48 L0,32 L42,14 L82,30 L132,6 L178,26 L218,12 L260,30 L260,48 Z" fill="url(#mtnGlow)" stroke="#a855f7" stroke-width="1.2"/>
            </svg>
        </div>
        """
    )


def renderizar_pie_sidebar_satelite() -> None:
    """Renderiza el satélite orbital y el horizonte terrestre en la parte inferior de la barra lateral."""
    st.html(
        """
        <div style="
            background: radial-gradient(circle at 50% 110%, rgba(56, 189, 248, 0.32), rgba(10, 14, 32, 0.95) 68%);
            border: 1px solid rgba(56, 189, 248, 0.28);
            border-radius: 16px;
            padding: 16px 12px 14px 12px;
            text-align: center;
            margin-top: 12px;
            position: relative;
            overflow: hidden;
        ">
            <svg viewBox="0 0 220 90" width="100%" height="78">
                <!-- Satélite SMAP / Sentinel estilizado -->
                <g transform="translate(110, 34) rotate(-18)">
                    <rect x="-52" y="-7" width="34" height="14" rx="2" fill="#1e3a8a" stroke="#38bdf8" stroke-width="1.3"/>
                    <line x1="-40" y1="-7" x2="-40" y2="7" stroke="#38bdf8" stroke-width="0.8"/>
                    <line x1="-29" y1="-7" x2="-29" y2="7" stroke="#38bdf8" stroke-width="0.8"/>
                    <rect x="18" y="-7" width="34" height="14" rx="2" fill="#1e3a8a" stroke="#38bdf8" stroke-width="1.3"/>
                    <line x1="29" y1="-7" x2="29" y2="7" stroke="#38bdf8" stroke-width="0.8"/>
                    <line x1="40" y1="-7" x2="40" y2="7" stroke="#38bdf8" stroke-width="0.8"/>
                    <rect x="-12" y="-10" width="24" height="20" rx="3" fill="#334155" stroke="#93c5fd" stroke-width="1.5"/>
                    <circle cx="0" cy="0" r="4.5" fill="#38bdf8"/>
                    <path d="M -8,10 Q 0,22 8,10" fill="none" stroke="#38bdf8" stroke-width="1.4"/>
                </g>
                <!-- Curva del planeta Tierra iluminado -->
                <path d="M -20,95 Q 110,48 240,95" fill="#0284c7" fill-opacity="0.28" stroke="#38bdf8" stroke-width="2"/>
            </svg>
            <div style="
                font-size: 0.78rem;
                font-style: italic;
                color: #cbd5e1;
                margin-top: 4px;
            ">
                Innovación que cultiva el futuro
            </div>
        </div>
        """
    )


# ==============================================================================
# 2. CONSOLA INTERACTIVA DE PARCELA Y ESCENARIOS (FIEL A LA IMAGEN DE REFERENCIA)
# ==============================================================================
_CONSOLA_HTML = """
<div class="space-console" id="space-console">
  <!-- 1. BANNER SUPERIOR HERO (Con tractor al atardecer, montaña andina, icono planta y "Sistema listo") -->
  <div class="hero-banner" id="hero-banner">
    <svg class="hero-art-svg" viewBox="0 0 1200 220" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="skySunset" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#080b1a"/>
          <stop offset="45%" stop-color="#151936"/>
          <stop offset="78%" stop-color="#3b2645"/>
          <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.55"/>
        </linearGradient>
        <radialGradient id="sunGlow" cx="92%" cy="58%" r="28%">
          <stop offset="0%" stop-color="#fef08a" stop-opacity="0.95"/>
          <stop offset="35%" stop-color="#f59e0b" stop-opacity="0.55"/>
          <stop offset="100%" stop-color="#151936" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="1200" height="220" fill="url(#skySunset)"/>
      <circle cx="1090" cy="126" r="190" fill="url(#sunGlow)"/>
      <!-- Cordillera del Illimani / Altiplano -->
      <path d="M520,165 L640,92 L725,132 L830,68 L945,135 L1045,98 L1200,152 L1200,220 L520,220 Z" fill="#1e2442" opacity="0.85"/>
      <path d="M640,92 L668,112 L618,115 Z" fill="#cbd5e1" opacity="0.45"/>
      <path d="M830,68 L866,98 L798,96 Z" fill="#e2e8f0" opacity="0.55"/>
      <!-- Surcos agrícolas verdes iluminados -->
      <path d="M480,220 L740,152 L1200,152 L1200,220 Z" fill="#0f291e"/>
      <g stroke="#22c55e" stroke-width="1.6" opacity="0.45">
        <line x1="560" y1="220" x2="780" y2="154"/>
        <line x1="650" y1="220" x2="835" y2="154"/>
        <line x1="740" y1="220" x2="890" y2="154"/>
        <line x1="840" y1="220" x2="950" y2="154"/>
        <line x1="950" y1="220" x2="1020" y2="154"/>
        <line x1="1060" y1="220" x2="1095" y2="154"/>
      </g>
      <!-- Silueta detallada de tractor agrícola moderno en el horizonte -->
      <g transform="translate(925, 92)">
        <!-- Cabina -->
        <path d="M38,10 L78,10 L86,42 L32,42 Z" fill="#1e293b" stroke="#f59e0b" stroke-width="1.5"/>
        <path d="M43,14 L74,14 L79,38 L38,38 Z" fill="#38bdf8" fill-opacity="0.28"/>
        <!-- Capó delantero y chimenea -->
        <rect x="4" y="28" width="32" height="20" rx="3" fill="#dc2626" stroke="#f97316" stroke-width="1.2"/>
        <rect x="14" y="10" width="4" height="18" fill="#475569"/>
        <!-- Faro encendido -->
        <circle cx="5" cy="35" r="3.5" fill="#fef08a"/>
        <polygon points="5,35 -45,22 -45,48" fill="#fef08a" opacity="0.18"/>
        <!-- Rueda trasera gigante -->
        <circle cx="68" cy="56" r="22" fill="#0f172a" stroke="#334155" stroke-width="4"/>
        <circle cx="68" cy="56" r="10" fill="#dc2626" stroke="#fbbf24" stroke-width="2"/>
        <!-- Rueda delantera -->
        <circle cx="16" cy="61" r="16" fill="#0f172a" stroke="#334155" stroke-width="3.5"/>
        <circle cx="16" cy="61" r="7" fill="#dc2626" stroke="#fbbf24" stroke-width="1.8"/>
      </g>
    </svg>

    <div class="hero-banner-content">
      <div class="hero-left-group">
        <!-- Icono de hoja y surcos verde neón -->
        <div class="neon-plant-logo">
          <svg viewBox="0 0 80 80" width="66" height="66">
            <defs>
              <linearGradient id="leafGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#84cc16"/>
                <stop offset="100%" stop-color="#15803d"/>
              </linearGradient>
            </defs>
            <path d="M40,42 C20,42 14,22 14,12 C28,12 40,22 40,42 Z" fill="url(#leafGrad)"/>
            <path d="M40,42 C40,20 56,10 68,10 C68,26 56,42 40,42 Z" fill="#4ade80"/>
            <path d="M10,56 Q40,38 70,52 L66,60 Q38,48 14,64 Z" fill="#22c55e"/>
            <path d="M18,68 Q44,54 72,64 L68,72 Q42,63 22,74 Z" fill="#16a34a"/>
          </svg>
        </div>
        <div>
          <h1 class="console-main-title">Consola de parcela<br/>y escenarios</h1>
          <p class="console-subtitle">Configura tu simulación agrícola y explora distintos escenarios</p>
        </div>
      </div>

      <div class="system-ready-pill">
        <span class="ready-dot"></span>
        <span>Sistema listo</span>
        <svg viewBox="0 0 28 16" width="22" height="14" fill="none" stroke="#4ade80" stroke-width="2">
          <polyline points="1,8 7,8 10,2 15,14 19,6 22,8 27,8"/>
        </svg>
      </div>
    </div>
  </div>

  <!-- 2. FILA INTERMEDIA: SELECCIÓN DE PARCELA + ESCENARIO MOTOR (IZQ) | VISTA PREVIA 3D (DER) -->
  <div class="middle-grid">
    <div class="left-stack">
      <!-- Tarjeta: Selección de parcela piloto -->
      <div class="neon-card">
        <div class="card-title-row">
          <div class="title-with-icon">
            <span class="icon-purple">🚜</span>
            <span>Selección de parcela piloto</span>
          </div>
          <span class="help-badge" title="Selecciona la parcela piloto del Altiplano boliviano">?</span>
        </div>

        <div class="parcel-select-body">
          <!-- Miniatura satelital con polígono cian brillante -->
          <div class="sat-thumb-box">
            <svg viewBox="0 0 180 140" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
              <rect width="180" height="140" fill="#2d3a2e"/>
              <!-- Textura de parcelas vecinas -->
              <path d="M0,25 L180,55 M0,85 L180,115 M45,0 L20,140 M125,0 L95,140" stroke="#475548" stroke-width="2"/>
              <polygon points="0,0 45,0 32,32 0,25" fill="#3f4d3b"/>
              <polygon points="45,0 125,0 112,44 32,32" fill="#4f5e46"/>
              <polygon points="125,0 180,0 180,55 112,44" fill="#3a4635"/>
              <!-- Polígono activo con resplandor cian -->
              <polygon points="48,36 128,48 106,118 26,96" fill="rgba(56, 189, 248, 0.24)" stroke="#38bdf8" stroke-width="3"/>
              <!-- Pin de ubicación central -->
              <circle cx="77" cy="76" r="10" fill="#38bdf8"/>
              <circle cx="77" cy="76" r="4" fill="#0f172a"/>
            </svg>
          </div>

          <div class="parcel-dropdowns">
            <label class="field-label">Departamento / Municipio</label>
            <div class="custom-select-wrap">
              <span class="select-prefix">📍</span>
              <select id="select-municipio" class="neon-select">
                <option value="piloto_01">Patacamaya (La Paz)</option>
                <option value="viacha_02">Viacha — Jalsuri (La Paz)</option>
                <option value="ejemplo_nulos">Contrato 9.2 (Prueba Nulos)</option>
              </select>
            </div>

            <label class="field-label" style="margin-top:8px;">Parcela piloto</label>
            <div class="custom-select-wrap">
              <span class="select-prefix">田</span>
              <select id="select-parcela" class="neon-select">
                <option value="piloto_01">Parcela piloto 01 (Altiplano)</option>
                <option value="viacha_02">Parcela Viacha 02 (Norte)</option>
                <option value="ejemplo_nulos">Parcela experimental (Con null)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Tarjeta: Escenario del motor (Rudy) -->
      <div class="neon-card">
        <div class="card-title-row">
          <div class="title-with-icon">
            <span class="icon-purple">⚙️</span>
            <span>Escenario del motor (Rudy)</span>
          </div>
        </div>

        <div class="engine-body">
          <!-- Ilustración holográfica cian del motor de reglas -->
          <div class="engine-holo">
            <svg viewBox="0 0 130 95" width="115" height="82">
              <defs>
                <filter id="cyanGlow">
                  <feGaussianBlur stdDeviation="2.5" result="blur"/>
                  <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <g filter="url(#cyanGlow)" stroke="#38bdf8" stroke-width="1.8" fill="rgba(14, 116, 144, 0.22)">
                <rect x="28" y="24" width="68" height="46" rx="8"/>
                <rect x="40" y="14" width="44" height="10" rx="3"/>
                <circle cx="50" cy="48" r="12"/>
                <circle cx="50" cy="48" r="5"/>
                <circle cx="78" cy="48" r="9"/>
                <path d="M14,38 L28,38 M14,56 L28,56 M96,38 L114,38 M96,56 L114,56"/>
                <path d="M36,70 L30,82 L94,82 L88,70"/>
              </g>
            </svg>
          </div>

          <div class="engine-select-col">
            <label class="field-label">Contrato</label>
            <div class="custom-select-wrap">
              <span class="select-prefix">📄</span>
              <select id="select-escenario" class="neon-select">
                <option value="contrato_base">9.3 base (Demostración oficial)</option>
                <option value="sequia_altiplano">Caso 1: Sequía (&lt;350 mm/año)</option>
                <option value="heladas_severas">Caso 2: Heladas severas (&gt;125 días)</option>
                <option value="prioridad_suelo">Caso 3: Suelo degradado (Fijación N)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Columna Derecha: Vista Previa 3D del Terreno del Altiplano -->
    <div class="neon-card preview-card">
      <div class="card-title-row">
        <div class="title-with-icon">
          <span class="icon-purple">🧊</span>
          <span>Vista previa</span>
        </div>
        <span class="compass-badge">N ▲</span>
      </div>

      <div class="terrain-viewport" id="terrain-viewport">
        <svg viewBox="0 0 500 310" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
          <defs>
            <linearGradient id="daySky" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#1e3a8a"/>
              <stop offset="50%" stop-color="#60a5fa"/>
              <stop offset="100%" stop-color="#dbeafe"/>
            </linearGradient>
            <linearGradient id="valleyGround" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#3f6212"/>
              <stop offset="50%" stop-color="#365314"/>
              <stop offset="100%" stop-color="#1a2e05"/>
            </linearGradient>
          </defs>
          <!-- Cielo y cordillera nevada del Altiplano -->
          <rect width="500" height="125" fill="url(#daySky)"/>
          <path d="M0,125 L0,88 L55,54 L115,82 L185,42 L255,78 L325,38 L395,76 L455,52 L500,82 L500,125 Z" fill="#64748b"/>
          <path d="M55,54 L72,68 L42,66 Z M185,42 L208,64 L165,62 Z M325,38 L352,64 L302,60 Z M455,52 L475,68 L438,67 Z" fill="#f8fafc" opacity="0.88"/>
          <!-- Planicie agrícola en perspectiva -->
          <rect y="122" width="500" height="188" fill="url(#valleyGround)"/>
          <!-- Malla de parcelas en perspectiva -->
          <g stroke="rgba(255,255,255,0.22)" stroke-width="1">
            <line x1="250" y1="122" x2="-80" y2="310"/>
            <line x1="250" y1="122" x2="60" y2="310"/>
            <line x1="250" y1="122" x2="200" y2="310"/>
            <line x1="250" y1="122" x2="350" y2="310"/>
            <line x1="250" y1="122" x2="500" y2="310"/>
            <line x1="250" y1="122" x2="640" y2="310"/>
            <line x1="0" y1="152" x2="500" y2="152"/>
            <line x1="0" y1="188" x2="500" y2="188"/>
            <line x1="0" y1="234" x2="500" y2="234"/>
            <line x1="0" y1="285" x2="500" y2="285"/>
          </g>
          <!-- Polígono holográfico 3D de la parcela seleccionada -->
          <g id="holo-parcel-poly">
            <polygon points="180,165 375,182 310,256 105,222" fill="rgba(56, 189, 248, 0.28)" stroke="#38bdf8" stroke-width="3"/>
            <!-- Líneas de malla interna cian -->
            <line x1="228" y1="169" x2="156" y2="230" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.65"/>
            <line x1="278" y1="173" x2="208" y2="239" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.65"/>
            <line x1="326" y1="178" x2="258" y2="247" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.65"/>
            <line x1="155" y1="184" x2="352" y2="206" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.65"/>
            <line x1="130" y1="203" x2="332" y2="231" stroke="#38bdf8" stroke-width="1" stroke-opacity="0.65"/>
          </g>
        </svg>

        <div class="preview-stats-bar">
          <div class="stat-chip">
            <span>🌱 Área: <strong id="preview-area">12.5 ha</strong></span>
          </div>
          <div class="stat-chip">
            <span>⛰️ Altitud: <strong id="preview-alt">3.799 m</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 3. TARJETA DE PRIORIDADES DEL PRODUCTOR ANDINO + HOLOGRAMA DE GANADERÍA SOSTENIBLE -->
  <div class="neon-card priorities-card">
    <div class="priorities-grid">
      <div class="sliders-col">
        <div class="card-title-row" style="margin-bottom:2px;">
          <div class="title-with-icon">
            <span class="star-icon">⭐</span>
            <span>Prioridades del productor andino</span>
          </div>
        </div>
        <div class="prio-sub">Ajusta el equilibrio entre producción, recuperación y sostenibilidad del suelo.</div>

        <!-- Slider 1: Agua (Azul Cian) -->
        <div class="slider-row">
          <div class="slider-icon water-icon">💧</div>
          <div class="slider-main">
            <div class="slider-label">Ahorro de agua y resistencia a sequía</div>
            <input type="range" id="range-agua" min="0" max="100" step="5" class="neon-range range-blue"/>
          </div>
          <div class="slider-val-box"><span id="val-agua">45</span></div>
          <span class="pct-sym">%</span>
        </div>

        <!-- Slider 2: Suelo (Verde Esmeralda) -->
        <div class="slider-row">
          <div class="slider-icon soil-icon">🌱</div>
          <div class="slider-main">
            <div class="slider-label">Recuperación y fertilidad del suelo</div>
            <input type="range" id="range-suelo" min="0" max="100" step="5" class="neon-range range-green"/>
          </div>
          <div class="slider-val-box"><span id="val-suelo">35</span></div>
          <span class="pct-sym">%</span>
        </div>

        <!-- Slider 3: Forraje (Naranja Ámbar) -->
        <div class="slider-row">
          <div class="slider-icon forage-icon">📊</div>
          <div class="slider-main">
            <div class="slider-label">Producción de forraje para ganado</div>
            <input type="range" id="range-forraje" min="0" max="100" step="5" class="neon-range range-orange"/>
          </div>
          <div class="slider-val-box"><span id="val-forraje">20</span></div>
          <span class="pct-sym">%</span>
        </div>
      </div>

      <!-- Tarjeta Holográfica Derecha (Bovino / Ganadería Andina Sostenible) -->
      <div class="cattle-holo-box">
        <svg viewBox="0 0 180 135" width="145" height="110">
          <defs>
            <filter id="blueNeon">
              <feGaussianBlur stdDeviation="2" result="b"/>
              <feMerge>
                <feMergeNode in="b"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <g filter="url(#blueNeon)" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <!-- Silueta frontal estilizada de ganado bovino andino + pasturas -->
            <path d="M58,38 C42,26 34,36 44,48 C50,54 56,52 60,48"/>
            <path d="M122,38 C138,26 146,36 136,48 C130,54 124,52 120,48"/>
            <path d="M64,34 C64,18 50,12 46,20"/>
            <path d="M116,34 C116,18 130,12 134,20"/>
            <path d="M60,36 L120,36 L114,82 C112,96 98,104 90,104 C82,104 68,96 66,82 Z" fill="rgba(56, 189, 248, 0.08)"/>
            <ellipse cx="90" cy="88" rx="16" ry="10"/>
            <circle cx="84" cy="88" r="2" fill="#38bdf8"/>
            <circle cx="96" cy="88" r="2" fill="#38bdf8"/>
            <circle cx="74" cy="56" r="3" fill="#38bdf8"/>
            <circle cx="106" cy="56" r="3" fill="#38bdf8"/>
            <!-- Brotes de forraje a los lados -->
            <path d="M26,118 L34,96 M26,118 L20,100 M26,118 L38,106" stroke="#22c55e"/>
            <path d="M152,118 L144,96 M152,118 L160,100 M152,118 L140,106" stroke="#22c55e"/>
          </g>
        </svg>
        <div class="cattle-caption">
          Un balance óptimo para una agricultura sostenible en los Andes.
        </div>
      </div>
    </div>
  </div>

  <!-- 4. BARRA DE ESTADO DEL NODO PICO W (NEFI / JOEL) -->
  <div class="neon-card pico-bar">
    <div class="pico-left">
      <div class="chip-icon-box">
        <svg viewBox="0 0 44 44" width="36" height="36" fill="none" stroke="#8b5cf6" stroke-width="2.2">
          <rect x="10" y="10" width="24" height="24" rx="4" fill="rgba(139, 92, 246, 0.16)"/>
          <rect x="16" y="16" width="12" height="12" rx="2" fill="#a855f7"/>
          <path d="M15,4 L15,10 M22,4 L22,10 M29,4 L29,10"/>
          <path d="M15,34 L15,40 M22,34 L22,40 M29,34 L29,40"/>
          <path d="M4,15 L10,15 M4,22 L10,22 M4,29 L10,29"/>
          <path d="M34,15 L40,15 M34,22 L40,22 M34,29 L40,29"/>
        </svg>
      </div>
      <div>
        <div class="pico-title">Estado del nodo Pico W (Nefi / Joel)</div>
        <div class="pico-sub" id="pico-sub-text">Contrato 9.1 oficial | hardware/telemetría</div>
      </div>
    </div>

    <div class="pico-center">
      <span class="conn-dot" id="conn-dot"></span>
      <span class="conn-label" id="conn-label">Conectado (Simulado)</span>
    </div>

    <div class="signal-bars" id="signal-bars" title="Intensidad de enlace de telemetría">
      <span class="s-bar b1 active"></span>
      <span class="s-bar b2 active"></span>
      <span class="s-bar b3 active"></span>
      <span class="s-bar b4 active"></span>
      <span class="s-bar b5 active"></span>
    </div>
  </div>

  <!-- 5. BARRA INFERIOR DE ACCIONES (RESTABLECER | APLICAR CONFIGURACIÓN >) -->
  <div class="bottom-actions">
    <button type="button" class="btn-reset" id="btn-reset">
      <span>↻</span>
      <span>Restablecer</span>
    </button>

    <button type="button" class="btn-apply" id="btn-apply">
      <span>✓</span>
      <span>Aplicar configuración</span>
      <span style="margin-left:4px;">›</span>
    </button>
  </div>
</div>
"""

_CONSOLA_CSS = """
:host {
  display: block;
  font-family: var(--st-font, 'Plus Jakarta Sans', sans-serif);
  color: #f8fafc;
}
.space-console {
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: radial-gradient(circle at 20% 10%, #151b38 0%, #070914 75%);
  border: 1.5px solid rgba(124, 58, 237, 0.42);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.55), inset 0 0 32px rgba(124, 58, 237, 0.08);
  margin-bottom: 14px;
}
.hero-banner {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 1.5px solid rgba(139, 92, 246, 0.5);
  min-height: 158px;
  display: flex;
  align-items: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
}
.hero-art-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}
.hero-banner-content {
  position: relative;
  z-index: 2;
  width: 100%;
  padding: 20px 26px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}
.hero-left-group {
  display: flex;
  align-items: center;
  gap: 18px;
}
.neon-plant-logo {
  width: 76px;
  height: 76px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.72);
  border: 1.5px solid rgba(74, 222, 128, 0.45);
  box-shadow: 0 0 24px rgba(34, 197, 94, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.console-main-title {
  font-size: 2.05rem;
  font-weight: 800;
  line-height: 1.12;
  margin: 0 0 6px 0;
  color: #ffffff;
  text-shadow: 0 2px 14px rgba(0, 0, 0, 0.65);
}
.console-subtitle {
  font-size: 0.9rem;
  color: #cbd5e1;
  margin: 0;
}
.system-ready-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(74, 222, 128, 0.55);
  color: #86efac;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 6px 13px;
  border-radius: 999px;
  box-shadow: 0 0 18px rgba(34, 197, 94, 0.25);
}
.ready-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 8px #4ade80;
}
.middle-grid {
  display: grid;
  grid-template-columns: 1.08fr 1fr;
  gap: 14px;
}
@media (max-width: 860px) {
  .middle-grid {
    grid-template-columns: 1fr;
  }
}
.left-stack {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.neon-card {
  background: linear-gradient(160deg, rgba(22, 28, 56, 0.92) 0%, rgba(12, 16, 34, 0.96) 100%);
  border: 1.5px solid rgba(99, 102, 241, 0.35);
  border-radius: 14px;
  padding: 15px 18px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.neon-card:hover {
  border-color: rgba(139, 92, 246, 0.75);
  box-shadow: 0 10px 28px rgba(124, 58, 237, 0.2);
}
.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.title-with-icon {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 1.02rem;
  font-weight: 700;
  color: #f8fafc;
}
.icon-purple {
  font-size: 1.15rem;
}
.help-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 1px solid rgba(148, 163, 184, 0.45);
  color: #94a3b8;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: help;
}
.parcel-select-body {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 14px;
  align-items: center;
}
@media (max-width: 560px) {
  .parcel-select-body {
    grid-template-columns: 1fr;
  }
}
.sat-thumb-box {
  height: 118px;
  border-radius: 10px;
  overflow: hidden;
  border: 1.5px solid rgba(56, 189, 248, 0.55);
  box-shadow: 0 0 16px rgba(56, 189, 248, 0.22);
}
.field-label {
  display: block;
  font-size: 0.76rem;
  color: #94a3b8;
  margin-bottom: 4px;
}
.custom-select-wrap {
  display: flex;
  align-items: center;
  background: rgba(10, 14, 30, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.42);
  border-radius: 9px;
  padding: 0 10px;
}
.select-prefix {
  font-size: 0.85rem;
  margin-right: 6px;
  color: #a78bfa;
}
.neon-select {
  width: 100%;
  background: transparent;
  color: #f8fafc;
  border: none;
  padding: 8px 4px;
  font-size: 0.84rem;
  font-family: inherit;
  outline: none;
  cursor: pointer;
}
.neon-select option {
  background: #0f172a;
  color: #f8fafc;
}
.engine-body {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px;
  align-items: center;
}
.engine-holo {
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.compass-badge {
  font-family: var(--st-code-font, monospace);
  font-size: 0.76rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.4);
  padding: 3px 8px;
  border-radius: 6px;
}
.terrain-viewport {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1.5px solid rgba(56, 189, 248, 0.45);
  height: 235px;
  box-shadow: inset 0 0 24px rgba(0, 0, 0, 0.45);
}
.preview-stats-bar {
  position: absolute;
  bottom: 10px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-around;
  gap: 10px;
  background: rgba(10, 14, 28, 0.86);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 10px;
  padding: 7px 12px;
  font-size: 0.82rem;
}
.priorities-grid {
  display: grid;
  grid-template-columns: 1.65fr 1fr;
  gap: 18px;
  align-items: center;
}
@media (max-width: 820px) {
  .priorities-grid {
    grid-template-columns: 1fr;
  }
}
.prio-sub {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 12px;
}
.slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.slider-icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.25);
  flex-shrink: 0;
}
.slider-main {
  flex: 1;
}
.slider-label {
  font-size: 0.83rem;
  font-weight: 600;
  margin-bottom: 4px;
}
.neon-range {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  appearance: none;
  outline: none;
  cursor: pointer;
}
.range-blue {
  background: linear-gradient(90deg, #0284c7, #38bdf8);
}
.range-green {
  background: linear-gradient(90deg, #15803d, #4ade80);
}
.range-orange {
  background: linear-gradient(90deg, #d97706, #fbbf24);
}
.neon-range::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.9);
  cursor: pointer;
}
.slider-val-box {
  width: 46px;
  text-align: center;
  font-family: var(--st-code-font, monospace);
  font-weight: 700;
  font-size: 0.9rem;
  background: rgba(10, 14, 30, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 8px;
  padding: 5px 0;
}
.pct-sym {
  font-size: 0.82rem;
  color: #94a3b8;
}
.cattle-holo-box {
  background: radial-gradient(circle at 50% 42%, rgba(56, 189, 248, 0.14), rgba(10, 14, 30, 0.92));
  border: 1px solid rgba(56, 189, 248, 0.35);
  border-radius: 12px;
  padding: 14px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.cattle-caption {
  font-size: 0.8rem;
  color: #cbd5e1;
  line-height: 1.4;
  margin-top: 6px;
}
.pico-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 18px;
}
.pico-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.pico-title {
  font-weight: 700;
  font-size: 0.95rem;
}
.pico-sub {
  font-size: 0.76rem;
  color: #94a3b8;
  font-family: var(--st-code-font, monospace);
}
.pico-center {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  color: #4ade80;
}
.conn-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 10px #22c55e;
}
.signal-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 24px;
}
.s-bar {
  width: 5px;
  border-radius: 2px;
  background: #334155;
}
.s-bar.active {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.7);
}
.s-bar.b1 { height: 6px; }
.s-bar.b2 { height: 10px; }
.s-bar.b3 { height: 14px; }
.s-bar.b4 { height: 19px; }
.s-bar.b5 { height: 24px; }
.bottom-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 2px;
}
.btn-reset {
  background: rgba(15, 23, 42, 0.85);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}
.btn-reset:hover {
  border-color: #38bdf8;
  color: #ffffff;
}
.btn-apply {
  background: linear-gradient(90deg, #6d28d9 0%, #9333ea 50%, #7c3aed 100%);
  color: #ffffff;
  border: 1.5px solid #c084fc;
  border-radius: 12px;
  padding: 11px 28px;
  font-size: 0.94rem;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 0 24px rgba(139, 92, 246, 0.55);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.btn-apply:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 0 32px rgba(168, 85, 247, 0.85);
}
"""

_CONSOLA_JS = """
export default function (component) {
  const { data, parentElement, setStateValue } = component;
  if (!data) return;

  const selMun = parentElement.querySelector("#select-municipio");
  const selPar = parentElement.querySelector("#select-parcela");
  const selEsc = parentElement.querySelector("#select-escenario");
  const rAgua = parentElement.querySelector("#range-agua");
  const rSuelo = parentElement.querySelector("#range-suelo");
  const rForraje = parentElement.querySelector("#range-forraje");
  const vAgua = parentElement.querySelector("#val-agua");
  const vSuelo = parentElement.querySelector("#val-suelo");
  const vForraje = parentElement.querySelector("#val-forraje");
  const prevAlt = parentElement.querySelector("#preview-alt");
  const prevArea = parentElement.querySelector("#preview-area");
  const connLabel = parentElement.querySelector("#conn-label");
  const connDot = parentElement.querySelector("#conn-dot");

  const parcelaId = data.parcela_id || "piloto_01";
  const escenarioId = data.escenario_id || "contrato_base";
  const pAgua = data.prio_agua ?? 45;
  const pSuelo = data.prio_suelo ?? 35;
  const pForraje = data.prio_forraje ?? 20;

  if (selMun && selMun.value !== parcelaId) selMun.value = parcelaId;
  if (selPar && selPar.value !== parcelaId) selPar.value = parcelaId;
  if (selEsc && selEsc.value !== escenarioId) selEsc.value = escenarioId;

  if (rAgua && document.activeElement !== rAgua) rAgua.value = pAgua;
  if (rSuelo && document.activeElement !== rSuelo) rSuelo.value = pSuelo;
  if (rForraje && document.activeElement !== rForraje) rForraje.value = pForraje;

  if (vAgua) vAgua.textContent = rAgua ? rAgua.value : pAgua;
  if (vSuelo) vSuelo.textContent = rSuelo ? rSuelo.value : pSuelo;
  if (vForraje) vForraje.textContent = rForraje ? rForraje.value : pForraje;

  if (prevAlt) {
    prevAlt.textContent = parcelaId === "viacha_02" ? "3.876 m" : "3.640 m";
  }
  if (prevArea) {
    prevArea.textContent = parcelaId === "viacha_02" ? "14.2 ha" : "12.5 ha";
  }

  if (connLabel && connDot) {
    if (data.origen_sensor === "simulado") {
      connLabel.textContent = "Conectado (Simulado)";
      connLabel.style.color = "#4ade80";
      connDot.style.background = "#22c55e";
    } else if (data.origen_sensor === "sensor_real") {
      connLabel.textContent = "Conectado (Sensor Real)";
      connLabel.style.color = "#38bdf8";
      connDot.style.background = "#38bdf8";
    } else {
      connLabel.textContent = "Sin señal de sensor (Modo Contingencia)";
      connLabel.style.color = "#f43f5e";
      connDot.style.background = "#f43f5e";
    }
  }

  if (rAgua) {
    rAgua.oninput = (e) => {
      if (vAgua) vAgua.textContent = e.target.value;
    };
  }
  if (rSuelo) {
    rSuelo.oninput = (e) => {
      if (vSuelo) vSuelo.textContent = e.target.value;
    };
  }
  if (rForraje) {
    rForraje.oninput = (e) => {
      if (vForraje) vForraje.textContent = e.target.value;
    };
  }

  if (selMun) {
    selMun.onchange = (e) => {
      if (selPar) selPar.value = e.target.value;
      setStateValue("parcela_id", e.target.value);
    };
  }
  if (selPar) {
    selPar.onchange = (e) => {
      if (selMun) selMun.value = e.target.value;
      setStateValue("parcela_id", e.target.value);
    };
  }
  if (selEsc) {
    selEsc.onchange = (e) => {
      setStateValue("escenario_id", e.target.value);
    };
  }

  const btnApply = parentElement.querySelector("#btn-apply");
  if (btnApply) {
    btnApply.onclick = () => {
      setStateValue("parcela_id", selPar ? selPar.value : parcelaId);
      setStateValue("escenario_id", selEsc ? selEsc.value : escenarioId);
      setStateValue("prio_agua", Number(rAgua ? rAgua.value : pAgua));
      setStateValue("prio_suelo", Number(rSuelo ? rSuelo.value : pSuelo));
      setStateValue("prio_forraje", Number(rForraje ? rForraje.value : pForraje));
    };
  }

  const btnReset = parentElement.querySelector("#btn-reset");
  if (btnReset) {
    btnReset.onclick = () => {
      setStateValue("parcela_id", "piloto_01");
      setStateValue("escenario_id", "contrato_base");
      setStateValue("prio_agua", 45);
      setStateValue("prio_suelo", 35);
      setStateValue("prio_forraje", 20);
    };
  }
}
"""

_COMPONENTE_CONSOLA_CCV2 = st.components.v2.component(
    "consola_nasa_la_paz_2026_v2",
    html=_CONSOLA_HTML,
    css=_CONSOLA_CSS,
    js=_CONSOLA_JS,
)


def renderizar_consola_interactiva_nasa(
    parcela_id: str,
    escenario_id: str,
    prio_agua: int,
    prio_suelo: int,
    prio_forraje: int,
    origen_sensor: str,
    key: str = "consola_principal_ccv2",
) -> dict[str, Any]:
    """Renderiza la Consola de Parcela y Escenarios idéntica a la imagen de referencia y sincroniza cambios."""
    res = _COMPONENTE_CONSOLA_CCV2(
        key=key,
        data={
            "parcela_id": parcela_id,
            "escenario_id": escenario_id,
            "prio_agua": prio_agua,
            "prio_suelo": prio_suelo,
            "prio_forraje": prio_forraje,
            "origen_sensor": origen_sensor,
        },
        on_parcela_id_change=lambda: None,
        on_escenario_id_change=lambda: None,
        on_prio_agua_change=lambda: None,
        on_prio_suelo_change=lambda: None,
        on_prio_forraje_change=lambda: None,
    )
    return {
        "parcela_id": getattr(res, "parcela_id", None) or parcela_id,
        "escenario_id": getattr(res, "escenario_id", None) or escenario_id,
        "prio_agua": getattr(res, "prio_agua", None) if getattr(res, "prio_agua", None) is not None else prio_agua,
        "prio_suelo": getattr(res, "prio_suelo", None) if getattr(res, "prio_suelo", None) is not None else prio_suelo,
        "prio_forraje": getattr(res, "prio_forraje", None) if getattr(res, "prio_forraje", None) is not None else prio_forraje,
    }


# ==============================================================================
# 3. COMPONENTE INTERACTIVO CCv2: TABLERO 3D DE ROTACIÓN + SCROLL ANIMATIONS
# ==============================================================================
_MATRIZ_ROTACION_HTML = """
<div class="rotation-experience" id="board-root"></div>
"""

_MATRIZ_ROTACION_CSS = """
:host {
  display: block;
  font-family: var(--st-font, 'Plus Jakarta Sans', sans-serif);
  color: #f8fafc;
}
.rotation-experience {
  display: flex;
  flex-direction: column;
  gap: 16px;
  perspective: 1200px;
}
.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 1.5px solid rgba(99, 102, 241, 0.35);
}
.board-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  color: #f8fafc;
}
.board-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
}
.strategy-row {
  position: relative;
  overflow: hidden;
  background: linear-gradient(160deg, rgba(22, 28, 56, 0.92) 0%, rgba(12, 16, 34, 0.96) 100%);
  border: 1.5px solid rgba(99, 102, 241, 0.35);
  border-radius: 14px;
  padding: 16px 18px;
  cursor: pointer;
  transform-style: preserve-3d;
  opacity: 0;
  transform: translateY(18px) rotateX(-5deg);
  transition:
    transform 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    opacity 0.45s ease;
}
.strategy-row.is-visible {
  opacity: 1;
  transform: translateY(0) rotateX(0deg);
}
.strategy-row:hover {
  border-color: #38bdf8;
  box-shadow: 0 12px 28px rgba(56, 189, 248, 0.16);
}
.strategy-row.is-recommended {
  border-left: 6px solid #22c55e;
  box-shadow: 0 0 26px rgba(34, 197, 94, 0.15);
}
.strategy-row.is-selected {
  outline: 2px solid #a855f7;
}
.row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 10px;
}
.strategy-name {
  font-size: 1.04rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
.badge-winner {
  background: linear-gradient(90deg, #16a34a, #22c55e);
  color: #ffffff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}
.score-pill {
  font-family: var(--st-code-font, monospace);
  font-size: 1.05rem;
  font-weight: 700;
  color: #38bdf8;
  background: rgba(10, 14, 30, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.45);
  padding: 4px 12px;
  border-radius: 8px;
}
.score-bar-track {
  width: 100%;
  height: 7px;
  background: rgba(30, 41, 59, 0.85);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 12px;
}
.score-bar-fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, #7c3aed, #38bdf8, #22c55e);
  border-radius: 999px;
  transition: width 0.85s cubic-bezier(0.22, 1, 0.36, 1);
}
.cycle-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(125px, 1fr));
  gap: 10px;
  margin-bottom: 10px;
}
@media (max-width: 700px) {
  .cycle-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
.cycle-step {
  background: rgba(10, 14, 30, 0.88);
  border: 1px solid rgba(99, 102, 241, 0.35);
  border-radius: 10px;
  padding: 9px 11px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.2s ease;
}
.cycle-step:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: #38bdf8;
}
.cycle-year {
  font-family: var(--st-code-font, monospace);
  font-size: 0.71rem;
  color: #a78bfa;
}
.cycle-crop {
  font-weight: 700;
  font-size: 0.86rem;
  color: #f8fafc;
}
.cycle-role {
  font-size: 0.74rem;
  color: #94a3b8;
}
.motivo-box {
  font-size: 0.84rem;
  line-height: 1.45;
  color: #cbd5e1;
  padding-top: 8px;
  border-top: 1px dashed rgba(148, 163, 184, 0.28);
}
"""

_MATRIZ_ROTACION_JS = """
export default function (component) {
  const { data, parentElement, setStateValue } = component;
  const root = parentElement.querySelector("#board-root");
  if (!root || !data) return;

  const rotaciones = data.rotaciones || [];
  const recomendacionId = data.recomendacion_id || "";
  const seleccionadaId = data.seleccionada_id || recomendacionId;

  root.innerHTML = "";

  const header = document.createElement("div");
  header.className = "board-header";
  header.innerHTML = `
    <div>
      <h3 class="board-title">Secuencia plurianual de rotación en parcela (Ciclo de 4 años)</h3>
      <div class="board-subtitle">Haz clic en cualquier cultivo (↗ 3D) para cargar su holograma 3D interactivo abajo</div>
    </div>
    <div class="board-subtitle">Contrato 9.3 • Recomendación activa: <strong style="color:#4ade80;">${recomendacionId}</strong></div>
  `;
  root.appendChild(header);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        const fill = entry.target.querySelector(".score-bar-fill");
        if (fill) {
          fill.style.width = fill.dataset.targetWidth || "50%";
        }
      }
    });
  }, { threshold: 0.12 });

  rotaciones.forEach((rot, idx) => {
    const isRec = rot.id === recomendacionId;
    const isSel = rot.id === seleccionadaId;
    const row = document.createElement("div");
    row.className = "strategy-row" + (isRec ? " is-recommended" : "") + (isSel ? " is-selected" : "");
    row.style.transitionDelay = `${idx * 90}ms`;

    const ciclos = rot.ciclos_detalle || [];
    const ciclosHtml = ciclos.map((c) => `
      <div class="cycle-step" data-cultivo-id="${c.cultivo_id || 'quinua_real'}" title="Haz clic para ver ${c.cultivo} en 3D">
        <span class="cycle-year">${c.anio}</span>
        <span class="cycle-crop">${c.cultivo} <span style="color:#38bdf8;font-size:0.74rem;">↗ 3D</span></span>
        <span class="cycle-role">${c.funcion}</span>
      </div>
    `).join("");

    const pct = Math.min(Math.max(Number(rot.puntaje) || 0, 0), 100);

    row.innerHTML = `
      <div class="row-top">
        <div class="strategy-name">
          <span>${rot.nombre}</span>
          ${isRec ? '<span class="badge-winner">★ Recomendada por el motor</span>' : ''}
        </div>
        <div class="score-pill" data-target="${pct}">0 / 100 pts</div>
      </div>
      <div class="score-bar-track">
        <div class="score-bar-fill" data-target-width="${pct}%"></div>
      </div>
      <div class="cycle-grid">${ciclosHtml}</div>
      <div class="motivo-box"><strong>Dictamen del motor (Rudy):</strong> ${rot.motivo}</div>
    `;

    const pill = row.querySelector(".score-pill");
    const targetScore = pct;
    let current = 0;
    const step = Math.max(1, Math.ceil(targetScore / 22));
    const timer = setInterval(() => {
      current += step;
      if (current >= targetScore) {
        current = targetScore;
        clearInterval(timer);
      }
      if (pill) pill.textContent = `${current} / 100 pts`;
    }, 24);

    row.onmousemove = (e) => {
      const rect = row.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) - 0.5;
      const ny = ((e.clientY - rect.top) / rect.height) - 0.5;
      row.style.transform = `translateY(-2px) rotateX(${-ny * 4}deg) rotateY(${nx * 5}deg)`;
    };

    row.onmouseleave = () => {
      row.style.transform = "translateY(0) rotateX(0deg) rotateY(0deg)";
    };

    row.onclick = (ev) => {
      const stepEl = ev.target.closest(".cycle-step");
      if (stepEl && stepEl.dataset.cultivoId) {
        setStateValue("cultivo_3d_id", stepEl.dataset.cultivoId);
      }
      setStateValue("seleccionada_id", rot.id);
    };

    root.appendChild(row);
    observer.observe(row);
  });
}
"""

_COMPONENTE_MATRIZ_CCV2 = st.components.v2.component(
    "matriz_rotacion_altiplano_v2",
    html=_MATRIZ_ROTACION_HTML,
    css=_MATRIZ_ROTACION_CSS,
    js=_MATRIZ_ROTACION_JS,
)


DETALLE_CICLOS_ANDINOS: dict[str, list[dict[str, str]]] = {
    "rotacion_1": [
        {"anio": "Año 1 • Siembra cabeza", "cultivo": "Papa nativa (Solanum)", "funcion": "Alta demanda de N y humedad", "cultivo_id": "papa_nativa"},
        {"anio": "Año 2 • Grano andino", "cultivo": "Quinua Real", "funcion": "Aprovecha fertilidad residual", "cultivo_id": "quinua_real"},
        {"anio": "Año 3 • Gramínea", "cultivo": "Cebada / Raíz", "funcion": "Cobertura media y forraje", "cultivo_id": "cebolla_zanahoria_altura"},
        {"anio": "Año 4 • Barbecho", "cultivo": "Descanso / Oca", "funcion": "Recuperación pasiva edáfica", "cultivo_id": "oca_isaño"},
    ],
    "rotacion_2": [
        {"anio": "Año 1 • Tolerancia hídrica", "cultivo": "Quinua Real", "funcion": "Bajo consumo de agua (raíz pivotante)", "cultivo_id": "quinua_real"},
        {"anio": "Año 2 • Fijación biológica", "cultivo": "Tarwi / Haba andina", "funcion": "Incorp. simbiótica de Nitrógeno", "cultivo_id": "tarwi_haba"},
        {"anio": "Año 3 • Aporte carbono", "cultivo": "Cebada / Hortaliza raíz", "funcion": "Rastrojo protector + biomasa", "cultivo_id": "cebolla_zanahoria_altura"},
        {"anio": "Año 4 • Suelo regenerado", "cultivo": "Papa nativa / Oca", "funcion": "Cosecha sobre cama rica en N", "cultivo_id": "papa_nativa"},
    ],
    "rotacion_3": [
        {"anio": "Año 1 • Criotolerancia", "cultivo": "Cañahua (Qañawa)", "funcion": "Resiste heladas extremas (-8 °C)", "cultivo_id": "canahua_andina"},
        {"anio": "Año 2 • Asociación mixta", "cultivo": "Avena + Vicia / Haba", "funcion": "Heno proteico + fijación parcial", "cultivo_id": "tarwi_haba"},
        {"anio": "Año 3 • Pastoreo controlado", "cultivo": "Descanso / Oca asociada", "funcion": "Reciclaje orgánico y cobertura", "cultivo_id": "oca_isaño"},
        {"anio": "Año 4 • Tubérculo amargo", "cultivo": "Papa Luk'i (Chuño)", "funcion": "Seguro alimentario ante helada", "cultivo_id": "papa_nativa"},
    ],
}


def renderizar_matriz_interactiva_rotaciones(
    rotaciones: list[dict[str, Any]],
    recomendacion_id: str,
    key: str = "tablero_rotaciones_ccv2",
) -> tuple[str, str]:
    """Renderiza el componente interactivo CCv2 y devuelve (rotacion_seleccionada_id, cultivo_3d_id)."""
    estado_actual = st.session_state.get(key, {})
    seleccionada_id = estado_actual.get("seleccionada_id", recomendacion_id)
    cultivo_3d_id = estado_actual.get("cultivo_3d_id", "quinua_real")
    ids_validos = [str(r.get("id", "")) for r in rotaciones]
    if seleccionada_id not in ids_validos:
        seleccionada_id = recomendacion_id

    rotaciones_enriquecidas = []
    for idx, rot in enumerate(rotaciones):
        rot_id = str(rot.get("id", f"rotacion_{idx+1}"))
        rotaciones_enriquecidas.append(
            {
                "id": rot_id,
                "nombre": rot.get("nombre", rot_id),
                "puntaje": rot.get("puntaje", 0),
                "motivo": rot.get("motivo", ""),
                "ciclos_detalle": DETALLE_CICLOS_ANDINOS.get(
                    rot_id,
                    [
                        {"anio": "Año 1", "cultivo": "Ciclo 1", "funcion": "Evaluación motor", "cultivo_id": "quinua_real"},
                        {"anio": "Año 2", "cultivo": "Ciclo 2", "funcion": "Evaluación motor", "cultivo_id": "tarwi_haba"},
                        {"anio": "Año 3", "cultivo": "Ciclo 3", "funcion": "Evaluación motor", "cultivo_id": "canahua_andina"},
                        {"anio": "Año 4", "cultivo": "Ciclo 4", "funcion": "Evaluación motor", "cultivo_id": "papa_nativa"},
                    ],
                ),
            }
        )

    res = _COMPONENTE_MATRIZ_CCV2(
        key=key,
        data={
            "rotaciones": rotaciones_enriquecidas,
            "recomendacion_id": recomendacion_id,
            "seleccionada_id": seleccionada_id,
            "cultivo_3d_id": cultivo_3d_id,
        },
        default={"seleccionada_id": seleccionada_id, "cultivo_3d_id": cultivo_3d_id},
        on_seleccionada_id_change=lambda: None,
        on_cultivo_3d_id_change=lambda: None,
    )
    rot_out = getattr(res, "seleccionada_id", None) or seleccionada_id
    cult_out = getattr(res, "cultivo_3d_id", None) or cultivo_3d_id
    return rot_out, cult_out


# ==============================================================================
# 4. PRISMA 3D INTERACTIVO DE HORIZONTES DEL SUELO Y ZONA RADICULAR (CCv2)
# ==============================================================================
_PRISMA_SUELO_HTML = """
<div class="soil-stage" id="soil-stage">
  <div class="soil-info">
    <div class="soil-eyebrow">VISUALIZACIÓN 3D INTERACTIVA • LÍMITE CIENTÍFICO SMAP vs. ZONA RADICULAR</div>
    <h4 class="soil-title">Perfil tridimensional de horizontes edáficos del Altiplano (0–45 cm)</h4>
    <p class="soil-desc">
      Mueve el cursor sobre el bloque 3D para rotar las capas del suelo. Observa por qué la lectura
      superficial satelital <strong>SMAP (0–5 cm)</strong> no equivale sin modelo a la humedad de la
      <strong>zona radicular (20–30 cm)</strong> donde operan la quinua, el tarwi y la papa.
    </p>
    <div class="layer-legend" id="layer-legend"></div>
  </div>
  <div class="prism-viewport" id="prism-viewport">
    <div class="prism-3d" id="prism-3d">
      <div class="soil-slab slab-top">
        <span>0–5 cm • Capa superficial (Alcance satelital SMAP / NDVI)</span>
      </div>
      <div class="soil-slab slab-mid">
        <span>5–20 cm • Horizonte A arable (Fijación simbiótica Tarwi / Haba)</span>
      </div>
      <div class="soil-slab slab-root">
        <span>20–30 cm • Zona radicular efectiva (Nodo sensor calibrado / Raíces)</span>
      </div>
      <div class="soil-slab slab-deep">
        <span>30–45 cm • Subsuelo mineral andino (Reserva hídrica profunda)</span>
      </div>
    </div>
  </div>
</div>
"""

_PRISMA_SUELO_CSS = """
:host {
  display: block;
  font-family: var(--st-font, 'Plus Jakarta Sans', sans-serif);
  color: #f8fafc;
}
.soil-stage {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 20px;
  align-items: center;
  background: linear-gradient(160deg, rgba(22, 28, 56, 0.92) 0%, rgba(12, 16, 34, 0.96) 100%);
  border: 1.5px solid rgba(99, 102, 241, 0.35);
  border-radius: 14px;
  padding: 18px 22px;
  margin-top: 10px;
}
@media (max-width: 780px) {
  .soil-stage {
    grid-template-columns: 1fr;
  }
}
.soil-eyebrow {
  font-family: var(--st-code-font, monospace);
  font-size: 0.72rem;
  font-weight: 700;
  color: #38bdf8;
  margin-bottom: 4px;
}
.soil-title {
  font-size: 1.12rem;
  margin: 0 0 8px 0;
  color: #f8fafc;
}
.soil-desc {
  font-size: 0.84rem;
  line-height: 1.48;
  margin: 0 0 12px 0;
  color: #cbd5e1;
}
.layer-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-family: var(--st-code-font, monospace);
  font-size: 0.74rem;
}
.legend-pill {
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(10, 14, 30, 0.9);
  border: 1px solid rgba(56, 189, 248, 0.35);
}
.prism-viewport {
  perspective: 900px;
  height: 215px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
}
.prism-3d {
  width: 92%;
  max-width: 340px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  transform-style: preserve-3d;
  transform: rotateX(18deg) rotateY(-18deg);
  transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.soil-slab {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 600;
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.35);
  transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), filter 0.2s ease;
}
.soil-slab:hover {
  transform: translateZ(22px) scale(1.03);
  filter: brightness(1.12);
}
.slab-top {
  background: linear-gradient(90deg, #7c3aed, #a855f7);
}
.slab-mid {
  background: linear-gradient(90deg, #15803d, #22c55e);
}
.slab-root {
  background: linear-gradient(90deg, #0284c7, #38bdf8);
}
.slab-deep {
  background: linear-gradient(90deg, #334155, #475569);
}
"""

_PRISMA_SUELO_JS = """
export default function (component) {
  const { data, parentElement } = component;
  const viewport = parentElement.querySelector("#prism-viewport");
  const prism = parentElement.querySelector("#prism-3d");
  const legend = parentElement.querySelector("#layer-legend");
  if (!viewport || !prism) return;

  if (legend && data) {
    const hum = data.humedad_suelo_pct !== null && data.humedad_suelo_pct !== undefined
      ? `${data.humedad_suelo_pct}% (${data.origen_sensor})`
      : "null (Sin calibrar)";
    legend.innerHTML = `
      <span class="legend-pill">Humedad nodo: <strong style="color:#4ade80;">${hum}</strong></span>
      <span class="legend-pill">Precipitación NASA: <strong style="color:#38bdf8;">${data.precip_mm ?? 'null'} mm</strong></span>
    `;
  }

  viewport.onmousemove = (e) => {
    const rect = viewport.getBoundingClientRect();
    const nx = ((e.clientX - rect.left) / rect.width) - 0.5;
    const ny = ((e.clientY - rect.top) / rect.height) - 0.5;
    const rotY = -18 + nx * 42;
    const rotX = 18 - ny * 34;
    prism.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg)`;
  };

  viewport.onmouseleave = () => {
    prism.style.transform = "rotateX(18deg) rotateY(-18deg)";
  };
}
"""

_COMPONENTE_PRISMA_SUELO_CCV2 = st.components.v2.component(
    "prisma_suelo_3d_v2",
    html=_PRISMA_SUELO_HTML,
    css=_PRISMA_SUELO_CSS,
    js=_PRISMA_SUELO_JS,
)


def renderizar_prisma_3d_suelo(
    humedad_suelo_pct: float | None,
    origen_sensor: str,
    precip_mm: float | None,
) -> None:
    """Renderiza el bloque 3D interactivo de horizontes de suelo y alcance radicular."""
    _COMPONENTE_PRISMA_SUELO_CCV2(
        key="prisma_suelo_3d_ccv2",
        data={
            "humedad_suelo_pct": humedad_suelo_pct,
            "origen_sensor": origen_sensor,
            "precip_mm": precip_mm,
        },
    )


# ==============================================================================
# 5. SISTEMA GLOBAL DE ANIMACIONES UI, TRANSICIONES Y ESTILO NEÓN ESPACIAL (`st.html`)
# ==============================================================================
def inyectar_motor_animaciones_css() -> None:
    """Aplica el estilo espacial oscuro con bordes luminosos neón de la imagen de referencia."""
    st.html(
        """
        <style>
        @keyframes pageSectionEnter {
          0% {
            opacity: 0;
            transform: translateY(12px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
          animation: pageSectionEnter 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
          background: linear-gradient(165deg, rgba(19, 25, 52, 0.94) 0%, rgba(10, 14, 30, 0.96) 100%);
          border: 1.5px solid rgba(99, 102, 241, 0.38) !important;
          border-radius: 16px !important;
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
          transition:
            transform 0.24s cubic-bezier(0.22, 1, 0.36, 1),
            box-shadow 0.24s ease,
            border-color 0.24s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
          border-color: rgba(139, 92, 246, 0.72) !important;
          box-shadow: 0 14px 36px rgba(124, 58, 237, 0.18);
        }
        div[data-testid="stMetric"] {
          background: rgba(11, 15, 32, 0.88);
          border: 1px solid rgba(56, 189, 248, 0.32) !important;
          border-radius: 12px !important;
          transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
          transform: translateY(-3px) scale(1.015);
          border-color: #38bdf8 !important;
          box-shadow: 0 0 18px rgba(56, 189, 248, 0.22);
        }
        </style>
        """
    )


# ==============================================================================
# 6. GRÁFICOS CIENTÍFICOS EN APACHE ECHARTS (`st.echarts_chart`)
# ==============================================================================
def renderizar_climograma_altiplano_echarts(mensual_list: list[dict[str, Any]]) -> None:
    """Dibuja un climograma ombrotérmico combinado con animación progresiva y zoom interactivo."""
    df_clima = pd.DataFrame(mensual_list)
    st.echarts_chart(
        {
            "animationDuration": 1100,
            "animationEasing": "cubicOut",
            "tooltip": {"trigger": "axis"},
            "legend": {"top": 0},
            "grid": {"left": "8%", "right": "8%", "bottom": "16%", "top": "18%"},
            "dataZoom": [{"type": "inside"}],
            "dataset": {"source": df_clima},
            "xAxis": {"type": "category"},
            "yAxis": [
                {"type": "value", "name": "Precipitación (mm)", "position": "left"},
                {"type": "value", "name": "Temp. media (°C)", "position": "right"},
            ],
            "series": [
                {
                    "name": "Precipitación mensual (mm)",
                    "type": "bar",
                    "yAxisIndex": 0,
                    "encode": {"x": "mes", "y": "precip_mm"},
                    "universalTransition": True,
                },
                {
                    "name": "Temperatura media 2m (°C)",
                    "type": "line",
                    "yAxisIndex": 1,
                    "smooth": True,
                    "encode": {"x": "mes", "y": "temp_c"},
                    "universalTransition": True,
                },
            ],
        },
        height=270,
        key="echarts_climograma_nasa",
        alt="Climograma mensual de la parcela en el Altiplano mostrando lluvias concentradas de diciembre a marzo y caída térmica en invierno",
    )


def renderizar_comparacion_rotaciones_echarts(df_rotaciones: pd.DataFrame) -> None:
    """Gráfico horizontal de barras con transición animada en Apache ECharts."""
    st.echarts_chart(
        {
            "animationDuration": 950,
            "animationEasing": "quarticOut",
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "4%", "right": "10%", "bottom": "8%", "top": "10%", "containLabel": True},
            "dataset": {"source": df_rotaciones},
            "xAxis": {"type": "value", "max": 100, "name": "Puntaje (0-100)"},
            "yAxis": {"type": "category"},
            "series": [
                {
                    "name": "Puntaje del motor (Rudy)",
                    "type": "bar",
                    "encode": {"x": "Puntaje (0-100)", "y": "ID Contrato"},
                    "label": {"show": True, "position": "right"},
                    "universalTransition": True,
                }
            ],
        },
        height=240,
        key="echarts_puntajes_motor",
        alt="Comparación de puntajes de las tres estrategias de rotación evaluadas por el motor de Rudy",
    )
