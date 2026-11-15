# Módulo de datos NASA POWER — Iván

## 1. Objetivo y contrato de integración

Este módulo descarga datos diarios NASA POWER para **Patacamaya** y **Viacha**, de forma independiente, y produce resúmenes agregados por campaña agrícola para el motor de Rudy.

- Periodo diario solicitado: `2020-01-01` a `2025-12-31`.
- Campaña: del 1 de septiembre al 30 de abril.
- Campañas completas dentro del periodo: 2020–2021, 2021–2022, 2022–2023, 2023–2024 y 2024–2025.
- Comunidad NASA POWER: `AG` (Agroclimatology).
- Variables: `PRECTOTCORR`, `T2M`, `T2M_MIN`, `T2M_MAX`, `RH2M`.
- Formato principal para Rudy: JSON por ubicación con el contrato que él proporcionó.

No se descargan imágenes satelitales. El entregable inicial de Iván son datos meteorológicos numéricos CSV/JSON.

## 2. Coordenadas configuradas

Se han colocado las coordenadas comunicadas por Rudy:

| Identificador | Ubicación | Latitud | Longitud |
|---|---|---:|---:|
| `patacamaya_01` | Patacamaya | -17.2333 | -67.9167 |
| `viacha_01` | Viacha | -16.6533 | -68.3017 |

**Verificación pendiente del equipo:** confirmar que estas coordenadas son los puntos piloto que desean analizar y no solo centros aproximados de las localidades. NASA POWER devuelve información de su celda/grilla para las coordenadas consultadas, no una medición física dentro de cada parcela.

## 3. Variables y significado

| Parámetro NASA | Uso | Unidad esperada |
|---|---|---|
| `PRECTOTCORR` | Precipitación corregida diaria; suma de la campaña | mm/día en la serie; mm en el total de campaña |
| `T2M` | Temperatura media diaria; media de la campaña | °C |
| `T2M_MIN` | Mínima diaria; mínimo absoluto de campaña y detección de heladas | °C |
| `T2M_MAX` | Máxima diaria; se conserva en la serie | °C |
| `RH2M` | Humedad relativa del aire; media de la campaña | % |

`RH2M` es humedad relativa del aire a 2 metros, **no** humedad del suelo.

El programa también conserva las unidades que NASA devuelve en su bloque de metadatos dentro de `metadata_nasa_power.json`. No se debe confundir el total de precipitación de campaña (mm) con la precipitación diaria (mm/día).

## 4. Instalación y ejecución en Windows

### Opción A: ejecutar con doble clic

1. Descomprime esta carpeta `datos_nasa` dentro del repositorio del equipo.
2. Asegúrate de tener Python 3 instalado y que funcione el comando `py` o `python`.
3. Entra a `datos_nasa` y haz doble clic en `ejecutar_descarga.bat`.
4. El programa instala/verifica `requests` y `pandas`, consulta NASA POWER y deja los resultados en `resultados/procesados/`.
5. No cierres la ventana hasta que aparezca `DESCARGA Y PROCESAMIENTO FINALIZADOS` o un mensaje de error.

### Opción B: ejecutar desde VS Code

Abre una terminal dentro de `datos_nasa` y ejecuta estos comandos, uno por uno:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py descargar_datos.py
```

Si `py` no funciona, sustituirlo por `python`. Si PowerShell impide activar el entorno, se puede abrir CMD en VS Code y ejecutar:

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python descargar_datos.py
```

Se necesita Internet durante la consulta. Los datos descargados quedan guardados localmente y después se pueden usar sin repetir la consulta.

## 5. Archivos generados

### Serie diaria

- `resultados/raw/nasa_power_patacamaya_2020-01-01_2025-12-31.json`: respuesta original de NASA para Patacamaya.
- `resultados/raw/nasa_power_viacha_2020-01-01_2025-12-31.json`: respuesta original de NASA para Viacha.
- `resultados/procesados/nasa_power_diario_patacamaya.csv`: serie diaria de Patacamaya.
- `resultados/procesados/nasa_power_diario_viacha.csv`: serie diaria de Viacha.
- `resultados/procesados/nasa_power_diario_dos_ubicaciones.csv`: ambas localidades en una tabla.

