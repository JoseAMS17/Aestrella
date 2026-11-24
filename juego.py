"""
Interfaz grafica (pygame).

Dos pantallas, y la primera es el editor, como pide el enunciado: el inicio, la
meta y los obstaculos se eligen con el raton ANTES de arrancar la busqueda.

    EDITOR     se dibuja el laberinto y se configura todo.
    ANIMACION  se ve a A* expandir nodos uno por uno hasta dar con la ruta.

Este archivo no sabe nada de A*: solo llama a busqueda.paso() y pinta lo que
encuentra en busqueda.cerrados, busqueda.en_frontera y busqueda.camino. Toda la
logica del algoritmo esta en astar.py.
"""

import pygame

import astar
import heuristicas
from laberinto import (Laberinto, LIBRE, PARED, BARRO,
                       LADO_MINIMO, LADO_MAXIMO)

# --- Medidas ----------------------------------------------------------------
ANCHO_PANEL = 320
MARGEN = 14
CELDA_MINIMA = 9
CELDA_MAXIMA = 40
ANCHO_MAXIMO_REJILLA = 1060
ALTO_MAXIMO_REJILLA = 720
ALTO_MINIMO_VENTANA = 660

# --- Colores (minimalistas: plano, sin degradados) --------------------------
C_FONDO = (18, 18, 20)
C_PANEL = (25, 25, 29)
C_BORDE = (44, 44, 50)
C_LIBRE = (31, 31, 35)
C_PARED = (122, 125, 133)
C_BARRO = (108, 78, 33)
C_CERRADO = (41, 63, 94)
C_FRONTERA = (58, 126, 160)
C_CAMINO = (240, 196, 80)
C_ACTUAL = (238, 241, 246)
C_INICIO = (82, 200, 120)
C_META = (226, 96, 92)
C_TEXTO = (226, 228, 233)
C_TENUE = (136, 140, 149)
C_ACENTO = (240, 196, 80)
C_ERROR = (226, 96, 92)

# --- Pinceles del editor ----------------------------------------------------
PINCEL_PARED = "pared"
PINCEL_BARRO = "barro (costo 5)"
PINCEL_INICIO = "inicio (A)"
PINCEL_META = "meta (B)"

VELOCIDADES = (1, 2, 4, 8, 16, 32, 64, 128)


def crear_fuente(tamano, negrita=False):
    try:
        fuente = pygame.font.SysFont(
            "consolas,dejavusansmono,couriernew,monospace", tamano, bold=negrita)
        if fuente is not None:
            return fuente
    except Exception:
        pass
    return pygame.font.Font(None, tamano + 4)


