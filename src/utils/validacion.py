"""Da el mismo formato a los registros del CSV y del JSON."""

from ipaddress import ip_address


def normalizar_evento(registro):
    """Devuelve el evento revisado o None si no es válido."""
    if not isinstance(registro, dict):
        return None

    try:
        identificador = registro["id"]
        ip = registro["ip"]
        codigo_http = registro["status_code"]
        cpu = registro["cpu"]
        memoria = registro["memoria"]

        # Evita convertir True en 1 o estructuras en texto.
        for valor in (identificador, ip, codigo_http, cpu, memoria):
            if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
                return None

        identificador = str(identificador).strip()
        ip = str(ip).strip()
        codigo_http = float(codigo_http)
        cpu = float(cpu)
        memoria = float(memoria)

        if not identificador or not 100 <= codigo_http <= 599:
            return None
        if codigo_http != int(codigo_http):
            return None
        if not 0 <= cpu <= 100 or not 0 <= memoria <= 100:
            return None

        # Escribe de la misma forma las direcciones IPv6 equivalentes.
        ip = str(ip_address(ip))
        return {
            "id": identificador,
            "ip": ip,
            "status_code": int(codigo_http),
            "cpu": cpu,
            "memoria": memoria,
        }
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
