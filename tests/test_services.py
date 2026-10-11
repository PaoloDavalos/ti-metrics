import json
from unittest.mock import Mock, patch

import pytest
import requests

from src.main import procesar_archivos
from src.services.consulta_ip import consultar_geografia, enriquecer_ips
from src.services.metricas import deduplicar_eventos, generar_reporte
from src.utils.persistencia import guardar_reporte_json


def evento(identificador, estado=200, cpu=25, memoria=40):
    return {
        "id": str(identificador), "ip": "8.8.8.8",
        "status_code": estado, "cpu": cpu, "memoria": memoria,
    }


def respuesta_api(datos, codigo=200, cuota="44"):
    respuesta = Mock()
    respuesta.status_code = codigo
    respuesta.headers = {"X-Rl": cuota}
    respuesta.json.return_value = datos
    return respuesta


def test_deduplicacion_conserva_primero():
    primero = evento(1)
    limpio, duplicados = deduplicar_eventos([primero, evento(1, 500), evento(2)])
    assert limpio == [primero, evento(2)]
    assert duplicados == 1


def test_metricas_y_umbral_critico():
    eventos = [evento(1), evento(2, 500), evento(3, cpu=90)]
    eventos[2]["ip"] = "1.1.1.1"
    reporte = generar_reporte(eventos, 2, 1, {})
    assert reporte["total_eventos"] == 3
    assert reporte["porcentaje_http_500"] == 33.33
    assert reporte["cpu_promedio_porcentaje"] == 46.67
    assert reporte["ips_criticas"] == ["1.1.1.1", "8.8.8.8"]


def test_memoria_en_limite_es_critica():
    reporte = generar_reporte([evento(1, memoria=90)], 0, 0, {})
    assert reporte["ips_criticas"] == ["8.8.8.8"]


def test_otro_error_http_no_cuenta_como_500():
    reporte = generar_reporte([evento(1, estado=503)], 0, 0, {})
    assert reporte["errores_http_500"] == 0
    assert reporte["porcentaje_http_500"] == 0.0
    assert reporte["ips_criticas"] == []


def test_sin_eventos_no_divide_por_cero():
    reporte = generar_reporte([], 0, 0, {})
    assert reporte["porcentaje_http_500"] == 0.0
    assert reporte["cpu_promedio_porcentaje"] == 0.0
    assert reporte["ips_criticas"] == []


def test_api_correcta_y_timeout_configurado():
    respuesta = respuesta_api({"status": "success", "country": "Ecuador", "city": "Quito"})
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta) as peticion:
        ubicacion, detener = consultar_geografia("8.8.8.8")
    assert ubicacion == {"estado": "consultada", "pais": "Ecuador", "ciudad": "Quito"}
    assert detener is False
    peticion.assert_called_once_with(
        "http://ip-api.com/json/8.8.8.8",
        params={"fields": "status,country,city", "lang": "es"},
        timeout=5,
    )


@pytest.mark.parametrize("error", [requests.Timeout, requests.ConnectionError])
def test_api_error_de_red(error):
    with patch("src.services.consulta_ip.requests.get", side_effect=error):
        ubicacion, detener = consultar_geografia("8.8.8.8")
    assert ubicacion["estado"] == "no_disponible"
    assert detener is False


def test_api_json_invalido():
    respuesta = respuesta_api({})
    respuesta.json.side_effect = ValueError("JSON inválido")
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta):
        ubicacion, _ = consultar_geografia("8.8.8.8")
    assert ubicacion["estado"] == "no_disponible"


def test_api_error_http():
    respuesta = respuesta_api({}, codigo=500)
    respuesta.raise_for_status.side_effect = requests.HTTPError("500")
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta):
        ubicacion, detener = consultar_geografia("8.8.8.8")
    assert ubicacion == {"estado": "no_disponible", "pais": None, "ciudad": None}
    assert detener is False


@pytest.mark.parametrize("datos", [{"status": "fail"}, [], {"status": "success"}])
def test_api_respuesta_incompleta(datos):
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta_api(datos)):
        ubicacion, _ = consultar_geografia("8.8.8.8")
    assert ubicacion["estado"] == "no_disponible"


