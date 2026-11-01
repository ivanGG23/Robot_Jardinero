"""Reglas del robot: estado, acciones y condición de meta.

No contiene búsqueda ni interfaz. La búsqueda y la animación usan las mismas
funciones de este módulo, de modo que comparten un único modelo de transiciones.
"""

from typing import NamedTuple, Optional

from jardin import COLUMNAS, FILAS, Jardin, Posicion


CAPACIDAD_TANQUE = 3

MOVIMIENTOS = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}
REGAR = "regar"
RELLENAR = "rellenar"
ACCIONES = tuple(MOVIMIENTOS) + (REGAR, RELLENAR)


class Estado(NamedTuple):
    """(posición, plantas_regadas, agua). Es inmutable y se puede usar como clave.

    `regadas` es una máscara de bits: el bit i vale 1 si la planta i de
    `jardin.plantas` ya fue regada.
    """

    posicion: Posicion
    regadas: int
    agua: int


class Escenario:
    """Datos fijos de una ejecución: mapa, agua inicial y condición de agua final.

    `agua_final` es None (cualquier nivel), 3 (lleno) o 0 (vacío), igual que lo
    devuelve `obtener_configuracion` de la interfaz.
    """

    def __init__(self, jardin: Jardin, agua_inicial: int = CAPACIDAD_TANQUE,
                 agua_final: Optional[int] = None):
        if type(agua_inicial) is not int or not 0 <= agua_inicial <= CAPACIDAD_TANQUE:
            raise ValueError("El agua inicial debe ser un entero de 0 a 3.")
        if agua_final is not None and (
            type(agua_final) is not int or not 0 <= agua_final <= CAPACIDAD_TANQUE
        ):
            raise ValueError("El agua final debe ser None o un entero de 0 a 3.")
        self.jardin = jardin
        self.agua_inicial = agua_inicial
        self.agua_final = agua_final
        self.base = jardin.base
        self.llave = jardin.llave
        self.obstaculos = jardin.obstaculos
        self.posiciones_plantas = tuple(p.posicion for p in jardin.plantas)
        self.necesidades = tuple(p.agua_necesaria for p in jardin.plantas)
        self.indice_planta = {
            posicion: indice for indice, posicion in enumerate(self.posiciones_plantas)
        }
        self.todas_regadas = (1 << len(self.posiciones_plantas)) - 1


def estado_inicial(escenario: Escenario) -> Estado:
    """Robot en la base, ninguna planta regada y el agua inicial elegida."""
    return Estado(escenario.base, 0, escenario.agua_inicial)


def aplicar_accion(escenario: Escenario, estado: Estado, accion: str) -> Optional[Estado]:
    """Devuelve el nuevo estado, o None si la acción no es legal.

    Nunca modifica `estado`: una acción rechazada deja todo como estaba.
    Cada acción legal cuesta 1.
    """
    if accion in MOVIMIENTOS:
        d_fila, d_columna = MOVIMIENTOS[accion]
        destino = (estado.posicion[0] + d_fila, estado.posicion[1] + d_columna)
        if not (0 <= destino[0] < FILAS and 0 <= destino[1] < COLUMNAS):
            return None
        if destino in escenario.obstaculos:
            return None
        return Estado(destino, estado.regadas, estado.agua)

    if accion == REGAR:
        indice = escenario.indice_planta.get(estado.posicion)
        if indice is None or (estado.regadas >> indice) & 1:
            return None
        necesaria = escenario.necesidades[indice]
        if estado.agua < necesaria:
            return None
        return Estado(estado.posicion, estado.regadas | (1 << indice),
                      estado.agua - necesaria)

    if accion == RELLENAR:
        if estado.posicion != escenario.llave or estado.agua >= CAPACIDAD_TANQUE:
            return None
        return Estado(estado.posicion, estado.regadas, CAPACIDAD_TANQUE)

    return None


def sucesores(escenario: Escenario, estado: Estado):
    """Genera (acción, nuevo_estado) para cada acción legal, en orden fijo."""
    for accion in ACCIONES:
        nuevo = aplicar_accion(escenario, estado, accion)
        if nuevo is not None:
            yield accion, nuevo


def es_meta(escenario: Escenario, estado: Estado) -> bool:
    """Todas regadas, robot en la base y agua final según la condición elegida."""
    if estado.regadas != escenario.todas_regadas:
        return False
    if estado.posicion != escenario.base:
        return False
    return escenario.agua_final is None or estado.agua == escenario.agua_final


def simular_plan(escenario: Escenario, plan) -> list:
    """Aplica un plan desde el estado inicial y devuelve todos los estados.

    El resultado tiene len(plan) + 1 estados (el primero es el inicial), útil
    para animar. Lanza ValueError si alguna acción no es legal.
    """
    estados = [estado_inicial(escenario)]
    for numero, accion in enumerate(plan, start=1):
        nuevo = aplicar_accion(escenario, estados[-1], accion)
        if nuevo is None:
            raise ValueError(f"La acción {numero} ('{accion}') no es legal.")
        estados.append(nuevo)
    return estados