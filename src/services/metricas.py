"""Eliminación de duplicados y cálculo del reporte."""


def deduplicar_eventos(eventos):
    """Conserva el primer evento de cada id usando un conjunto."""
    vistos = set()
    limpios = []
    duplicados = 0
    for evento in eventos:
        if evento["id"] in vistos:
            duplicados += 1
        else:
            vistos.add(evento["id"])
            limpios.append(evento)
    return limpios, duplicados


def generar_reporte(eventos, invalidos, duplicados, geografia):
    """Calcula el reporte con los eventos válidos sin repetir."""
    total_eventos = len(eventos)
    errores_500 = 0
    porcentaje = 0.0
    promedio_cpu = 0.0
    promedio_memoria = 0.0
    suma_cpu = 0.0
    suma_memoria = 0.0
    ips_criticas = set()

    for evento in eventos:
        suma_cpu += evento["cpu"]
        suma_memoria += evento["memoria"]
        es_error_500 = evento["status_code"] == 500
        if es_error_500:
            errores_500 += 1
        if (
            es_error_500
            or evento["cpu"] >= 90
            or evento["memoria"] >= 90
        ):
            ips_criticas.add(evento["ip"])

    if total_eventos > 0:
        porcentaje = round(errores_500 / total_eventos * 100, 2)
        promedio_cpu = round(suma_cpu / total_eventos, 2)
        promedio_memoria = round(suma_memoria / total_eventos, 2)

    return {
        "total_eventos": total_eventos,
        "eventos_invalidos": invalidos,
        "eventos_duplicados": duplicados,
        "errores_http_500": errores_500,
        "porcentaje_http_500": porcentaje,
        "cpu_promedio_porcentaje": promedio_cpu,
        "memoria_promedio_porcentaje": promedio_memoria,
        "ips_criticas": sorted(ips_criticas),
        "geografia_por_ip": geografia,
        "eventos_procesados": eventos,
    }
