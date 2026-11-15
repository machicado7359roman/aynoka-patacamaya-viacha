# Aprendizaje de patrones en ASTRA

`aprendiz.py` proviene del commit fdab709 de la rama APRENDIZAJE-CON-SENSORES del equipo. Se integra la clase AprendizContinuo de River 0.27.0, sin cargar archivos pickle externos.

ASTRA 1.8 crea un modelo por torre, zona, dirección y geometría. El adaptador app/seguimiento.py entrega eventos simulados de VWC_25CM en m3/m3 con fecha y zona horaria. La selección de seis tomas y la mediana pertenecen al adaptador; el detector aprende en paralelo y comienza a clasificar desde la observación 351.

Las puntuaciones expresan rareza estadística, no diagnóstico ni probabilidad. El aprendizaje incorpora también lecturas inusuales; una falla persistente puede normalizarse. Validación con hardware pendiente. La fecha simulada no demuestra una fecha física de captura.

El historial/modelo vive en la sesión Streamlit. Se puede exportar el historial; no se ofrece importación de modelos pickle. El perfil original de 20 variables y su adaptador no están conectados en esta versión.

Fuente del módulo completo: https://github.com/machicado7359roman/space-apps-2026-astables/tree/fdab709e619f3b7c7e0b1a7fcf891846a4f488d8/APRENDIZAJE_TUS_SENSORES/aprendizaje_continuo
