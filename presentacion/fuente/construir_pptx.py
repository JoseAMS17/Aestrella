"""
Genera la versión PowerPoint de la presentacion.

    python construir_pptx.py

Deja "Presentacion Algoritmo A-estrella.pptx" en la carpeta del proyecto.

Mismo contenido y mismo esquema de color que la versión web, pero con fuentes
que existen en cualquier Windows (Calibri y Consolas), para que se vea igual en
la PC del aula.
"""

import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPTURAS = os.path.join(AQUI, "..", "CAPTURAS")
SALIDA = os.path.join(AQUI, "..", "Presentacion Algoritmo A-estrella.pptx")

# --- paleta, la misma de la version web -------------------------------------
FONDO = RGBColor(0x15, 0x16, 0x1A)
TARJETA = RGBColor(0x1C, 0x1E, 0x25)
TARJETA_ON = RGBColor(0x24, 0x1F, 0x13)
BORDE = RGBColor(0x30, 0x34, 0x3E)
CLARO = RGBColor(0xEC, 0xEE, 0xF2)
TENUE = RGBColor(0x99, 0xA2, 0xB2)
AMBAR = RGBColor(0xF0, 0xC4, 0x50)
AZUL = RGBColor(0x6F, 0xB3, 0xDC)
VERDE = RGBColor(0x68, 0xD3, 0x91)
ROJO = RGBColor(0xF0, 0x8A, 0x86)
OSCURO = RGBColor(0x15, 0x16, 0x1A)
AMBAR_TEXTO = RGBColor(0x3A, 0x2F, 0x12)

TEXTO = "Calibri"
MONO = "Consolas"

MARGEN = Inches(0.7)
ANCHO_UTIL = Inches(11.93)


# --- utilidades -------------------------------------------------------------
def caja(slide, x, y, ancho, alto):
    forma = slide.shapes.add_textbox(x, y, ancho, alto)
    marco = forma.text_frame
    marco.word_wrap = True
    marco.margin_left = 0
    marco.margin_right = 0
    marco.margin_top = 0
    marco.margin_bottom = 0
    return marco


def escribir(marco, trozos, tamano=16, color=CLARO, fuente=TEXTO,
             interlineado=1.25, espacio_antes=0, alineacion=PP_ALIGN.LEFT,
             nuevo=False):
    """trozos: un texto, o una lista de (texto, {bold, color, fuente, size})."""
    parrafo = marco.paragraphs[0] if not nuevo else marco.add_paragraph()
    parrafo.alignment = alineacion
    parrafo.line_spacing = interlineado
    if espacio_antes:
        parrafo.space_before = Pt(espacio_antes)
    if isinstance(trozos, str):
        trozos = [(trozos, {})]
    for texto, opciones in trozos:
        corrida = parrafo.add_run()
        corrida.text = texto
        fuente_corrida = corrida.font
        fuente_corrida.name = opciones.get("fuente", fuente)
        fuente_corrida.size = Pt(opciones.get("size", tamano))
        fuente_corrida.bold = opciones.get("bold", False)
        fuente_corrida.italic = opciones.get("italic", False)
        fuente_corrida.color.rgb = opciones.get("color", color)
    return parrafo


def lamina(presentacion, fondo=FONDO):
    slide = presentacion.slides.add_slide(presentacion.slide_layouts[6])
    relleno = slide.background.fill
    relleno.solid()
    relleno.fore_color.rgb = fondo
    return slide


def encabezado(slide, etiqueta, titulo, color_titulo=CLARO,
               color_etiqueta=AMBAR, tamano_titulo=34):
    marco = caja(slide, MARGEN, Inches(0.42), ANCHO_UTIL, Inches(0.3))
    escribir(marco, etiqueta, tamano=12, color=color_etiqueta, fuente=MONO)
    alto = Inches(1.0) if "\n" not in titulo else Inches(1.5)
    marco = caja(slide, MARGEN, Inches(0.82), ANCHO_UTIL, alto)
    for indice, linea in enumerate(titulo.split("\n")):
        escribir(marco, linea, tamano=tamano_titulo, color=color_titulo,
                 interlineado=1.08, nuevo=bool(indice))
    for parrafo in marco.paragraphs:
        for corrida in parrafo.runs:
            corrida.font.bold = True
    return Inches(0.82) + alto


def pie(slide, numero, claro=False):
    color = TENUE if not claro else AMBAR_TEXTO
    marco = caja(slide, MARGEN, Inches(6.93), Inches(9.0), Inches(0.3))
    escribir(marco, "Algoritmo A*  ·  Ruta óptima en un laberinto",
             tamano=10, color=color, fuente=MONO)
    marco = caja(slide, Inches(10.6), Inches(6.93), Inches(2.03), Inches(0.3))
    escribir(marco, str(numero), tamano=10, color=color, fuente=MONO,
             alineacion=PP_ALIGN.RIGHT)


def tarjeta(slide, x, y, ancho, alto, destacada=False):
    forma = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, ancho, alto)
    forma.adjustments[0] = 0.06
    forma.fill.solid()
    forma.fill.fore_color.rgb = TARJETA_ON if destacada else TARJETA
    forma.line.color.rgb = AMBAR if destacada else BORDE
    forma.line.width = Pt(1)
    forma.shadow.inherit = False
    forma.text_frame.text = ""
    return forma


def contenido_tarjeta(slide, x, y, ancho, titulo, cuerpo, color_titulo=AMBAR,
                      extra=None):
    marco = caja(slide, x + Inches(0.26), y + Inches(0.22),
                 ancho - Inches(0.52), Inches(0.4))
    escribir(marco, titulo, tamano=17, color=color_titulo)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, x + Inches(0.26), y + Inches(0.68),
                 ancho - Inches(0.52), Inches(1.4))
    escribir(marco, cuerpo, tamano=14, color=TENUE, interlineado=1.3)
    if extra:
        escribir(marco, extra, tamano=12, color=TENUE, interlineado=1.3,
                 espacio_antes=8, nuevo=True)


