"""
Modelo del laberinto.

Aqui no hay nada de A* ni de pygame: solo la rejilla, que casillas se pueden
pisar y cuanto cuesta entrar en cada una.

La razon de que esto sea un modulo aparte es conceptual: A* no ve casillas,
paredes ni pixeles. A* solo ve un GRAFO (nodos, y aristas con un costo). Este
modulo es el traductor: convierte "una matriz de casillas" en "un grafo".
Por eso el mismo A* de astar.py funcionaria sobre una rejilla hexagonal sin
cambiar una sola linea del buscador: solo habria que reescribir vecinos().
"""

import math
import random

# --- Tipos de casilla -------------------------------------------------------
LIBRE = 0
PARED = 1
BARRO = 2   # transitable, pero caro. Es lo que hace que g() importe de verdad.

COSTO_CASILLA = {LIBRE: 1.0, BARRO: 5.0}

# El costo del paso mas barato que existe en el laberinto.
# Las heuristicas se escalan con este valor, asi que tiene que ser el MINIMO y
# no un promedio: si fuera mayor que el minimo real, h sobreestimaria y A*
# perderia la garantia de la ruta optima.
COSTO_MINIMO = min(COSTO_CASILLA.values())

# --- Limites del tamano de la rejilla ---------------------------------------
# "Ni tan grande ni tan pequeno": 8x8 = 64 nodos de piso, 40x40 = 1600 de techo.
# Por encima de eso la animacion deja de verse, y por debajo el laberinto no
# tiene suficientes rutas alternativas para que "optima" signifique algo.
LADO_MINIMO = 8
LADO_MAXIMO = 40
FILAS_POR_OMISION = 16
COLUMNAS_POR_OMISION = 24

DESPLAZAMIENTOS_4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
DESPLAZAMIENTOS_DIAGONALES = ((-1, -1), (-1, 1), (1, -1), (1, 1))


def acotar_lado(valor):
    """Deja el valor dentro de [LADO_MINIMO, LADO_MAXIMO]."""
    return max(LADO_MINIMO, min(LADO_MAXIMO, int(valor)))


