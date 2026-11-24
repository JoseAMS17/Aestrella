"""
Prueba de correccion, sin pygame.

    python prueba_consola.py

La idea sale de la pagina de heuristicas de Amit Patel: DIJKSTRA ES EL ORACULO.
Dijkstra (A* con h = 0) siempre devuelve el costo optimo verdadero. Entonces,
si A* con nuestra heuristica devuelve un costo distinto al de Dijkstra sobre el
mismo laberinto, la heuristica no es admisible y hay un bug.

Esta prueba es tambien el argumento del video: no decimos "nuestro A* encuentra
la ruta optima", lo comprobamos contra un algoritmo que la garantiza.
"""

import astar
import heuristicas
from laberinto import Laberinto, LIBRE, PARED, BARRO

SIMBOLOS = {LIBRE: ".", PARED: "#", BARRO: "~"}


def dibujar(laberinto, camino=()):
    """Mapa en texto. A = inicio, B = meta, o = camino."""
    camino = set(camino)
    lineas = []
    for fila in range(laberinto.filas):
        trozos = []
        for col in range(laberinto.columnas):
            posicion = (fila, col)
            if posicion == laberinto.inicio:
                trozos.append("A")
            elif posicion == laberinto.meta:
                trozos.append("B")
            elif posicion in camino:
                trozos.append("o")
            else:
                trozos.append(SIMBOLOS[laberinto.casillas[fila][col]])
        lineas.append("".join(trozos))
    return "\n".join(lineas)


def comparar(titulo, laberinto, desempate=False):
    print("=" * 66)
    print(titulo)
    print("  rejilla: %d x %d = %d nodos   diagonales: %s   desempate: %s"
          % (laberinto.filas, laberinto.columnas, laberinto.nodos,
             "si" if laberinto.diagonales else "no",
             "si" if desempate else "no"))
    motivo = laberinto.validar()
    if motivo:
        print("  LABERINTO INVALIDO:", motivo)
        return None

    resultados = {}
    print()
    print("  %-10s %9s %8s %10s %9s %9s"
          % ("modo", "costo", "pasos", "expandidos", "frontera", "ms"))
    print("  " + "-" * 60)
    for nombre, _, _ in astar.MODOS:
        busqueda = astar.buscar(laberinto, nombre, desempate=desempate).resolver()
        resultados[nombre] = busqueda
        if busqueda.exito:
            print("  %-10s %9.2f %8d %10d %9d %9.2f"
                  % (nombre, busqueda.costo, len(busqueda.camino),
                     busqueda.expandidos, busqueda.max_frontera,
                     busqueda.tiempo_ms))
        else:
            print("  %-10s %9s %8s %10d %9d %9.2f"
                  % (nombre, "sin ruta", "-", busqueda.expandidos,
                     busqueda.max_frontera, busqueda.tiempo_ms))
    print()
    return resultados


def verificar(resultados):
    """A* tiene que empatar con Dijkstra en costo. Greedy puede ser peor."""
    estrella = resultados["A*"]
    dijkstra = resultados["Dijkstra"]
    greedy = resultados["Greedy"]

    if estrella.exito != dijkstra.exito:
        print("  FALLO: A* y Dijkstra no coinciden en si hay ruta.")
        return False
    if not estrella.exito:
        print("  OK: no hay ruta, y los dos lo detectan.")
        return True

    diferencia = abs(estrella.costo - dijkstra.costo)
    if diferencia > 1e-6:
        print("  FALLO: A* costo %.4f pero el optimo es %.4f."
              % (estrella.costo, dijkstra.costo))
        print("         La heuristica no es admisible.")
        return False

    print("  OK: A* = %.2f = Dijkstra. La ruta es optima." % estrella.costo)
    ahorro = dijkstra.expandidos - estrella.expandidos
    if dijkstra.expandidos:
        print("      A* expandio %d nodos menos que Dijkstra (%.0f%% menos)."
              % (ahorro, 100.0 * ahorro / dijkstra.expandidos))
    if greedy.exito and greedy.costo > estrella.costo + 1e-6:
        print("      Greedy costo %.2f: %.2f mas caro. No garantiza el optimo."
              % (greedy.costo, greedy.costo - estrella.costo))
    elif greedy.exito:
        print("      Greedy acerto el optimo en este laberinto (puede pasar).")
    return True