def tabla(slide, x, y, ancho, filas, anchos, alto_fila=Inches(0.42),
          tamano=13):
    numero_filas = len(filas)
    forma = slide.shapes.add_table(numero_filas, len(anchos), x, y, ancho,
                                   alto_fila * numero_filas)
    tabla_real = forma.table
    tabla_real.first_row = False
    tabla_real.horz_banding = False
    total = sum(anchos)
    for indice, proporcion in enumerate(anchos):
        tabla_real.columns[indice].width = Emu(int(ancho * proporcion / total))
    for indice_fila, fila in enumerate(filas):
        tabla_real.rows[indice_fila].height = alto_fila
        for indice_col, celda_datos in enumerate(fila):
            celda = tabla_real.cell(indice_fila, indice_col)
            celda.fill.solid()
            celda.fill.fore_color.rgb = (
                FONDO if indice_fila == 0
                else (TARJETA if indice_fila % 2 == 0 else FONDO))
            celda.vertical_anchor = MSO_ANCHOR.MIDDLE
            celda.margin_left = Inches(0.12)
            celda.margin_right = Inches(0.12)
            celda.margin_top = 0
            celda.margin_bottom = 0
            marco = celda.text_frame
            marco.word_wrap = True
            if isinstance(celda_datos, str):
                celda_datos = [(celda_datos, {})]
            parrafo = marco.paragraphs[0]
            for texto, opciones in celda_datos:
                corrida = parrafo.add_run()
                corrida.text = texto
                corrida.font.name = opciones.get("fuente", TEXTO)
                corrida.font.size = Pt(opciones.get("size", tamano))
                corrida.font.bold = opciones.get(
                    "bold", indice_fila == 0)
                corrida.font.color.rgb = opciones.get(
                    "color", AMBAR if indice_fila == 0 else CLARO)
    return forma


def bloque_codigo(slide, x, y, ancho, alto, lineas, tamano=13):
    forma = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, ancho, alto)
    forma.adjustments[0] = 0.04
    forma.fill.solid()
    forma.fill.fore_color.rgb = TARJETA
    forma.line.color.rgb = BORDE
    forma.line.width = Pt(1)
    forma.shadow.inherit = False
    marco = caja(slide, x + Inches(0.26), y + Inches(0.2),
                 ancho - Inches(0.52), alto - Inches(0.4))
    for indice, linea in enumerate(lineas):
        escribir(marco, linea, tamano=tamano, color=CLARO, fuente=MONO,
                 interlineado=1.35, nuevo=bool(indice))


def imagen(slide, nombre, x, y, ancho):
    ruta = os.path.join(CAPTURAS, nombre)
    return slide.shapes.add_picture(ruta, x, y, width=ancho)


