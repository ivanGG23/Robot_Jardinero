"""Generación del jardín; no contiene reglas de riego ni de búsqueda."""
# /usr/bin/python "/home/ivangg/Desktop/ARCHIVOS DE LA ESCUELA/IA/Robot_Jardinero/interfaz.py"

from dataclasses import dataclass
import random


FILAS = 8
COLUMNAS = 8
MIN_LADO = 3
MAX_LADO = 15
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
    filas: int = FILAS
    columnas: int = COLUMNAS


def obstaculos_para(filas: int, columnas: int) -> int:
    """Obstáculos escalados con el área del jardín."""
    return round(filas * columnas * TOTAL_OBSTACULOS / (FILAS * COLUMNAS))


def celdas_conectadas(obstaculos, filas=FILAS, columnas=COLUMNAS) -> bool:
    """Comprueba que todas las celdas libres formen un solo grupo conectado."""
    libres = {
        (f, c) for f in range(filas) for c in range(columnas)
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


def generar_jardin(cantidad_sedientas=2, filas=FILAS, columnas=COLUMNAS) -> Jardin:
    if type(cantidad_sedientas) is not int or not 0 <= cantidad_sedientas <= 5:
        raise ValueError("La cantidad de plantas sedientas debe ser un entero de 0 a 5.")
    if not (MIN_LADO <= filas <= MAX_LADO and MIN_LADO <= columnas <= MAX_LADO):
        raise ValueError(f"Filas y columnas deben estar entre {MIN_LADO} y {MAX_LADO}.")

    total_obstaculos = obstaculos_para(filas, columnas)
    if filas * columnas - total_obstaculos < TOTAL_PLANTAS + 2:
        raise ValueError("El mapa es demasiado pequeño para plantas, base y llave.")

    celdas = [(f, c) for f in range(filas) for c in range(columnas)]
    for _ in range(1000):
        obstaculos = frozenset(random.sample(celdas, total_obstaculos))
        if celdas_conectadas(obstaculos, filas, columnas):
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
    return Jardin(obstaculos, plantas, base, llave, filas, columnas)
