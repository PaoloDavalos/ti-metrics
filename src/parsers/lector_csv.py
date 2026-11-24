"""Lectura del archivo logs.csv."""

import csv

from src.parsers.base_parser import BaseLogParser


class CSVLogParser(BaseLogParser):
    def parse(self, ruta):
        """Devuelve los eventos válidos y la cantidad de registros inválidos."""
        eventos = []
        invalidos = 0
        with open(ruta, "r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo, strict=True)
            requeridos = ("id", "ip", "status_code", "cpu", "memoria")
            for campo in requeridos:
                if campo not in (lector.fieldnames or []):
                    raise ValueError(
                        "El CSV no contiene todas las columnas requeridas."
                    )

            for fila in lector:
                evento = self._validador.normalizar(fila)
                if evento is None or None in fila:
                    invalidos += 1
                else:
                    eventos.append(evento)
        return eventos, invalidos


def leer_logs_csv(ruta_csv):
    return CSVLogParser().parse(ruta_csv)
