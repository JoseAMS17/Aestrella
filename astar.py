"""
El buscador.

UNA sola clase hace los tres algoritmos, porque los tres son la misma busqueda
con distinta prioridad:

    prioridad = peso_g * g(n)  +  peso_h * h(n)

    peso_g = 1, peso_h = 1   ->  A*        (balancea las dos cosas)
    peso_g = 1, peso_h = 0   ->  Dijkstra  (solo mira lo que ya costo)
    peso_g = 0, peso_h = 1   ->  Greedy    (solo mira lo que falta)

Eso es literalmente lo que dice la pagina de Amit Patel: A* es como Dijkstra en
que favorece nodos cercanos al inicio, y como Greedy en que favorece nodos
cercanos a la meta. No son dos algoritmos parecidos a A*: son A* con uno de los
dos terminos apagado.

La clase expone paso(), que ejecuta UNA iteracion del bucle while. Asi la
interfaz puede animar la busqueda expansion por expansion, y el codigo se lee
igual que el pseudocodigo.
"""

import heapq
import time

from laberinto import COSTO_MINIMO

# Los tres modos: (nombre, peso_g, peso_h)
MODOS = (
    ("A*", 1.0, 1.0),
    ("Dijkstra", 1.0, 0.0),
    ("Greedy", 0.0, 1.0),
)


def epsilon_desempate(laberinto):
    """
    El factor de desempate de la pagina de heuristicas de Amit Patel.

        h = h * (1 + p)     con    p < costo_minimo_de_un_paso / largo_maximo

    En un laberinto de costo uniforme hay muchisimos caminos de la misma
    longitud, asi que un monton de nodos empatan en f y A* los explora todos.
    Inflar h un poquito rompe esos empates a favor de los nodos mas cercanos a
    la meta. El camino sale igual; el trabajo baja mucho.

    El largo maximo que un camino puede tener es, como tope, el numero de
    nodos del laberinto.
    """
    return COSTO_MINIMO / float(laberinto.nodos)


