# AYNOKA · demo pública del Altiplano

Demostración del Sistema Híbrido de Apoyo a la Decisión para la Rotación de Cultivos en el Altiplano Boliviano, desarrollada por el equipo ASTABLES de la UMSA para NASA Space Apps Challenge 2026.

## Abrir

**[Abrir la página web AYNOKA](https://astra-altiplano-2026.streamlit.app/)**

La versión web se despliega en Streamlit Community Cloud desde `app/main.py`. Para ejecutarla localmente:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/main.py
```

## Alcance y procedencia

- El clima histórico proviene de las respuestas NASA POWER guardadas en `datos_nasa/`, con coordenadas, fechas y metadatos incluidos.
- Las torres y las lecturas de suelo de la demo son simuladas; no hay sensores físicos conectados.
- El diagrama de Fritzing en `referencias/` es un diseño del prototipo electrónico realizado por el equipo; no acredita montaje ni calibración física.
- Las recomendaciones son comparaciones exploratorias del motor del equipo, pendientes de validación agronómica y de campo.
- El registro es local a la instancia web de prueba. No verifica correo, no sincroniza con el APK y puede perderse cuando Streamlit reinicia la instancia. Usa una contraseña exclusiva para la demo.
- El APK AYNOKA en `descargas/` es una compilación de prueba; su instalación física en Android no quedó verificada.

Esta copia contiene los módulos necesarios para la demostración pública. El repositorio de trabajo del equipo permanece privado.
