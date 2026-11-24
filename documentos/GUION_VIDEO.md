# Guion del video

### Algoritmo A\* — búsqueda de la ruta óptima en un laberinto

Cuatro integrantes · duración objetivo **8 minutos** (el rango pedido es 5 a 10)

---

> ⚠️ **Dos huecos que hay que rellenar antes de grabar**
>
> 1. **La descripción del laberinto** del grupo, en el bloque de José Matos (lámina 12).
> 2. Los números `[X]`, `[Y]`, `[Z]` y `[N]` de la demostración: córranlos una vez
>    antes de grabar y anótenlos. **No los improvisen delante de la cámara.**

---

## El reparto va por tramos de láminas

Cada persona cubre **un tramo seguido** de la presentación, así que nadie tiene que volver
atrás ni saltar hacia adelante. Basta con avanzar las láminas en orden.

| Quién | Láminas | Minutos | Lo que exige el enunciado |
|---|---|---|---|
| **Todos** | 1 | 0:00 – 0:40 | Presentación de los integrantes |
| **Junior Castillo** | 2 – 3 | 0:40 – 1:45 | El problema y la idea de A\* |
| **Haniel García** | 4 – 8 | 1:45 – 3:45 | Función de costo y heurística utilizada |
| **José Pacheco** | 9 – 11 | 3:45 – 5:05 | Manejo de los nodos |
| **José Matos** | 12 – 17 | 5:05 – 7:40 | El laberinto, la **demostración** y la programación |
| **Todos** | 18 – 19 | 7:40 – 8:00 | Cierre |

Los cinco puntos del enunciado quedan cubiertos, en ese orden.

> 🔑 **Cada lámina lleva además sus propias notas del orador**, con este mismo texto.
> Quien presente puede leerlas desde la vista de presentador.

---

## Apertura — los cuatro · lámina 1 · 0:00 – 0:40

> 🎥 **En pantalla:** la portada.

**Junior Castillo:** Buenas. Somos el grupo que presenta el proyecto del algoritmo A
estrella. Yo soy Junior Castillo.

**Haniel García:** Yo soy Haniel García.

**José Pacheco:** José Pacheco.

**José Matos:** Y yo José Matos.

**Junior Castillo:** Desarrollamos en Python un programa que encuentra la ruta óptima dentro
de un laberinto, desde un punto A hasta un punto B. Les vamos a explicar cómo funciona el
algoritmo, cómo diseñamos el laberinto, y al final lo vamos a correr en vivo.

---

## Junior Castillo — El problema y la idea de A\* · láminas 2 – 3 · 0:40 – 1:45

### Lámina 2 — El problema

**Junior Castillo:**

Primero, qué problema resolvemos. Tenemos una rejilla. Algunas casillas se pueden pisar y
otras son obstáculos. Hay un punto de partida, que llamamos A, y un punto de llegada, que
llamamos B.

Lo que buscamos no es *una* ruta cualquiera: es la **ruta óptima**, la más barata de todas
las posibles.

Y digo barata, no corta, a propósito. En nuestro laberinto no todas las casillas cuestan lo
mismo. El suelo normal cuesta uno. El barro cuesta cinco. Entonces el camino con menos pasos
puede terminar siendo el más caro. Eso es importante y van a ver por qué al final.

### Lámina 3 — A\* son dos algoritmos trabajando juntos

A estrella se entiende mejor si se sabe de dónde sale, porque combina dos algoritmos
anteriores.

El primero es **Dijkstra**. Expande siempre la casilla más cercana al punto de partida, y
crece como una mancha en todas las direcciones. Encuentra la ruta de menor costo, pero como
no sabe dónde está la meta, trabaja de más.

El segundo es la **búsqueda voraz**, o Greedy. Hace lo contrario: expande la casilla que
parece más cercana a la meta. Va derecho hacia B y es rapidísima, pero como ignora lo que ya
gastó, no garantiza la mejor ruta.

**A estrella mira las dos cosas a la vez**: lo que ya costó llegar y lo que falta por
recorrer. Haniel les explica ahora cómo se calcula eso.

---

## Haniel García — La función de costo y la heurística · láminas 4 – 8 · 1:45 – 3:45

### Lámina 4 — La ecuación

**Haniel García:**

Todo el algoritmo sale de una sola fórmula:

**f de n, igual a g de n más h de n.**

En cada vuelta del ciclo, A estrella elige la casilla con la f más baja.

### Lámina 5 — Qué significa cada letra

Son tres cosas y cada una significa algo distinto.

**G es lo que ya gastaste.** Es el costo real del camino desde A hasta la casilla donde
estás. No es una estimación: ya recorriste ese camino, sabes exactamente lo que costó.

