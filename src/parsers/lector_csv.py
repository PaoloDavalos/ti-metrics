"""Lectura del archivo logs.csv."""

import csv

from src.utils.validacion import normalizar_evento


def leer_logs_csv(ruta_csv):
    """Devuelve los eventos válidos y la cantidad de registros inválidos."""
    eventos = []
    invalidos = 0
    with open(ruta_csv, "r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo, strict=True)
        requeridos = ("id", "ip", "status_code", "cpu", "memoria")
        for campo in requeridos:
            if campo not in (lector.fieldnames or []):
                raise ValueError(
                    "El CSV no contiene todas las columnas requeridas."
                )

        for fila in lector:
            evento = normalizar_evento(fila)
            if evento is None or None in fila:
                invalidos += 1
            else:
                eventos.append(evento)
    return eventos, invalidos
