# Algoritmo A\* — ruta óptima en un laberinto

Proyecto de clase · Robótica TMC-306 · Instituto Tecnológico de Las Américas (ITLA)

**Junior Alexandro Castillo** · **Haniel García** · **José Javier Pacheco** · **José Alejandro Matos**

Buscador de rutas en Python con interfaz gráfica. El laberinto —inicio, meta y obstáculos— se
dibuja con el ratón **antes** de arrancar, y después se ve a A\* expandir nodos uno por uno hasta
encontrar la ruta.

El mismo buscador ejecuta **tres algoritmos** cambiando un parámetro, que es lo que permite
demostrar en vivo por qué A\* es mejor que cada uno por separado.

---

## Qué hay en este repositorio

| Carpeta | Qué contiene |
|---|---|
| **raíz** | El programa: los seis archivos `.py` y `requirements.txt` |
| [`documentos/`](documentos) | El **manual**, el **guion del video**, el **informe técnico** y las fuentes |
| [`presentacion/`](presentacion) | La presentación en **PowerPoint**, con su código fuente |
| [`CAPTURAS/`](CAPTURAS) | Las capturas del programa usadas en todos los documentos |

### Los documentos

| Archivo | Qué es |
|---|---|
| [`documentos/MANUAL.pdf`](documentos/MANUAL.pdf) | **Cómo se hizo y cómo funciona todo.** 30 páginas: el algoritmo, las ecuaciones, la heurística, un ejemplo numérico y los seis archivos `.py` explicados uno por uno |
| [`documentos/Informe Tecnico Algoritmo A-estrella.pdf`](documentos/Informe%20Tecnico%20Algoritmo%20A-estrella.pdf) | El **informe de entrega**, 4 páginas |
| [`documentos/GUION_VIDEO.pdf`](documentos/GUION_VIDEO.pdf) | El **guion del video**, repartido entre los cuatro y alineado lámina por lámina |
| [`documentos/FUENTES.md`](documentos/FUENTES.md) | El material recopilado de cada fuente, con las citas verificadas |
| [`presentacion/Presentacion Algoritmo A-estrella.pptx`](presentacion) | 19 láminas, con las notas del orador en cada una |

Cada documento lleva su **fuente** al lado (`documentos/fuente/`, `presentacion/fuente/`), por si
hay que regenerarlo.

---

## Cómo ejecutarlo

Abrir **esta carpeta** en VS Code (no un archivo suelto, o fallan los imports) y en la terminal:

```
pip install pygame
python main.py
```

Hace falta **Python 3.12**. Si pygame diera problemas, el algoritmo se comprueba sin interfaz
gráfica:

```
python prueba_consola.py
```

Termina imprimiendo `RESULTADO: TODO CORRECTO`.

---

## Controles

### En el editor, antes de empezar

Funciona en **dos tiempos**: primero se elige *qué* pintar, después *dónde*.

1. **Elegir qué pintar**, con los cuatro botones del panel derecho o con su tecla. El botón
   activo queda resaltado en amarillo.
2. **Hacer clic en el laberinto.** Clic izquierdo pinta, clic derecho borra, y se puede arrastrar.
3. **`ENTER`** para empezar la búsqueda.

| Botón / tecla | Pone |
|---|---|
| `A` | el punto de **inicio** (verde) |
| `B` | el punto de **llegada** (rojo) |
| `O` | un **obstáculo** (pared) |
| `W` | barro, que cuesta 5 en vez de 1 |

El inicio y la meta **se mueven** en vez de duplicarse, y no se pueden tapar con una pared.

| Otras teclas | Qué hacen |
|---|---|
| `C` | vaciar el laberinto |
| `R` | obstáculos al azar |
| `U` | generar la trampa en U |
| `+` / `-` | más o menos nodos (de 8×8 a 40×40) |

### Durante la búsqueda

| Tecla | Qué hace |
|---|---|
| `ESPACIO` | pausa / continuar |
| `.` | **un solo paso** — una expansión |
| `[` `]` | más lento / más rápido |
| `ENTER` | repetir |
| `ESC` | volver al editor |
| `Q` | salir |

### En cualquier momento

| Tecla | Alterna entre |
|---|---|
| `M` | **A\*** → **Dijkstra** → **Greedy** |
| `H` | heurística: auto → manhattan → octile → euclidiana |
| `D` | 4 u 8 direcciones |
| `T` | desempate sí / no |

---

## Los tres modos

Los tres son la misma búsqueda con distinta prioridad:

```
prioridad = peso_g · g(n) + peso_h · h(n)
```

| Modo | peso_g | peso_h | Qué mira | ¿Ruta óptima? |
|---|---|---|---|---|
| **A\*** | 1 | 1 | lo que costó **y** lo que falta | **sí** |
| **Dijkstra** | 1 | 0 | solo lo que costó | sí, pero explora mucho más |
| **Greedy** | 0 | 1 | solo lo que falta | **no** |

---

## Qué hace cada archivo

| Archivo | Responsabilidad | Líneas |
|---|---|---|
| `main.py` | punto de entrada; comprueba que pygame esté instalado | 26 |
| `laberinto.py` | la rejilla: casillas, vecinos y costos | 168 |
| `heuristicas.py` | las funciones h(n) | 78 |
| **`astar.py`** | **el algoritmo** | **211** |
| `juego.py` | la interfaz: editor y animación | 462 |
| `prueba_consola.py` | las pruebas de corrección, sin pygame | 163 |

La separación no es decorativa: **A\* no sabe que existe una rejilla.** Solo pide
`laberinto.vecinos(n)` y un costo. Por eso el mismo `astar.py` funcionaría sobre una rejilla
hexagonal cambiando únicamente `vecinos()` y la heurística.

---

## Cómo se comprueba que la ruta es óptima

`prueba_consola.py` usa **Dijkstra como oráculo**: ese algoritmo siempre devuelve el costo óptimo
verdadero, así que si A\* con nuestra heurística diera un costo distinto sobre el mismo laberinto,
la heurística no sería admisible y habría un error.

Las pruebas cubren seis escenarios: la trampa en U, un laberinto aleatorio con barro, el mismo con
8 direcciones, el efecto del desempate, un laberinto sin solución y la comparación entre
heurísticas. **En todos los casos los costos coinciden.**

---

## El resultado que mejor resume el proyecto

Sobre el laberinto de demostración (16 × 24 = 384 nodos, 22 paredes, 20 casillas de barro):

| Modo | Costo | Pasos | Nodos expandidos |
|---|---|---|---|
| **A\*** | **29,00** | 29 | **111** |
| Dijkstra | 29,00 | 29 | 276 |
| Greedy | **53,00** | 29 | 46 |

Los tres llegan en **los mismos 29 pasos**, pero Greedy cuesta un **83 % más**: atraviesa 6
casillas de barro y A\* ninguna, de donde 6 × 5 + 23 × 1 = 53. Pisa el barro porque ignora `g`, y
`g` es lo único que sabe que el barro es caro.