### JSON que se entrega a Rudy

- `resultados/procesados/patacamaya_power.json`: objeto con la campaña 2024–2025 y el esquema que indicó Rudy.
- `resultados/procesados/viacha_power.json`: objeto equivalente para Viacha.
- `resultados/procesados/patacamaya_power_campanas.json`: historial de las cinco campañas completas para Patacamaya.
- `resultados/procesados/viacha_power_campanas.json`: historial de las cinco campañas completas para Viacha.
- `resultados/procesados/campanas/`: un JSON individual por ubicación y campaña.

### Verificación y procedencia

- `resultados/procesados/control_calidad_datos.csv`: cantidad de datos válidos y faltantes por variable y ubicación.
- `resultados/procesados/resumen_campanas_dos_ubicaciones.csv`: resumen de las campañas y cobertura.
- `resultados/procesados/metadata_nasa_power.json`: URL efectiva, coordenadas, fechas, unidades devueltas por NASA, estándar temporal y advertencias.

## 6. Reglas de agregación acordadas con Rudy

- `temperatura_media_c`: media aritmética de los valores diarios `T2M` disponibles.
- `temperatura_minima_absoluta_c`: mínimo de `T2M_MIN` en la campaña. Si falta al menos un día de `T2M_MIN`, se entrega `null` para no afirmar que se conoce el mínimo absoluto de toda la campaña.
- `dias_helada`: número de días con `T2M_MIN < 0 °C`. Si falta al menos un día de `T2M_MIN`, se entrega `null`, porque el conteo podría quedar incompleto. Nunca se infieren heladas usando `T2M`.
- `precipitacion_total_mm`: suma de `PRECTOTCORR`. Si falta al menos un día de precipitación, se entrega `null` y no se supone que el día faltante tuvo 0 mm.
- `humedad_relativa_pct`: media aritmética de los valores diarios `RH2M` disponibles.

Los valores `-999`, `-99`, `-9999` y `-99999` se convierten a faltantes. En JSON se representan como `null`; no se reemplazan por cero. `valores_faltantes_detectados` cuenta celdas diarias faltantes entre las cinco variables de esa campaña. `porcentaje_datos_validos` es el porcentaje de celdas válidas sobre el total esperado de días × cinco variables.

## 7. Estándar temporal

La consulta omite el parámetro `time-standard`, igual que la URL de referencia enviada por Rudy. Según la documentación de NASA POWER, la API diaria usa **LST (Local Solar Time)** por defecto; UTC se debe solicitar explícitamente. El estándar usado se registra en los metadatos.

## 8. Fuente y reproducibilidad

- Servicio: NASA POWER Daily Point API.
- Endpoint: <https://power.larc.nasa.gov/api/temporal/daily/point>
- Documentación: <https://power.larc.nasa.gov/docs/services/api/temporal/daily/>
- Comunidad: `AG`.

Cada JSON diario original y cada metadato permiten rastrear qué consulta se realizó. El campo `url_consulta` de cada JSON de campaña es una URL reproducible con exactamente las fechas de esa campaña. La URL de la descarga diaria completa queda registrada en `metadata_nasa_power.json`.

## 9. Cómo compartir con el equipo

1. Ejecutar el programa y revisar `control_calidad_datos.csv`.
2. Abrir `patacamaya_power.json` y `viacha_power.json`; verificar que las fechas sean 2024-09-01 a 2025-04-30 y que `es_simulacion_o_ejemplo` sea `false`.
3. Enviar esos dos JSON a Rudy para probar su validador.
4. Compartir también los CSV diarios y los archivos `*_power_campanas.json` si el motor quiere comparar años.
5. Guardar los archivos generados en la rama de Iván y abrir un Pull Request para revisión, según el flujo del repositorio.

## 10. Limitaciones científicas

1. La serie diaria de NASA POWER es información de productos meteorológicos/grillas y no una medición de estación dentro de la parcela.
2. La coordenada necesita confirmación agrícola del equipo.
3. `RH2M` no es humedad del suelo. No debe presentarse como tal.
4. La descarga no demuestra por sí sola que una rotación aumente el rendimiento. Los criterios agronómicos y las recomendaciones necesitan fuentes y validación local.