def notas(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto


def tres_columnas():
    ancho = Emu(int((ANCHO_UTIL - Inches(0.6)) / 3))
    return [MARGEN + Emu(int(i * (ancho + Inches(0.3)))) for i in range(3)], ancho


# ===========================================================================
# Las laminas
# ===========================================================================
def construir():
    presentacion = Presentation()
    presentacion.slide_width = Inches(13.333)
    presentacion.slide_height = Inches(7.5)
    xs, ancho3 = tres_columnas()

    # --- 1. portada --------------------------------------------------------
    slide = lamina(presentacion)
    marco = caja(slide, MARGEN, Inches(1.35), ANCHO_UTIL, Inches(0.3))
    escribir(marco, "PROYECTO DE CLASE  ·  ITLA  ·  2026", tamano=13,
             color=AMBAR, fuente=MONO)
    marco = caja(slide, MARGEN, Inches(1.85), ANCHO_UTIL, Inches(1.1))
    escribir(marco, "Algoritmo A*", tamano=60, color=CLARO)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, MARGEN, Inches(3.05), ANCHO_UTIL, Inches(0.5))
    escribir(marco, "Búsqueda de la ruta óptima en un laberinto", tamano=24,
             color=AMBAR)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, MARGEN, Inches(4.15), ANCHO_UTIL, Inches(0.9))
    escribir(marco, "Implementado en Python con pygame  ·  El laberinto se "
             "dibuja antes de arrancar", tamano=14, color=TENUE)
    escribir(marco, "El mismo buscador ejecuta A*, Dijkstra y Greedy",
             tamano=14, color=TENUE, nuevo=True)
    marco = caja(slide, MARGEN, Inches(5.5), ANCHO_UTIL, Inches(0.9))
    escribir(marco, "Integrantes", tamano=14, color=AMBAR)
    marco.paragraphs[0].runs[0].font.bold = True
    escribir(marco, "Junior Alexandro Castillo  ·  Haniel García  ·  "
             "José Javier Pacheco  ·  José Alejandro Matos",
             tamano=15, color=TENUE, espacio_antes=6, nuevo=True)
    notas(slide, "Buenas. Somos el grupo que presenta el proyecto del "
          "algoritmo A estrella. Desarrollamos en Python un programa que "
          "encuentra la ruta óptima dentro de un laberinto, desde un punto A "
          "hasta un punto B.")

    # --- 2. el problema ----------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "01 · EL PROBLEMA",
               "No buscamos una ruta:\nbuscamos la más barata")
    marco = caja(slide, MARGEN, Inches(2.45), Inches(10.6), Inches(0.8))
    escribir(marco, [
        ("Una rejilla con obstaculos, un punto de partida ", {}),
        ("A", {"bold": True, "color": VERDE}),
        (" y uno de llegada ", {}),
        ("B", {"bold": True, "color": ROJO}),
        (". De todos los caminos posibles, queremos el de menor costo.", {}),
    ], tamano=17, color=TENUE, interlineado=1.3)
    for indice, (titulo, cuerpo) in enumerate([
            ("Barata, no corta",
             "No todas las casillas cuestan lo mismo. El suelo cuesta 1 y el "
             "barro cuesta 5."),
            ("La consecuencia",
             "El camino con menos pasos puede ser el más caro. Por eso "
             "hablamos de ruta óptima y no de ruta corta."),
            ("Para el algoritmo",
             "Un laberinto es un grafo: cada casilla es un nodo y cada "
             "movimiento una arista con su costo.")]):
        tarjeta(slide, xs[indice], Inches(3.7), ancho3, Inches(2.1),
                destacada=(indice == 2))
        contenido_tarjeta(slide, xs[indice], Inches(3.7), ancho3, titulo, cuerpo)
    pie(slide, 2)
    notas(slide, "Lo que buscamos no es una ruta cualquiera: es la ruta "
          "óptima, la más barata. El suelo normal cuesta uno y el barro cuesta "
          "cinco, así que el camino con menos pasos puede ser el más caro.")

    # --- 3. dos algoritmos -------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "02 · LA IDEA CENTRAL",
               "A* son dos algoritmos trabajando juntos")
    for indice, (titulo, cuerpo, extra, color) in enumerate([
            ("Dijkstra",
             "Explora el nodo más cercano al inicio. Crece como una mancha, "
             "en todas las direcciones.",
             "Encuentra el óptimo, pero trabaja de más", AZUL),
            ("Greedy Best-First",
             "Explora el nodo que parece más cercano a la meta. Va derecho "
             "hacia B.",
             "Muy rápido, pero no garantiza el óptimo", AZUL),
            ("A*",
             "Mira las dos cosas: lo que ya costo llegar y lo que falta por "
             "recorrer.",
             "Encuentra el óptimo y además trabaja poco", AMBAR)]):
        tarjeta(slide, xs[indice], Inches(2.45), ancho3, Inches(2.75),
                destacada=(indice == 2))
        contenido_tarjeta(slide, xs[indice], Inches(2.45), ancho3, titulo,
                          cuerpo, color_titulo=color, extra=extra)
    marco = caja(slide, MARGEN, Inches(5.6), ANCHO_UTIL, Inches(0.6))
    escribir(marco, "Dijkstra ignora donde esta la meta. Greedy ignora lo que "
             "ya gasto. A* es el equilibrio entre los dos.", tamano=14,
             color=TENUE)
    pie(slide, 3)
    notas(slide, "Dijkstra garantiza la ruta más corta pero trabaja de más "
          "porque no sabe donde esta la meta. Greedy es mucho más rápido pero "
          "no garantiza la ruta más corta porque ignora el costo recorrido. "
          "A estrella balancea las dos cosas.")

    # --- 4. la ecuacion (afirmacion) --------------------------------------
    slide = lamina(presentacion, fondo=AMBAR)
    marco = caja(slide, MARGEN, Inches(0.42), ANCHO_UTIL, Inches(0.3))
    escribir(marco, "03 · LA FUNCIÓN DE COSTO", tamano=12,
             color=AMBAR_TEXTO, fuente=MONO)
    marco = caja(slide, MARGEN, Inches(2.4), ANCHO_UTIL, Inches(1.3))
    escribir(marco, "f(n) = g(n) + h(n)", tamano=66, color=OSCURO, fuente=MONO)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, MARGEN, Inches(4.4), Inches(10.0), Inches(1.0))
    escribir(marco, "Todo el algoritmo sale de esta suma. En cada vuelta del "
             "ciclo, A* elige la casilla con la f más baja.", tamano=21,
             color=AMBAR_TEXTO, interlineado=1.3)
    pie(slide, 4, claro=True)
    notas(slide, "Todo sale de una sola fórmula: f de n igual a g de n más h "
          "de n. En cada vuelta, el algoritmo elige la casilla con la f más "
          "baja.")

    # --- 5. los tres terminos ---------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "04 · LOS TRES TÉRMINOS", "Qué significa cada letra")
    tabla(slide, MARGEN, Inches(2.2), ANCHO_UTIL, [
        ["Termino", "Qué es", "Naturaleza"],
        [[("g(n)", {"bold": True, "color": AMBAR, "fuente": MONO})],
         "Costo real y exacto del camino desde A hasta n",
         "Un hecho: ya se recorrio"],
        [[("h(n)", {"bold": True, "color": AMBAR, "fuente": MONO})],
         "Costo estimado desde n hasta B",
         "Una suposición: aun no ocurre"],
        [[("f(n)", {"bold": True, "color": AMBAR, "fuente": MONO})],
         "Estimación del costo total del camino que pasa por n",
         "La prioridad de la cola"],
    ], [0.16, 0.5, 0.34], alto_fila=Inches(0.5))
    bloque_codigo(slide, MARGEN, Inches(4.5), ANCHO_UTIL, Inches(1.35), [
        "g es lo que ya gastaste.",
        "h es lo que crees que te falta.",
        "f es lo que crees que te va a costar el viaje entero.",
    ], tamano=15)
    marco = caja(slide, MARGEN, Inches(6.1), ANCHO_UTIL, Inches(0.6))
    escribir(marco, "g se acumula: g(vecino) = g(actual) + costo de entrar al "
             "vecino. Si el paso es diagonal, ese costo se multiplica por "
             "raíz de 2.", tamano=13, color=TENUE)
    pie(slide, 5)
    notas(slide, "G es lo que ya gastaste: el costo real desde A hasta donde "
          "estas. H es lo que crees que te falta, la estimación: esa es la "
          "heuristica. Y F es la suma.")

    # --- 6. un solo buscador ----------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "05 · UN SOLO BUSCADOR",
               "No programamos tres algoritmos:\nprogramamos uno con dos pesos")
    bloque_codigo(slide, MARGEN, Inches(2.5), ANCHO_UTIL, Inches(0.78),
                  ["prioridad = peso_g · g(n) + peso_h · h(n)"], tamano=17)
    tabla(slide, MARGEN, Inches(3.55), ANCHO_UTIL, [
        ["Modo", "peso_g", "peso_h", "Qué mira", "Ruta óptima"],
        [[("A*", {"bold": True, "color": AMBAR})],
         [("1", {"fuente": MONO, "bold": True})],
         [("1", {"fuente": MONO, "bold": True})],
         "Lo que costo y lo que falta",
         [("Si", {"bold": True, "color": VERDE})]],
        ["Dijkstra",
         [("1", {"fuente": MONO, "bold": True})],
         [("0", {"fuente": MONO, "bold": True})],
         "Solo lo que costo",
         [("Si, explorando mucho más", {"color": VERDE})]],
        ["Greedy",
         [("0", {"fuente": MONO, "bold": True})],
         [("1", {"fuente": MONO, "bold": True})],
         "Solo lo que falta",
         [("No", {"bold": True, "color": ROJO})]],
    ], [0.17, 0.12, 0.12, 0.33, 0.26], alto_fila=Inches(0.48))
    marco = caja(slide, MARGEN, Inches(5.7), ANCHO_UTIL, Inches(0.8))
    escribir(marco, "Apagar un término convierte A* en el otro algoritmo. En "
             "el programa se cambia con la tecla M, sobre el mismo laberinto: "
             "eso es lo que permite comparar en vivo.", tamano=14, color=TENUE)
    pie(slide, 6)
    notas(slide, "No programamos tres algoritmos, programamos uno solo con dos "
          "pesos. Si apagamos el peso de h queda Dijkstra; si apagamos el de g "
          "queda Greedy. Se cambia con la tecla M sobre el mismo laberinto.")

    # --- 7. la heuristica --------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "06 · LA HEURISTICA",
               "Distancia Manhattan, y una condicion que lo decide todo")
    tarjeta(slide, MARGEN, Inches(2.35), Inches(6.4), Inches(1.95))
    marco = caja(slide, MARGEN + Inches(0.26), Inches(2.57), Inches(5.9),
                 Inches(0.35))
    escribir(marco, "La fórmula que usamos", tamano=17, color=AMBAR)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, MARGEN + Inches(0.26), Inches(3.0), Inches(5.9),
                 Inches(0.4))
    escribir(marco, "h = D · (dx + dy)", tamano=19, color=CLARO, fuente=MONO)
    marco = caja(slide, MARGEN + Inches(0.26), Inches(3.5), Inches(5.9),
                 Inches(0.7))
    escribir(marco, "Con movimiento en 4 direcciones: cuantos pasos en línea "
             "recta faltan. D es el costo del paso más barato, y se importa "
             "del laberinto en vez de escribirse a mano.", tamano=13,
             color=TENUE, interlineado=1.3)
    tarjeta(slide, MARGEN + Inches(6.7), Inches(2.35), Inches(5.23),
            Inches(1.95), destacada=True)
    contenido_tarjeta(slide, MARGEN + Inches(6.7), Inches(2.35), Inches(5.23),
                      "Admisible",
                      "Una heuristica es admisible si nunca sobreestima lo que "
                      "falta. Solo con una heuristica admisible A* garantiza "
                      "la ruta óptima.")
    tabla(slide, MARGEN, Inches(4.6), ANCHO_UTIL, [
        ["Si h(n)…", "Entonces A*..."],
        [[("= 0", {"fuente": MONO, "bold": True})],
         "es Dijkstra. Óptimo, pero explora muchisimo"],
        [[("<= costo real", {"fuente": MONO, "bold": True})],
         [("garantiza la ruta óptima", {"bold": True, "color": VERDE})]],
        [[("> costo real", {"fuente": MONO, "bold": True})],
         [("ya no garantiza el óptimo", {"bold": True, "color": ROJO}),
          (", aunque puede ser más rápido", {})]],
    ], [0.3, 0.7], alto_fila=Inches(0.48))
    pie(slide, 7)
    notas(slide, "Usamos la distancia Manhattan. Y hay una condicion que es la "
          "más importante del proyecto: la heuristica tiene que ser admisible, "
          "nunca puede sobrestimar. Si estima de más, A estrella deja de "
          "garantizar la ruta óptima.")

    # --- 8. la formula que no usamos ---------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "07 · UNA DECISIÓN DOCUMENTADA",
               "La fórmula que no usamos")
    marco = caja(slide, MARGEN, Inches(1.95), Inches(10.8), Inches(0.6))
    escribir(marco, "Una de las referencias que nos dieron trae un código que "
             "calcula la heuristica como distancia euclidiana al cuadrado.",
             tamano=16, color=TENUE, interlineado=1.3)
    bloque_codigo(slide, MARGEN, Inches(2.7), ANCHO_UTIL, Inches(0.78),
                  ["h = dx² + dy²      # distancia euclidiana AL CUADRADO"],
                  tamano=16)
    for indice, (titulo, cuerpo, color) in enumerate([
            ("Por qué falla",
             "El cuadrado crece mucho más rápido que g. Al sumar g + h, la "
             "heuristica domina y sobreestima.", ROJO),
            ("La consecuencia",
             "Deja de ser admisible, y en distancias largas A* degenera en "
             "Greedy: encuentra un camino, no el óptimo.", ROJO),
            ("Qué hicimos",
             "Descartarla. El enunciado pide la ruta óptima, y queda "
             "documentado en el encabezado de heuristicas.py.", AMBAR)]):
        tarjeta(slide, xs[indice], Inches(3.75), ancho3, Inches(1.95),
                destacada=(indice == 2))
        contenido_tarjeta(slide, xs[indice], Inches(3.75), ancho3, titulo,
                          cuerpo, color_titulo=color)
    marco = caja(slide, MARGEN, Inches(6.0), ANCHO_UTIL, Inches(0.6))
    escribir(marco, "La página de heuristicas de Amit Patel dedica una sección "
             "a esa fórmula. Su veredicto, literal: «Do not do this!»",
             tamano=13, color=TENUE)
    pie(slide, 8)
    notas(slide, "Una de las referencias traia un código que usa la distancia "
          "euclidiana al cuadrado, y esa fórmula sobrestima. No la usamos, y "
          "lo dejamos documentado en el código con la razon.")

    # --- 9. el manejo de los nodos -----------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "08 · EL MANEJO DE LOS NODOS", "Dos listas, y nada más")
    tarjeta(slide, MARGEN, Inches(2.05), Inches(4.5), Inches(1.8))
    contenido_tarjeta(slide, MARGEN, Inches(2.05), Inches(4.5),
                      "Lista abierta · la frontera",
                      "Casillas descubiertas pero no examinadas. Siempre "
                      "sacamos la de menor f.",
                      color_titulo=AZUL, extra="Un montículo (heapq).")
    tarjeta(slide, MARGEN, Inches(3.95), Inches(4.5), Inches(1.75))
    contenido_tarjeta(slide, MARGEN, Inches(3.95), Inches(4.5),
                      "Lista cerrada",
                      "Casillas ya examinadas, que no se vuelven a tocar.",
                      extra="Un set: es la consulta más repetida.")
    marco = caja(slide, MARGEN, Inches(5.85), Inches(4.5), Inches(0.9))
    escribir(marco, "Además, dos diccionarios: g con el costo real de cada "
             "nodo y padre con el rastro de migas para reconstruir el camino.",
             tamano=13, color=TENUE, interlineado=1.3)
    imagen(slide, "02_astar_medio.png", MARGEN + Inches(4.85), Inches(2.1),
           Inches(7.08))
    pie(slide, 9)
    notas(slide, "La lista abierta, o frontera, son las casillas descubiertas "
          "pero no examinadas, en azul claro. La lista cerrada son las ya "
          "examinadas, en azul oscuro. El panel muestra la G, la H y la F de "
          "la casilla que se esta examinando.")

    # --- 10. el ciclo -------------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "09 · EL CICLO", "Lo que se repite hasta llegar a la meta")
    bloque_codigo(slide, MARGEN, Inches(2.1), Inches(7.1), Inches(4.3), [
        "1. Si la lista abierta esta vacia -> no hay camino.",
        "2. Sacar el nodo con menor f.",
        "3. ¿Ya estaba cerrado? -> descartarlo y volver a 1.",
        "4. ¿Es la meta? -> terminar con éxito.",
        "5. Marcarlo como cerrado.",
        "6. Para cada vecino transitable:",
        "      nuevo_g = g[actual] + costo del paso",
        "      si es nuevo, o nuevo_g mejora lo anterior:",
        "            g[vecino] = nuevo_g",
        "            padre[vecino] = actual",
        "            encolar con nuevo_g + h(vecino)",
        "7. Volver a 1.",
    ], tamano=14)
    tarjeta(slide, MARGEN + Inches(7.4), Inches(2.1), Inches(4.53),
            Inches(2.0), destacada=True)
    contenido_tarjeta(slide, MARGEN + Inches(7.4), Inches(2.1), Inches(4.53),
                      "La meta se comprueba al sacar",
                      "Nunca al insertar. Comprobarla al insertar parece "
                      "funcionar y falla en cuanto hay costos distintos.")
    tarjeta(slide, MARGEN + Inches(7.4), Inches(4.3), Inches(4.53), Inches(2.1))
    contenido_tarjeta(slide, MARGEN + Inches(7.4), Inches(4.3), Inches(4.53),
                      "La relajación",
                      "El paso 6 es lo que permite corregirse: una casilla se "
                      "alcanza por varios caminos y nos quedamos con el mejor.")
    pie(slide, 10)
    notas(slide, "Sacamos la casilla con la F más baja; si es la meta "
          "terminamos, y si no la cerramos y miramos sus vecinos. Si el vecino "
          "es nuevo o llegamos por un camino más barato, actualizamos. Ese "
          "paso se llama relajación.")

    # --- 11. el ejemplo numerico -------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "10 · EL ALGORITMO EN NÚMEROS",
               "Las primeras expansiones, una por una")
    filas = [["#", "Expande", "g", "h", "f"]]
    datos = [("1", "(2,0)", "0", "6", "6", AMBAR), ("2", "(2,1)", "1", "5", "6", AMBAR),
             ("3", "(2,2)", "2", "4", "6", AMBAR), ("4", "(1,0)", "1", "7", "8", AZUL),
             ("5", "(3,0)", "1", "7", "8", AZUL), ("6", "(1,1)", "2", "6", "8", AZUL)]
    for numero, nodo, g, h, f, color in datos:
        filas.append([
            numero,
            [(nodo, {"fuente": MONO})],
            [(g, {"fuente": MONO})],
            [(h, {"fuente": MONO})],
            [(f, {"fuente": MONO, "bold": True, "color": color})],
        ])
    tabla(slide, MARGEN, Inches(2.1), Inches(6.1), filas,
          [0.14, 0.3, 0.18, 0.18, 0.2], alto_fila=Inches(0.42))
    marco = caja(slide, MARGEN, Inches(5.2), Inches(6.1), Inches(0.7))
    escribir(marco, "Laberinto de 8 x 8 con una pared vertical. Traza generada "
             "por el propio programa, no inventada.", tamano=12, color=TENUE)
    for indice, (titulo, cuerpo, destacada) in enumerate([
            ("f se queda en 6",
             "g sube 0, 1, 2 y h baja 6, 5, 4 a la misma velocidad. Cada "
             "unidad gastada compra una de progreso.", True),
            ("f salta a 8",
             "Ahí A* se topó con la pared. El salto de f es el precio del "
             "desvío, y no lo paga hasta agotar los nodos de f = 6.", False),
            ("El orden es por f",
             "Expande (2,2), lejos de A, antes que (1,0), su vecino directo. "
             "Dijkstra habría hecho lo contrario.", False)]):
        y = Inches(2.1 + indice * 1.5)
        tarjeta(slide, MARGEN + Inches(6.4), y, Inches(5.53), Inches(1.35),
                destacada=destacada)
        contenido_tarjeta(slide, MARGEN + Inches(6.4), y, Inches(5.53),
                          titulo, cuerpo,
                          color_titulo=AMBAR if destacada else AZUL)
    pie(slide, 11)
    notas(slide, "En las tres primeras filas f vale 6 y no cambia: g sube y h "
          "baja a la misma velocidad, el camino es perfecto. En la fila 4 f "
          "salta a 8: ahi se topó con la pared. El salto de f es el precio del "
          "desvío.")

    # --- 12. el laberinto ---------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "11 · EL LABERINTO", "Se dibuja antes de arrancar")
    imagen(slide, "01_editor.png", MARGEN, Inches(2.1), Inches(7.3))
    for indice, (titulo, cuerpo) in enumerate([
            ("Qué se elige con el ratón",
             "A inicio · B meta · paredes · barro. No busca nada hasta pulsar "
             "Enter."),
            ("Este laberinto",
             "16 x 24 = 384 nodos, 22 paredes y 20 casillas de barro. "
             "A en (7, 1) y B en (7, 22)."),
            ("Tamaño configurable",
             "De 8 x 8 a 40 x 40 con las teclas más y menos.")]):
        y = Inches(2.1 + indice * 1.5)
        tarjeta(slide, MARGEN + Inches(7.6), y, Inches(4.33), Inches(1.35),
                destacada=(indice == 2))
        contenido_tarjeta(slide, MARGEN + Inches(7.6), y, Inches(4.33),
                          titulo, cuerpo)
    pie(slide, 12)
    notas(slide, "El punto A es la casilla verde y el B la roja. Todo se "
          "dibuja antes de arrancar, con el ratón. El programa no busca nada "
          "hasta que uno le da a Enter.")

    # --- 13. la demostracion ------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "12 · LA DEMOSTRACIÓN", "A* encuentra la ruta óptima")
    imagen(slide, "03_astar.png", MARGEN, Inches(2.1), Inches(8.3))
    for indice, (cifra, rotulo) in enumerate([
            ("29,00", "costo total"), ("29", "pasos"),
            ("111", "nodos expandidos"), ("0,6", "milisegundos")]):
        y = Inches(2.1 + indice * 1.12)
        tarjeta(slide, MARGEN + Inches(8.6), y, Inches(3.33), Inches(1.0),
                destacada=(indice == 0))
        marco = caja(slide, MARGEN + Inches(8.82), y + Inches(0.12),
                     Inches(2.9), Inches(0.5))
        escribir(marco, cifra, tamano=26, color=AMBAR, fuente=MONO)
        marco.paragraphs[0].runs[0].font.bold = True
        marco = caja(slide, MARGEN + Inches(8.82), y + Inches(0.62),
                     Inches(2.9), Inches(0.3))
        escribir(marco, rotulo, tamano=12, color=TENUE)
    pie(slide, 13)
    notas(slide, "Vean cómo se extiende hacia la meta, no en todas las "
          "direcciones. Encontro la ruta en amarillo, con costo 29, y expandió "
          "111 nodos. La ruta rodea el barro en vez de atravesarlo.")

    # --- 14. los tres modos -------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "13 · LOS TRES MODOS, EL MISMO LABERINTO",
               "Misma búsqueda, distinta prioridad")
    for indice, (archivo, nombre, costo, nodos, destacada, color_costo) in enumerate([
            ("03_astar_rejilla.png", "A*", "29,00", "111", True, AMBAR),
            ("04_dijkstra_rejilla.png", "Dijkstra", "29,00", "276", False, CLARO),
            ("05_greedy_rejilla.png", "Greedy", "53,00", "46", False, ROJO)]):
        tarjeta(slide, xs[indice], Inches(2.15), ancho3, Inches(3.75),
                destacada=destacada)
        ancho_imagen = ancho3 - Inches(0.44)
        imagen(slide, archivo, xs[indice] + Inches(0.22), Inches(2.37),
               ancho_imagen)
        y_texto = Inches(2.37) + Emu(int(ancho_imagen * 640 / 960)) + Inches(0.14)
        marco = caja(slide, xs[indice] + Inches(0.22), y_texto,
                     ancho3 - Inches(0.44), Inches(0.35))
        escribir(marco, nombre, tamano=17,
                 color=AMBAR if destacada else AZUL)
        marco.paragraphs[0].runs[0].font.bold = True
        marco = caja(slide, xs[indice] + Inches(0.22), y_texto + Inches(0.4),
                     ancho3 - Inches(0.44), Inches(0.6))
        escribir(marco, [("costo ", {"color": TENUE}),
                         (costo, {"bold": True, "color": color_costo,
                                  "fuente": MONO}),
                         ("    expandidos ", {"color": TENUE}),
                         (nodos, {"bold": True, "fuente": MONO})],
                 tamano=14, color=CLARO)
    marco = caja(slide, MARGEN, Inches(6.15), ANCHO_UTIL, Inches(0.6))
    escribir(marco, "Dijkstra llega al mismo resultado expandiendo un 60 % más "
             "de nodos. Greedy explora muy poco, pero su ruta cuesta un 83 % "
             "más.", tamano=14, color=TENUE)
    pie(slide, 14)
    notas(slide, "Dijkstra encontró la misma ruta con el mismo costo, pero "
          "expandió 276 nodos contra 111. Greedy expandió solo 46, pero su "
          "costo es 53 contra 29.")

    # --- 15. el barro (afirmacion) ------------------------------------------
    slide = lamina(presentacion, fondo=AMBAR)
    marco = caja(slide, MARGEN, Inches(0.42), ANCHO_UTIL, Inches(0.3))
    escribir(marco, "14 · PARA QUÉ SIRVE g", tamano=12, color=AMBAR_TEXTO,
             fuente=MONO)
    marco = caja(slide, MARGEN, Inches(1.1), ANCHO_UTIL, Inches(1.5))
    escribir(marco, "Los tres llegan en 29 pasos.", tamano=40, color=OSCURO)
    escribir(marco, "Greedy cuesta un 83 % más.", tamano=40, color=OSCURO,
             nuevo=True)
    for parrafo in marco.paragraphs:
        for corrida in parrafo.runs:
            corrida.font.bold = True
    marco = caja(slide, MARGEN, Inches(3.3), Inches(6.6), Inches(2.6))
    escribir(marco, "Greedy pisa 6 casillas de barro; A* no pisa ninguna.",
             tamano=19, color=AMBAR_TEXTO, interlineado=1.35)
    escribir(marco, "6 × 5 + 23 × 1 = 53", tamano=22, color=OSCURO,
             fuente=MONO, espacio_antes=16, nuevo=True)
    escribir(marco, "Pisa el barro porque ignora g, y g es lo único que sabe "
             "que el barro es caro.", tamano=16, color=AMBAR_TEXTO,
             espacio_antes=16, interlineado=1.35, nuevo=True)
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   MARGEN + Inches(7.2), Inches(3.2),
                                   Inches(4.73), Inches(2.9))
    panel.adjustments[0] = 0.06
    panel.fill.solid()
    panel.fill.fore_color.rgb = OSCURO
    panel.line.fill.background()
    panel.shadow.inherit = False
    marco = caja(slide, MARGEN + Inches(7.5), Inches(3.45), Inches(4.2),
                 Inches(2.5))
    escribir(marco, "Mismo número de pasos", tamano=13, color=TENUE)
    escribir(marco, "29", tamano=30, color=AMBAR, fuente=MONO, nuevo=True)
    escribir(marco, "Costos distintos", tamano=13, color=TENUE,
             espacio_antes=14, nuevo=True)
    escribir(marco, [("29,00", {"bold": True, "color": VERDE, "size": 26,
                                "fuente": MONO}),
                     ("  A*", {"color": TENUE, "size": 15})],
             nuevo=True)
    escribir(marco, [("53,00", {"bold": True, "color": ROJO, "size": 26,
                                "fuente": MONO}),
                     ("  Greedy", {"color": TENUE, "size": 15})],
             nuevo=True)
    marco.paragraphs[1].runs[0].font.bold = True
    pie(slide, 15, claro=True)
    notas(slide, "Los tres llegan en el mismo número de pasos, veintinueve. "
          "Pero Greedy pisa seis casillas de barro, que cuestan cinco cada "
          "una, y A estrella no pisa ninguna. Pisa el barro porque ignora la "
          "G. Esa es la demostracion de para que sirve la G.")

    # --- 16. el codigo ------------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "15 · CÓMO SE ESTRUCTURÓ LA PROGRAMACIÓN",
               "Seis archivos, una responsabilidad cada uno")
    archivos = [["Archivo", "Responsabilidad", "Lineas"]]
    for nombre, responsabilidad, lineas, fuerte in [
            ("main.py", "Arranque; comprueba pygame", "26", False),
            ("laberinto.py", "La rejilla: casillas, vecinos y costos", "168", False),
            ("heuristicas.py", "Las funciones h(n)", "78", False),
            ("astar.py", "El algoritmo", "211", True),
            ("juego.py", "La interfaz: editor y animación", "462", False),
            ("prueba_consola.py", "Las pruebas de corrección", "163", False)]:
        color = AMBAR if fuerte else CLARO
        archivos.append([
            [(nombre, {"fuente": MONO, "color": color, "bold": fuerte})],
            [(responsabilidad, {"color": color, "bold": fuerte})],
            [(lineas, {"fuente": MONO, "color": color, "bold": fuerte})],
        ])
    tabla(slide, MARGEN, Inches(2.1), Inches(6.9), archivos,
          [0.36, 0.48, 0.16], alto_fila=Inches(0.44))
    tarjeta(slide, MARGEN + Inches(7.2), Inches(2.1), Inches(4.73),
            Inches(2.0), destacada=True)
    contenido_tarjeta(slide, MARGEN + Inches(7.2), Inches(2.1), Inches(4.73),
                      "La decisión de diseño",
                      "astar.py no sabe que existe un laberinto. No importa "
                      "pygame ni sabe que es una pared. Solo pide "
                      "laberinto.vecinos(actual).")
    tarjeta(slide, MARGEN + Inches(7.2), Inches(4.3), Inches(4.73), Inches(1.7))
    contenido_tarjeta(slide, MARGEN + Inches(7.2), Inches(4.3), Inches(4.73),
                      "La consecuencia",
                      "Para una rejilla hexagonal no habría que tocar el "
                      "algoritmo: solo los vecinos y la heuristica.")
    marco = caja(slide, MARGEN, Inches(5.1), Inches(6.9), Inches(0.9))
    escribir(marco, "Más de la mitad del programa es interfaz. El algoritmo en "
             "si son 211 lineas, y sin comentarios, unas 80.", tamano=13,
             color=TENUE, interlineado=1.3)
    pie(slide, 16)
    notas(slide, "Son seis archivos. La decisión de diseño más importante es "
          "que astar punto pe y no sabe que existe un laberinto: solo pide los "
          "vecinos y el costo. Para el algoritmo todo es un grafo.")

    # --- 17. la verificacion ------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "16 · CÓMO SABEMOS QUE ES ÓPTIMA", "Dijkstra es el oráculo")
    marco = caja(slide, MARGEN, Inches(1.95), Inches(11.0), Inches(0.8))
    escribir(marco, "Dijkstra siempre devuelve el costo óptimo verdadero. Si "
             "A* diera un costo distinto sobre el mismo laberinto, la "
             "heuristica no sería admisible y habría un error.", tamano=16,
             color=TENUE, interlineado=1.3)
    bloque_codigo(slide, MARGEN, Inches(2.95), Inches(6.9), Inches(2.0), [
        "> python prueba_consola.py",
        "",
        "  A* = 29.00 = Dijkstra. La ruta es óptima.",
        "  A* expandió 165 nodos menos (60% menos).",
        "",
        "  RESULTADO: TODO CORRECTO",
    ], tamano=13)
    marco = caja(slide, MARGEN, Inches(5.15), Inches(6.9), Inches(1.2))
    escribir(marco, "Las pruebas no necesitan pygame. Cubren la trampa en U, "
             "un laberinto aleatorio con barro, el mismo con 8 direcciones, el "
             "desempate, un laberinto sin solución y la comparacion entre "
             "heuristicas.", tamano=13, color=TENUE, interlineado=1.3)
    tarjeta(slide, MARGEN + Inches(7.2), Inches(2.95), Inches(4.73),
            Inches(2.1), destacada=True)
    contenido_tarjeta(slide, MARGEN + Inches(7.2), Inches(2.95), Inches(4.73),
                      "Y además comprobamos",
                      "Que el camino empieza en A y acaba en B, que cada paso "
                      "va a un vecino real, que ninguna casilla es pared, y "
                      "que el costo recalculado a mano coincide.")
    tarjeta(slide, MARGEN + Inches(7.2), Inches(5.25), Inches(4.73), Inches(1.4))
    contenido_tarjeta(slide, MARGEN + Inches(7.2), Inches(5.25), Inches(4.73),
                      "El resultado",
                      "Los tres modos devuelven caminos válidos, y A* y "
                      "Dijkstra coinciden en costo en todos los casos.")
    pie(slide, 17)
    notas(slide, "No afirmamos que nuestro algoritmo encuentra la ruta óptima: "
          "lo comprobamos. Comparamos contra Dijkstra, que si la garantiza. "
          "Coinciden en todos los casos.")

    # --- 18. el cierre ------------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "17 · EN RESUMEN", "Lo que entregamos")
    for indice, (titulo, cuerpo) in enumerate([
            ("Un programa",
             "Editor de laberintos con ratón, animación paso a paso y tres "
             "algoritmos en un solo buscador."),
            ("Una comprobación",
             "Pruebas automáticas que verifican la optimalidad contra "
             "Dijkstra, sin interfaz gráfica."),
            ("Una decisión",
             "Descartamos la heuristica de una de las fuentes, con la razon "
             "escrita en el código.")]):
        tarjeta(slide, xs[indice], Inches(2.1), ancho3, Inches(1.8))
        contenido_tarjeta(slide, xs[indice], Inches(2.1), ancho3, titulo, cuerpo)
    tarjeta(slide, MARGEN, Inches(4.15), ANCHO_UTIL, Inches(2.2),
            destacada=True)
    marco = caja(slide, MARGEN + Inches(0.3), Inches(4.4), Inches(11.3),
                 Inches(0.35))
    escribir(marco, "Una limitación que declaramos", tamano=17, color=AMBAR)
    marco.paragraphs[0].runs[0].font.bold = True
    marco = caja(slide, MARGEN + Inches(0.3), Inches(4.85), Inches(11.3),
                 Inches(1.4))
    escribir(marco, "En el obstáculo cóncavo clásico —la «trampa en U»— Greedy "
             "encontró el mismo costo que A*. La versión simplificada que "
             "suele contarse no se cumplio en nuestro programa, porque al "
             "expandir un nodo se generan todos sus vecinos y la salida se "
             "descubre enseguida.", tamano=14, color=TENUE, interlineado=1.3)
    escribir(marco, "Conclusion más precisa: el obstáculo cóncavo le cuesta a "
             "Greedy exploracion; el terreno con costos distintos le cuesta "
             "calidad de ruta. Lo medimos en vez de repetirlo.", tamano=13,
             color=TENUE, espacio_antes=8, interlineado=1.3, nuevo=True)
    pie(slide, 18)
    notas(slide, "Entregamos un programa con editor y animación, pruebas que "
          "verifican la optimalidad, y una decisión tecnica documentada. Y "
          "declaramos una limitación: en la trampa en U, Greedy empato con A "
          "estrella. Lo medimos en vez de repetirlo.")

    # --- 19. las fuentes ----------------------------------------------------
    slide = lamina(presentacion)
    encabezado(slide, "18 · FUENTES", "Referencias consultadas")
    marco = caja(slide, MARGEN, Inches(1.95), ANCHO_UTIL, Inches(3.7))
    referencias = [
        ("Patel, A. Introduction to A*. Stanford University.",
         "theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html"),
        ("Patel, A. Heuristics. Stanford University.",
         "theory.stanford.edu/~amitp/GameProgramming/Heuristics.html"),
        ("A* Search. Brilliant.org.",
         "brilliant.org/wiki/a-star-search/"),
        ("Swift, N. Easy A* (star) Pathfinding. Medium.",
         "medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2"),
        ("Magdziarz, M. Pathfinding on a hexagonal grid. The Knights of U.",
         "theknightsofu.com/pathfinding-on-a-hexagonal-grid-a-algorithm-2/"),
        ("Patel, A. Introduction to the A* Algorithm. Red Blob Games.",
         "redblobgames.com/pathfinding/a-star/introduction.html"),
    ]
    for indice, (cita, enlace) in enumerate(referencias):
        escribir(marco, cita, tamano=14, color=CLARO,
                 espacio_antes=0 if indice == 0 else 9, nuevo=bool(indice))
        escribir(marco, enlace, tamano=11, color=TENUE, fuente=MONO, nuevo=True)
    marco = caja(slide, MARGEN, Inches(6.0), ANCHO_UTIL, Inches(0.5))
    escribir(marco, "El material recopilado de cada fuente está en FUENTES.md. "
             "El desarrollo completo, en MANUAL.md.", tamano=13, color=TENUE)
    pie(slide, 19)
    notas(slide, "Las dos de Amit Patel traen las formulas de las heuristicas "
          "y la regla de la escala. Brilliant aporta la definicion formal. Red "
          "Blob Games es la implementacion limpia de referencia. Gracias por su "
          "atención, y quedamos a disposicion para preguntas.")

    presentacion.save(SALIDA)
    print("LISTO:", os.path.abspath(SALIDA))
    print("laminas:", len(presentacion.slides.__iter__.__self__._sldIdLst))


if __name__ == "__main__":
    construir()
