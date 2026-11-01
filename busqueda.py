"""IDA*, heurística y métricas de búsqueda para el Robot Jardinero."""

from dataclasses import dataclass, field
import time
from typing import Optional

from modelo import (
    MOVIMIENTOS, REGAR, RELLENAR, Escenario, Estado,
    es_meta, estado_inicial, simular_plan, sucesores,
)


INFINITO = float("inf")

SOLUCION = "solucion"
SIN_SOLUCION = "sin_solucion"
INTERRUMPIDO = "interrumpido"

MENSAJE_SIN_SOLUCION = "No existe un plan que cumpla la meta seleccionada"


@dataclass
class Resultado:
    """Resultado de una búsqueda.

    `estado_busqueda` distingue tres casos: SOLUCION, SIN_SOLUCION (la búsqueda
    se agotó y se demostró que no hay plan) e INTERRUMPIDO (se alcanzó el límite
    de tiempo; no prueba nada sobre la existencia de solución).
    """

    estado_busqueda: str
    plan: list = field(default_factory=list)
    trayectoria: list = field(default_factory=list)  # estados, incluye el inicial
    costo: int = 0
    movimientos: int = 0
    riegos: int = 0
    rellenos: int = 0
    nodos_expandidos: int = 0   # expansiones efectivas en todas las iteraciones
    iteraciones: int = 0        # umbrales probados
    tiempo: float = 0.0         # segundos de búsqueda, sin animación
    plantas_regadas: int = 0
    agua_consumida: int = 0
    agua_restante: Optional[int] = None
    agua_desperdiciada: int = 0
    meta_cumplida: bool = False
    mensaje: str = ""


class _TiempoAgotado(Exception):
    pass


def explorar_alcanzables(escenario: Escenario):
    """Recorre todos los estados alcanzables desde el inicial (máximo 7,040).

    Devuelve (cantidad de estados alcanzables, si alguno cumple la meta).
    Es una verificación de existencia, no la búsqueda del plan: decide la
    imposibilidad en milisegundos, mientras que IDA* necesitaría agotar uno a
    uno todos los umbrales (cientos de iteraciones) para llegar a la misma
    conclusión.
    """
    inicial = estado_inicial(escenario)
    vistos = {inicial}
    pendientes = [inicial]
    hay_meta = False
    while pendientes:
        estado = pendientes.pop()
        if es_meta(escenario, estado):
            hay_meta = True
        for _, siguiente in sucesores(escenario, estado):
            if siguiente not in vistos:
                vistos.add(siguiente)
                pendientes.append(siguiente)
    return len(vistos), hay_meta


def distancia_manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica(escenario: Escenario, estado: Estado) -> int:
    """Estimación admisible del costo restante.

    Con plantas secas: cantidad de secas (un riego cada una) más la distancia
    Manhattan a la más lejana (hay que llegar hasta ella). Sin plantas secas:
    distancia a la base. No cuenta rellenos ni rodeos, por eso nunca sobreestima.
    """
    secas = [
        posicion
        for indice, posicion in enumerate(escenario.posiciones_plantas)
        if not (estado.regadas >> indice) & 1
    ]
    if secas:
        lejana = max(distancia_manhattan(estado.posicion, p) for p in secas)
        return len(secas) + lejana
    return distancia_manhattan(estado.posicion, escenario.base)


