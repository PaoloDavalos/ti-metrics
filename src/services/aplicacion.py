"""Coordina la lectura, las consultas y el reporte desde la consola."""

import csv

from src.parsers.lector_csv import CSVLogParser
from src.parsers.lector_json import JSONLogParser
from src.services.consulta_ip import ClienteUbicacion
from src.services.metricas import ProcesadorEventos
from src.utils.persistencia import RepositorioReporteJSON
from src.utils.validacion import ValidadorEventos


class AplicacionTIMetrics:
    def __init__(self):
        self._validador = ValidadorEventos()
        self._procesador = ProcesadorEventos()
        self._cliente = ClienteUbicacion()
        self._repositorio = RepositorioReporteJSON()

    def ejecutar(self):
        print("TI-Metrics")
        print("1. Procesar datos con ubicación de las IP")
        print("2. Procesar datos sin consultar ubicación")
        opcion = input("Selecciona una opción: ").strip()
        if opcion not in ("1", "2"):
            print("Opción inválida.")
            return False
        return self.procesar_archivos(
            "data/logs.csv", "data/events.json", "data/reporte.json",
            usar_api=opcion == "1",
        )

    def procesar_archivos(self, ruta_csv, ruta_json, ruta_reporte, usar_api=True):
        """Lee los archivos y devuelve si pudo guardar el reporte."""
        fuentes = [
            (CSVLogParser(self._validador), ruta_csv),
            (JSONLogParser(self._validador), ruta_json),
        ]
        eventos = []
        invalidos = 0
        try:
            for parser, ruta in fuentes:
                leidos, descartados = parser.parse(ruta)
                eventos.extend(leidos)
                invalidos += descartados
        except (OSError, ValueError, csv.Error) as error:
            print("No se pudieron leer los archivos:", error)
            return False

        eventos, duplicados = self._procesador.deduplicar(eventos)
        geografia = self._cliente.obtener_ubicaciones(eventos, usar_api)
        reporte = self._procesador.generar_reporte(
            eventos, invalidos, duplicados, geografia,
        )
        if not self._repositorio.guardar(ruta_reporte, reporte):
            print("No se pudo guardar el reporte. Revisa la ruta y los permisos.")
            return False

        print("Reporte guardado en:", ruta_reporte)
        print("Eventos válidos sin repetir:", reporte["total_eventos"])
        print("Registros inválidos:", reporte["eventos_invalidos"])
        print("Duplicados eliminados:", reporte["eventos_duplicados"])
        print("Errores HTTP 500:", reporte["errores_http_500"])
        print("Porcentaje HTTP 500:", reporte["porcentaje_http_500"], "%")
        print("IP críticas:", ", ".join(reporte["ips_criticas"]) or "Ninguna")
        print("Estado de las consultas de ubicación:")
        for ip, ubicacion in geografia.items():
            print(" ", ip, "->", ubicacion["estado"])
        return True
