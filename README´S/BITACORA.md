# Bitácora de actividades — Robot Jardinero

**Elaborada:** 31 de octubre de 2026.  
**Participantes:** Karolina Guadalupe Ramírez Trujillo e Ivan Girón Gómez.  
**Duración prevista:** un día, 10 horas transcurridas con 1 hora de descansos.  
**Fecha de ejecución:** por completar.  
**Hora de inicio:** por completar.

Esta bitácora contiene actividades planificadas. Todas comienzan pendientes; completar horas reales, evidencia y resultados conforme se realicen. No afirmar que una prueba pasó ni inventar métricas antes de ejecutarla. El alcance técnico está en [README.md](README.md).

## Responsabilidades y orden

| N.º | Bloque relativo | Responsable | Actividad y evidencia esperada | Estado |
|---|---|---|---|---|
| 1 | 00:00–00:30 | Ambos | Revisar README y pendientes del profesor; comprobar Python/Tkinter; acordar estructuras de datos y nombres de acciones. Evidencia: acuerdos anotados y entorno ejecutable. | Pendiente |
| 2A | 00:30–02:00 | Karolina | Generar jardín con 5 plantas, 9 obstáculos, base y llave sin superposición; verificar conectividad; dibujar cuadrícula. Evidencia: mapa generado y validación. | Pendiente |
| 2B | 00:30–02:00 | Ivan | Implementar estado, movimientos, riego, relleno, meta y heurística. Evidencia: comprobaciones de consumo, restricciones y metas. | Pendiente |
| 3 | 02:00–02:15 | Ambos | Descanso. | Pendiente |
| 4A | 02:15–04:00 | Karolina | Crear controles de proporción, agua inicial/final y velocidad; animar una secuencia de prueba, implementar repetición. La secuencia temporal no sustituye el plan real. Evidencia: interfaz funcional. | Pendiente |
| 4B | 02:15–04:00 | Ivan | Implementar IDA*, control de ciclos por estado completo, recuperación del plan, expansiones, tiempo y tratamiento de imposibilidad. Evidencia: búsqueda ejecutada sin interfaz. | Pendiente |
| 5 | 04:00–04:30 | Ambos | Conectar configuración, búsqueda y animación. Evidencia: primera ejecución completa con plan calculado. | Pendiente |
| 6 | 04:30–05:00 | Ambos | Descanso/comida. | Pendiente |
| 7A | 05:00–06:30 | Karolina | Revisar planes de Ivan: acciones legales, costos, agua y cumplimiento de metas; registrar fallos y corregir su interfaz. Evidencia: tabla de casos y observaciones. | Pendiente |
| 7B | 05:00–06:30 | Ivan | Revisar generador y controles de Karolina: conectividad, proporción, cambios de configuración y repetición; corregir búsqueda. Evidencia: tabla de casos y observaciones. | Pendiente |
| 8 | 06:30–06:45 | Ambos | Descanso. | Pendiente |
| 9A | 06:45–08:00 | Karolina | Redactar introducción, PEAS, escenario e interfaz; capturar inicio, riego, relleno y final. Evidencia: secciones y capturas reales. | Pendiente |
| 9B | 06:45–08:00 | Ivan | Redactar estados, transiciones, IDA*, heurística y resultados medidos. Evidencia: secciones y tabla de métricas reales. | Pendiente |
| 10 | 08:00–09:00 | Ambos | Integrar reporte, discutir resultados y límites, revisar las secciones del compañero y ensayar explicación. Evidencia: borrador final y explicación de ambos sobre agua y algoritmo. | Pendiente |
| 11 | 09:00–10:00 | Ambos | Corregir incidencias pendientes, ejecutar desde cero, completar instrucciones y revisar archivos. Evidencia: entrega preparada y bitácora actualizada. | Pendiente |

Las letras A/B indican trabajo simultáneo. Las horas son una estimación, no resultados garantizados. El último bloque es margen de corrección y cierre; no se dedica a agregar funcionalidades.

## Acuerdos técnicos de la primera media hora

- Ivan define con Karolina cómo representar estado y aplicar acciones; Karolina define con Ivan la estructura del mapa generado.
- El resultado de búsqueda debe contener plan, métricas y estado de solución. El caso sin solución debe distinguirse de un error o interrupción.
- La animación utiliza el mismo modelo de transiciones que la búsqueda.
- Cambiar configuración invalida el plan previo. Repetir restaura el estado inicial del mismo escenario.
- Responsables de archivos previstos: Karolina, `jardin.py` e `interfaz.py`; Ivan, `modelo.py` y `busqueda.py`.
- El algoritmo de trabajo es IDA* conforme a la interpretación documentada; registrar cualquier aclaración real del profesor antes de modificarlo.

