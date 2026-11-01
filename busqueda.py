"""IDA*, heurística y métricas de búsqueda para el Robot Jardinero."""

from dataclasses import dataclass, field
import time

from modelo import (
    MOVIMIENTOS, REGAR, RELLENAR,
    es_meta, estado_inicial, simular_plan, sucesores,
)


INFINITO = float("inf")
MENSAJE_SIN_SOLUCION = "No existe un plan que cumpla la meta seleccionada"


@dataclass
class Resultado:
    """Lo que devuelve la búsqueda: el plan y sus métricas."""

    hay_solucion: bool
    plan: list = field(default_factory=list)
    costo: int = 0
    movimientos: int = 0
    riegos: int = 0
    rellenos: int = 0
    nodos_expandidos: int = 0
    tiempo: float = 0.0          # segundos de búsqueda, sin la animación
    plantas_regadas: int = 0
    agua_consumida: int = 0
    agua_restante: int = 0
    agua_desperdiciada: int = 0
    meta_cumplida: bool = False
    mensaje: str = ""


def distancia_manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristica(escenario, estado):
    """Estimación del costo que falta; nunca lo sobreestima (es admisible).

    Si quedan plantas secas: (cantidad de secas) + (distancia a la más lejana).
    Cada planta seca necesita al menos un riego, y hay que llegar hasta la más
    lejana. Si no quedan secas: distancia a la base.
    No cuenta rellenos ni rodeos por obstáculos, por eso nunca pasa del costo real.
    """
    cantidad_secas = 0
    distancia_lejana = 0
    for planta, regada in zip(escenario.jardin.plantas, estado.regadas):
        if not regada:
            cantidad_secas += 1
            distancia = distancia_manhattan(estado.posicion, planta.posicion)
            if distancia > distancia_lejana:
                distancia_lejana = distancia
    if cantidad_secas > 0:
        return cantidad_secas + distancia_lejana
    return distancia_manhattan(estado.posicion, escenario.jardin.base)


def explorar_alcanzables(escenario):
    """Recorre todos los estados que se pueden alcanzar (máximo 7,040).

    Devuelve (cuántos son, si alguno cumple la meta). Sirve para saber, antes de
    buscar, si existe solución: así los casos imposibles se detectan al instante.
    """
    inicial = estado_inicial(escenario)
    vistos = {inicial}
    pendientes = [inicial]
    hay_meta = False
    while pendientes:
        estado = pendientes.pop()
        if es_meta(escenario, estado):
            hay_meta = True
        for accion, siguiente in sucesores(escenario, estado):
            if siguiente not in vistos:
                vistos.add(siguiente)
                pendientes.append(siguiente)
    return len(vistos), hay_meta


def resolver(escenario):
    """Busca con IDA* un plan de costo mínimo.

    IDA* repite una búsqueda en profundidad con un umbral de f = g + h:
      g = acciones hechas hasta ahora, h = heurística.
    Se corta cualquier camino cuyo f pase del umbral. Si no se encuentra la meta,
    el nuevo umbral es el menor f que se pasó, y se vuelve a empezar.

    Para no dar vueltas en círculos se compara el estado completo
    (posición, plantas regadas, agua): en cada iteración se recuerda con qué
    costo se llegó a cada estado y se descarta llegar a él con igual o más costo.
    """
    inicio_reloj = time.perf_counter()

    # Primero se comprueba que la meta se pueda alcanzar; si no, no hay plan.
    alcanzables, hay_meta = explorar_alcanzables(escenario)
    if not hay_meta:
        return Resultado(
            hay_solucion=False,
            nodos_expandidos=alcanzables,   # aquí: estados alcanzables revisados
            tiempo=time.perf_counter() - inicio_reloj,
            mensaje=MENSAJE_SIN_SOLUCION,
        )

    inicial = estado_inicial(escenario)
    nodos = 0

    def profundidad(estado, g, umbral, mejor_g, plan):
        """Devuelve (encontrado, f). Si no se encontró, f es el menor valor que pasó el umbral."""
        nonlocal nodos
        if mejor_g.get(estado, INFINITO) <= g:   # ya llegamos aquí igual o mejor
            return False, INFINITO
        f = g + heuristica(escenario, estado)
        if f > umbral:
            return False, f
        mejor_g[estado] = g
        if es_meta(escenario, estado):
            return True, f
        nodos += 1
        menor_excedido = INFINITO
        for accion, siguiente in sucesores(escenario, estado):
            plan.append(accion)
            encontrado, valor = profundidad(siguiente, g + 1, umbral, mejor_g, plan)
            if encontrado:
                return True, valor
            plan.pop()
            menor_excedido = min(menor_excedido, valor)
        return False, menor_excedido

    umbral = heuristica(escenario, inicial)
    while True:
        plan = []
        encontrado, siguiente = profundidad(inicial, 0, umbral, {}, plan)
        if encontrado or siguiente == INFINITO:
            break
        umbral = siguiente

    resultado = Resultado(hay_solucion=encontrado, nodos_expandidos=nodos)
    if encontrado:
        calcular_metricas(escenario, plan, resultado)
    else:
        resultado.mensaje = MENSAJE_SIN_SOLUCION
    resultado.tiempo = time.perf_counter() - inicio_reloj
    return resultado


def calcular_metricas(escenario, plan, resultado):
    """Rellena las métricas simulando el plan encontrado."""
    estados = simular_plan(escenario, plan)
    consumida = 0
    for accion, antes, despues in zip(plan, estados, estados[1:]):
        if accion == REGAR:
            consumida += antes.agua - despues.agua
    final = estados[-1]

    necesidad = 0
    for planta, regada in zip(escenario.jardin.plantas, final.regadas):
        if regada:
            necesidad += planta.agua_necesaria

    resultado.plan = list(plan)
    resultado.costo = len(plan)
    resultado.movimientos = sum(1 for a in plan if a in MOVIMIENTOS)
    resultado.riegos = plan.count(REGAR)
    resultado.rellenos = plan.count(RELLENAR)
    resultado.plantas_regadas = sum(final.regadas)
    resultado.agua_consumida = consumida
    resultado.agua_restante = final.agua
    resultado.agua_desperdiciada = consumida - necesidad
    resultado.meta_cumplida = es_meta(escenario, final)