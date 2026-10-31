# Robot Jardinero

Proyecto escolar de Fundamentos de Inteligencia Artificial.

**Estado:** definición del proyecto; implementación pendiente.  
**Última actualización:** 31 de octubre de 2026.

Este documento reúne los acuerdos del chat y sirve como referencia de alcance. Debe consultarse antes de implementar cambios y actualizarse cuando se acuerden nuevas decisiones. Las sugerencias pendientes no deben tratarse como requisitos confirmados por el profesor.

## Integrantes

- 7C — 243733 — Ramírez Trujillo Karolina Guadalupe.
- 7C — 243836 — Girón Gómez Ivan.
- Propuesta registrada por: 243836@ids.upchiapas.edu.mx.

## Propuesta y observación del profesor

Título registrado: **Robot Jardinero - Robot jardinero con depósito de agua limitado: planeación de riego con A* ponderada.**

El robot debe regar cinco plantas en un jardín de 8×8, administrar un tanque de tres unidades, rellenar en una llave y regresar a la base. La implementación será en Python y mostrará visualmente la ejecución del plan.

Observación del profesor del 29 de octubre de 2026:

> Dado que el líquido está límitado, se debe considerar un A* con profundidad iterativa
>
> Aceptado si se considera la influencia del vaciado del líquido

Posteriormente pidió entradas y salidas configurables, cambios de estado inicial y meta, y un escenario configurable.

**Decisión de trabajo:** utilizar IDA* (A* con profundización iterativa), interpretando esa observación. Falta confirmar explícitamente con el profesor que se refiere a IDA* en sustitución de A* ponderada. La propuesta original usaba ε = 1.5; la definición actual de IDA* utiliza `f = g + h`, sin esa ponderación. El cambio debe explicarse en el reporte, no presentarse como si ambos algoritmos fueran idénticos.

## Alcance acordado

| Elemento | Definición |
|---|---|
| Lenguaje | Python |
| Interfaz prevista | Tkinter, una ventana con animación por pasos |
| Jardín | Cuadrícula fija de 8×8 |
| Plantas | Exactamente cinco |
| Tipos | Normales: requieren 1 unidad; sedientas: requieren 2 |
| Proporción | Selector de 0 a 5 sedientas; normales = 5 − sedientas |
| Proporción predeterminada | 2 sedientas y 3 normales |
| Obstáculos | 9 celdas bloqueadas |
| Base y llave | Una de cada una, en celdas distintas y sin superposición con plantas u obstáculos |
| Tanque | Capacidad fija de 3 unidades |
| Posición inicial | La base |
| Agua inicial | Configurable entre 0 y 3; predeterminado: 3 |
| Plantas al inicio | Todas secas |
| Meta | Todas regadas y robot en la base, con condición seleccionable de agua final |
| Agua final | Cualquier nivel, tanque lleno (3) o tanque vacío (0) |
| Meta predeterminada | Cualquier nivel de agua |

No se incorporarán editor manual, tamaños de jardín variables, más de cinco plantas, sensores físicos, múltiples robots, algoritmos genéticos ni una acción para tirar agua. Las opciones sugeridas anteriormente de seleccionar plantas ya regadas o iniciar fuera de la base no forman parte de la configuración final acordada.

## Generación y configuración del escenario

El botón **Generar mapa** distribuye aleatoriamente las cinco plantas, nueve obstáculos, base y llave. Respeta la proporción de plantas seleccionada, evita superposiciones y verifica que las 55 celdas libres estén conectadas mediante movimientos ortogonales.

La conectividad permite acceder a plantas, base y llave, pero no garantiza toda condición de agua final para todas las proporciones de plantas. La búsqueda debe determinar si existe solución.

El mapa permanece fijo durante la búsqueda y la animación. Los cambios se hacen antes de una nueva ejecución y descartan el plan anterior. Repetir la animación conserva el escenario y restaura su estado inicial.

## Estado, acciones y meta

Estado: `(posición, plantas_regadas, agua)`.

- `posición`: `(fila, columna)` en una celda libre.
- `plantas_regadas`: cinco indicadores booleanos; puede representarse internamente con una máscara de bits.
- `agua`: entero entre 0 y 3.

Estado inicial: `(base, ninguna planta regada, agua inicial seleccionada)`.

Cada acción cuesta **1**:

| Acción | Condición | Efecto |
|---|---|---|
| Mover arriba, abajo, izquierda o derecha | Destino dentro del jardín y libre de obstáculos | Cambia la posición; no consume agua |
| Regar | Estar sobre una planta seca y disponer del agua necesaria | Marca la planta como regada y descuenta 1 o 2 unidades |
| Rellenar | Estar en la llave | Deja el tanque en 3; añade únicamente el agua faltante |

Pasar sobre una planta no la riega automáticamente. Se puede transitar sobre plantas, base y llave. No se permite regar plantas ya atendidas. Rellenar un tanque lleno no aporta progreso y puede omitirse en la búsqueda.

La meta exige simultáneamente:

1. Las cinco plantas regadas.
2. Robot en la base.
3. Agua final igual a 3 si se eligió lleno, igual a 0 si se eligió vacío, o cualquier valor si se eligió cualquier nivel.

Tamaño máximo combinatorio: `55 × 2^5 × 4 = 7,040` estados. No todos tienen que ser alcanzables.

## Algoritmo y heurística

