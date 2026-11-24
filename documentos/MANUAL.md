# Manual del algoritmo A\*

### Búsqueda de la ruta óptima en un laberinto

Proyecto de clase · Instituto Tecnológico de Las Américas (ITLA)
Noviembre de 2026

---

## Índice

1. [El problema](#1-el-problema)
2. [A\* son dos algoritmos trabajando juntos](#2-a-son-dos-algoritmos-trabajando-juntos)
3. [Las ecuaciones](#3-las-ecuaciones)
4. [La heurística](#4-la-heurística)
5. [Ejemplo numérico completo](#5-ejemplo-numérico-completo)
6. [El manejo de los nodos](#6-el-manejo-de-los-nodos)
7. [Cómo usar el programa](#7-cómo-usar-el-programa)
8. [Cómo cambiar la cantidad de nodos](#8-cómo-cambiar-la-cantidad-de-nodos)
9. [Cómo funciona el código](#9-cómo-funciona-el-código)
10. [Resultados medidos](#10-resultados-medidos)
11. [Errores que evitamos a propósito](#11-errores-que-evitamos-a-propósito)
12. [Preguntas probables en la defensa](#12-preguntas-probables-en-la-defensa)
13. [Fuentes](#13-fuentes)

---

## 1. El problema

Tenemos un laberinto: una rejilla donde cada casilla se puede pisar o no, un
punto de partida **A** y un punto de llegada **B**. Queremos la **ruta óptima**,
que no es lo mismo que *una* ruta: es la más barata de todas las posibles.

La palabra "barata" importa. Si todas las casillas cuestan lo mismo, la ruta
óptima es simplemente la más corta. Pero si algunas casillas cuestan más que
otras —en nuestro programa el **barro cuesta 5** y el suelo normal cuesta 1—
entonces la ruta más corta en número de pasos puede ser la más cara. A\*
resuelve el caso general.

Un laberinto es, para el algoritmo, un **grafo**: cada casilla es un *nodo* y
cada movimiento permitido es una *arista* con un costo. Esto es importante y
volveremos sobre ello: A\* no sabe que existen casillas, paredes ni pantallas.
Solo pide "dame los vecinos de este nodo y lo que cuesta llegar a cada uno".

---

## 2. A\* son dos algoritmos trabajando juntos

Esta es la idea central del proyecto, y conviene contarla en tres pasos.

### 2.1 Dijkstra: mirar hacia atrás

El algoritmo de Dijkstra explora siempre el nodo **no examinado más cercano al
punto de partida**. Va creciendo como una mancha de aceite alrededor de A, en
todas las direcciones por igual.

- ✅ **Garantiza la ruta más corta**, siempre que ningún costo sea negativo.
- ❌ **Trabaja de más.** No sabe dónde está B, así que explora hacia atrás, hacia
  los lados y hacia zonas que nunca podrían servir.

### 2.2 Greedy Best-First: mirar hacia adelante

Greedy Best-First Search hace lo contrario: explora siempre el nodo que *parece*
**más cercano a la meta**, usando una estimación.

- ✅ **Mucho más rápido.** Va derecho hacia B.
- ❌ **No garantiza la ruta más corta.** Como dice Amit Patel: es codicioso e
  intenta avanzar hacia la meta aunque no sea el camino correcto, y como ignora
  el costo del camino recorrido, sigue adelante aunque ese camino se haya
  vuelto larguísimo.

### 2.3 A\*: las dos cosas a la vez

A\* es como Dijkstra en que puede encontrar la ruta más corta, y como Greedy en
que usa una estimación para guiarse. **Balancea las dos** al avanzar de A hacia B.

| | Qué mira | Resultado |
|---|---|---|
| **Dijkstra** | solo lo que **ya costó** | óptimo, pero lento |
| **Greedy** | solo lo que **falta** | rápido, pero no óptimo |
| **A\*** | **las dos cosas** | óptimo **y** rápido |

### 2.4 Y en nuestro programa es literal, no una metáfora

No programamos tres algoritmos. Programamos **uno**, con dos pesos:

```
prioridad = peso_g · g(n) + peso_h · h(n)
```

| Modo | `peso_g` | `peso_h` | Qué queda |
|---|---|---|---|
| **A\*** | 1 | 1 | la fórmula completa |
| **Dijkstra** | 1 | 0 | desaparece `h`: solo cuenta lo que costó |
| **Greedy** | 0 | 1 | desaparece `g`: solo cuenta lo que falta |

👉 En el programa se cambia con la tecla **`M`**, sobre el mismo laberinto. Esa
es la demostración: no decimos que A\* combina dos algoritmos, **lo enseñamos
apagando un término y viendo en qué se convierte.**

Las fuentes lo confirman desde los dos lados. Si `h(n) = 0`, A\* *es* Dijkstra.
Si `h(n)` es enorme frente a `g(n)`, solo importa `h` y A\* *es* Greedy.

---

## 3. Las ecuaciones

### 3.1 La función de costo

```
f(n) = g(n) + h(n)
```

| Término | Qué es | Naturaleza |
|---|---|---|
| **`g(n)`** | costo **real y exacto** del camino desde A hasta `n` | un hecho: ya se recorrió |
| **`h(n)`** | costo **estimado** desde `n` hasta B | una suposición: aún no se recorre |
| **`f(n)`** | estimación del costo **total** del camino que pasa por `n` | la prioridad de la cola |

La frase para recordarlo: **`g` es lo que ya gastaste, `h` es lo que crees que
te falta, `f` es lo que crees que te va a costar el viaje entero.**

### 3.2 Cómo se calcula `g`

`g` se acumula paso a paso:

```
g(vecino) = g(actual) + costo_del_paso(actual → vecino)
```

En nuestro programa el costo del paso es el **costo de entrar** en la casilla
destino:

| Casilla destino | Costo |
|---|---|
| suelo libre | 1 |
| barro | 5 |
| pared | no se puede entrar |

Y si el movimiento es **diagonal**, ese costo se multiplica por **√2 ≈ 1,414**,
porque la diagonal de un cuadrado de lado 1 mide √2. Esto no es un adorno: si
las diagonales costaran 1 igual que las rectas, el algoritmo creería que
moverse en diagonal es gratis y devolvería rutas falsas.

### 3.3 La regla de la escala

> **`g` y `h` tienen que estar en las mismas unidades.**

A\* las **suma**, así que si `g` se midiera en una escala y `h` en otra, A\*
pesaría mal una de las dos y las rutas empeorarían. Por eso, en nuestro código,
la constante `D` de las heurísticas **no está escrita a mano**: sale del propio
laberinto.

```python
# laberinto.py
COSTO_MINIMO = min(COSTO_CASILLA.values())   # el paso más barato que existe

# heuristicas.py
D = COSTO_MINIMO
```

**Prueba práctica** (de la página de heurísticas): en un mapa sin obstáculos y
con costos uniformes, el camino más corto es una línea recta. Calcula `h` de A a
B y compáralo con el costo real. Si no coinciden, hay un problema de escala.

---

## 4. La heurística

### 4.1 Admisibilidad: la condición que lo decide todo

> Una heurística es **admisible** si **nunca sobreestima** el costo real que
> falta hasta la meta.

**Solo con una heurística admisible A\* garantiza la ruta óptima.** Esta es la
única condición, y es la que separa un A\* correcto de uno que parece correcto.

La escala completa:

| Si `h(n)`… | Entonces A\* … |
|---|---|
| **= 0** | **es Dijkstra.** Óptimo, pero explora muchísimo |
| **≤ costo real** siempre | **garantiza la ruta óptima.** Cuanto menor sea `h`, más nodos expande |
| **= costo real** exacto | sigue solo el mejor camino. Expande poquísimo |
| **> costo real** a veces | **ya no garantiza el óptimo**, aunque puede ser más rápido |
| **≫ `g(n)`** | degenera en **Greedy** |

### 4.2 Las fórmulas

`D` = costo del paso más barato. `dx`, `dy` = diferencias absolutas de
coordenadas entre el nodo y la meta.

**Manhattan — para movimiento en 4 direcciones** (la que usamos por defecto)

```
h = D · (dx + dy)
```

Cuenta los pasos en línea recta que faltan. Con 4 vecinos y un mapa vacío es
**exacta**, o sea la mejor heurística admisible posible.

**Octile — para movimiento en 8 direcciones**

```
h = D · (dx + dy) + (D2 − 2·D) · min(dx, dy)
```

con `D = 1` y `D2 = √2`. El razonamiento: se cuentan los pasos sin diagonales y
luego se descuentan los que se ahorran. Hay `min(dx, dy)` pasos diagonales, cada
uno cuesta `D2` pero ahorra dos pasos rectos de `D`.

**Euclidiana — para movimiento en cualquier ángulo**

```
h = D · √(dx² + dy²)
```

En una rejilla **subestima** (la línea recta es más corta que cualquier camino
por casillas). Sigue siendo admisible, así que la ruta sale óptima, pero A\*
expande más nodos de los necesarios. En el programa está disponible con `H`
justamente para poder demostrarlo.

### 4.3 🔴 La fórmula que NO usamos, y por qué

El código del artículo de Medium que nos dieron como referencia calcula:

```python
child.h = (dx)**2 + (dy)**2      # distancia euclidiana AL CUADRADO
```

La página de heurísticas de Amit Patel dedica una sección a esa fórmula y su
veredicto es: "Do not do this!"

**El motivo:** el cuadrado crece mucho más rápido que `g`. Al sumar `g + h`, la
heurística domina, **sobreestima**, deja de ser admisible y en distancias largas
A\* degenera en Greedy. Si se reescala hacia abajo para compensar, en distancias
cortas queda demasiado pequeña y degenera en Dijkstra.

Como nuestro enunciado pide la **ruta óptima**, esa fórmula quedó fuera del
proyecto. Está documentado en el encabezado de `heuristicas.py`.

### 4.4 El desempate

En un laberinto de costo uniforme existen **muchísimos** caminos de la misma
longitud, así que un montón de nodos empatan en `f` y A\* los explora todos sin
necesidad. La solución de la página de heurísticas:

```
h = h · (1 + p)      con      p < (costo mínimo de un paso) / (largo máximo del camino)
```

En nuestro código, `p = COSTO_MINIMO / número_de_nodos`, y se activa con la
tecla **`T`**. Rompe ligeramente la admisibilidad, pero el autor advierte que en
la práctica casi nunca importa — y nuestras mediciones lo confirman: **el costo
no cambia y los nodos expandidos bajan de 58 a 37.**

⚠️ Hay un **segundo desempate** que ya está siempre activo y conviene saberlo: la
cola guarda tripletas `(prioridad, orden, nodo)`, donde `orden` es un contador
incremental. Eso es exactamente el desempate "por orden de inserción" que
también lista Amit Patel, y además evita que Python intente comparar las tuplas
de coordenadas cuando dos prioridades son idénticas.

---

## 5. Ejemplo numérico completo

Esta traza **no está inventada**: la generó nuestro propio código. Laberinto de
8×8 con una pared vertical, movimiento en 4 direcciones, heurística Manhattan.

```
Laberinto                       h = Manhattan hasta B(2,6)

. . . # . . . .                  8  7  6  #  4  3  2  3
. . . # . . . .                  7  6  5  #  3  2  1  2
A . . # . . B .                  6  5  4  #  2  1  0  1
. . . # . . . .                  7  6  5  #  3  2  1  2
. . . . . . . .                  8  7  6  5  4  3  2  3
. . . . . . . .                  9  8  7  6  5  4  3  4
. . . . . . . .                 10  9  8  7  6  5  4  5
. . . . . . . .                 11 10  9  8  7  6  5  6
```

A está en (2,0) y B en (2,6). La pared tapa la columna 3 en las filas 0 a 3, así
que **hay que rodearla por abajo**.

### Las primeras nueve expansiones

| # | Expande | `g` | `h` | `f` | Vecinos que mejora |
|---|---|---|---|---|---|
| 1 | (2,0) | 0 | 6 | **6** | (1,0) g=1 · (3,0) g=1 · (2,1) g=1 |
| 2 | (2,1) | 1 | 5 | **6** | (1,1) g=2 · (3,1) g=2 · (2,2) g=2 |
| 3 | (2,2) | 2 | 4 | **6** | (1,2) g=3 · (3,2) g=3 |
| 4 | (1,0) | 1 | 7 | **8** | (0,0) g=2 |
| 5 | (3,0) | 1 | 7 | **8** | (4,0) g=2 |
| 6 | (1,1) | 2 | 6 | **8** | (0,1) g=3 |
| 7 | (3,1) | 2 | 6 | **8** | (4,1) g=3 |
| 8 | (1,2) | 3 | 5 | **8** | (0,2) g=4 |
| 9 | (3,2) | 3 | 5 | **8** | (4,2) g=4 |

**Lo que hay que leer en esta tabla, y es el corazón del algoritmo:**

🔑 **En las tres primeras filas `f` vale 6 y no cambia.** `g` sube de 0 a 1 a 2,
y `h` baja de 6 a 5 a 4, exactamente a la misma velocidad. Eso significa que
esos pasos avanzan hacia la meta **sin desperdiciar nada**: cada unidad gastada
compra una unidad de progreso. Cuando `f` se mantiene constante, A\* va por el
camino perfecto.

🔑 **En la fila 4, `f` salta a 8.** Ahí A\* ya se topó con la pared y tiene que
empezar a considerar el rodeo. El salto de `f` **es el precio del desvío**, y
A\* no lo paga hasta que no le queda más remedio: primero agotó todos los nodos
de `f = 6`.

🔑 **El orden no es por cercanía ni por profundidad: es por `f`.** Fíjate en que
expande (2,2) —que está lejos de A— antes que (1,0), que es vecino directo de A.
Dijkstra habría hecho lo contrario.

### El final

```
Resultado: éxito  ·  costo = 10  ·  25 nodos expandidos

Camino: (2,0) → (2,1) → (2,2) → (3,2) → (4,2) → (4,3) → (4,4) → (3,4) → (2,4) → (2,5) → (2,6)
```

Baja para esquivar la pared por la fila 4 y vuelve a subir. **10 pasos, que es
el óptimo.**

### Los tres modos sobre este mismo laberinto

| Modo | Costo | Nodos expandidos |
|---|---|---|
| **A\*** | **10** | **25** |
| Dijkstra | 10 | **50** — el doble de trabajo para el mismo resultado |
| Greedy | 10 | 15 — aquí acertó, pero no está garantizado |

El laberinto tiene **60 casillas libres** y Dijkstra expandió **50**: casi
todas, porque sin heurística no tiene forma de saber hacia dónde está B. A\*
expandió **25**, la mitad, y llegó al mismo resultado. Ese ahorro es `h`
haciendo su trabajo.

---

## 6. El manejo de los nodos

### 6.1 Las dos listas

| Lista | Qué guarda | Cómo está hecha |
|---|---|---|
| **Abierta** (frontera) | nodos descubiertos pero **no** expandidos | un **montículo** (`heapq`): devuelve siempre el de menor `f` |
| **Cerrada** | nodos **ya** expandidos | un **`set`**: "¿está aquí?" es la pregunta más repetida del algoritmo |

Además llevamos dos diccionarios:

```python
g = {}        # g[n]     = costo real del mejor camino conocido hasta n
padre = {}    # padre[n] = desde qué nodo se llegó a n
```

🔑 **Usar diccionarios y no una clase `Nodo` no es un capricho de estilo.** Con
una clase, el mismo nodo puede existir dos veces en la lista abierta con valores
de `g` distintos, y entonces el algoritmo se contradice a sí mismo. Es el error
más repetido en las implementaciones que circulan por internet. Con un
diccionario indexado por la coordenada, **ese error no puede ocurrir**.

### 6.2 El ciclo, paso a paso

```
1. Si la lista abierta está vacía → no hay camino. Terminar.
2. Sacar el nodo con menor f.
3. ¿Ya estaba cerrado? → descartarlo y volver al paso 1.
4. ¿Es la meta? → terminar con éxito.
5. Marcarlo como cerrado.
6. Para cada vecino transitable:
      nuevo_g = g[actual] + costo_del_paso
      si el vecino es nuevo, o nuevo_g mejora lo que teníamos:
          g[vecino] = nuevo_g
          padre[vecino] = actual
          meter el vecino en la lista abierta con prioridad nuevo_g + h(vecino)
7. Volver al paso 1.
```

### 6.3 Tres detalles que separan lo correcto de lo que "casi" funciona

**1. Comprobar la meta AL SACAR de la cola, nunca al insertar.**
Comprobarla al insertar parece funcionar y deja de hacerlo en cuanto hay costos
de movimiento, porque un camino más barato a la meta puede descubrirse *después*
de haberla visto por primera vez.

**2. La relajación.** Un nodo se puede alcanzar por varios caminos con costos
distintos. Solo nos interesa cuando el camino nuevo es **estrictamente mejor**:

```python
if vecino not in self.g or nuevo_g < self.g[vecino] - 1e-9:
```

El `1e-9` es por la √2 de las diagonales: comparar números con coma sin margen
provoca reinserciones infinitas por error de redondeo.

**3. Borrado perezoso.** Cuando encontramos un camino mejor a un nodo que ya
estaba en la cola, **no** modificamos la entrada vieja: metemos una nueva y
descartamos la obsoleta al sacarla (paso 3 del ciclo). Modificar un montículo
por dentro rompe su invariante de ordenación, y es un error reportado durante
años en el código de referencia de Medium.

### 6.4 La reconstrucción del camino

Al llegar a la meta, se sigue la cadena de padres hacia atrás y se da vuelta la
lista:

```python
camino = []
actual = self.meta
while actual is not None:
    camino.append(actual)
    actual = self.padre[actual]
camino.reverse()
```

Es O(largo del camino) y **no puede equivocarse**. La página de la rejilla
hexagonal propone en cambio retroceder buscando un vecino con `g` menor; con
costo uniforme puede haber varios vecinos empatados y devolver un camino
distinto del que el buscador encontró de verdad. Por eso usamos el puntero al
padre.

---

## 7. Cómo usar el programa

### 7.1 Instalación

Abrir en VS Code **la carpeta** `Algoritmo Aestrella` (no un archivo suelto, o
fallan los imports) y en la terminal integrada:

```
pip install pygame
python main.py
```

### 7.2 El editor: dibujar el laberinto

El programa arranca en el editor. **No busca nada hasta que se lo pides.**
Funciona en tres tiempos:

**1. Elegir qué pintar.** Con los cuatro botones del panel derecho, o con su
tecla. El botón activo queda con borde amarillo.

| Botón / tecla | Pone |
|---|---|
| `A` | el punto de **inicio** (verde) |
| `B` | el punto de **llegada** (rojo) |
| `O` | un **obstáculo** (pared) |
| `W` | **barro**, que cuesta 5 en vez de 1 |

**2. Hacer clic en el laberinto.** Clic izquierdo pinta, clic derecho borra, y se
puede arrastrar sin soltar. El inicio y la meta **se mueven** en vez de
duplicarse, y no se pueden tapar con una pared.

**3. `ENTER`** para empezar la búsqueda.

Atajos para no dibujar desde cero: `C` vacía, `R` pone obstáculos al azar y `U`
genera la trampa en U.

### 7.3 La animación

| Tecla | Qué hace |
|---|---|
| `ESPACIO` | pausa / continuar |
| `.` | **un solo paso** — una expansión |
| `[` `]` | más lento / más rápido |
| `ENTER` | repetir |
| `ESC` | volver al editor |

Los colores:

| Color | Significa |
|---|---|
| 🟦 azul oscuro | nodo **cerrado**: ya expandido |
| 🟦 azul claro | nodo en la **frontera**: descubierto, aún no expandido |
| ⬜ borde blanco | el nodo que se está expandiendo **ahora** |
| 🟨 amarillo | la **ruta óptima** encontrada |

Durante la pausa, el panel muestra `g`, `h` y `f` del nodo actual. **Pulsar `.`
repetidamente con el panel a la vista es la mejor forma de explicar el algoritmo
en el video**: se ve la tabla del apartado 5 ocurriendo en vivo.

### 7.4 Cambiar de algoritmo y de heurística

| Tecla | Alterna entre |
|---|---|
| `M` | **A\*** → **Dijkstra** → **Greedy** |
| `H` | automática → manhattan → octile → euclidiana |
| `D` | 4 u 8 direcciones |
| `T` | desempate sí / no |

Si se pulsan con una búsqueda a medias, la búsqueda **se reinicia** con la
configuración nueva, para que la comparación sea sobre el mismo laberinto.

---

## 8. Cómo cambiar la cantidad de nodos

Hay dos formas, y sirven para cosas distintas.

### 8.1 Desde el programa, con `+` y `-`

En el editor, las teclas `+` y `-` cambian el tamaño de la rejilla. Cada
pulsación suma o resta **2 filas y 3 columnas**, manteniendo la proporción.

El panel muestra siempre el total: `rejilla 16 x 24 = 384 nodos`.

⚠️ Cambiar el tamaño **vacía el laberinto**, porque la rejilla cambia de forma y
las paredes antiguas dejarían de significar lo mismo. Dibuja primero el tamaño,
después el laberinto.

### 8.2 Desde el código, cambiando los límites

Los topes están en `laberinto.py`, arriba del todo:

```python
LADO_MINIMO = 8            # 8 x 8  =   64 nodos
LADO_MAXIMO = 40           # 40 x 40 = 1600 nodos
FILAS_POR_OMISION = 16     # el tamaño con el que arranca
COLUMNAS_POR_OMISION = 24
```

**Por qué esos límites y no otros:**

| | Problema |
|---|---|
| **Menos de 8×8** | no caben rutas alternativas: con un solo camino posible, la palabra "óptima" no significa nada y la demostración no demuestra nada |
| **Más de 40×40** | la animación deja de verse (las casillas bajan de 9 píxeles) y A\* resuelve tan rápido que no se aprecia el proceso |

Si cambias `LADO_MAXIMO`, **no hace falta tocar nada más**: el tamaño de cada
casilla se recalcula solo para que la rejilla siempre quepa en la ventana.

```python
# juego.py — esto ya se encarga de que quepa
self.celda = max(CELDA_MINIMA,
                 min(CELDA_MAXIMA,
                     ANCHO_MAXIMO_REJILLA // lab.columnas,
                     ALTO_MAXIMO_REJILLA // lab.filas))
```

### 8.3 Otras cosas que se pueden ajustar

| Qué | Dónde | Efecto |
|---|---|---|
| Costo del barro | `COSTO_CASILLA` en `laberinto.py` | cuánto castiga el terreno caro |
| Densidad de obstáculos al azar | parámetros de `aleatorio()` | laberintos más o menos cerrados |
| Velocidad de la animación | `VELOCIDADES` en `juego.py` | pasos por fotograma |
| Colores | las constantes `C_*` en `juego.py` | el aspecto |

---

## 9. Cómo funciona el código

### 9.1 Los archivos

| Archivo | Responsabilidad | Líneas |
|---|---|---|
| `main.py` | arranque; comprueba que pygame esté instalado | 26 |
| `laberinto.py` | la rejilla: casillas, vecinos y costos | 168 |
| `heuristicas.py` | las funciones `h(n)` | 78 |
| `astar.py` | **el algoritmo** | 211 |
| `juego.py` | la interfaz: editor y animación | 462 |
| `prueba_consola.py` | las pruebas de corrección | 163 |

Más de la mitad del programa es interfaz. **El algoritmo en sí son 211 líneas,
y comentarios aparte, unas 80.**

### 9.2 La decisión de diseño más importante

**`astar.py` no sabe que existe un laberinto.** No importa `pygame`, no sabe qué
es una pared y no conoce la palabra "casilla". Lo único que hace es:

```python
for vecino, costo_paso in self.laberinto.vecinos(actual):
```

Le pide al laberinto sus vecinos y el costo, y eso es todo. Quien traduce "una
matriz de casillas" a "un grafo" es `laberinto.vecinos()`.

**La consecuencia práctica, y vale la pena decirla en la defensa:** para que
este mismo A\* funcione sobre una **rejilla hexagonal** no habría que tocar
`astar.py` ni una línea. Bastaría reescribir `vecinos()` con las seis
direcciones hexagonales y cambiar la heurística por la distancia en coordenadas
cúbicas, `h = max(|dx|, |dy|, |dz|)`.

### 9.3 Quién depende de quién

```
            main.py
               │  comprueba pygame y arranca
               ▼
            juego.py  ──────────┐
               │                │
     pide una  │                │ pide los vecinos
     búsqueda  ▼                ▼
            astar.py ──────> laberinto.py
               │                  ▲
               │ pide h(n)        │ pide COSTO_MINIMO
               ▼                  │
          heuristicas.py ─────────┘

            prueba_consola.py ──> astar.py, laberinto.py, heuristicas.py
                                  (nunca toca juego.py: por eso corre sin pygame)
```

Las flechas van en un solo sentido y **nunca vuelven**. `laberinto.py` no sabe
que existe `astar.py`, y `astar.py` no sabe que existe `juego.py`. Esa es la
razón de que las pruebas puedan correr sin interfaz gráfica.

---

### 9.4 `main.py` — el arranque (26 líneas)

El archivo que se ejecuta. Hace una sola cosa además de lanzar el programa:
**comprueba que pygame esté instalado antes de importar nada de la interfaz.**

```python
try:
    import pygame
except ImportError:
    print("Falta pygame. Instalalo con:  pip install pygame")
    return 1

from juego import Juego
Juego().correr()
```

🔑 **El orden importa.** El `import` de `juego` va *dentro* de la función y
*después* de la comprobación. Si estuviera arriba del archivo, al faltar pygame
el programa moriría con un rastro de error de Python en vez de con un mensaje
que explica qué hacer. Además sugiere `prueba_consola.py`, que sí funciona sin
pygame.

---

### 9.5 `laberinto.py` — la rejilla (168 líneas)

Convierte "una matriz de casillas" en "un grafo". **No sabe nada de A\* ni de
pygame.**

**Las constantes que definen las reglas del juego**

| Constante | Valor | Para qué |
|---|---|---|
| `LIBRE`, `PARED`, `BARRO` | 0, 1, 2 | los tres tipos de casilla |
| `COSTO_CASILLA` | `{LIBRE: 1.0, BARRO: 5.0}` | lo que cuesta entrar en cada una |
| `COSTO_MINIMO` | el mínimo del anterior | **la `D` de las heurísticas** |
| `LADO_MINIMO`, `LADO_MAXIMO` | 8, 40 | los topes de tamaño |
| `DESPLAZAMIENTOS_4`, `..._DIAGONALES` | 4 + 4 pares | las direcciones de movimiento |

**Los métodos que usa A\***

| Método | Qué hace |
|---|---|
| `dentro(p)` | ¿la coordenada cae en la rejilla? |
| `transitable(p)` | ¿está dentro y no es pared? |
| `costo_de_entrar(p)` | 1 si es suelo, 5 si es barro |
| **`vecinos(p)`** | **el método clave**: cede `(vecino, costo_del_paso)` |

```python
def vecinos(self, p):
    """Cede (vecino, costo_del_paso) por cada vecino transitable."""
```

Genera los 4 vecinos ortogonales y, si las diagonales están activadas, los 4
diagonales con costo `√2 × costo_de_la_casilla`.

🔑 **Hace una comprobación que casi todas las implementaciones olvidan: prohíbe
cortar esquinas.** Para pasar en diagonal, las dos casillas ortogonales que
forman esa esquina tienen que estar libres. Sin esto, la ruta se cuela entre dos
paredes que solo se tocan en un vértice — y en la demostración se ve fatal.

**Los métodos que usa el editor**

| Método | Qué hace |
|---|---|
| `pintar(p, tipo)` | pone pared o barro, **nunca encima del inicio o la meta** |
| `poner_inicio(p)`, `poner_meta(p)` | **mueven** el punto y dejan su casilla libre |
| `limpiar()` | todo a `LIBRE` |
| `redimensionar(filas, columnas)` | nueva rejilla, acotada entre 8 y 40 |

**Los generadores de laberintos**

`aleatorio(densidad_pared, densidad_barro, semilla)` siembra obstáculos al azar
y después **despeja el inicio, la meta y sus vecinos ortogonales**. Sin ese
despeje, el azar tapia la salida cada tantas tiradas y el laberinto nace sin
solución — nos pasó al probarlo.

`trampa_en_u()` construye el obstáculo cóncavo con la boca mirando al inicio, y
coloca A y B a los lados. Es el laberinto del apartado 10.

**La validación**

`validar()` devuelve `None` si se puede buscar, o el motivo si no: inicio igual
a meta, inicio sobre una pared, o meta sobre una pared. El editor lo llama antes
de arrancar y enseña el motivo en rojo.

---

### 9.6 `heuristicas.py` — las funciones h(n) (78 líneas)

Cuatro funciones con la misma firma `h(a, b)`, lo que permite pasarlas como
parámetro y cambiarlas sin tocar el algoritmo.

| Función | Para qué movimiento |
|---|---|
| `manhattan(a, b)` | 4 direcciones |
| `octile(a, b)` | 8 direcciones |
| `euclidiana(a, b)` | cualquier ángulo; en rejilla subestima |
| `cero(a, b)` | devuelve 0,0 → **convierte A\* en Dijkstra** |

Las fórmulas están en el apartado 4.2. Dos detalles del archivo:

```python
from laberinto import COSTO_MINIMO
D = COSTO_MINIMO
D2 = math.sqrt(2.0) * COSTO_MINIMO
```

🔑 **`D` no está escrita a mano: se importa del laberinto.** Si mañana el barro
pasara a costar 0,5, `D` se ajustaría solo y las heurísticas seguirían siendo
admisibles. Es la regla de la escala del apartado 3.3 hecha código.

`recomendada(diagonales)` devuelve `octile` o `manhattan` según el tipo de
movimiento, y es lo que hace que la tecla `D` no pueda dejar una heurística
equivocada por accidente.

⚠️ El encabezado del archivo documenta **la función que no está**: la euclidiana
al cuadrado, y por qué (apartado 4.3).

---

### 9.7 `astar.py` — el algoritmo (211 líneas)

**La clase `Busqueda`.** Guarda todo el estado de una búsqueda en curso:

| Atributo | Qué es |
|---|---|
| `g` | diccionario `{nodo: costo real}` |
| `padre` | diccionario `{hijo: nodo anterior}` |
| `cerrados` | `set` de nodos ya expandidos |
| `frontera` | montículo de `(prioridad, orden, nodo)` |
| `en_frontera` | `set` paralelo, solo para que la interfaz pueda pintarla |
| `expandidos`, `generados`, `max_frontera`, `tiempo_ms` | estadísticas |

| Método | Qué hace |
|---|---|
| `_prioridad(pos, g)` | **`f = peso_g·g + peso_h·h`**, con el desempate aplicado |
| **`paso()`** | **una sola iteración** del ciclo. Devuelve `False` al terminar |
| `_finalizar(exito)` | para el reloj y reconstruye el camino |
| `_reconstruir()` | sigue la cadena de padres y da vuelta la lista |
| `resolver()` | llama a `paso()` en bucle hasta el final |

🔑 **Que `paso()` sea una sola iteración es la decisión que lo permite todo:**

- la interfaz la llama varias veces por fotograma y **anima** la búsqueda;
- `resolver()` la llama en bucle y da el resultado de golpe, para las pruebas;
- y como `paso()` es literalmente una vuelta del ciclo del apartado 6.2, **el
  código se lee igual que el pseudocódigo.**

**La función `buscar()`** traduce el nombre del modo a los pesos:

```python
def buscar(laberinto, modo="A*", heuristica=None, desempate=False):
    """Crea la búsqueda configurada: 'A*', 'Dijkstra' o 'Greedy'."""
```

Y **`MODOS`** es la tabla del apartado 2.4 escrita como dato:

```python
MODOS = (("A*", 1.0, 1.0), ("Dijkstra", 1.0, 0.0), ("Greedy", 0.0, 1.0))
```

⚠️ Un detalle que no se ve a simple vista: el atributo `self.relajar` vale
`False` cuando `peso_g == 0`, o sea en modo Greedy. **Greedy no reconsidera un
nodo ya visto**, y por eso sus rutas salen peores. Si relajara como A\*,
acabaría encontrando el óptimo casi siempre y la comparación no demostraría nada.

---

### 9.8 `juego.py` — la interfaz (462 líneas)

El archivo más largo, y el que **menos tiene que ver con el algoritmo**. No sabe
qué es `f = g + h`: solo llama a `busqueda.paso()` y pinta lo que encuentra en
`busqueda.cerrados`, `busqueda.en_frontera` y `busqueda.camino`.

**Lo de arriba del archivo**

| Bloque | Qué define |
|---|---|
| Medidas | `ANCHO_PANEL`, `CELDA_MINIMA/MAXIMA`, los máximos de la rejilla |
| Colores | las constantes `C_*`, todas planas, sin degradados |
| Pinceles | `PINCEL_PARED`, `PINCEL_BARRO`, `PINCEL_INICIO`, `PINCEL_META` |
| `VELOCIDADES` | `(1, 2, 4, …, 128)` pasos por fotograma |
| `crear_fuente()` | busca Consolas y cae a la fuente por defecto si no está |

**La clase `Juego`, por grupos**

*Ventana y coordenadas*

| Método | Qué hace |
|---|---|
| `_crear_ventana()` | **calcula el tamaño de celda** para que la rejilla siempre quepa, y dimensiona la ventana |
| `_casilla_en(pixel)` | convierte píxeles en `(fila, columna)`, o `None` si el clic cayó fuera |

```python
self.celda = max(CELDA_MINIMA,
                 min(CELDA_MAXIMA,
                     ANCHO_MAXIMO_REJILLA // lab.columnas,
                     ALTO_MAXIMO_REJILLA // lab.filas))
```

🔑 **Por eso `+` y `-` funcionan sin romper nada.** No hay ningún tamaño de
celda fijo en el código: se recalcula cada vez que cambia la rejilla.

*El bucle principal*

`correr()` es el bucle de siempre en los juegos: procesar eventos, actualizar,
dibujar, esperar al siguiente fotograma a 60 por segundo.

```python
while funcionando:
    for evento in pygame.event.get():   # teclas, ratón, cerrar ventana
        ...
    self._raton()      # pintar arrastrando
    self._avanzar()    # dar N pasos de la búsqueda
    self._dibujar()
    self.reloj.tick(60)
```

*Entrada*

| Método | Qué hace |
|---|---|
| `_raton()` | pintar **arrastrando**: mira si el botón sigue pulsado, no solo el clic |
| `_clic_panel(pixel)` | ¿el clic cayó en un botón de pincel? Entonces lo selecciona |
| `_tecla(tecla)` | el despachador de todas las teclas. Devuelve `False` para cerrar |

`_tecla()` está ordenado a propósito: primero las teclas que valen en las dos
pantallas (`M`, `H`, `D`, `T`, velocidad, salir) y al final, tras un
`if self.busqueda is not None: return`, las que **solo tienen sentido en el
editor** (`O`, `W`, `A`, `B`, `C`, `R`, `U`, `+`, `-`). Así es imposible
repintar el laberinto a media búsqueda.

*Acciones*

| Método | Qué hace |
|---|---|
| `_avisar(texto, color)` | el mensaje de la esquina inferior |
| `_cambiar_tamano(delta)` | ±2 filas y ±3 columnas, respetando los topes |
| `_empezar()` | **valida** y crea la `Busqueda` con la configuración actual |
| `_reiniciar_si_corre()` | si cambias de modo a media búsqueda, la rehace |
| `_avanzar()` | da `VELOCIDADES[indice]` pasos en este fotograma |

🔑 **`_reiniciar_si_corre()` es lo que hace posible la demostración:** pulsas `M`
con la búsqueda a medias y vuelve a empezar sobre **el mismo laberinto** con el
otro algoritmo, listo para comparar.

*Dibujo*

| Método | Qué hace |
|---|---|
| `_dibujar()` | limpia la pantalla, pinta rejilla y panel, y hace el volcado |
| `_rect(posicion)` | el rectángulo en píxeles de una casilla |
| `_dibujar_rejilla()` | pinta las casillas, por capas |
| `_linea(x, y, texto, …)` | escribe una línea en el panel y devuelve la `y` siguiente |
| `_boton(…)` | dibuja un botón de pincel y **devuelve su rectángulo** |
| `_dibujar_panel()` | todo el panel derecho |

**El orden de las capas en `_dibujar_rejilla()` importa**, y es lo que hace que
la animación se entienda:

1. el terreno: libre, pared o barro;
2. encima, y **solo si no es pared**: camino → cerrado → frontera;
3. el nodo que se expande ahora, con un borde blanco;
4. el inicio y la meta, siempre visibles por encima de todo.

Y `_boton()` devuelve su rectángulo para que `_dibujar_panel()` los vaya
guardando en `self.botones`. Es el truco que permite que los botones sean
pulsables sin usar ninguna librería de interfaz: **se dibujan y se recuerda
dónde quedaron**, y `_clic_panel()` compara la posición del clic contra esa
lista.

---

### 9.9 `prueba_consola.py` — las pruebas (163 líneas)

```
python prueba_consola.py
```

No necesita pygame. La idea: **Dijkstra es el oráculo.** Dijkstra siempre
devuelve el costo óptimo verdadero, así que si A\* con nuestra heurística
devolviera un costo distinto sobre el mismo laberinto, la heurística no sería
admisible y habría un error.

| Función | Qué hace |
|---|---|
| `dibujar(laberinto, camino)` | el mapa en texto: `A`, `B`, `#` pared, `~` barro, `o` ruta |
| `comparar(titulo, laberinto, …)` | corre los tres modos y saca la tabla de resultados |
| `verificar(resultados)` | **comprueba que A\* empate con Dijkstra en costo** |
| `main()` | los seis casos |

Los seis casos: la trampa en U, un aleatorio con barro, el mismo con 8
direcciones, el efecto del desempate, un laberinto sin solución y la comparación
entre heurísticas. Termina imprimiendo `RESULTADO: TODO CORRECTO` y devuelve
código de salida 0, para poder encadenarlo.

👉 **No afirmamos que nuestro A\* encuentra la ruta óptima: lo comprobamos
contra un algoritmo que la garantiza.**

---

## 10. Resultados medidos

Todos salen de ejecutar `prueba_consola.py`.

### A\* contra Dijkstra: mismo resultado, menos trabajo

| Laberinto | Costo A\* | Costo Dijkstra | Nodos A\* | Nodos Dijkstra | Ahorro |
|---|---|---|---|---|---|
| Trampa en U, 15×25 | 32,00 | 32,00 | 243 | 353 | 31 % |
| Aleatorio con barro, 16×24 | 25,00 | 25,00 | 58 | 207 | 72 % |
| Con obstáculos, 20×30 | 29,00 | 29,00 | 58 | 452 | 87 % |
| Ejemplo del apartado 5, 8×8 | 10,00 | 10,00 | 25 | 50 | 50 % |

**Los costos coinciden siempre.** Esa columna es la prueba de que la heurística
es admisible y la ruta es óptima.

### Greedy: dónde falla de verdad

| Laberinto | A\* | Greedy | Diferencia |
|---|---|---|---|
| Aleatorio con barro | **25,00** | **41,00** | **64 % más caro** |
| Otro aleatorio | **34,00** | **48,00** | 41 % más caro |

🔑 En el mapa con barro, Greedy llega en **el mismo número de pasos** que A\*
pero con un costo muy superior: **pisa el barro**. Y pisa el barro porque ignora
`g`, que es lo único que sabe que el barro es caro.

**Esa es la demostración de para qué sirve `g`**, y es el mejor momento del
video: dos rutas con la misma longitud y precios muy distintos.

### El desempate

| | Costo | Nodos expandidos |
|---|---|---|
| Sin desempate | 29,00 | 58 |
| Con desempate | 29,00 | **37** |

Misma ruta, 36 % menos trabajo.

### Las heurísticas comparadas

Mismo laberinto 20×30, modo A\*, 4 direcciones:

| Heurística | Costo | Nodos expandidos |
|---|---|---|
| **manhattan** (la correcta para 4 direcciones) | 39,00 | **154** |
| octile | 39,00 | 220 |
| euclidiana | 39,00 | 245 |

Las tres son admisibles, **por eso las tres dan el mismo costo**. Pero
euclidiana subestima más, guía peor y expande un 59 % más de nodos. Es la teoría
confirmada con números propios.

### ⚠️ Un resultado honesto que conviene declarar

En la **trampa en U**, Greedy encontró **el mismo costo** que A\* (32,00). La
versión simplificada que se cuenta habitualmente —"Greedy se queda atrapado en
la U"— no se cumple tal cual en nuestro programa, porque al expandir un nodo se
generan **todos** sus vecinos de una vez y la salida se descubre casi al mismo
tiempo que se entra en la U.

**Conclusión más precisa:** el obstáculo cóncavo le cuesta a Greedy
*exploración*; el terreno con costos distintos le cuesta *calidad de ruta*.

Declarar esto suma en la evaluación: demuestra que medimos en vez de repetir.

---

## 11. Errores que evitamos a propósito

Las fuentes que nos dieron **se contradicen entre sí**. Esta sección documenta
las decisiones.

| # | Error | Dónde estaba | Qué hicimos |
|---|---|---|---|
| 1 | Heurística euclidiana **al cuadrado** → inadmisible → no garantiza el óptimo | código de Medium | Manhattan / octile, documentado en `heuristicas.py` |
| 2 | `continue` dentro de un bucle interno: **no salta nada**, así que reexpande nodos cerrados | código de Medium | `set` de cerrados y comprobación al sacar de la cola |
| 3 | Diagonales a **costo 1** teniendo `h` al cuadrado → escalas incompatibles | código de Medium | diagonal = √2 × costo de la casilla |
| 4 | Búsqueda **lineal** del menor `f` en vez de cola de prioridad | código de Medium | `heapq` |
| 5 | Modificar el montículo por dentro **rompe su invariante** | comentarios del fork | borrado perezoso |
| 6 | Reconstruir el camino buscando un vecino con `g` menor → puede devolver otro camino | página hexagonal | puntero al padre |
| 7 | **Cortar esquinas** en diagonal entre dos paredes | no se comprueba en ninguna fuente | comprobación explícita en `vecinos()` |
| 8 | Devolver `None` en silencio si no hay ruta | código de Medium | estado `exito` y mensaje en pantalla |

### Sobre las fuentes en sí

⚠️ Dos de los cinco enlaces no sirven tal cual:

- El de **Medium devuelve error 403**. El código se leyó del gist público del
  propio autor.
- El de **Stanford es la parte 1 de 13** y no contiene ni una sola heurística.
  Todas las fórmulas salieron de `Heuristics.html`, enlazada desde ahí.
- El **pseudocódigo de Brilliant está incompleto**: nunca calcula `f` y termina
  cortado. Sirve para la teoría, no para implementar.
- La **página hexagonal no trae el código**: está en dos enlaces de Google Drive.

---

## 12. Preguntas probables en la defensa

**¿Por qué A\* y no Dijkstra, si Dijkstra también da el óptimo?**
Porque da el mismo resultado haciendo mucho más trabajo. En nuestras medidas,
entre 31 % y 87 % más nodos expandidos para llegar exactamente a la misma ruta.

**¿Por qué A\* y no Greedy, si Greedy es más rápido?**
Porque no garantiza el óptimo. En nuestro mapa con barro, Greedy devolvió una
ruta un 64 % más cara con el mismo número de pasos.

**¿Cómo saben que la ruta es realmente óptima?**
La comparamos contra Dijkstra, que la garantiza, sobre el mismo laberinto. Está
automatizado en `prueba_consola.py`.

**¿Qué pasa si la heurística se equivoca?**
Depende de hacia dónde. Si subestima, la ruta sigue siendo óptima pero A\*
trabaja más. Si sobreestima, se pierde la garantía del óptimo. Por eso
descartamos la euclidiana al cuadrado.

**¿Qué complejidad tiene?**
En el peor caso, el número de nodos expandidos es exponencial en la longitud de
la solución; es polinomial si el espacio de búsqueda es un árbol. Su mayor
limitación práctica no es el tiempo sino **la memoria**: hay que mantener la
lista abierta completa.

**¿Funcionaría con otra forma de laberinto?**
Sí, y casi sin tocar nada: solo `vecinos()` y la heurística. `astar.py` solo ve
un grafo.

**¿Por qué el barro cuesta 5?**
Para que `g` tenga algo que medir. Si todas las casillas costaran lo mismo, la
ruta óptima sería simplemente la más corta y no se podría demostrar la
diferencia entre A\* y Greedy.

---

## 13. Fuentes

1. Patel, A. *Introduction to A\**. Stanford University.
   https://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html
2. Patel, A. *Heuristics*. Stanford University.
   https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html
3. *A\* Search*. Brilliant.org. https://brilliant.org/wiki/a-star-search/
4. Swift, N. *Easy A\* (star) Pathfinding*. Medium.
   https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
5. Magdziarz, M. *Pathfinding on a hexagonal grid – A\* algorithm*. The Knights of U.
   https://theknightsofu.com/pathfinding-on-a-hexagonal-grid-a-algorithm-2/
6. Patel, A. *Introduction to the A\* Algorithm*. Red Blob Games.
   https://www.redblobgames.com/pathfinding/a-star/introduction.html

El material recopilado de cada una, con las citas verificadas, está en
[`FUENTES.md`](FUENTES.md).
