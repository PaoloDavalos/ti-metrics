"""Punto de entrada de TI-Metrics."""

from src.services.aplicacion import AplicacionTIMetrics


def procesar_archivos(ruta_csv, ruta_json, ruta_reporte, usar_api=True):
    return AplicacionTIMetrics().procesar_archivos(
        ruta_csv, ruta_json, ruta_reporte, usar_api,
    )


def main():
    return AplicacionTIMetrics().ejecutar()


if __name__ == "__main__":
    if not main():
        raise SystemExit(1)