class Juego:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(
            "Algoritmo A* - ruta optima en un laberinto")

        self.laberinto = Laberinto()
        self.pincel = PINCEL_PARED
        self.modo = "A*"
        self.nombre_heuristica = None   # None = la que toque por el movimiento
        self.desempate = False
        self.indice_velocidad = 2

        self.busqueda = None
        self.pausado = False
        self.mensaje = ""
        self.color_mensaje = C_TENUE

        # Botones de pincel del panel: lista de (rectangulo, pincel).
        # Se rellena al dibujar y se consulta al hacer clic.
        self.botones = []

        self.fuente = crear_fuente(15)
        self.fuente_chica = crear_fuente(13)
        self.fuente_titulo = crear_fuente(19, negrita=True)

        self.pantalla = None
        self._crear_ventana()
        self.reloj = pygame.time.Clock()

    # =======================================================================
    # Ventana y coordenadas
    # =======================================================================
    def _crear_ventana(self):
        lab = self.laberinto
        # El tamano de celda se calcula para que la rejilla SIEMPRE quepa,
        # cualquiera sea el numero de nodos elegido.
        self.celda = max(CELDA_MINIMA,
                         min(CELDA_MAXIMA,
                             ANCHO_MAXIMO_REJILLA // lab.columnas,
                             ALTO_MAXIMO_REJILLA // lab.filas))
        self.ancho_rejilla = lab.columnas * self.celda
        self.alto_rejilla = lab.filas * self.celda

        ancho = self.ancho_rejilla + ANCHO_PANEL + MARGEN * 3
        alto = max(ALTO_MINIMO_VENTANA, self.alto_rejilla + MARGEN * 2)
        self.origen = (MARGEN, (alto - self.alto_rejilla) // 2)
        self.pantalla = pygame.display.set_mode((ancho, alto))

    def _casilla_en(self, pixel):
        """Pasa de pixeles de pantalla a (fila, columna), o None si esta fuera."""
        x, y = pixel
        ox, oy = self.origen
        if not (ox <= x < ox + self.ancho_rejilla):
            return None
        if not (oy <= y < oy + self.alto_rejilla):
            return None
        return ((y - oy) // self.celda, (x - ox) // self.celda)

    # =======================================================================
    # Bucle principal
    # =======================================================================
    def correr(self):
        funcionando = True
        while funcionando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    funcionando = False
                elif evento.type == pygame.KEYDOWN:
                    if self._tecla(evento.key) is False:
                        funcionando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self._clic_panel(evento.pos)
            self._raton()
            self._avanzar()
            self._dibujar()
            self.reloj.tick(60)
        pygame.quit()

    # =======================================================================
    # Entrada
    # =======================================================================
    def _raton(self):
        """Pintar arrastrando. Solo en el editor."""
        if self.busqueda is not None:
            return
        botones = pygame.mouse.get_pressed()
        if not (botones[0] or botones[2]):
            return
        casilla = self._casilla_en(pygame.mouse.get_pos())
        if casilla is None:
            return

        if botones[2]:                      # boton derecho: borrar
            self.laberinto.pintar(casilla, LIBRE)
        elif self.pincel == PINCEL_INICIO:
            self.laberinto.poner_inicio(casilla)
        elif self.pincel == PINCEL_META:
            self.laberinto.poner_meta(casilla)
        elif self.pincel == PINCEL_BARRO:
            self.laberinto.pintar(casilla, BARRO)
        else:
            self.laberinto.pintar(casilla, PARED)

    def _clic_panel(self, pixel):
        """Si el clic cayo en un boton de pincel, lo selecciona."""
        for rectangulo, pincel in self.botones:
            if rectangulo.collidepoint(pixel):
                self.pincel = pincel
                return True
        return False

    def _tecla(self, tecla):
        """Devuelve False si hay que cerrar el programa."""
        if tecla == pygame.K_q:
            return False

        if tecla == pygame.K_ESCAPE:
            self.busqueda = None
            self.mensaje = ""
            return True

        if tecla in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._empezar()
            return True

        if tecla == pygame.K_SPACE:
            if self.busqueda is None:
                self._empezar()
            else:
                self.pausado = not self.pausado
            return True

        if tecla == pygame.K_PERIOD and self.busqueda is not None:
            self.pausado = True
            self.busqueda.paso()
            return True

        if tecla == pygame.K_LEFTBRACKET:
            self.indice_velocidad = max(0, self.indice_velocidad - 1)
            return True
        if tecla == pygame.K_RIGHTBRACKET:
            self.indice_velocidad = min(len(VELOCIDADES) - 1,
                                        self.indice_velocidad + 1)
            return True

        # Configuracion del algoritmo. Vale en las dos pantallas: si se cambia
        # con la busqueda a medias, se reinicia con la nueva configuracion.
        if tecla == pygame.K_m:
            nombres = [n for n, _, _ in astar.MODOS]
            self.modo = nombres[(nombres.index(self.modo) + 1) % len(nombres)]
            self._reiniciar_si_corre()
            return True

        if tecla == pygame.K_h:
            opciones = [None] + [n for n, _ in heuristicas.CATALOGO]
            actual = opciones.index(self.nombre_heuristica)
            self.nombre_heuristica = opciones[(actual + 1) % len(opciones)]
            self._reiniciar_si_corre()
            return True

        if tecla == pygame.K_d:
            self.laberinto.diagonales = not self.laberinto.diagonales
            self._reiniciar_si_corre()
            return True

        if tecla == pygame.K_t:
            self.desempate = not self.desempate
            self._reiniciar_si_corre()
            return True

        # A partir de aqui, solo en el editor.
        if self.busqueda is not None:
            return True

        if tecla == pygame.K_o:
            self.pincel = PINCEL_PARED
        elif tecla == pygame.K_w:
            self.pincel = PINCEL_BARRO
        elif tecla == pygame.K_a:
            self.pincel = PINCEL_INICIO
        elif tecla == pygame.K_b:
            self.pincel = PINCEL_META
        elif tecla == pygame.K_c:
            self.laberinto.limpiar()
            self._avisar("Laberinto vacio.", C_TENUE)
        elif tecla == pygame.K_r:
            self.laberinto.aleatorio()
            self._avisar("Obstaculos al azar.", C_TENUE)
        elif tecla == pygame.K_u:
            self.laberinto.trampa_en_u()
            self._avisar("Trampa en U: prueba el modo Greedy.", C_ACENTO)
        elif tecla in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self._cambiar_tamano(2)
        elif tecla in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self._cambiar_tamano(-2)
        return True

    # =======================================================================
    # Acciones
    # =======================================================================
    def _avisar(self, texto, color=C_TENUE):
        self.mensaje = texto
        self.color_mensaje = color

    def _cambiar_tamano(self, delta):
        """Cambia el numero de nodos. Vacia el laberinto, porque la rejilla
        cambia de forma y las paredes viejas ya no significan lo mismo."""
        lab = self.laberinto
        filas = lab.filas + delta
        columnas = lab.columnas + delta * 3 // 2
        fuera = (filas < LADO_MINIMO or filas > LADO_MAXIMO
                 or columnas < LADO_MINIMO or columnas > LADO_MAXIMO)
        if fuera:
            self._avisar("Limite: de %d a %d casillas por lado."
                         % (LADO_MINIMO, LADO_MAXIMO), C_ERROR)
            return
        diagonales = lab.diagonales
        lab.redimensionar(filas, columnas)
        lab.diagonales = diagonales
        self.busqueda = None
        self._crear_ventana()
        self._avisar("Rejilla %d x %d = %d nodos."
                     % (lab.filas, lab.columnas, lab.nodos), C_TENUE)

    def _empezar(self):
        motivo = self.laberinto.validar()
        if motivo:
            self._avisar(motivo, C_ERROR)
            return
        heuristica = None
        if self.nombre_heuristica is not None:
            heuristica = dict(heuristicas.CATALOGO)[self.nombre_heuristica]
        self.busqueda = astar.buscar(self.laberinto, self.modo,
                                     heuristica=heuristica,
                                     desempate=self.desempate)
        self.pausado = False
        self.mensaje = ""

    def _reiniciar_si_corre(self):
        if self.busqueda is not None:
            self._empezar()

    def _avanzar(self):
        if self.busqueda is None or self.pausado or self.busqueda.terminado:
            return
        for _ in range(VELOCIDADES[self.indice_velocidad]):
            if not self.busqueda.paso():
                break

    # =======================================================================
    # Dibujo
    # =======================================================================
    def _dibujar(self):
        self.pantalla.fill(C_FONDO)
        self._dibujar_rejilla()
        self._dibujar_panel()
        pygame.display.flip()

    def _rect(self, posicion):
        ox, oy = self.origen
        fila, col = posicion
        return (ox + col * self.celda, oy + fila * self.celda,
                self.celda - 1, self.celda - 1)

    def _dibujar_rejilla(self):
        lab = self.laberinto
        busqueda = self.busqueda

        ox, oy = self.origen
        pygame.draw.rect(self.pantalla, C_BORDE,
                         (ox - 2, oy - 2,
                          self.ancho_rejilla + 3, self.alto_rejilla + 3))

        camino = set(busqueda.camino) if busqueda is not None else set()

        for fila in range(lab.filas):
            for col in range(lab.columnas):
                posicion = (fila, col)
                tipo = lab.casillas[fila][col]

                if tipo == PARED:
                    color = C_PARED
                elif tipo == BARRO:
                    color = C_BARRO
                else:
                    color = C_LIBRE

                # Las capas de la busqueda van encima del terreno libre, pero
                # nunca encima de una pared (una pared nunca se explora).
                if busqueda is not None and tipo != PARED:
                    if posicion in camino:
                        color = C_CAMINO
                    elif posicion in busqueda.cerrados:
                        color = C_CERRADO
                    elif posicion in busqueda.en_frontera:
                        color = C_FRONTERA

                pygame.draw.rect(self.pantalla, color, self._rect(posicion))

        # El nodo que se esta expandiendo ahora mismo.
        if (busqueda is not None and busqueda.actual is not None
                and not busqueda.terminado):
            pygame.draw.rect(self.pantalla, C_ACTUAL,
                             self._rect(busqueda.actual), 2)

        # Inicio y meta siempre visibles, encima de todo.
        pygame.draw.rect(self.pantalla, C_INICIO, self._rect(lab.inicio))
        pygame.draw.rect(self.pantalla, C_META, self._rect(lab.meta))

    def _linea(self, x, y, texto, color=C_TEXTO, fuente=None):
        if texto:
            fuente = fuente or self.fuente_chica
            self.pantalla.blit(fuente.render(texto, True, color), (x, y))
            return y + fuente.get_height() + 2
        return y + 7

    def _boton(self, x, y, ancho, etiqueta, color, activo):
        """Boton de pincel. Devuelve su rectangulo, para detectar el clic."""
        rectangulo = pygame.Rect(x, y, ancho, 28)
        pygame.draw.rect(self.pantalla,
                         (48, 48, 56) if activo else (33, 33, 39), rectangulo)
        if activo:
            pygame.draw.rect(self.pantalla, C_ACENTO, rectangulo, 2)
        pygame.draw.rect(self.pantalla, color,
                         (rectangulo.x + 8, rectangulo.y + 9, 12, 12))
        self.pantalla.blit(
            self.fuente_chica.render(etiqueta, True,
                                     C_TEXTO if activo else C_TENUE),
            (rectangulo.x + 28, rectangulo.y + 7))
        return rectangulo

    def _dibujar_panel(self):
        self.botones = []
        x = self.origen[0] + self.ancho_rejilla + MARGEN * 2
        pygame.draw.rect(self.pantalla, C_PANEL,
                         (x - MARGEN, 0, ANCHO_PANEL + MARGEN,
                          self.pantalla.get_height()))

        lab = self.laberinto
        busqueda = self.busqueda
        y = MARGEN

        y = self._linea(x, y, "ALGORITMO A*", C_ACENTO, self.fuente_titulo)
        y = self._linea(x, y, "f(n) = g(n) + h(n)", C_TEXTO, self.fuente)
        y = self._linea(x, y, "")

        # --- configuracion -------------------------------------------------
        if self.modo == "Dijkstra":
            texto_h = "h = 0  (por eso es Dijkstra)"
        elif self.nombre_heuristica is None:
            texto_h = "auto: " + heuristicas.nombre_recomendada(lab.diagonales)
        else:
            texto_h = self.nombre_heuristica
            correcta = heuristicas.nombre_recomendada(lab.diagonales)
            if self.nombre_heuristica != correcta:
                texto_h += "  (la propia es " + correcta + ")"

        y = self._linea(x, y, "modo        " + self.modo, C_ACENTO)
        y = self._linea(x, y, "heuristica  " + texto_h)
        y = self._linea(x, y, "vecinos     %d direcciones"
                        % (8 if lab.diagonales else 4))
        y = self._linea(x, y, "desempate   " + ("si" if self.desempate else "no"))
        y = self._linea(x, y, "rejilla     %d x %d = %d nodos"
                        % (lab.filas, lab.columnas, lab.nodos))
        y = self._linea(x, y, "velocidad   %d pasos/frame"
                        % VELOCIDADES[self.indice_velocidad])
        y = self._linea(x, y, "")

        # --- estado ---------------------------------------------------------
        if busqueda is None:
            ancho_boton = ANCHO_PANEL - MARGEN * 2

            y = self._linea(x, y, "1. ELIGE QUE PINTAR", C_ACENTO, self.fuente)
            for etiqueta, pincel, color in (
                    ("A    punto de INICIO", PINCEL_INICIO, C_INICIO),
                    ("B    punto de LLEGADA", PINCEL_META, C_META),
                    ("O    OBSTACULO (pared)", PINCEL_PARED, C_PARED),
                    ("W    barro, cuesta 5", PINCEL_BARRO, C_BARRO)):
                rectangulo = self._boton(x, y, ancho_boton, etiqueta, color,
                                         self.pincel == pincel)
                self.botones.append((rectangulo, pincel))
                y += 31

            y = self._linea(x, y, "")
            y = self._linea(x, y, "2. CLIC EN EL LABERINTO", C_ACENTO,
                            self.fuente)
            y = self._linea(x, y, "clic izquierdo pinta, derecho borra",
                            C_TENUE)
            y = self._linea(x, y, "se puede arrastrar sin soltar", C_TENUE)

            y = self._linea(x, y, "")
            y = self._linea(x, y, "3. PULSA ENTER PARA EMPEZAR", C_ACENTO,
                            self.fuente)

            y = self._linea(x, y, "")
            y = self._linea(x, y, "atajos", C_TENUE)
            y = self._linea(x, y, "C vaciar   R azar   U trampa en U", C_TENUE)
            y = self._linea(x, y, "+ -  mas / menos nodos", C_TENUE)
            y = self._linea(x, y, "M modo     H heuristica", C_TENUE)
            y = self._linea(x, y, "D 4 u 8 dir.   T desempate", C_TENUE)
            y = self._linea(x, y, "Q salir", C_TENUE)
        else:
            if busqueda.terminado:
                estado = "terminada"
            elif self.pausado:
                estado = "en pausa"
            else:
                estado = "buscando..."
            y = self._linea(x, y, "BUSQUEDA " + estado, C_ACENTO, self.fuente)
            y = self._linea(x, y, "expandidos (cerrados)  %d"
                            % busqueda.expandidos)
            y = self._linea(x, y, "en la frontera         %d"
                            % len(busqueda.en_frontera))
            y = self._linea(x, y, "frontera maxima        %d"
                            % busqueda.max_frontera)

            if busqueda.actual is not None:
                g = busqueda.g.get(busqueda.actual, 0.0)
                h = busqueda.heuristica(busqueda.actual, busqueda.meta)
                y = self._linea(x, y, "")
                y = self._linea(x, y, "nodo actual  (%d, %d)" % busqueda.actual)
                y = self._linea(x, y, "  g = %7.2f  lo que costo" % g)
                y = self._linea(x, y, "  h = %7.2f  lo que falta" % h)
                y = self._linea(x, y, "  f = %7.2f  g + h" % (g + h), C_CAMINO)

            y = self._linea(x, y, "")
            if busqueda.terminado and busqueda.exito:
                y = self._linea(x, y, "RUTA ENCONTRADA", C_CAMINO, self.fuente)
                y = self._linea(x, y, "costo total  %.2f" % busqueda.costo)
                y = self._linea(x, y, "pasos        %d" % (len(busqueda.camino) - 1))
                y = self._linea(x, y, "tiempo       %.1f ms" % busqueda.tiempo_ms)
            elif busqueda.terminado:
                y = self._linea(x, y, "NO HAY RUTA", C_ERROR, self.fuente)
                y = self._linea(x, y, "La frontera se vacio sin llegar a B.",
                                C_TENUE)

            y = self._linea(x, y, "")
            y = self._linea(x, y, "ESPACIO     pausa", C_TENUE)
            y = self._linea(x, y, ".           un solo paso", C_TENUE)
            y = self._linea(x, y, "[ ]         velocidad", C_TENUE)
            y = self._linea(x, y, "M           cambiar modo y repetir", C_TENUE)
            y = self._linea(x, y, "ENTER       repetir", C_TENUE)
            y = self._linea(x, y, "ESC         volver al editor", C_TENUE)

        # --- leyenda de colores y mensaje -----------------------------------
        leyenda = ((C_INICIO, "inicio A"), (C_META, "meta B"),
                   (C_PARED, "pared"), (C_BARRO, "barro, costo 5"),
                   (C_CERRADO, "ya expandido"),
                   (C_FRONTERA, "en la frontera"),
                   (C_CAMINO, "ruta optima"))

        alto = self.pantalla.get_height()
        y = alto - (len(leyenda) * 15 + 42)
        y = self._linea(x, y, "colores", C_TENUE)
        for color, etiqueta in leyenda:
            pygame.draw.rect(self.pantalla, color, (x, y + 3, 10, 10))
            self.pantalla.blit(
                self.fuente_chica.render(etiqueta, True, C_TENUE), (x + 18, y))
            y += 15

        if self.mensaje:
            self.pantalla.blit(
                self.fuente_chica.render(self.mensaje, True, self.color_mensaje),
                (x, alto - 20))