class Laberinto:
    """Una rejilla rectangular con un inicio (A), una meta (B) y obstaculos."""

    def __init__(self, filas=FILAS_POR_OMISION, columnas=COLUMNAS_POR_OMISION):
        self.redimensionar(filas, columnas)
        # Si es True se permiten los 8 vecinos. Cambia cual es la heuristica
        # correcta: con 4 vecinos toca Manhattan, con 8 toca octile.
        self.diagonales = False

    # --- tamano -------------------------------------------------------------
    def redimensionar(self, filas, columnas):
        self.filas = acotar_lado(filas)
        self.columnas = acotar_lado(columnas)
        self.casillas = [[LIBRE] * self.columnas for _ in range(self.filas)]
        fila_media = self.filas // 2
        self.inicio = (fila_media, 1)
        self.meta = (fila_media, self.columnas - 2)

    @property
    def nodos(self):
        return self.filas * self.columnas

    # --- consultas que usa A* ----------------------------------------------
    def dentro(self, p):
        fila, col = p
        return 0 <= fila < self.filas and 0 <= col < self.columnas

    def transitable(self, p):
        return self.dentro(p) and self.casillas[p[0]][p[1]] != PARED

    def costo_de_entrar(self, p):
        return COSTO_CASILLA[self.casillas[p[0]][p[1]]]

    def vecinos(self, p):
        """
        Cede (vecino, costo_del_paso) por cada vecino transitable.

        El costo del paso es el costo de ENTRAR en la casilla destino,
        multiplicado por raiz de 2 si el paso es diagonal. Esa raiz de 2 no es
        un adorno: si las diagonales costaran 1 como las ortogonales, g y h
        quedarian en escalas distintas y A* devolveria rutas que parecen
        correctas y no lo son.
        """
        fila, col = p

        for dfila, dcol in DESPLAZAMIENTOS_4:
            vecino = (fila + dfila, col + dcol)
            if self.transitable(vecino):
                yield vecino, self.costo_de_entrar(vecino)

        if not self.diagonales:
            return

        for dfila, dcol in DESPLAZAMIENTOS_DIAGONALES:
            vecino = (fila + dfila, col + dcol)
            if not self.transitable(vecino):
                continue
            # Prohibido cortar esquinas: para pasar en diagonal, las dos
            # casillas ortogonales que forman la esquina tienen que estar
            # libres. Sin esta comprobacion el camino se cuela entre dos
            # paredes que solo se tocan en un vertice, y se ve fatal en la demo.
            if not self.transitable((fila + dfila, col)):
                continue
            if not self.transitable((fila, col + dcol)):
                continue
            yield vecino, math.sqrt(2.0) * self.costo_de_entrar(vecino)

    # --- edicion (lo que hace el raton en el editor) ------------------------
    def pintar(self, p, tipo):
        """Pone una pared o barro, sin pisar nunca el inicio ni la meta."""
        if not self.dentro(p) or p == self.inicio or p == self.meta:
            return
        self.casillas[p[0]][p[1]] = tipo

    def poner_inicio(self, p):
        if not self.dentro(p) or p == self.meta:
            return
        self.casillas[p[0]][p[1]] = LIBRE
        self.inicio = p

    def poner_meta(self, p):
        if not self.dentro(p) or p == self.inicio:
            return
        self.casillas[p[0]][p[1]] = LIBRE
        self.meta = p

    def limpiar(self):
        for fila in range(self.filas):
            for col in range(self.columnas):
                self.casillas[fila][col] = LIBRE

    # --- generadores de laberintos de ejemplo -------------------------------
    def aleatorio(self, densidad_pared=0.22, densidad_barro=0.12, semilla=None):
        """
        Obstaculos al azar. La semilla fija lo hace reproducible.

        Despues de generar, despeja el inicio, la meta y sus vecinos
        ortogonales. Sin esto el azar tapia la salida cada tantas tiradas y el
        laberinto nace sin solucion, que para una demo es un desastre.
        """
        azar = random.Random(semilla)
        self.limpiar()
        for fila in range(self.filas):
            for col in range(self.columnas):
                tirada = azar.random()
                if tirada < densidad_pared:
                    self.casillas[fila][col] = PARED
                elif tirada < densidad_pared + densidad_barro:
                    self.casillas[fila][col] = BARRO

        for extremo in (self.inicio, self.meta):
            self.casillas[extremo[0]][extremo[1]] = LIBRE
            for dfila, dcol in DESPLAZAMIENTOS_4:
                vecino = (extremo[0] + dfila, extremo[1] + dcol)
                if self.dentro(vecino):
                    self.casillas[vecino[0]][vecino[1]] = LIBRE

    def trampa_en_u(self):
        """
        El obstaculo concavo de la pagina de Amit Patel, con la boca mirando al
        inicio y el fondo cerrado entre el inicio y la meta.

        Es el laberinto que DEMUESTRA la diferencia entre los tres modos:
        Greedy entra en la U porque solo mira h (la meta esta al otro lado),
        se come el callejon entero y tiene que salir. A* no entra, porque g le
        cobra el desvio.
        """
        self.limpiar()
        fila_sup = self.filas // 4
        fila_inf = self.filas - 1 - self.filas // 4
        col_boca = self.columnas // 3
        col_fondo = min(self.columnas - 3,
                        col_boca + max(3, self.columnas // 5))

        for fila in range(fila_sup, fila_inf + 1):
            self.casillas[fila][col_fondo] = PARED
        for col in range(col_boca, col_fondo + 1):
            self.casillas[fila_sup][col] = PARED
            self.casillas[fila_inf][col] = PARED

        fila_media = (fila_sup + fila_inf) // 2
        self.inicio = (fila_media, 1)
        self.meta = (fila_media, self.columnas - 2)
        self.casillas[self.inicio[0]][self.inicio[1]] = LIBRE
        self.casillas[self.meta[0]][self.meta[1]] = LIBRE

    # --- validacion ---------------------------------------------------------
    def validar(self):
        """Devuelve None si se puede buscar, o el motivo por el que no."""
        if self.inicio == self.meta:
            return "El inicio y la meta son la misma casilla."
        if not self.transitable(self.inicio):
            return "El inicio esta sobre una pared."
        if not self.transitable(self.meta):
            return "La meta esta sobre una pared."
        return None
