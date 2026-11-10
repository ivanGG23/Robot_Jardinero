"""Generación del jardín; no contiene reglas de riego ni de búsqueda."""

from dataclasses import dataclass
import random


FILAS = 8
COLUMNAS = 8
TOTAL_PLANTAS = 5
TOTAL_OBSTACULOS = 9
Posicion = tuple[int, int]


@dataclass(frozen=True)
class Planta:
    """Una planta normal necesita 1 unidad; una sedienta necesita 2."""

    posicion: Posicion
    agua_necesaria: int


@dataclass(frozen=True)
class Jardin:
    """Mapa fijo durante una ejecución; el orden de plantas identifica cada una."""

    obstaculos: frozenset[Posicion]
    plantas: tuple[Planta, ...]
    base: Posicion
    llave: Posicion


def celdas_conectadas(obstaculos: frozenset[Posicion]) -> bool:
    """Comprueba que todas las celdas libres formen un solo grupo conectado."""
    libres = {
        (fila, columna)
        for fila in range(FILAS)
        for columna in range(COLUMNAS)
    } - obstaculos
    if not libres:
        return False

    inicio = min(libres)
    pendientes = [inicio]
    visitadas = {inicio}
    while pendientes:
        fila, columna = pendientes.pop()
        for desplazamiento_fila, desplazamiento_columna in (
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ):
            vecina = (
                fila + desplazamiento_fila,
                columna + desplazamiento_columna,
            )
            if vecina in libres and vecina not in visitadas:
                visitadas.add(vecina)
                pendientes.append(vecina)

    return visitadas == libres


def generar_jardin(cantidad_sedientas: int = 2) -> Jardin:
    """Genera un mapa conectado con cinco plantas y nueve obstáculos.

    Las coordenadas (fila, columna) van de 0 a 7. El resultado se conserva
    durante la ejecución; generar otro jardín es una operación explícita.
    """
    if type(cantidad_sedientas) is not int or not 0 <= cantidad_sedientas <= 5:
        raise ValueError("La cantidad de plantas sedientas debe ser un entero de 0 a 5.")

    celdas = [
        (fila, columna)
        for fila in range(FILAS)
        for columna in range(COLUMNAS)
    ]
    # Se descartan distribuciones que dejen celdas libres aisladas.
    # El límite evita un ciclo sin fin ante un fallo inesperado.
    for _ in range(1000):
        obstaculos = frozenset(random.sample(celdas, TOTAL_OBSTACULOS))
        if celdas_conectadas(obstaculos):
            break
    else:
        raise RuntimeError("No se pudo generar un mapa conectado. Intenta nuevamente.")

    libres = [celda for celda in celdas if celda not in obstaculos]
    ubicaciones = random.sample(libres, TOTAL_PLANTAS + 2)
    base, llave = ubicaciones[:2]
    necesidades = [2] * cantidad_sedientas + [1] * (
        TOTAL_PLANTAS - cantidad_sedientas
    )
    random.shuffle(necesidades)
    plantas = tuple(
        Planta(posicion, agua)
        for posicion, agua in zip(ubicaciones[2:], necesidades)
    )
    return Jardin(obstaculos, plantas, base, llave)
