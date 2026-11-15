"""Aprendizaje multivariable, no supervisado y continuo de sensores numéricos."""
from collections import deque
from datetime import datetime
import math
import pickle
from pathlib import Path

import river
from river import anomaly, preprocessing


class AprendizContinuo:
    """Aprende de cada evento válido. No tiene sensores ni etiquetas prefijados.

    Un archivo de estado corresponde a un flujo, un origen y un esquema de variables.
    Evalúa frente al pasado antes de incorporar la nueva lectura.
    """
    VERSION = 1

    def __init__(self, ventana=250, calibracion=100, cuantil=0.98, semilla=42):
        if type(ventana) is not int or not 20 <= ventana <= 5000:
            raise ValueError("ventana debe ser un entero entre 20 y 5000.")
        if type(calibracion) is not int or not 20 <= calibracion <= 5000:
            raise ValueError("calibracion debe ser un entero entre 20 y 5000.")
        if isinstance(cuantil, bool) or not isinstance(cuantil, (int, float)) or not 0.5 <= cuantil < 1:
            raise ValueError("cuantil debe estar entre 0.5 y 1 (sin incluir 1).")
        self.ventana = ventana
        self.calibracion = calibracion
        self.cuantil = cuantil
        self.escalador = preprocessing.MinMaxScaler()
        self.bosque = anomaly.HalfSpaceTrees(n_trees=25, height=8, window_size=ventana, seed=semilla)
        self.puntuaciones = deque(maxlen=max(ventana * 4, calibracion))
        self.observaciones = 0
        self.ultimo_timestamp = None
        self.flujo_id = None
        self.origen = None
        self.variables = None
        self.unidades = None
        self.river_version = river.__version__
        self.version = self.VERSION

    def _validar(self, evento):
        if not isinstance(evento, dict):
            raise ValueError("El evento debe ser un objeto JSON.")
        flujo = evento.get("flujo_id")
        if not isinstance(flujo, str) or not flujo.strip() or len(flujo) > 120:
            raise ValueError("Declara flujo_id (1 a 120 caracteres).")
        origen = evento.get("origen")
        if origen not in ("simulacion", "medicion_real"):
            raise ValueError("Declara origen=simulacion o medicion_real.")
        try:
            timestamp = datetime.fromisoformat(evento["timestamp"])
        except (KeyError, TypeError, ValueError):
            raise ValueError("timestamp debe ser ISO 8601 con zona horaria.") from None
        if timestamp.utcoffset() is None:
            raise ValueError("timestamp debe incluir zona horaria.")
        if self.ultimo_timestamp is not None and timestamp <= datetime.fromisoformat(self.ultimo_timestamp):
            raise ValueError("Las nuevas lecturas deben ser posteriores a las ya aprendidas, sin duplicados.")
        valores = evento.get("valores")
        if not isinstance(valores, dict) or not 1 <= len(valores) <= 128:
            raise ValueError("valores debe contener entre 1 y 128 variables numéricas.")
        x = {}
        for clave, valor in valores.items():
            if not isinstance(clave, str) or not clave.strip() or len(clave) > 120:
                raise ValueError("Nombre de variable inválido.")
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise ValueError(f"{clave}: se requiere un número finito, sin nulos ni texto.")
            try:
                numero = float(valor)
            except OverflowError:
                raise ValueError(f"{clave}: valor demasiado grande.") from None
            if not math.isfinite(numero) or abs(numero) > 1e100:
                raise ValueError(f"{clave}: valor no finito o demasiado grande.")
            x[clave] = numero
        unidades = evento.get("unidades")
        if not isinstance(unidades, dict) or set(unidades) != set(x):
            raise ValueError("Declara unidades para todas las variables (usa '1' si no tienen unidad).")
        if any(not isinstance(u, str) or not u.strip() or len(u) > 60 for u in unidades.values()):
            raise ValueError("Cada unidad debe ser un texto de 1 a 60 caracteres.")
        if self.variables is not None:
            if (flujo, origen) != (self.flujo_id, self.origen):
                raise ValueError("Usa otro modelo para un flujo u origen distinto.")
            if set(x) != set(self.variables) or unidades != self.unidades:
                raise ValueError("El esquema/unidades cambió: inicia otro modelo para esa configuración.")
        return x, timestamp.isoformat(), flujo, origen, dict(unidades)

    def procesar(self, evento, aprender=True):
        """Puntúa con el estado previo; después, opcionalmente, aprende la lectura."""
        if type(aprender) is not bool:
            raise ValueError("aprender debe ser booleano.")
        x, timestamp, flujo, origen, unidades = self._validar(evento)
        previas = self.observaciones
        puntuacion, umbral, inusual = None, None, None
        estado = "aprendiendo_patrones"
        if previas >= self.ventana:
            # El escalador y el bosque que puntúan solo conocen lecturas anteriores.
            z = {k: min(1.0, max(0.0, v)) for k, v in self.escalador.transform_one(x).items()}
            puntuacion = float(self.bosque.score_one(z))
            estado = "calibrando_referencia"
            if len(self.puntuaciones) >= self.calibracion:
                ordenadas = sorted(self.puntuaciones)
                # Cuantil empírico del pasado. No se incluye la lectura que se evalúa.
                umbral = ordenadas[min(len(ordenadas) - 1, math.ceil(self.cuantil * len(ordenadas)) - 1)]
                inusual = puntuacion > umbral
                estado = "patron_inusual" if inusual else "dentro_del_patron"
        if aprender:
            if self.variables is None:
                self.variables = tuple(sorted(x))
                self.unidades = unidades
                self.flujo_id, self.origen = flujo, origen
            # Actualiza la normalización y aprende con la nueva escala, en [0, 1].
            self.escalador.learn_one(x)
            z_aprender = {k: min(1.0, max(0.0, v)) for k, v in self.escalador.transform_one(x).items()}
            self.bosque.learn_one(z_aprender)
            self.observaciones += 1
            self.ultimo_timestamp = timestamp
            if puntuacion is not None:
                self.puntuaciones.append(puntuacion)
        return {
            "estado": estado, "flujo_id": flujo, "origen": origen,
            "timestamp": timestamp, "variables": sorted(x), "aprendio_esta_lectura": aprender,
            "lecturas_aprendidas_antes": previas, "lecturas_aprendidas_despues": self.observaciones,
            "puntuacion_inusual": puntuacion, "umbral_aprendido": umbral, "es_inusual": inusual,
            "aviso": "Puntuación estadística, no probabilidad ni diagnóstico. NASA no interviene.",
        }

    def resumen(self):
        return {"algoritmo": "River HalfSpaceTrees + normalizacion incremental",
                "river_version": self.river_version, "flujo_id": self.flujo_id, "origen": self.origen,
                "variables": list(self.variables or ()), "unidades": self.unidades,
                "lecturas_aprendidas": self.observaciones, "ultimo_timestamp": self.ultimo_timestamp,
                "ventana_bosque": self.ventana, "minimo_puntuaciones_calibracion": self.calibracion,
                "puntuaciones_en_referencia": len(self.puntuaciones), "cuantil": self.cuantil,
                "limites_aprendidos": {k: {"minimo": self.escalador.min[k].get(),
                                          "maximo": self.escalador.max[k].get()} for k in self.variables or ()}}

    def guardar(self, ruta):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        # Escritura reemplazable para no dejar a medias el estado tras un fallo.
        temporal = ruta.with_name(ruta.name + ".tmp")
        temporal.write_bytes(pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL))
        temporal.replace(ruta)

    @classmethod
    def cargar(cls, ruta):
        """Solo estados propios/confiables: pickle no es un formato de intercambio seguro."""
        modelo = pickle.loads(Path(ruta).read_bytes())
        if not isinstance(modelo, cls) or modelo.version != cls.VERSION or modelo.river_version != river.__version__:
            raise ValueError("Estado incompatible: usa la misma versión del módulo y River.")
        return modelo
