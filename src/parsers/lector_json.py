"""Lectura del archivo events.json."""

import json

from src.utils.validacion import normalizar_evento


def leer_eventos_json(ruta_json):
    """Devuelve los eventos válidos y la cantidad de registros inválidos."""
    with open(ruta_json, "r", encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if not isinstance(registros, list):
        raise ValueError("El JSON debe contener una lista de eventos.")

    eventos = []
    invalidos = 0
    for registro in registros:
        evento = normalizar_evento(registro)
        if evento is None:
            invalidos += 1
        else:
            eventos.append(evento)
    return eventos, invalidos