**H es lo que crees que te falta.** Es la estimación de lo que cuesta ir desde donde estás
hasta B. Esa es la heurística.

**Y F es la suma**: lo que crees que te va a costar el viaje completo si pasas por ahí.

### Lámina 6 — Un solo buscador

Aquí está lo interesante, y es la parte de la que estamos más contentos. **Nosotros no
programamos tres algoritmos: programamos uno solo**, con dos pesos.

Si le apagamos el peso de h, queda Dijkstra. Si le apagamos el peso de g, queda la búsqueda
voraz. Y con los dos encendidos, es A estrella.

Eso se cambia con una tecla mientras el programa corre, así que los tres se pueden comparar
sobre el mismo laberinto y en las mismas condiciones.

### Lámina 7 — La heurística

La heurística que usamos es la **distancia Manhattan**: la diferencia de filas más la
diferencia de columnas. Es decir, cuántos pasos en línea recta faltan si no hubiera
obstáculos. Se usa esa porque nos movemos en cuatro direcciones.

Y hay una condición que es la más importante de todo el proyecto: la heurística tiene que ser
**admisible**. Eso significa que **nunca puede sobrestimar** lo que falta. Si estima de menos,
no pasa nada. Si estima de más, A estrella deja de garantizar la ruta óptima.

### Lámina 8 — La fórmula que no usamos

Esto no es teoría. Una de las referencias que nos dieron trae un código que usa la distancia
euclidiana **al cuadrado**, y esa fórmula sobrestima: deja de ser admisible, y en distancias
largas A estrella degenera en búsqueda voraz.

Como nuestro enunciado pide la ruta **óptima**, la descartamos, y dejamos escrita la razón en
el código.

---

## José Pacheco — El manejo de los nodos · láminas 9 – 11 · 3:45 – 5:05

### Lámina 9 — Las dos listas

**José Pacheco:**

Yo les explico cómo el algoritmo organiza las casillas mientras busca. Trabaja con **dos
listas**.

La **lista abierta**, que también llamamos la frontera. Son las casillas que ya descubrimos
pero todavía no examinamos. En la pantalla son las de **azul claro** *(señalar)*. De esta
lista siempre sacamos la de menor f.

La **lista cerrada**. Son las que ya examinamos y no se vuelven a tocar. Son las de **azul
oscuro** *(señalar)*.

Fíjense en el panel de la derecha: muestra la G, la H y la F de la casilla que se está
examinando en ese momento.

### Lámina 10 — El ciclo

El ciclo se repite hasta encontrar la meta. Sacamos la casilla con la F más baja; si es la
meta, terminamos; si no, la pasamos a la lista cerrada y miramos sus vecinos. Para cada
vecino calculamos el nuevo G, y si el vecino es nuevo o llegamos por un camino **más barato**,
lo actualizamos y lo metemos en la lista abierta.

Ese paso tiene nombre: se llama **relajación**, y es lo que permite que el algoritmo se
corrija a sí mismo.

Un detalle importante: **la meta se comprueba al sacar la casilla de la lista, no al
meterla.** Si se comprueba al meterla, parece que funciona, pero falla en cuanto hay casillas
con costos distintos.

### Lámina 11 — El ejemplo numérico

Aquí se ve el algoritmo en números, en un laberinto chiquito de ocho por ocho. Esta tabla la
generó el propio programa.

Miren las tres primeras filas: **la f vale 6 y no cambia**. La g sube de 0 a 1 a 2, y la h
baja de 6 a 5 a 4, a la misma velocidad. Eso significa que esos pasos avanzan hacia la meta
sin desperdiciar nada.

Y en la fila 4, **la f salta a 8**. Ahí el algoritmo ya se topó con la pared y tiene que
empezar a considerar el rodeo. **Ese salto es el precio del desvío.**

---

## José Matos — El laberinto, la demostración y la programación · láminas 12 – 17 · 5:05 – 7:40

### Lámina 12 — El laberinto

**José Matos:**

Este es el laberinto que diseñamos.

> 🔴 **AQUÍ VA LA DESCRIPCIÓN DEL LABERINTO DE USTEDES.**
> Tres o cuatro frases: qué forma tiene, por qué lo diseñaron así, dónde pusieron las zonas
> de barro, y qué tiene que lo hace distinto al de los demás grupos. Señalen con el cursor
> mientras hablan.

El punto A es la casilla verde y el punto B es la roja.

Una cosa importante: **todo esto se dibuja antes de arrancar**, con el ratón, usando estos
cuatro botones del panel. El programa no busca nada hasta que uno le da a Enter. Y el tamaño
se puede cambiar: de ocho por ocho hasta cuarenta por cuarenta. Ahora mismo son [N] nodos.

### Lámina 13 — La demostración