IDA* realiza búsquedas en profundidad con un umbral creciente de `f(n) = g(n) + h(n)`. El umbral es de costo estimado, no solamente de cantidad de pasos. El siguiente umbral corresponde al menor valor que excedió el anterior.

- `g(n)`: total de movimientos, riegos y rellenos ejecutados hasta el estado.
- Si quedan plantas secas: `h(n) = cantidad de plantas secas + máxima distancia Manhattan desde el robot a una planta seca`.
- Si no quedan plantas secas: `h(n) = distancia Manhattan desde el robot a la base`.
- Distancia Manhattan: `|fila1 − fila2| + |columna1 − columna2|`.

La heurística es admisible: estima trabajo necesario sin incluir todos los desplazamientos, obstáculos o rellenos. Puede valer cero en la base aunque falte cumplir la condición de agua; por ello, la prueba de meta debe comprobar el estado completo, no solamente `h = 0`.

Con una implementación correcta, costos positivos y esta heurística, IDA* busca un plan de costo mínimo. La implementación deberá evitar ciclos comparando estados completos: volver a una posición con distinta agua o distintas plantas regadas puede ser necesario. También deberá terminar e informar cuando no exista solución; un límite artificial de tiempo no debe confundirse con una prueba de imposibilidad.

El agua participa en la búsqueda desde el inicio: restringe los riegos y obliga a planear visitas a la llave. No se añadirá el relleno como corrección posterior a una ruta calculada sin agua.

## Configuraciones sin solución

No se alterará automáticamente el mapa ni la meta para forzar una solución. Se mostrará: **“No existe un plan que cumpla la meta seleccionada”** cuando la búsqueda determine imposibilidad.

Ejemplo: cinco plantas sedientas, agua inicial de 3 y meta de tanque vacío. Cada riego desde un tanque lleno deja 1 unidad; antes del siguiente hay que rellenar a 3. Como no se puede tirar agua ni regar nuevamente, no se puede terminar en 0.

Con la distribución predeterminada de tres normales y dos sedientas y un mapa conectado, las tres metas son alcanzables para los niveles iniciales permitidos. La posibilidad de fallo aparece al permitir otras proporciones; no implica un defecto del generador.

## Interfaz y resultados

Controles previstos:

- Cantidad de plantas sedientas; mostrar automáticamente las normales restantes.
- Generar mapa.
- Agua inicial: 0, 1, 2 o 3.
- Agua final: cualquiera, lleno o vacío.
- Resolver/Iniciar.
- Repetir animación.
- Velocidad de animación.

La ventana mostrará la cuadrícula, obstáculos, base, llave, robot, diferencia visual entre tipos de plantas, cambio de secas a regadas y barra del tanque.

Resultados:

- Costo total del plan y desglose de movimientos, riegos y rellenos.
- Nodos expandidos: contar expansiones efectivas en todas las iteraciones de IDA*, incluyendo repeticiones; no confundir con estados únicos.
- Tiempo de búsqueda en segundos, excluyendo la animación.
- Plantas regadas: 5 de 5 cuando exista solución.
- Agua consumida al regar, agua restante y agua desperdiciada.
- Cumplimiento de la condición final seleccionada.

**Agua desperdiciada** = agua consumida al regar − necesidad total de las plantas efectivamente regadas. Será 0 por las reglas: cada planta recibe exactamente lo necesario. El agua que queda en el tanque es una reserva, no desperdicio. Esta métrica verifica el comportamiento; la optimización compara el costo de las acciones.

## PEAS y características del entorno

- **Rendimiento:** completar la meta, minimizar acciones y evitar desperdicio; medir expansiones y tiempo de búsqueda.
- **Entorno:** jardín de 8×8, plantas normales y sedientas, obstáculos, base y llave.
- **Actuadores simulados:** ruedas, regadera y válvula de llenado.
- **Sensores simulados:** humedad, nivel del tanque, posición y obstáculos, representados por los datos del programa.

Entorno determinista, monoagente, secuencial, completamente observable, discreto, estático y conocido durante cada ejecución. Generar aleatoriamente el mapa antes de comenzar no modifica el carácter determinista de las acciones.

## Organización prevista y entrega

Separar configuración/modelo del jardín, búsqueda y visualización, sin añadir una arquitectura innecesaria. El algoritmo debe recibir los datos del escenario; no habrá recorridos predefinidos.

El reporte puede incluir portada, introducción, PEAS, estados y acciones, algoritmo y heurística, implementación, resultados, discusión y bibliografía. El ejemplo del compañero es una referencia de estructura, no un requisito de usar población, cruces, mutaciones o poda genética. No se requieren videos exportados ni gráficas de evolución de población por aparecer en ese ejemplo.

## Pendientes de confirmar

1. Confirmar con el profesor IDA* como sustituto de A* ponderada.
2. Aclarar qué entiende por **salidas configurables**. Por ahora se contempla velocidad de animación configurable y resultados calculados para cada entrada/meta; no se afirma que eso cubra su criterio completo.
3. Conocer rúbrica, formato del reporte y posibles restricciones de bibliotecas.
4. Verificar Python y Tkinter en la computadora donde se presentará.

## Registro de decisiones

- **2026-10-31:** consolidación del alcance; mapa aleatorio conectado; inicio con agua configurable; meta con agua final configurable; cinco plantas con proporción configurable; IDA* como interpretación de trabajo pendiente de confirmación; definición explícita de casos sin solución y desperdicio.
