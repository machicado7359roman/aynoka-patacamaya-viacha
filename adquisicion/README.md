# AYNOKA · Adquisición 1.1

Simulador web local de 1 a 12 torres de parcela y una estación central. Creado en una carpeta independiente por solicitud de Román. Las versiones PAGINA WEB ASTRA no se modifican.

## Abrir

Abre `index.html` con doble clic en Edge, Chrome o Firefox. No necesita instalaciones, servidor, internet ni cuenta. Los archivos `styles.css`, `model.js` y `app.js` deben mantenerse junto al HTML.

## Recorrido de demostración

1. Selecciona la cantidad de torres en Campo. Abre una torre y usa **Identificar esta torre** para guardar su dirección lógica única y, si quieres, el nombre del lugar. La central utiliza la dirección 0.
2. Escoge un sensor, o selecciónalo en el dibujo «Dentro de la torre». Cambia el número o el deslizador: la vista previa JSON cambia inmediatamente.
3. Pulsa **Enviar paquete simulado**. La central recibe una copia del escenario y se anima el enlace. **Transmitir todas las torres** envía los valores de las parcelas activas.
4. Abre **Estación central** para ver recepción, condiciones activas y umbrales. Ejemplo: batería P01 = 3 V; después transmite y revisa la alerta.
5. Avanza 15 min y luego 1 min para probar datos antiguos. El reloj es manual y no transmite automáticamente. Exactamente 15 minutos todavía cuenta como reciente.
6. Interrumpe el enlace LoRa para probar pérdida de señal. Los datos anteriores permanecen visibles con su estado y antigüedad.
7. Abre **Laboratorio: probar un paquete inválido** y envía el ejemplo incompleto. La central lo rechaza y conserva el último paquete válido. Un envío válido resuelve esa condición.
8. Compara **Vista previa editable** y **Último recibido**. Descarga el JSON que estás viendo con su procedencia simulada.

**Descargar JSON de toda la red** guarda las torres activas con su dirección y ubicación. Cada entrada incluye la vista previa local y el último paquete válido recibido con su dirección al momento de transmisión. Las torres que aún no han transmitido llevan `last_valid_received: null`. Al reducir la cantidad, las torres apartadas conservan sus valores dentro de la sesión.

**Reiniciar o recargar la página borra la sesión.** Descarga los JSON antes si deseas conservarlos. No hay almacenamiento ni envío a terceros. No hay SMS.

## Contrato y procedencia

Referencia revisada: rama local remota `origin/Nefi-hardware`, commit `b69ef6d`, archivos `hardware_estacion/firmware/` y `datos_estacion/ejemplo/ejemplo_json_nodo_P01.json`. No se altera el firmware.

Se conserva la estructura `Feature`, `properties.parameter[variable][AAAAMMDD]`, `header`, `messages` y `parameters`. El nodo se identifica mediante `header.api.name`, como en el ejemplo de Nefi. El tiempo de recepción se mantiene separado del JSON diario.

Adaptaciones explícitas de este simulador:

- `header.sources = ["SIMULACION"]`: ningún dato se atribuye a sensores físicos ni a NASA.
- Con ubicación asignada, GeoJSON guarda un Point en orden longitud, latitud. Sin coordenadas, geometry es null. El dibujo sigue siendo esquemático.
- `PH_SOIL` se añade como extensión propuesta, con `parameters.PH_SOIL.proposed = true`; no existe en el firmware revisado. EC no equivale a pH.
- Los controles representan un escenario diario ilustrativo. No reproducen el muestreo, promedios ni acumuladores del dispositivo.
- `GWETTOP` = VWC a 5 cm / 0.45, limitado a 1. `GWETROOT` = (0.15 × VWC5 + 0.45 × VWC25 + 0.40 × VWC100) / 0.45, limitado a 1. Se redondean a tres decimales. Son transformaciones ilustrativas, no calibración validada.
- La humedad se edita y exporta en m³/m³. Las tarjetas la muestran como porcentaje volumétrico (×100).
- Los umbrales son valores de demostración. Las alertas evalúan el último paquete válido recibido, incluso si es antiguo; la antigüedad se indica por separado.
- Se simulan LoRa y Wi-Fi conceptualmente. No se simulan propagación, interferencias, colisiones, fragmentación ni electrónica real. No hay integración de red ni backend.
- La validación local exige los campos del simulador, rangos numéricos y coherencia mínima/media/máxima y viento medio/ráfaga. No es un validador general del protocolo físico.

## Archivos

- `index.html`: estructura accesible en español.
- `styles.css`: diseño adaptable, contraste y preferencia de movimiento reducido.
- `app.js`: dibujos SVG originales, interacción, alertas y descarga local.
- `model.js`: contrato, estado, datos simulados, validación y recepción.
- `model.test.js`: pruebas funcionales del modelo con Node, sin dependencias.
- `browser.qa.cjs`: comprobación opcional con Edge headless y su puerto de depuración **local** 9337. Cierra esa instancia al terminar. No se usa durante el funcionamiento normal.

Pruebas: `node --test model.test.js` desde esta carpeta. La revisión en navegador se documenta en `../estado/adquisicion_1_1.md`.

Pendiente: revisión de distribución física de instrumentos y unidades con Nefi; calibraciones y umbrales con responsables técnicos; integración futura con firmware real y con la interfaz principal. Este prototipo no establece esa integración.

## Torres y ubicación

**Quitar** retira la torre seleccionada. **Añadir torre** recupera primero la última retirada durante la sesión. En **Identificar esta torre**, escribe el nombre del lugar y abre Google Maps para encontrar el marcador. Pega sus coordenadas decimales o su enlace completo con coordenadas. Para enlaces cortos abre primero el enlace en Maps. La identificación muestra un nombre derivado del lugar y el ID de torre (por ejemplo, viacha-norte-p02.test) y una IPv4 privada simulada derivada de la dirección lógica. El nombre cambia al renombrar el lugar. La IP cambia al editar la dirección lógica. Los paquetes conservan la identificación que tenían al transmitirse.
