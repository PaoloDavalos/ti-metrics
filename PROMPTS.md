# Registro de consultas

Este archivo reúne las consultas sobre el Hito 1 de TI-Metrics.

## Registro de Prompt # 1

- **Fecha:** 2026-09-29
- **Módulo/Función:** Requisitos del Hito 1.
- **Prompt Enviado:** «¿Qué requisitos debo cumplir en el Hito 1 de TI-Metrics? ¿Necesito utilizar clases y hacer un diagrama UML en esta etapa?».
- **Respuesta de la IA:** El Hito 1 requiere leer archivos CSV y JSON, filtrar registros, eliminar duplicados, consultar datos geográficos mediante una API y generar un reporte JSON. Se utilizan tuplas, diccionarios y conjuntos, además de manejar errores al leer los archivos. Las clases y el diagrama UML corresponden al Hito 2.
- **Análisis Crítico:** Separar los requisitos por hitos permite trabajar primero con funciones y estructuras de datos, dejando las clases y el UML para la siguiente etapa.
- **Solución Final Aplicada:** Organización del Hito 1 en lectura de datos, validación, eliminación de duplicados, consulta de ubicación y generación del reporte.

## Registro de Prompt # 2

- **Fecha:** 2026-09-30
- **Módulo/Función:** Conceptos de programación para el Hito 1.
- **Prompt Enviado:** «¿Cómo puedo aplicar funciones, diccionarios, tuplas, conjuntos y manejo de archivos al Hito 1 de TI-Metrics?».
- **Respuesta de la IA:** Los diccionarios permiten representar los eventos; las listas, agruparlos; los conjuntos, identificar duplicados; y las tuplas, devolver varios resultados desde una función. Para leer y guardar archivos se utilizan csv y json. Para consultar la API se usa requests con timeout y manejo de excepciones.
- **Análisis Crítico:** Cada estructura cumple una función distinta. El conjunto permite detectar identificadores repetidos, mientras que la lista conserva los eventos completos. El diccionario de ubicaciones evita consultar varias veces una misma IP.
- **Solución Final Aplicada:** Los eventos se guardan en diccionarios y listas. Los lectores y la eliminación de duplicados devuelven tuplas. Se usa un conjunto para los identificadores y un diccionario para las ubicaciones. El código se organiza mediante funciones.

## Registro de Prompt # 3

- **Fecha:** 2026-10-01
- **Módulo/Función:** Estructura de data/, src/, tests/ y docs/.
- **Prompt Enviado:** «¿Cómo se organizan las carpetas y los archivos del Hito 1 de TI-Metrics?».
- **Respuesta de la IA:** data/ guarda las entradas y el reporte. src/ contiene el código: parsers/ agrupa los lectores, services/ las métricas y la consulta de ubicación, y utils/ la validación y el guardado. tests/ contiene las pruebas. models/ queda reservado para las clases y docs/ para la documentación y el UML del Hito 2. Los archivos __init__.py identifican las carpetas como paquetes de Python.
- **Análisis Crítico:** Separar los archivos según su función facilita encontrar y modificar cada parte del programa. Los lectores procesan las entradas, los servicios calculan métricas y consultan la API, y las utilidades validan y guardan los datos. main.py conecta estos pasos.
- **Solución Final Aplicada:** Se mantienen las carpetas requeridas. main.py conecta lector_csv.py, lector_json.py, metricas.py, consulta_ip.py y persistencia.py. Ambos lectores utilizan validacion.py. La carpeta docs/ se conserva para la documentación del proyecto.

## Registro de Prompt # 4

- **Fecha:** 2026-10-02
- **Módulo/Función:** src/utils/validacion.py
- **Prompt Enviado:** ¿Cómo puedo hacer que los registros del CSV y del JSON tengan el mismo formato antes de procesarlos?
- **Respuesta de la IA:** Usa una función para dar el mismo formato a los registros. Convierte el id a texto, el código HTTP a entero y los valores de CPU y memoria a números. Devuelve un diccionario con las mismas claves para ambos formatos.
- **Análisis Crítico:** CSV y JSON pueden representar el mismo identificador con tipos distintos. Si no se les da el mismo formato, el número 2 y el texto "2" podrían tratarse como identificadores diferentes.
- **Solución Final Aplicada:** La función normalizar_evento deja los datos con los mismos tipos y devuelve None cuando el registro no pasa las validaciones.

