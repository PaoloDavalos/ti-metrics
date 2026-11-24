# Diagrama de clases de TI-Metrics

```mermaid
classDiagram
    class BaseLogParser {
        <<abstract>>
        #ValidadorEventos _validador
        +parse(ruta) tuple*
    }

    class CSVLogParser {
        +parse(ruta) tuple
    }

    class JSONLogParser {
        +parse(ruta) tuple
    }

    class ValidadorEventos {
        +normalizar(registro)
    }

    class ProcesadorEventos {
        +deduplicar(eventos) tuple
        +generar_reporte(eventos, invalidos, duplicados, geografia) dict
    }

    class ClienteUbicacion {
        -int __timeout
        +int timeout
        +consultar(ip) tuple
        +obtener_ubicaciones(eventos, usar_api) dict
    }

    class RepositorioReporteJSON {
        +guardar(ruta_json, reporte) bool
    }

    class AplicacionTIMetrics {
        #ValidadorEventos _validador
        #ProcesadorEventos _procesador
        #ClienteUbicacion _cliente
        #RepositorioReporteJSON _repositorio
        +ejecutar() bool
        +procesar_archivos(ruta_csv, ruta_json, ruta_reporte, usar_api) bool
    }

    BaseLogParser <|-- CSVLogParser
    BaseLogParser <|-- JSONLogParser
    BaseLogParser --> ValidadorEventos : valida registros
    AplicacionTIMetrics ..> CSVLogParser : crea primero
    AplicacionTIMetrics ..> JSONLogParser : crea después
    AplicacionTIMetrics ..> BaseLogParser : llama parse
    AplicacionTIMetrics *-- ValidadorEventos : comparte con los lectores
    AplicacionTIMetrics *-- ProcesadorEventos
    AplicacionTIMetrics *-- ClienteUbicacion
    AplicacionTIMetrics *-- RepositorioReporteJSON

    note for ClienteUbicacion "timeout es una propiedad de solo lectura de 5 segundos."
```

`python -m src.main` crea la aplicación y ejecuta el menú. La aplicación
llama a `parse(ruta)` primero con el lector CSV y luego con el lector JSON.
El método devuelve una lista de eventos válidos y la cantidad de registros
inválidos. `ValidadorEventos.normalizar` devuelve un diccionario o `None`.
