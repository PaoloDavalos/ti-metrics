# TI-Metrics

## Qué hace

Programa en Python 3 que lee archivos CSV y JSON, revisa los registros,
elimina los duplicados por id, consulta la ubicación de las IP y guarda un reporte JSON.

## Instalación

```bash
python -m pip install -r requirements.txt
```

## Cómo ejecutarlo

Desde la carpeta principal de `ti-metrics`:

```bash
python -m src.main
```

Selecciona `1` para consultar la ubicación de las IP o `2` para trabajar sin consultarla.
El resultado se guarda en `data/reporte.json`.
Si no se puede leer una entrada, no se genera un reporte nuevo.

Cada IP se consulta una sola vez, con timeout de 5 segundos y un máximo de
45 consultas por ejecución. HTTP 429 o `X-Rl: 0` detienen las consultas restantes.
Los errores de la API se indican como `no_disponible`; las IP pendientes por
el límite se indican como `pendiente_por_limite`. Sin API, el estado es `omitida`.

## Archivos de entrada

- `data/logs.csv`: encabezado `id,ip,status_code,cpu,memoria` y una fila por evento.
- `data/events.json`: lista de objetos con los mismos cinco campos.

| Campo | Valor válido |
| --- | --- |
| `id` | Número o texto no vacío que identifica el evento en ambos archivos; se convierte a texto. |
| `ip` | Dirección IPv4 o IPv6 válida. |
| `status_code` | Código HTTP entero entre 100 y 599. |
| `cpu` | Porcentaje entre 0 y 100. |
| `memoria` | Porcentaje entre 0 y 100. |

Los registros inválidos se descartan. Se conserva el primer evento válido
de cada id; el CSV se lee antes que el JSON.

## Reporte generado

- Total de eventos válidos sin repetir.
- Cantidad de registros inválidos y duplicados descartados.
- Cantidad de eventos con HTTP exactamente 500.
- Porcentaje HTTP 500: `errores HTTP 500 / eventos válidos y únicos × 100`.
- CPU y memoria promedio de los eventos válidos sin repetir.
- IP críticas ordenadas y sin repetir.

Los porcentajes y promedios se redondean a dos decimales; sin eventos valen 0.
Una IP es crítica si algún evento tiene **HTTP 500, CPU ≥ 90% o memoria ≥ 90%**.
El reporte también contiene los eventos procesados y las ubicaciones por IP.

## Pruebas

```bash
python -m pytest -q
```

Las pruebas de la API usan `unittest.mock` y no requieren internet.