> 🎥 *Pasar al programa y pulsar `ENTER`.*

Aquí está A estrella buscando. Vean cómo se extiende **hacia la meta**, no en todas las
direcciones.

*(esperar a que termine)*

Listo. Encontró la ruta, en amarillo. Costo **[X]**, y expandió **[Y]** nodos. Fíjense en que
rodea el barro en vez de atravesarlo.

### Lámina 14 — Los tres modos

> 🎥 *`ESC`, luego `M` para pasar a Dijkstra, y `ENTER`. Después `M` otra vez para Greedy.*

Ahora el mismo laberinto con los otros dos modos.

Dijkstra encontró **la misma ruta**, con el mismo costo, pero miren los nodos expandidos:
**[Z]** contra **[Y]**. Mucho más trabajo para el mismo resultado, porque no sabía hacia
dónde estaba B.

Y la búsqueda voraz fue rapidísima, expandió muy pocos nodos… **pero su ruta cuesta más**.

### Lámina 15 — Por qué

Y aquí está la explicación, que es lo mejor que encontramos del proyecto.

**Los tres llegan en el mismo número de pasos: veintinueve.** Pero la búsqueda voraz cuesta un
83 % más. ¿Por qué? Porque **pisa seis casillas de barro**, que cuestan cinco cada una, y A
estrella no pisa ninguna.

Pisa el barro porque **ignora la g**, y la g es lo único que sabe que el barro es caro.
**Esa es la demostración de para qué sirve la g.**

### Lámina 16 — Cómo está hecho el código

Les cuento cómo organizamos el programa. Son **seis archivos**, cada uno con una
responsabilidad: el laberinto, las heurísticas, el algoritmo, la interfaz, el arranque y las
pruebas.

La decisión más importante es que **el archivo del algoritmo no sabe que existe un
laberinto**. No sabe qué es una pared ni qué es una casilla: solo pide los vecinos de un nodo
y lo que cuesta llegar a cada uno. Para el algoritmo, todo es un grafo.

Eso significa que si quisiéramos usar una rejilla **hexagonal**, no habría que tocar el
algoritmo ni una línea.

### Lámina 17 — Cómo sabemos que es óptima

Y una última cosa: nosotros no afirmamos que nuestro algoritmo encuentra la ruta óptima,
**lo comprobamos**.

> 🎥 *Opcional: correr `python prueba_consola.py` y dejar que llegue al final.*

Comparamos A estrella contra Dijkstra, que sí la garantiza, sobre varios laberintos. Si los
costos no coincidieran, nuestra heurística estaría mal. Coinciden en todos los casos.

---

## Cierre — los cuatro · láminas 18 – 19 · 7:40 – 8:00

**José Matos:** En resumen: entregamos el programa, las pruebas que verifican la ruta, y una
decisión técnica documentada, la heurística que descartamos.

**Haniel García:** Y declaramos una limitación: en el obstáculo en forma de U, la búsqueda
voraz obtuvo el mismo costo que A estrella, al contrario de lo que dice la literatura. Lo
medimos en vez de repetirlo.

**Junior Castillo:** Eso es todo. Gracias por su atención, y quedamos a disposición para
cualquier pregunta.

---

## Notas de grabación

| | |
|---|---|
| **Antes de grabar** | Dibujen el laberinto y **guárdenlo o apréndanselo**: cambiar el tamaño de la rejilla lo borra. Tengan el programa ya abierto en una ventana aparte. |
| **Los huecos** | Corran los tres modos una vez antes de grabar y anoten `[X]`, `[Y]`, `[Z]` y `[N]`. |
| **El cambio de persona** | Cada uno empieza justo al pasar a su primera lámina. Nadie tiene que retroceder. |
| **Ritmo** | Hablen más lento de lo que les parece natural. Un guion de 8 minutos leído con nervios se va en 6. |
| **Si se pasan de 10 minutos** | Lo que se recorta es la tercera corrida de la lámina 14 y la prueba en consola de la 17. |
| **Si algo falla en vivo** | No lo arreglen frente a la cámara. Corten y vuelvan a grabar ese bloque. |
| **Puntos gratis** | Presentarse, mirar a la cámara, cumplir el tiempo y ofrecerse para preguntas al final. Está pedido en el enunciado. |

---

## Antes de enviar

- [ ] El video dura entre 5 y 10 minutos
- [ ] Participan los cuatro integrantes
- [ ] Se presentan por su nombre
- [ ] Se explica la función de costo, la heurística y el manejo de los nodos
- [ ] Se describe el laberinto y se señalan A y B
- [ ] Se ve el programa encontrando la ruta óptima
- [ ] Se explica cómo se estructuró la programación
- [ ] Subido a Microsoft Teams **con permisos de acceso habilitados**
