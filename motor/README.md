# Motor de Evaluación Multicriterio y Recomendaciones Explicables (XAI)

**Proyecto:** NASA Space Apps Challenge 2026 — *Field Shift: Adapting Farms with NASA Data*  
**Módulo:** `motor/`  
**Responsable:** Rudy Ramos (Ingeniero responsable del motor de evaluación, modelado matemático, comparación multicriterio y generación de recomendaciones explicables)  
**Rama:** `rudy-motor`

---

## 1. Arquitectura Modular

El paquete `motor/` utiliza exclusivamente la biblioteca estándar de Python (`dataclasses`, `math`, `json`, `datetime`, `pathlib`, `typing`) sin dependencias externas frágiles ni modelos de caja negra:

```text
motor/
├── __init__.py          # Exportación de la API pública (evaluar_rotaciones, modelos y excepciones)
├── evaluador.py         # Orquestación principal, desempates deterministas y ejecución CLI offline
├── modelos.py           # Dataclasses inmutables de dominio y jerarquía de excepciones
├── validacion.py        # Adaptadores y validadores de contratos (NASA POWER de Iván y telemetría de Nefi)
├── criterios.py         # Funciones puras para calcular r_{ij} en [0, 1] (agua, suelo, produccion)
├── ponderaciones.py     # Normalización y validación matemática de prioridades w_j
├── explicaciones.py     # Generador determinista de explicaciones verificables (XAI)
├── configuracion.py     # Reglas científicas trazables, límites físicos y estrategias parametrizadas
└── README.md            # Documentación científica, matemática y guía de integración
```

---

## 2. Modelo Matemático Multicriterio (MCDA)

Cada alternativa de rotación $i \in \{1, 2, 3\}$ se evalúa sobre $m = 3$ criterios normalizados $j \in \{\text{agua}, \text{suelo}, \text{produccion}\}$ mediante el modelo aditivo lineal ponderado:

$$S_i = 100 \sum_{j=1}^{m} w_j \, r_{ij}$$

Sujeto a las restricciones estrictas:

$$0 \le r_{ij} \le 1, \qquad w_j \ge 0, \qquad \sum_{j=1}^{m} w_j = 1$$

- **Interpretación científica:** El puntaje $S_i \in [0, 100]$ es una **comparación relativa interna del modelo** bajo los datos climáticos y prioridades suministradas. **No representa** una probabilidad de éxito agrícola ni una garantía de rendimiento físico (t/ha).
- **Desempate determinista:** Cuando dos alternativas empatan en puntaje entero, la prelación se resuelve de forma determinista por: (1) mayor puntaje exacto en punto flotante, (2) mayor $r_{ij}$ en el criterio de mayor peso del agricultor, (3) mayor $r_{i,\text{agua}}$, (4) mayor $r_{i,\text{suelo}}$, y (5) orden lexicográfico del identificador (`rotacion_1` < `rotacion_2` < `rotacion_3`).

---

## 3. Trazabilidad Científica de las Reglas (Sección 12)

| ID Regla | Nombre | Variable Utilizada | Fórmula / Transformación | Unidad | Fundamento y Referencia Verificable | Condiciones de Aplicabilidad | Limitaciones | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `REGLA_AGUA_01` | Respuesta normalizada de eficiencia y satisfacción hídrica | `precipitacion_total_mm` (`PRECTOTCORR`) y `humedad_suelo_pct` opcional | $f_{\text{hid}} = \text{clip}\!\left(\frac{P - P_{\text{crit}}}{P_{\text{opt}} - P_{\text{crit}}}, 0, 1\right)$; ajuste sobre eficiencia base | `mm` $\to [0, 1]$ | Geerts et al. (2006), *Agric. Water Manag.* 81(3):339–355 (`doi:10.1016/j.agwat.2005.04.008`); Allen et al. (1998) FAO-56 | Secano en Altiplano boliviano (3.600–4.100 m s.n.m.), campaña sep–abr | Suma acumulada no desagrega veranillos intracamapaña sin serie diaria | `hipotesis_trabajo` |
| `REGLA_TERMICA_01` | Penalización térmica por temperatura mínima absoluta y frecuencia de heladas | `temperatura_minima_absoluta_c` (`T2M_MIN`) y `dias_helada` ($T_{\min} < 0\,^\circ\text{C}$) | $\Delta T = \max(0, T_{\text{tol},i} - T_{\min})$; $\Delta D = \max(0, D - D_{\text{tol},i})/40$ | `°C`, `dias` $\to [0, 0.75]$ | Jacobsen et al. (2005), *Eur. J. Agron.* 22(2):131–143 (`doi:10.1016/j.eja.2004.01.003`); NASA POWER Methodology | Exige `T2M_MIN` o `dias_helada`; **prohibido evaluar con `T2M` media** | Grilla MERRA-2 (~50 km) a 2 m puede diferir 1–2 °C de la temperatura a nivel de dosel | `validada_bibliograficamente` |
| `REGLA_SUELO_01` | Índice de recuperación edáfica, cobertura y fijación de N | `recuperacion_suelo_base`, `aporte_cobertura_y_fijacion_n` y `precipitacion_total_mm` | Combinación convexa $0.65 B_{\text{suelo}} + 0.25 N_{\text{cob}} + 0.10 f_{\text{min}} B_{\text{suelo}}$ | $[0, 1]$ | Tapia & Fries (2007), *Guía de campo de los cultivos andinos* (FAO); Ortuño et al. (2013), PROINPA/FAO | Suelos altoandinos con baja materia orgánica (< 1.5 %) en rotación trienal | Mineralización microbiana se reduce bajo sequía extrema (< 200 mm) | `hipotesis_trabajo` |
| `REGLA_MCDA_01` | Agregación lineal ponderada (WSM) | $w_j$ y $r_{ij}$ | $S_i = \text{round}\!\left(100 \sum_{j=1}^3 w_j r_{ij}\right)$ | Puntos $[0, 100]$ | Fishburn (1967); Triantaphyllou (2000), *Multi-Criteria Decision Making Methods*, Springer | Comparación determinista de 3 estrategias con criterios en $[0,1]$ | Compensación lineal parcial; se complementa con alertas explícitas en XAI | `demostracion` |

---

## 4. Guía de Integración para el Equipo (Sección 13)

### Consumo desde el Sitio Web (Jorge)
```python
from motor import cargar_datos_nasa_locales, evaluar_rotaciones

entrada = {
    "parcela_id": "piloto_01",
    "prioridades": {"agua": 0.50, "suelo": 0.25, "produccion": 0.25},
    "datos_nasa": cargar_datos_nasa_locales("datos_nasa/escenario_a_sequia_power.json"),
}

respuesta_json = evaluar_rotaciones(entrada)
```

Estructura garantizada de `respuesta_json`:
```json
{
  "parcela_id": "piloto_01",
  "recomendacion_id": "rotacion_2",
  "rotaciones": [
    {"id": "rotacion_1", "puntaje": 52, "motivo": "..."},
    {"id": "rotacion_2", "puntaje": 86, "motivo": "..."},
    {"id": "rotacion_3", "puntaje": 75, "motivo": "..."}
  ],
  "estatus": "demostracion"
}
```

---

## 5. Comandos Exactos de Reproducción (100 % Offline)

```powershell
# 1. Ejecutar la demostración de los 3 escenarios obligatorios (Sequía, Heladas, Prioridad Suelo)
python -m motor.evaluador

# 2. Ejecutar la suite completa con unittest estándar (16 pruebas verificadas, 0 dependencias externas)
python -m unittest discover -s pruebas/motor -v
```
