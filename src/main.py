"""Menú y procesamiento de datos."""

import csv
from src.parsers.lector_csv import leer_logs_csv
from src.parsers.lector_json import leer_eventos_json
from src.services.consulta_ip import enriquecer_ips
from src.services.metricas import deduplicar_eventos, generar_reporte
from src.utils.persistencia import guardar_reporte_json


def procesar_archivos(ruta_csv, ruta_json, ruta_reporte, usar_api=True):
    """Lee los archivos y devuelve si pudo guardar el reporte."""
    try:
        eventos_csv, invalidos_csv = leer_logs_csv(ruta_csv)
        eventos_json, invalidos_json = leer_eventos_json(ruta_json)
    except (OSError, ValueError, csv.Error) as error:
        print("No se pudieron leer los archivos:", error)
        return False

    eventos, duplicados = deduplicar_eventos(eventos_csv + eventos_json)
    geografia = enriquecer_ips(eventos, usar_api)
    reporte = generar_reporte(
        eventos, invalidos_csv + invalidos_json, duplicados, geografia,
    )
    if not guardar_reporte_json(ruta_reporte, reporte):
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


def main():
    print("TI-Metrics")
    print("1. Procesar datos con ubicación de las IP")
    print("2. Procesar datos sin consultar ubicación")
    opcion = input("Selecciona una opción: ").strip()
    if opcion not in ("1", "2"):
        print("Opción inválida.")
        return False
    return procesar_archivos(
        "data/logs.csv", "data/events.json", "data/reporte.json",
        usar_api=opcion == "1",
    )


if __name__ == "__main__":
    if not main():
        raise SystemExit(1)
