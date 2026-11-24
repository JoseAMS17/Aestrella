"""
Las heuristicas: h(n), la estimacion de lo que falta desde n hasta la meta.

Dos reglas mandan sobre todo lo demas en este archivo.

1) ESCALA.  h tiene que estar en las MISMAS UNIDADES que g. Por eso todas las
   funciones de aqui se multiplican por D, el costo del paso mas barato del
   laberinto, y no por un numero inventado. Si g se mide en una escala y h en
   otra, A* pesa mal una de las dos y las rutas empeoran.

2) ADMISIBILIDAD.  Una heuristica es admisible si NUNCA sobreestima el costo
   real que falta. Solo con heuristicas admisibles A* garantiza la ruta optima.
   Todas las de aqui lo son.

Lo que NO esta aqui, a proposito: la distancia euclidiana AL CUADRADO
(dx*dx + dy*dy sin raiz). Es la que usa el codigo del articulo de Medium, y la
pagina de heuristicas de Amit Patel la prohibe por nombre. El cuadrado crece
mucho mas rapido que g, asi que h sobreestima, deja de ser admisible y A*
degenera en Greedy: encuentra UN camino, no el OPTIMO. Nuestra entrega pide la
ruta optima, asi que esa formula no entra.
"""

import math

from laberinto import COSTO_MINIMO

# D  = costo del paso ortogonal mas barato.
# D2 = costo del paso diagonal mas barato (la diagonal mide raiz de 2).
D = COSTO_MINIMO
D2 = math.sqrt(2.0) * COSTO_MINIMO


def manhattan(a, b):
    """
    Para movimiento en 4 direcciones.

        h = D * (dx + dy)

    Cuenta los pasos en linea recta que faltan. Con 4 vecinos es exacta en un
    mapa vacio, asi que es la mejor heuristica admisible posible para ese caso.
    """
    dfila = abs(a[0] - b[0])
    dcol = abs(a[1] - b[1])
    return D * (dfila + dcol)


def octile(a, b):
    """
    Para movimiento en 8 direcciones.

        h = D * (dx + dy) + (D2 - 2*D) * min(dx, dy)

    La idea: se cuentan los pasos sin diagonales y despues se descuentan los
    que se ahorran. Hay min(dx, dy) pasos diagonales, y cada uno cuesta D2
    pero ahorra dos pasos ortogonales de D.
    """
    dfila = abs(a[0] - b[0])
    dcol = abs(a[1] - b[1])
    return D * (dfila + dcol) + (D2 - 2.0 * D) * min(dfila, dcol)


def euclidiana(a, b):
    """
    Distancia en linea recta.

        h = D * sqrt(dx^2 + dy^2)

    Solo es la heuristica correcta si se puede mover en cualquier angulo. En
    una rejilla SUBESTIMA (la linea recta es mas corta que cualquier camino por
    casillas), asi que sigue siendo admisible y la ruta sigue siendo optima,
    pero A* expande mas nodos de los necesarios. Esta aqui para poder
    demostrar en el video que una h mas floja cuesta mas trabajo.
    """
    dfila = a[0] - b[0]
    dcol = a[1] - b[1]
    return D * math.sqrt(dfila * dfila + dcol * dcol)


def cero(a, b):
    """
    h = 0.

    Con esta heuristica A* no es una aproximacion de Dijkstra: ES Dijkstra.
    Sin informacion sobre donde esta la meta, la prioridad f = g + 0 = g, y el
    buscador se expande en todas las direcciones por igual. Sirve de ORACULO:
    el costo que devuelve Dijkstra es el optimo verdadero, asi que comparar A*
    contra el es la forma de comprobar que nuestra heuristica es admisible.
    """
    return 0.0


# Las que se pueden rotar con la tecla H en el programa.
CATALOGO = (
    ("manhattan", manhattan),
    ("octile", octile),
    ("euclidiana", euclidiana),
)


def recomendada(diagonales):
    """La heuristica que corresponde al tipo de movimiento elegido."""
    return octile if diagonales else manhattan


def nombre_recomendada(diagonales):
    return "octile" if diagonales else "manhattan"