def resolver(escenario: Escenario, limite_tiempo: Optional[float] = None) -> Resultado:
    """Busca con IDA* un plan de costo mínimo.

    El umbral es de costo estimado f = g + h. Cada iteración es una búsqueda en
    profundidad que corta cuando f supera el umbral; el siguiente umbral es el
    menor f que lo excedió.

    Control de ciclos: se compara el estado completo (posición, plantas, agua).
    En cada iteración se recuerda el menor g con que se alcanzó cada estado y se
    descarta quien llegue con g igual o mayor. Esto evita ciclos y repeticiones
    sin perder optimalidad. La tabla se reinicia en cada iteración.

    Antes de iterar se comprueba que la meta sea alcanzable (ver
    `explorar_alcanzables`); si no lo es, se informa SIN_SOLUCION. Si lo es,
    IDA* termina siempre con el plan de costo mínimo. `limite_tiempo`
    (segundos) es opcional y produce INTERRUMPIDO, que no es una prueba de
    imposibilidad.
    """
    inicio_reloj = time.perf_counter()

    # Si ningún estado alcanzable cumple la meta, no hay plan: se informa de
    # inmediato. `nodos_expandidos` es aquí la cantidad de estados alcanzables
    # recorridos por la verificación (IDA* no llega a ejecutarse).
    alcanzables, hay_meta = explorar_alcanzables(escenario)
    if not hay_meta:
        return Resultado(
            estado_busqueda=SIN_SOLUCION,
            nodos_expandidos=alcanzables,
            tiempo=time.perf_counter() - inicio_reloj,
            mensaje=MENSAJE_SIN_SOLUCION,
        )

    inicial = estado_inicial(escenario)
    cache_h = {}
    expansiones = 0
    iteraciones = 0

    def h(estado):
        valor = cache_h.get(estado)
        if valor is None:
            valor = cache_h[estado] = heuristica(escenario, estado)
        return valor

    def profundidad(estado, g, umbral, mejor_g, plan):
        nonlocal expansiones
        f = g + h(estado)
        if f > umbral:
            return False, f
        if mejor_g.get(estado, INFINITO) <= g:
            return False, INFINITO
        mejor_g[estado] = g
        if es_meta(escenario, estado):
            return True, f
        if limite_tiempo is not None and time.perf_counter() - inicio_reloj > limite_tiempo:
            raise _TiempoAgotado()
        expansiones += 1
        menor_excedido = INFINITO
        for accion, siguiente in sucesores(escenario, estado):
            plan.append(accion)
            encontrado, valor = profundidad(siguiente, g + 1, umbral, mejor_g, plan)
            if encontrado:
                return True, valor
            plan.pop()
            if valor < menor_excedido:
                menor_excedido = valor
        return False, menor_excedido

    umbral = h(inicial)
    plan = []
    try:
        while True:
            iteraciones += 1
            plan = []
            encontrado, siguiente = profundidad(inicial, 0, umbral, {}, plan)
            if encontrado:
                estado_final = SOLUCION
                break
            if siguiente == INFINITO:
                estado_final = SIN_SOLUCION
                break
            umbral = siguiente
    except _TiempoAgotado:
        estado_final = INTERRUMPIDO
        plan = []

    tiempo = time.perf_counter() - inicio_reloj
    resultado = Resultado(
        estado_busqueda=estado_final,
        nodos_expandidos=expansiones,
        iteraciones=iteraciones,
        tiempo=tiempo,
    )
    if estado_final == SOLUCION:
        _calcular_metricas(escenario, plan, resultado)
    elif estado_final == SIN_SOLUCION:
        resultado.mensaje = MENSAJE_SIN_SOLUCION
    else:
        resultado.mensaje = "La búsqueda se interrumpió por el límite de tiempo."
    return resultado


def _calcular_metricas(escenario: Escenario, plan, resultado: Resultado) -> None:
    """Rellena las métricas a partir de la simulación del plan encontrado."""
    trayectoria = simular_plan(escenario, plan)
    consumida = 0
    for antes, despues in zip(trayectoria, trayectoria[1:]):
        if despues.regadas != antes.regadas:
            consumida += antes.agua - despues.agua
    final = trayectoria[-1]
    regadas = [i for i in range(len(escenario.necesidades)) if (final.regadas >> i) & 1]
    necesidad = sum(escenario.necesidades[i] for i in regadas)

    resultado.plan = list(plan)
    resultado.trayectoria = trayectoria
    resultado.costo = len(plan)
    resultado.movimientos = sum(1 for a in plan if a in MOVIMIENTOS)
    resultado.riegos = sum(1 for a in plan if a == REGAR)
    resultado.rellenos = sum(1 for a in plan if a == RELLENAR)
    resultado.plantas_regadas = len(regadas)
    resultado.agua_consumida = consumida
    resultado.agua_restante = final.agua
    resultado.agua_desperdiciada = consumida - necesidad
    resultado.meta_cumplida = es_meta(escenario, final)