def main():
    todo_bien = True

    # 1. La trampa en U: el laberinto que separa A* de Greedy.
    laberinto = Laberinto(15, 25)
    laberinto.trampa_en_u()
    resultados = comparar("1. TRAMPA EN U (obstaculo concavo)", laberinto)
    print(dibujar(laberinto, resultados["A*"].camino))
    print()
    todo_bien &= verificar(resultados)

    # 2. Aleatorio con barro, 4 direcciones. Aqui g importa de verdad.
    laberinto = Laberinto(16, 24)
    laberinto.aleatorio(semilla=7)
    resultados = comparar("2. ALEATORIO CON BARRO, 4 direcciones", laberinto)
    print(dibujar(laberinto, resultados["A*"].camino))
    print()
    todo_bien &= verificar(resultados)

    # 3. El mismo, con 8 direcciones y heuristica octile.
    laberinto.diagonales = True
    resultados = comparar("3. EL MISMO, 8 direcciones (octile)", laberinto)
    todo_bien &= verificar(resultados)

    # 4. Con desempate: mismo camino, menos trabajo.
    # Tiene que ser un mapa CON obstaculos. En uno vacio, Manhattan es exacta
    # y no hay nodos de sobra que recortar, asi que el desempate no haria nada.
    laberinto_limpio = Laberinto(20, 30)
    laberinto_limpio.aleatorio(densidad_pared=0.12, densidad_barro=0.0,
                               semilla=11)
    sin = comparar("4a. CON OBSTACULOS, sin desempate", laberinto_limpio)
    con = comparar("4b. EL MISMO, con desempate", laberinto_limpio,
                   desempate=True)
    todo_bien &= verificar(sin)
    if abs(sin["A*"].costo - con["A*"].costo) < 1e-6:
        print("  OK: el desempate no cambio el costo (%.2f), y expandio %d"
              " nodos en vez de %d."
              % (con["A*"].costo, con["A*"].expandidos, sin["A*"].expandidos))
    else:
        print("  AVISO: el desempate cambio el costo. Es posible (rompe la"
              " admisibilidad un poquito), pero revisalo.")

    # 5. Sin salida: la meta tapiada.
    laberinto = Laberinto(10, 12)
    for fila in range(laberinto.filas):
        laberinto.casillas[fila][6] = PARED
    resultados = comparar("5. SIN RUTA POSIBLE (muro completo)", laberinto)
    print(dibujar(laberinto))
    print()
    todo_bien &= verificar(resultados)

    # 6. Heuristicas comparadas sobre el mismo mapa.
    laberinto = Laberinto(20, 30)
    laberinto.aleatorio(semilla=3)
    print("=" * 66)
    print("6. LA MISMA BUSQUEDA CON DISTINTAS HEURISTICAS")
    print()
    print("  %-12s %9s %10s" % ("heuristica", "costo", "expandidos"))
    print("  " + "-" * 34)
    optimo = None
    for nombre, funcion in heuristicas.CATALOGO:
        b = astar.buscar(laberinto, "A*", heuristica=funcion).resolver()
        if optimo is None:
            optimo = b.costo
        print("  %-12s %9.2f %10d" % (nombre, b.costo, b.expandidos))
        if b.exito and abs(b.costo - optimo) > 1e-6:
            print("     AVISO: costo distinto al de manhattan.")
            todo_bien = False
    print()
    print("  Manhattan y euclidiana dan el MISMO costo (las dos son")
    print("  admisibles), pero euclidiana expande mas: subestima mas, asi que")
    print("  guia peor. Eso es exactamente lo que predice la teoria.")
    print()

    print("=" * 66)
    print("RESULTADO:", "TODO CORRECTO" if todo_bien else "HAY FALLOS")
    print("=" * 66)
    return 0 if todo_bien else 1


if __name__ == "__main__":
    raise SystemExit(main())