def test_api_http_429_detiene_consultas():
    respuesta = respuesta_api({}, codigo=429, cuota="44")
    respuesta.raise_for_status.side_effect = requests.HTTPError("429")
    eventos = [evento(1), evento(2)]
    eventos[1]["ip"] = "1.1.1.1"
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta) as peticion:
        geografia = enriquecer_ips(eventos)
    assert peticion.call_count == 1
    assert geografia["1.1.1.1"]["estado"] == "pendiente_por_limite"


def test_api_cuota_agotada_detiene_consultas():
    respuesta = respuesta_api(
        {"status": "success", "country": "Ecuador", "city": "Quito"},
        cuota="0",
    )
    eventos = [evento(1), evento(2)]
    eventos[1]["ip"] = "1.1.1.1"
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta) as peticion:
        geografia = enriquecer_ips(eventos)
    assert peticion.call_count == 1
    assert geografia["8.8.8.8"]["estado"] == "consultada"
    assert geografia["1.1.1.1"]["estado"] == "pendiente_por_limite"


def test_api_limita_a_45_consultas():
    eventos = []
    for identificador in range(1, 47):
        registro = evento(identificador)
        registro["ip"] = "1.1.1." + str(identificador)
        eventos.append(registro)
    respuesta = respuesta_api(
        {"status": "success", "country": "Ecuador", "city": "Quito"},
    )
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta) as peticion:
        geografia = enriquecer_ips(eventos)
    assert peticion.call_count == 45
    assert len(geografia) == 46
    assert geografia["1.1.1.45"]["estado"] == "consultada"
    assert geografia["1.1.1.46"]["estado"] == "pendiente_por_limite"


def test_api_consulta_ip_repetida_una_sola_vez():
    respuesta = respuesta_api({"status": "success", "country": "Ecuador", "city": "Quito"})
    with patch("src.services.consulta_ip.requests.get", return_value=respuesta) as peticion:
        geografia = enriquecer_ips([evento(1), evento(2)])
    assert peticion.call_count == 1
    assert len(geografia) == 1


def test_modo_sin_api_no_hace_peticiones():
    with patch("src.services.consulta_ip.requests.get") as peticion:
        geografia = enriquecer_ips([evento(1)], usar_api=False)
    peticion.assert_not_called()
    assert geografia["8.8.8.8"]["estado"] == "omitida"


def test_persistencia_y_error_de_ruta(tmp_path):
    ruta = tmp_path / "reporte.json"
    assert guardar_reporte_json(ruta, {"pais": "Perú"}) is True
    assert json.loads(ruta.read_text(encoding="utf-8")) == {"pais": "Perú"}
    assert guardar_reporte_json(tmp_path / "inexistente" / "reporte.json", {}) is False


def test_pipeline_completo_con_datos_de_ejemplo(tmp_path):
    ruta = tmp_path / "reporte.json"
    assert procesar_archivos("data/logs.csv", "data/events.json", ruta, False) is True
    reporte = json.loads(ruta.read_text(encoding="utf-8"))
    assert reporte["total_eventos"] == 6
    assert reporte["eventos_invalidos"] == 2
    assert reporte["eventos_duplicados"] == 1
    assert reporte["errores_http_500"] == 2
    assert reporte["porcentaje_http_500"] == 33.33
    assert reporte["cpu_promedio_porcentaje"] == 56.67
    assert reporte["memoria_promedio_porcentaje"] == 67.0


def test_pipeline_falla_sin_entrada_y_no_crea_reporte(tmp_path):
    ruta = tmp_path / "reporte.json"
    assert procesar_archivos(tmp_path / "falta.csv", "data/events.json", ruta, False) is False
    assert not ruta.exists()


def test_procesamiento_con_api_fallida_conserva_metricas(tmp_path):
    ruta = tmp_path / "reporte.json"
    with patch("src.services.consulta_ip.requests.get", side_effect=requests.ConnectionError) as peticion:
        assert procesar_archivos("data/logs.csv", "data/events.json", ruta, True) is True
    reporte = json.loads(ruta.read_text(encoding="utf-8"))
    assert peticion.call_count == 3
    assert reporte["total_eventos"] == 6
    assert reporte["porcentaje_http_500"] == 33.33
    assert reporte["ips_criticas"] == ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
    for ubicacion in reporte["geografia_por_ip"].values():
        assert ubicacion == {"estado": "no_disponible", "pais": None, "ciudad": None}
