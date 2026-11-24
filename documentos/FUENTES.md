# Material recopilado de las fuentes — base para la guía final

> Esto **no es la guía**. Es la materia prima: lo que dice cada fuente, verificado
> leyéndola, más las decisiones que se tomaron al programar y por qué. La guía
> final se redacta a partir de este archivo.
>
> Recopilado el 9 de noviembre de 2026.

---

## Las fuentes, y qué aporta cada una

| # | Fuente | Qué aporta | Estado |
|---|---|---|---|
| 1 | [Amit Patel — Introduction to A\*](https://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html) | El *porqué*: Dijkstra vs Greedy vs A\*, obstáculo cóncavo | ✅ leída |
| 2 | [Brilliant — A\* Search](https://brilliant.org/wiki/a-star-search/) | Definición formal, admisibilidad, complejidad | ✅ leída |
| 3 | [Nicholas Swift — Easy A\* Pathfinding (Medium)](https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2) | Código Python con clase `Node` | 🔴 **403.** Leído del [gist del autor](https://gist.github.com/Nicholas-Swift/003e1932ef2804bebef2710527008f44) |
| 4 | [The Knights of U — Hexagonal grid](https://theknightsofu.com/pathfinding-on-a-hexagonal-grid-a-algorithm-2/) | Coordenadas cúbicas y distancia hexagonal | ✅ leída (el código está en Google Drive, no en la página) |

**Dos que no estaban en la lista y hacían falta:**

| # | Fuente | Por qué |
|---|---|---|
| 5 | [Amit Patel — Heuristics](https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html) | La #1 es la **parte 1 de 13** y no trae ni una heurística. Las fórmulas están aquí |
| 6 | [Red Blob Games — Introduction to A\*](https://www.redblobgames.com/pathfinding/a-star/introduction.html) | La única implementación limpia y correcta del conjunto |

---

## 1. La ecuación, y por qué son dos algoritmos trabajando juntos

```
f(n) = g(n) + h(n)
```

| Término | Qué es | Naturaleza |
|---|---|---|
| `g(n)` | costo **real y exacto** del camino desde el inicio hasta `n` | hecho, ya ocurrió |
| `h(n)` | costo **estimado** desde `n` hasta la meta | suposición, aún no ocurre |
| `f(n)` | estimación del costo total del camino que pasa por `n` | la prioridad de la cola |

La fuente #1 lo plantea exactamente como "dos algoritmos":

- **Dijkstra** favorece los vértices cercanos al **inicio**. Garantiza el camino
  más corto mientras ninguna arista tenga costo negativo. Trabaja de más.
- **Greedy Best-First-Search** favorece los vértices cercanos a la **meta**.
  Es mucho más rápido, pero no garantiza el camino más corto.
- **A\*** balancea los dos al moverse del inicio hacia la meta.

La fuente #1 explica por qué Greedy falla: es "codicioso" e intenta avanzar
hacia la meta aunque no sea el camino correcto; como solo considera el costo
hasta la meta e **ignora el costo del camino recorrido**, sigue adelante aunque
el camino se haya vuelto larguísimo.

**En nuestro código esto es literal**, no una metáfora (`astar.py`):

```
prioridad = peso_g · g(n) + peso_h · h(n)

peso_g=1, peso_h=1  →  A*
peso_g=1, peso_h=0  →  Dijkstra
peso_g=0, peso_h=1  →  Greedy
```

La fuente #5 lo confirma desde el otro lado: si `h(n) = 0`, A\* **es** Dijkstra.
Si `h(n)` es muy grande frente a `g(n)`, solo importa `h` y A\* **es** Greedy.
La #6 lo resume: cuanto menor la heurística, A\* se vuelve Dijkstra; cuanto
mayor, se vuelve Greedy Best-First.

---

## 2. Admisibilidad: la condición que da la ruta óptima

**Fuente #2 (Brilliant):** la función heurística debe ser *admisible*, lo que
significa que nunca puede sobreestimar el costo de llegar a la meta. Manhattan
y `h(n)=0` lo son.

**Fuente #5 (Heuristics), la escala completa:**

| Si h(n)... | Entonces |
|---|---|
| = 0 | A\* es Dijkstra. Garantiza el camino más corto |
| ≤ costo real siempre | A\* garantiza el camino más corto. Cuanto menor, más nodos expande |
| = costo real exacto | A\* sigue solo el mejor camino. Expande poquísimo |
| > costo real a veces | **No** garantiza el más corto, pero puede ser más rápido |
| ≫ g(n) | A\* degenera en Greedy |

**Fuente #6:** mientras la heurística no sobreestime distancias, A\* encuentra
un camino óptimo.

⚠️ La fuente #4 (hexágonos) afirma que A\* es completo y óptimo y que siempre
será el camino más corto, **sin mencionar la admisibilidad en ningún momento**.
En su caso concreto se cumple, pero como enunciado general está incompleto.

---

## 3. Las heurísticas — fórmulas verificadas (fuente #5)

`D` = costo del paso más barato entre casillas adyacentes. `dx`, `dy` =
diferencias absolutas de coordenadas.

**Manhattan — movimiento en 4 direcciones**
```
h = D * (dx + dy)
```

**Octile / Chebyshev — movimiento en 8 direcciones**
```
h = D * (dx + dy) + (D2 - 2*D) * min(dx, dy)
```
Con `D=1, D2=√2` es **octile**. Con `D=1, D2=1` es **Chebyshev**.
Razonamiento del autor: hay `min(dx,dy)` pasos diagonales, cada uno cuesta `D2`
y ahorra dos pasos ortogonales de `D`.

**Euclidiana — movimiento en cualquier ángulo**
```
h = D * sqrt(dx*dx + dy*dy)
```
Advertencia: si el movimiento no sigue la rejilla, `g` y `h` no coinciden en
escala. En rejilla subestima, así que sigue siendo admisible, pero A\* tarda más.

**Hexagonal, en coordenadas cúbicas (fuente #4)**
```
x + y + z = 0
h = max(|x1-x2|, |y1-y2|, |z1-z2|)
```
Equivale a `(|dx|+|dy|+|dz|)/2`. Con costo 1 por hexágono es **exacta**.

### 🔴 La contradicción entre las fuentes

El código de la fuente #3 calcula:
```python
child.h = (dx)**2 + (dy)**2      # euclidiana AL CUADRADO
```

La fuente #5 dedica una sección a esa fórmula y dice, textual: "Do not do this!"

Razón: el cuadrado crece mucho más rápido que `g`, así que `h` **sobreestima**,
deja de ser admisible y en distancias largas A\* degenera en Greedy. Si se
reescala hacia abajo para compensar, en distancias cortas queda demasiado
pequeña y degenera en Dijkstra.

**Nuestra entrega pide la ruta óptima, así que esa fórmula quedó fuera.**
`heuristicas.py` lo documenta en su encabezado.

### La regla de la escala (fuente #5)

`g` y `h` tienen que estar en las mismas unidades, porque A\* las suma. Si `g`
se mide en horas y `h` en metros, A\* pesa mal una de las dos.

**Prueba práctica:** en un mapa sin obstáculos y costos uniformes, el camino más
corto es una línea recta. Calcular `h` de A a B y compararlo con el costo real.
Si no coinciden, hay problema de escala o de tipo de heurística.

➡️ En nuestro código, `D = COSTO_MINIMO` sale del propio `laberinto.py`, no de
una constante escrita a mano.

---

## 4. Manejo de los nodos

**Las dos listas** (fuentes #2 y #3):
- **Lista abierta (frontera):** nodos descubiertos pero no expandidos. Se saca
  siempre el de menor `f`. En nuestro código es un `heapq`.
- **Lista cerrada:** nodos ya expandidos. En nuestro código es un `set`.

**El bucle (fuente #6), la parte que importa:**
```
new_cost = cost_so_far[current] + graph.cost(current, next)
if next not in cost_so_far or new_cost < cost_so_far[next]:
    cost_so_far[next] = new_cost
    priority = new_cost + heuristic(goal, next)
    frontier.put(next, priority)
    came_from[next] = current
```
La #6 señala que la ÚNICA diferencia con Dijkstra es sumar `heuristic(...)` a la
prioridad.

**Reconstrucción (fuente #6):** seguir las flechas hacia atrás desde la meta
hasta el inicio, con `came_from[B] == A`, y dar vuelta la lista.

### Advertencias de implementación recogidas

| Advertencia | Fuente |
|---|---|
| Comprobar la meta **al sacar** de la cola, no al insertar. Al insertar deja de funcionar en cuanto hay costos de movimiento | #6 |
| Un nodo puede visitarse varias veces con costos distintos; por eso solo se añade si el camino nuevo es mejor | #6 |
| La open list debe ser una cola de prioridad | comentarios del fork de la #3 |
| Reemplazar un elemento del montículo viola su invariante; hay que re-ordenarlo | comentarios del fork de la #3 |
| El complejidad temporal es exponencial en el largo de la solución en el peor caso, polinomial si el espacio es un árbol | #2 |
| El mayor inconveniente de A\* es la **memoria**: hay que guardar la lista abierta entera | #2 |

### 🔴 Los errores del código de la fuente #3, verificados en el gist

1. **Los tres `continue` no hacen nada.** Están dentro de un `for` interno, así
   que continúan ese bucle y no el de los hijos: los nodos ya cerrados se
   vuelven a meter en la lista abierta.
2. **Heurística inadmisible** (euclidiana al cuadrado) → no garantiza el óptimo.
3. **Diagonales a costo 1** (`child.g = current_node.g + 1`) mientras `h` está al
   cuadrado → escalas incompatibles.
4. **Búsqueda lineal del mínimo `f`** recorriendo toda la lista; no hay cola de
   prioridad.
5. **Devuelve `None` en silencio** si no hay camino.
6. **No comprueba corte de esquinas** con 8 direcciones.
7. Coordenadas en `(fila, columna)`, no `(x, y)` — fuente de confusión
   documentada en los comentarios del fork.

### 🔴 El error de la fuente #4

Reconstruye el camino retrocediendo desde el destino y eligiendo un vecino que
esté en la lista cerrada y tenga `G` menor que el anterior. Con costo uniforme
puede haber varios vecinos empatados y devolver un camino distinto del que el
buscador encontró. **Nuestro código usa puntero al padre**, que no puede fallar.

---

## 5. Desempate (fuente #5)

En rejillas con terreno uniforme hay muchos caminos de igual longitud, así que
muchos nodos empatan en `f` y A\* explora de más. El desempate debe ser
determinista respecto al vértice, no aleatorio.

Soluciones que propone:
- `heuristic *= (1.0 + p)` con `p < (costo mínimo de un paso) / (largo máximo esperado)`.
  Rompe ligeramente la admisibilidad, pero "casi nunca importa".
- Comparar por `h` cuando los `f` empatan (Steven van Dijk).
- Número pseudoaleatorio determinista.
- Producto cruzado respecto a la línea inicio–meta.
- **Orden de inserción en la cola de prioridad.**
- Penalizar los giros.

El autor advierte que todo esto es un parche sobre una ineficiencia de fondo, y
menciona alternativas: Jump Point Search, pathfinding jerárquico, Fringe Search.

➡️ **En nuestro código hay dos desempates, y conviene saberlo:**
1. El montículo guarda `(prioridad, orden, nodo)`. Ese `orden` incremental **ya
   es** el desempate por orden de inserción de la lista de arriba, y además
   evita que Python intente comparar tuplas de posición.
2. La tecla `T` activa el `(1 + p)`, con `p = costo_mínimo / número_de_nodos`.

Medido en `prueba_consola.py`, mapa 20×30 con obstáculos:
**58 nodos expandidos sin desempate, 37 con desempate, mismo costo (29.00).**

---

## 6. El obstáculo cóncavo (fuente #1)

La fuente #1 usa una "U": una unidad que solo mira hacia delante sigue su
camino, detecta el obstáculo cerca de la cima, cambia de dirección y rodea la U.
Dice que Dijkstra trabaja más pero garantiza el camino más corto, que Greedy
trabaja menos pero su camino claramente no es tan bueno, y que en el ejemplo con
obstáculo cóncavo A\* encuentra un camino tan bueno como el de Dijkstra.
Remedios que propone: evitar crear obstáculos cóncavos, o marcar su envolvente
convexa como peligrosa.

### ⚠️ Resultado real en nuestro programa — honesto

En la trampa en U de `laberinto.py`, **Greedy encontró el mismo costo que A\***
(32.00 los dos). No es un fallo nuestro: al expandir un nodo se generan **todos**
sus vecinos de una vez, así que la ruta de escape por fuera de la U se descubre
casi al mismo tiempo que se entra en ella.

**Dónde sí falla Greedy de verdad: con terreno de costos distintos.** Medido:

| Mapa | A\* | Dijkstra | Greedy |
|---|---|---|---|
| Trampa en U | 32.00 (243 exp.) | 32.00 (353 exp.) | 32.00 (92 exp.) |
| Aleatorio con barro | **25.00** (58 exp.) | 25.00 (207 exp.) | **41.00** (26 exp.) |
| Aleatorio, otro mapa | **34.00** (134 exp.) | 34.00 (231 exp.) | **48.00** (31 exp.) |

🔑 En el mapa con barro, Greedy llega en **el mismo número de pasos** pero con un
costo **64 % mayor**: pisa el barro porque ignora `g`, y `g` es lo único que
sabe que el barro es caro. **Esa es la demostración honesta de para qué sirve
`g`**, y es mejor argumento que la U.

📌 Para la guía: declarar esto como resultado medido, no esconderlo. Decir que
la trampa en U cuesta *exploración* y que el terreno con costos cuesta *calidad
de ruta* es más preciso que la versión simplificada de la fuente #1.

---

## 7. Comparación guardada entre heurísticas

Mismo laberinto 20×30, modo A\*, 4 direcciones:

| Heurística | Costo | Nodos expandidos |
|---|---|---|
| manhattan (la correcta para 4 dir.) | 39.00 | **154** |
| octile | 39.00 | 220 |
| euclidiana | 39.00 | 245 |

Las tres son admisibles, por eso **las tres dan el mismo costo**. Pero
euclidiana subestima más, guía peor y expande 59 % más nodos. Es la teoría de la
fuente #5 confirmada con números propios.

---

## 8. Lo que falta para la guía final

- [x] ~~Redactar la guía a partir de este archivo.~~ **Hecho el 9 de noviembre:
      [`MANUAL.md`](MANUAL.md)**, 13 secciones, con una traza numérica generada
      por el propio código y todas las cifras verificadas
- [ ] Capturas de pantalla del programa (editor, a medias, resuelto, los 3 modos)
- [ ] Reparto de quién explica qué en el video
- [ ] Decidir si se añade la variante hexagonal (fuente #4) o se menciona como
      trabajo futuro
