import json

import pytest

from src.parsers.lector_csv import leer_logs_csv
from src.parsers.lector_json import leer_eventos_json
from src.utils.validacion import normalizar_evento


def evento_base():
    return {
        "id": 1, "ip": "8.8.8.8", "status_code": 200,
        "cpu": 25, "memoria": 40,
    }


def test_csv_normaliza_y_descarta_fila_invalida(tmp_path):
    ruta = tmp_path / "logs.csv"
    ruta.write_text(
        "id,ip,status_code,cpu,memoria\n"
        "1,8.8.8.8,200,25,40\n"
        "2,1.1.1.1,error,25,40\n",
        encoding="utf-8",
    )
    eventos, invalidos = leer_logs_csv(ruta)
    assert len(eventos) == 1
    assert eventos[0]["id"] == "1"
    assert eventos[0]["status_code"] == 200
    assert eventos[0]["cpu"] == 25.0
    assert invalidos == 1


def test_csv_rechaza_columnas_incompletas(tmp_path):
    ruta = tmp_path / "logs.csv"
    ruta.write_text("id,ip\n1,8.8.8.8\n", encoding="utf-8")
    with pytest.raises(ValueError):
        leer_logs_csv(ruta)


def test_json_filtra_eventos_incompletos(tmp_path):
    ruta = tmp_path / "events.json"
    ruta.write_text(json.dumps([evento_base(), {"id": 2}, None]))
    eventos, invalidos = leer_eventos_json(ruta)
    assert eventos == [normalizar_evento(evento_base())]
    assert invalidos == 2


def test_json_rechaza_objeto_en_lugar_de_lista(tmp_path):
    ruta = tmp_path / "events.json"
    ruta.write_text('{}', encoding="utf-8")
    with pytest.raises(ValueError):
        leer_eventos_json(ruta)


def test_json_mal_formado(tmp_path):
    ruta = tmp_path / "events.json"
    ruta.write_text('[', encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        leer_eventos_json(ruta)


@pytest.mark.parametrize("campo,valor", [
    ("ip", "invalida"), ("cpu", -1), ("cpu", 101),
    ("memoria", "NaN"), ("memoria", "inf"),
    ("status_code", 99), ("status_code", 600),
    ("status_code", 200.5), ("id", "  "), ("cpu", True),
])
def test_valida_campos_y_rangos(campo, valor):
    registro = evento_base()
    registro[campo] = valor
    assert normalizar_evento(registro) is None
