"""Lectura del archivo events.json."""

import json

from src.parsers.base_parser import BaseLogParser


class JSONLogParser(BaseLogParser):
    def parse(self, ruta):
        """Devuelve los eventos válidos y la cantidad de registros inválidos."""
        with open(ruta, "r", encoding="utf-8") as archivo:
            registros = json.load(archivo)
        if not isinstance(registros, list):
            raise ValueError("El JSON debe contener una lista de eventos.")

        eventos = []
        invalidos = 0
        for registro in registros:
            evento = self._validador.normalizar(registro)
            if evento is None:
                invalidos += 1
            else:
                eventos.append(evento)
        return eventos, invalidos


def leer_eventos_json(ruta_json):
    return JSONLogParser().parse(ruta_json)
