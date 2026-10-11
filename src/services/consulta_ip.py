"""Consulta de ubicación con ip-api.com: una vez por IP y timeout de 5 segundos."""

import requests


def consultar_geografia(ip):
    """Devuelve la ubicación y si se alcanzó el límite de consultas."""
    ubicacion = {"estado": "no_disponible", "pais": None, "ciudad": None}
    detener = False
    try:
        respuesta = requests.get(
            "http://ip-api.com/json/" + ip,
            params={"fields": "status,country,city", "lang": "es"},
            timeout=5,
        )
        # Deja de consultar cuando se alcanza el límite de la API.
        detener = (
            respuesta.headers.get("X-Rl") == "0"
            or respuesta.status_code == 429
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        if (
            isinstance(datos, dict)
            and datos.get("status") == "success"
            and isinstance(datos.get("country"), str)
            and isinstance(datos.get("city"), str)
        ):
            ubicacion = {
                "estado": "consultada",
                "pais": datos["country"],
                "ciudad": datos["city"],
            }
    except (requests.RequestException, ValueError):
        pass
    return ubicacion, detener


def enriquecer_ips(eventos, usar_api=True):
    """Guarda un resultado por IP para evitar consultas repetidas."""
    geografia = {}
    detener = False
    consultas = 0
    for evento in eventos:
        ip = evento["ip"]
        if ip in geografia:
            continue
        if not usar_api:
            geografia[ip] = {"estado": "omitida", "pais": None, "ciudad": None}
        elif detener or consultas >= 45:
            geografia[ip] = {
                "estado": "pendiente_por_limite", "pais": None, "ciudad": None,
            }
        else:
            geografia[ip], detener = consultar_geografia(ip)
            consultas += 1
    return geografia
