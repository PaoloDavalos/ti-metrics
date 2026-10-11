"""Guardado del reporte en JSON."""

import json


def guardar_reporte_json(ruta_json, reporte):
    """Devuelve True si guarda el reporte y False si ocurre un error."""
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(reporte, archivo, indent=4, ensure_ascii=False)
        return True
    except (OSError, TypeError, ValueError):
        return False
