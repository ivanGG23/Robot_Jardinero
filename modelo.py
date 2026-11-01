"""Reglas del robot: estado, acciones y condición de meta.

No contiene búsqueda ni interfaz. La búsqueda y la animación usan las mismas
funciones de este módulo, así que comparten un único modelo de transiciones.
"""

from collections import namedtuple

from jardin import COLUMNAS, FILAS


CAPACIDAD_TANQUE = 3

MOVIMIENTOS = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}
REGAR = "regar"
RELLENAR = "rellenar"
ACCIONES = list(MOVIMIENTOS) + [REGAR, RELLENAR]

# Estado = (posición, plantas_regadas, agua)
#   posicion: (fila, columna)
#   regadas:  tupla de 5 booleanos; regadas[i] es True si la planta i ya se regó
#   agua:     unidades en el tanque (0 a 3)
Estado = namedtuple("Estado", ["posicion", "regadas", "agua"])


class Escenario:
    """Datos fijos de una ejecución: el mapa, el agua inicial y el agua final.

    agua_final es None (cualquier nivel), 3 (lleno) o 0 (vacío).
    """

    def __init__(self, jardin, agua_inicial=CAPACIDAD_TANQUE, agua_final=None):
        self.jardin = jardin
        self.agua_inicial = agua_inicial
        self.agua_final = agua_final


def estado_inicial(escenario):
    """Robot en la base, ninguna planta regada y el agua inicial elegida."""
    sin_regar = (False,) * len(escenario.jardin.plantas)
    return Estado(escenario.jardin.base, sin_regar, escenario.agua_inicial)


def buscar_planta(escenario, posicion):
    """Devuelve el índice de la planta que está en esa celda, o None."""
    for indice, planta in enumerate(escenario.jardin.plantas):
        if planta.posicion == posicion:
            return indice
    return None


def aplicar_accion(escenario, estado, accion):
    """Devuelve el nuevo estado, o None si la acción no es legal.

    Nunca modifica `estado`. Cada acción legal cuesta 1.
    """
    if accion in MOVIMIENTOS:
        d_fila, d_columna = MOVIMIENTOS[accion]
        destino = (estado.posicion[0] + d_fila, estado.posicion[1] + d_columna)
        if not (0 <= destino[0] < FILAS and 0 <= destino[1] < COLUMNAS):
            return None
        if destino in escenario.jardin.obstaculos:
            return None
        return Estado(destino, estado.regadas, estado.agua)

    if accion == REGAR:
        indice = buscar_planta(escenario, estado.posicion)
        if indice is None or estado.regadas[indice]:
            return None
        necesaria = escenario.jardin.plantas[indice].agua_necesaria
        if estado.agua < necesaria:
            return None
        regadas = list(estado.regadas)
        regadas[indice] = True
        return Estado(estado.posicion, tuple(regadas), estado.agua - necesaria)

    if accion == RELLENAR:
        if estado.posicion != escenario.jardin.llave:
            return None
        if estado.agua == CAPACIDAD_TANQUE:
            return None
        return Estado(estado.posicion, estado.regadas, CAPACIDAD_TANQUE)

    return None


def sucesores(escenario, estado):
    """Lista de (acción, nuevo_estado) para cada acción legal."""
    resultado = []
    for accion in ACCIONES:
        nuevo = aplicar_accion(escenario, estado, accion)
        if nuevo is not None:
            resultado.append((accion, nuevo))
    return resultado


def es_meta(escenario, estado):
    """Todas regadas, robot en la base y agua final según la condición elegida."""
    if not all(estado.regadas):
        return False
    if estado.posicion != escenario.jardin.base:
        return False
    if escenario.agua_final is None:
        return True
    return estado.agua == escenario.agua_final


def simular_plan(escenario, plan):
    """Aplica un plan desde el estado inicial y devuelve todos los estados.

    El resultado tiene len(plan) + 1 estados (el primero es el inicial); sirve
    para animar y para calcular métricas. Lanza ValueError si una acción no es legal.
    """
    estados = [estado_inicial(escenario)]
    for numero, accion in enumerate(plan, start=1):
        nuevo = aplicar_accion(escenario, estados[-1], accion)
        if nuevo is None:
            raise ValueError(f"La acción {numero} ('{accion}') no es legal.")
        estados.append(nuevo)
    return estados