## Registro de Prompt # 5

- **Fecha:** 2026-10-03
- **Módulo/Función:** src/services/metricas.py
- **Prompt Enviado:** ¿Cómo puedo eliminar los eventos duplicados utilizando un conjunto?
- **Respuesta de la IA:** Recorre los eventos y guarda los identificadores en un set. Si un identificador ya está presente, cuenta el duplicado; si no está presente, agrégalo al conjunto y conserva el evento.
- **Análisis Crítico:** El conjunto permite comprobar si un id ya está guardado, con coste promedio O(1). Hay que decidir qué evento conservar cuando varios tengan el mismo id.
- **Solución Final Aplicada:** deduplicar_eventos conserva el primer evento válido de cada id y devuelve la lista sin duplicados junto con la cantidad de duplicados.

## Registro de Prompt # 6

- **Fecha:** 2026-10-05
- **Módulo/Función:** src/services/metricas.py
- **Prompt Enviado:** ¿Cómo calculo el porcentaje de errores HTTP 500 y qué hago si no hay eventos?
- **Respuesta de la IA:** Divide la cantidad de eventos con código exactamente 500 para el total de eventos válidos y únicos, multiplica por 100 y redondea a dos decimales. Si el total es cero, devuelve 0 para evitar una división entre cero.
- **Análisis Crítico:** Usar las entradas originales como denominador incluiría registros descartados o duplicados y alteraría el porcentaje.
- **Solución Final Aplicada:** generar_reporte calcula el porcentaje después de validar y deduplicar. Comprueba que el total sea mayor que cero antes de dividir.

## Registro de Prompt # 7

- **Fecha:** 2026-10-06
- **Módulo/Función:** src/services/consulta_ip.py
- **Prompt Enviado:** ¿Cómo manejo los errores al consultar la API sin perder las métricas locales?
- **Respuesta de la IA:** Configura un timeout de cinco segundos, comprueba el estado HTTP y captura las excepciones de requests y de lectura del JSON. Si la consulta falla, devuelve una ubicación marcada como no disponible.
- **Análisis Crítico:** Una respuesta HTTP correcta no garantiza que se haya obtenido la ubicación. También hay que revisar los datos del JSON.
- **Solución Final Aplicada:** consultar_geografia revisa la respuesta y devuelve el estado no_disponible cuando ocurre uno de los errores previstos. El reporte conserva las métricas locales.

## Registro de Prompt # 8

- **Fecha:** 2026-10-08
- **Módulo/Función:** src/services/consulta_ip.py
- **Prompt Enviado:** ¿Cómo evito consultar varias veces la ubicación de una misma IP?
- **Respuesta de la IA:** Guarda los resultados en un diccionario cuya clave sea la IP. Antes de consultar, comprueba si esa dirección ya tiene un resultado almacenado.
- **Análisis Crítico:** Repetir consultas aumenta el tiempo de ejecución y consume innecesariamente la cuota de la API.
- **Solución Final Aplicada:** enriquecer_ips realiza como máximo una consulta por IP durante cada ejecución y usa el mismo resultado para los registros con esa IP.

## Registro de Prompt # 9

- **Fecha:** 2026-10-09
- **Módulo/Función:** tests/test_services.py
- **Prompt Enviado:** ¿Cómo puedo probar el cliente de la API sin depender de internet?
- **Respuesta de la IA:** Utiliza unittest.mock.patch para sustituir requests.get durante las pruebas. Simula respuestas correctas, errores de conexión, timeouts y JSON inválido.
- **Análisis Crítico:** Las pruebas que dependen de una API real pueden fallar por problemas externos. Con respuestas simuladas se puede revisar cómo responde el programa en cada caso.
- **Solución Final Aplicada:** Las pruebas del cliente usan respuestas simuladas y comprueban tanto el resultado correcto como los errores previstos.