class Busqueda:
    """
    Una busqueda en curso. Se crea, se le llama paso() hasta que devuelve
    False, y despues se leen camino, costo y las estadisticas.
    """

    def __init__(self, laberinto, heuristica, peso_g=1.0, peso_h=1.0,
                 epsilon=0.0):
        self.laberinto = laberinto
        self.heuristica = heuristica
        self.peso_g = peso_g
        self.peso_h = peso_h
        self.epsilon = epsilon

        # Greedy de verdad no lleva cuentas: el primer camino que llega a un
        # nodo se queda, y nunca lo reconsidera. A* y Dijkstra si reconsideran
        # (relajan) cuando aparece un camino mas barato. ESTA linea es la que
        # hace que Greedy devuelva rutas peores; si Greedy tambien relajara,
        # acabaria encontrando el optimo casi siempre y la comparacion del
        # video no demostraria nada.
        self.relajar = peso_g != 0.0

        self.inicio = laberinto.inicio
        self.meta = laberinto.meta

        # g[n] = costo REAL del mejor camino conocido desde el inicio hasta n.
        # Un diccionario, no un atributo dentro de una clase Nodo: asi no
        # pueden existir dos copias del mismo nodo con g distintos, que es el
        # bug clasico de las implementaciones con clase Nodo.
        self.g = {self.inicio: 0.0}

        # padre[hijo] = nodo desde el que se llego a hijo.
        # Es el rastro de migas con el que se reconstruye el camino al final.
        self.padre = {self.inicio: None}

        # La lista cerrada: nodos ya expandidos. Un set, no una lista, porque
        # "esta este nodo dentro?" es la pregunta mas repetida del algoritmo.
        self.cerrados = set()

        # La lista abierta (la frontera): monticulo de (prioridad, orden, nodo).
        # El "orden" es un contador incremental y cumple dos funciones: rompe
        # los empates de prioridad de forma determinista, y evita que Python
        # intente comparar las tuplas de posicion cuando dos prioridades son
        # exactamente iguales.
        self._orden = 0
        self.frontera = []
        heapq.heappush(self.frontera,
                       (self._prioridad(self.inicio, 0.0), self._orden,
                        self.inicio))
        self.en_frontera = {self.inicio}

        # Estadisticas, para poder comparar los modos en el video.
        self.expandidos = 0
        self.generados = 1
        self.max_frontera = 1

        self.actual = None
        self.terminado = False
        self.exito = False
        self.camino = []
        self.costo = 0.0
        self.tiempo_ms = 0.0
        self._reloj = time.perf_counter()

    # --- f = g + h ----------------------------------------------------------
    def _prioridad(self, posicion, g):
        """
        La funcion de costo. Es el corazon del algoritmo:

            f(n) = g(n) + h(n)

        Los pesos permiten apagar un termino para obtener Dijkstra o Greedy, y
        epsilon es el desempate.
        """
        h = self.heuristica(posicion, self.meta) * (1.0 + self.epsilon)
        return self.peso_g * g + self.peso_h * h

    def f_de(self, posicion):
        """f del mejor camino conocido a esa posicion (para mostrarla en la UI)."""
        if posicion not in self.g:
            return None
        return self._prioridad(posicion, self.g[posicion])

    # --- una iteracion del bucle principal ---------------------------------
    def paso(self):
        """
        Ejecuta UNA expansion. Devuelve True si queda trabajo, False si la
        busqueda ya termino (con exito o sin camino posible).
        """
        if self.terminado:
            return False

        # Si la frontera se vacia sin haber llegado a la meta, no hay camino.
        if not self.frontera:
            self._finalizar(False)
            return False

        # 1. Sacar el nodo con la prioridad mas baja.
        _, _, actual = heapq.heappop(self.frontera)
        self.en_frontera.discard(actual)

        # Borrado perezoso: cuando encontramos un camino mejor a un nodo, lo
        # metemos otra vez en el monticulo en vez de buscar y modificar la
        # entrada vieja. Eso deja entradas obsoletas, que se descartan aqui.
        # Modificar un monticulo por dentro rompe su invariante, y es el bug que
        # los lectores del codigo de Medium llevan anos reportando.
        if actual in self.cerrados:
            return True

        self.actual = actual
        self.cerrados.add(actual)
        self.expandidos += 1

        # 2. Comprobar la meta AL SACAR, nunca al insertar.
        # Comprobarla al insertar parece funcionar y deja de hacerlo en cuanto
        # hay costos de movimiento: un camino mas barato a la meta puede
        # descubrirse despues de haberla visto por primera vez.
        if actual == self.meta:
            self._finalizar(True)
            return False

        # 3. Expandir los vecinos.
        for vecino, costo_paso in self.laberinto.vecinos(actual):
            nuevo_g = self.g[actual] + costo_paso

            # La relajacion: nos interesa el vecino si no lo conociamos, o si
            # este camino es ESTRICTAMENTE mejor que el que ya teniamos.
            # El 1e-9 es por la raiz de 2 de las diagonales: comparar flotantes
            # con < pelado mete reinserciones infinitas por error de redondeo.
            if self.relajar:
                vale_la_pena = (vecino not in self.g
                                or nuevo_g < self.g[vecino] - 1e-9)
            else:
                vale_la_pena = vecino not in self.g

            if vale_la_pena:
                self.g[vecino] = nuevo_g
                self.padre[vecino] = actual
                self._orden += 1
                heapq.heappush(self.frontera,
                               (self._prioridad(vecino, nuevo_g), self._orden,
                                vecino))
                self.en_frontera.add(vecino)
                self.generados += 1

        if len(self.frontera) > self.max_frontera:
            self.max_frontera = len(self.frontera)
        return True

    # --- cierre -------------------------------------------------------------
    def _finalizar(self, exito):
        self.terminado = True
        self.exito = exito
        self.tiempo_ms = (time.perf_counter() - self._reloj) * 1000.0
        if exito:
            self.camino = self._reconstruir()
            self.costo = self.g[self.meta]

    def _reconstruir(self):
        """
        Sigue la cadena de padres desde la meta hasta el inicio y da vuelta la
        lista. O(largo del camino), y no puede equivocarse.

        Esto es mejor que lo que hace la pagina de la rejilla hexagonal, que
        reconstruye buscando un vecino con g menor: con costo uniforme puede
        haber varios vecinos empatados en g y acabar devolviendo un camino que
        no es el que el buscador encontro.
        """
        camino = []
        actual = self.meta
        while actual is not None:
            camino.append(actual)
            actual = self.padre[actual]
        camino.reverse()
        return camino

    # --- atajo para uso sin animacion --------------------------------------
    def resolver(self):
        """Corre la busqueda completa de un tiron y se devuelve a si misma."""
        while self.paso():
            pass
        return self


def buscar(laberinto, modo="A*", heuristica=None, desempate=False):
    """
    Crea la busqueda ya configurada segun el modo elegido.

    modo: "A*", "Dijkstra" o "Greedy".
    """
    import heuristicas as heu

    if heuristica is None:
        heuristica = heu.recomendada(laberinto.diagonales)

    for nombre, peso_g, peso_h in MODOS:
        if nombre == modo:
            break
    else:
        raise ValueError("Modo desconocido: " + str(modo))

    # Dijkstra es, por definicion, h = 0. Apagamos el peso y ademas usamos la
    # heuristica cero, para que quede explicito en el codigo.
    if peso_h == 0.0:
        heuristica = heu.cero

    epsilon = epsilon_desempate(laberinto) if desempate else 0.0
    return Busqueda(laberinto, heuristica, peso_g, peso_h, epsilon)