## Casos mínimos de verificación

| Caso | Resultado esperado | Ejecuta/revisa | Resultado real |
|---|---|---|---|
| Generar varios mapas | 8×8, 9 obstáculos, 5 plantas, base/llave distintas, sin superposiciones y celdas libres conectadas | Ivan / Karolina | Pendiente |
| 2 sedientas, 3 normales, inicio 3, meta cualquiera | Cinco plantas regadas y regreso a base | Karolina / Ivan | Pendiente |
| Distribución predeterminada, inicio 0 | Plan incluye relleno antes del primer riego | Karolina / Ivan | Pendiente |
| Distribución predeterminada, meta lleno | Termina en base con 3 y cinco plantas regadas | Karolina / Ivan | Pendiente |
| Distribución predeterminada, meta vacío | Termina en base con 0 y cinco plantas regadas | Karolina / Ivan | Pendiente |
| 5 sedientas, inicio 3, meta vacío | Informa imposibilidad, sin falsear éxito ni tirar agua | Karolina / Ivan | Pendiente |
| 5 normales, inicio 3, meta cualquiera | Plan válido; confirma extremo del selector | Karolina / Ivan | Pendiente |
| Regar sin agua suficiente o una planta atendida | Acción rechazada; estado no se modifica | Karolina / Ivan | Pendiente |
| Cambiar configuración y repetir animación | No se ejecutan planes obsoletos; repetir restaura el inicio | Ivan / Karolina | Pendiente |
| Métricas de un plan válido | Costo = movimientos + riegos + rellenos; desperdicio 0; tiempo excluye animación | Ambos | Pendiente |

Si una búsqueda tarda demasiado, registrar el caso y corregir el problema antes de afirmar que no existe solución. No incluir cifras ficticias en el informe.

## Registro real de ejecución

Agregar una fila por actividad completada o incidencia. Estados sugeridos: pendiente, en curso, completada o bloqueada.

| Fecha y hora real | N.º de actividad | Participante | Trabajo realizado | Evidencia/archivo | Estado y siguiente acción |
|---|---|---|---|---|---|
| Por completar | — | — | — | — | Pendiente |

## Cierre de la jornada

- [ ] Ambos participaron en programación, pruebas y documentación.
- [ ] El programa ejecuta una búsqueda real y anima su plan.
- [ ] Se verificaron las configuraciones y el caso sin solución.
- [ ] Las métricas y capturas provienen de ejecuciones reales.
- [ ] El README explica cómo ejecutar la versión implementada.
- [ ] Se registraron decisiones, fallos y cambios de alcance, si los hubo.
- [ ] Ambos pueden explicar estados, heurística, algoritmo y efecto del agua.
- [ ] Archivos de entrega revisados y listos.


Robot Jardinero - FIA/
│
├── README.md             # Definición e instrucciones del proyecto
├── BITACORA.md           # Actividades, responsables y avances
│
├── interfaz.py           # Ventana, controles y animación; inicia el programa
├── jardin.py             # Generación aleatoria y validación del mapa
├── modelo.py             # Estado, acciones y condiciones de meta
├── busqueda.py           # IDA*, heurística y métricas de búsqueda
│
├── pruebas/
│   └── test_robot.py     # Comprobaciones del modelo y la búsqueda
│
└── documentos/
    ├── reporte.md        # Borrador del documento entregable
    └── capturas/          # Imágenes de ejecuciones para el reporte



Archivo	              |Qué contiene	                                                    |  Responsable principal
interfaz.py	          |Cuadrícula, selectores, botones, barra del tanque y reproducción del plan	   |Karolina
jardin.py	          |Colocación de plantas, obstáculos, base y llave; comprobación de conectividad   |Karolina
modelo.py	          |Representación del estado y reglas para mover, regar, rellenar y comprobar la meta |Ivan
busqueda.py	          |Algoritmo IDA*, heurística, plan encontrado y estadísticas	                    |Ivan
pruebas/test_robot.py |Verificaciones de reglas, planes y casos sin solución	                        |Ambos
Documentación	      |README, bitácora, reporte y capturas	                                            |Ambos