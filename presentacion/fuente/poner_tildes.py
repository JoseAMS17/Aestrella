"""
Pone las tildes al TEXTO de construir_pptx.py, sin tocar el codigo.

Recorre el archivo con el tokenizador de Python y solo reescribe los literales
de cadena. Asi un nombre de parametro como `tamano=` se queda como esta y solo
cambia el texto que acaba en las laminas.

    python poner_tildes.py
"""

import io
import re
import sys
import tokenize

OBJETIVO = "construir_pptx.py"

# Palabras que en este texto SIEMPRE llevan tilde.
PALABRAS = [
    ("mas", "más"), ("Mas", "Más"), ("ademas", "además"), ("Ademas", "Además"),
    ("busqueda", "búsqueda"), ("Busqueda", "Búsqueda"), ("BUSQUEDA", "BÚSQUEDA"),
    ("optima", "óptima"), ("Optima", "Óptima"), ("OPTIMA", "ÓPTIMA"),
    ("optimo", "óptimo"), ("Optimo", "Óptimo"),
    ("formula", "fórmula"), ("Formula", "Fórmula"),
    ("numero", "número"), ("Numero", "Número"), ("NUMEROS", "NÚMEROS"),
    ("unico", "único"), ("unica", "única"),
    ("termino", "término"), ("terminos", "términos"), ("TERMINOS", "TÉRMINOS"),
    ("decision", "decisión"), ("Decision", "Decisión"), ("DECISION", "DECISIÓN"),
    ("funcion", "función"), ("Funcion", "Función"), ("FUNCION", "FUNCIÓN"),
    ("codigo", "código"), ("Codigo", "Código"),
    ("animacion", "animación"), ("correccion", "corrección"),
    ("comprobacion", "comprobación"), ("Comprobacion", "Comprobación"),
    ("limitacion", "limitación"), ("version", "versión"), ("Version", "Versión"),
    ("concavo", "cóncavo"), ("atencion", "atención"), ("raton", "ratón"),
    ("tamano", "tamaño"), ("Tamano", "Tamaño"),
    ("diseno", "diseño"), ("Diseno", "Diseño"),
    ("linea", "línea"), ("monticulo", "montículo"),
    ("automaticas", "automáticas"), ("grafica", "gráfica"),
    ("estimacion", "estimación"), ("Estimacion", "Estimación"),
    ("suposicion", "suposición"), ("exito", "éxito"),
    ("expandio", "expandió"), ("encontro", "encontró"), ("topo", "topó"),
    ("Garcia", "García"), ("Jose", "José"),
    ("programacion", "programación"), ("PROGRAMACION", "PROGRAMACIÓN"),
    ("relajacion", "relajación"), ("Relajacion", "Relajación"),
    ("estructuro", "estructuró"), ("ESTRUCTURO", "ESTRUCTURÓ"),
    ("DEMOSTRACION", "DEMOSTRACIÓN"), ("COMO", "CÓMO"),
    ("Ahi", "Ahí"), ("Asi", "Así"), ("asi", "así"),
    ("seria", "sería"), ("habria", "habría"), ("rapido", "rápido"),
    ("pagina", "página"), ("Pagina", "Página"),
    ("seccion", "sección"), ("obstaculo", "obstáculo"), ("clasico", "clásico"),
    ("desvio", "desvío"), ("raiz", "raíz"), ("oraculo", "oráculo"),
    ("solucion", "solución"), ("validos", "válidos"),
    ("proposito", "propósito"),
]

# Casos que dependen del contexto: aqui "que" y "como" solo llevan tilde
# cuando preguntan, y "esta" solo cuando es del verbo estar.
FRASES = [
    ("Que es", "Qué es"), ("Que mira", "Qué mira"),
    ("Que se elige", "Qué se elige"), ("Que hicimos", "Qué hicimos"),
    ("Por que falla", "Por qué falla"), ("Que significa", "Qué significa"),
    ("PARA QUE SIRVE", "PARA QUÉ SIRVE"),
    ("Ya estaba cerrado?", "¿Ya estaba cerrado?"),
    ("Es la meta?", "¿Es la meta?"),
    ("que esta lejos", "que está lejos"),
    ("fuente esta en", "fuente está en"),
    ("Vean como", "Vean cómo"),
    ("Si h(n)...", "Si h(n)…"),
]

# "heuristicas.py" es un nombre de archivo: no se le pone tilde.
ARCHIVOS = re.compile(r"\b(heuristicas|astar|laberinto|juego|main|"
                      r"prueba_consola)\.py\b")


def arreglar(texto):
    marcadores = {}

    def guardar(coincidencia):
        clave = "\x00%d\x00" % len(marcadores)
        marcadores[clave] = coincidencia.group(0)
        return clave

    texto = ARCHIVOS.sub(guardar, texto)
    for antes, despues in PALABRAS:
        texto = re.sub(r"\b%s\b" % re.escape(antes), despues, texto)
    for antes, despues in FRASES:
        texto = texto.replace(antes, despues)
    for clave, valor in marcadores.items():
        texto = texto.replace(clave, valor)
    return texto


fuente = io.open(OBJETIVO, encoding="utf-8").read()
resultado = []
cambios = 0
for ficha in tokenize.generate_tokens(io.StringIO(fuente).readline):
    tipo, cadena, inicio, fin, _ = ficha
    if tipo == tokenize.STRING:
        nueva = arreglar(cadena)
        if nueva != cadena:
            cambios += 1
            ficha = tokenize.TokenInfo(tipo, nueva, inicio, fin, _)
    resultado.append(ficha)

salida = tokenize.untokenize(resultado)
io.open(OBJETIVO, "w", encoding="utf-8").write(salida)
print("literales de cadena corregidos:", cambios)

# Comprobacion: el archivo sigue siendo Python valido.
compile(io.open(OBJETIVO, encoding="utf-8").read(), OBJETIVO, "exec")
print("el archivo sigue compilando")
