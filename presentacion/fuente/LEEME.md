# Fuente de la presentación

Esta carpeta es **el código de la presentación**, no la presentación en sí.

## 🔴 Hay DOS versiones, y conviene no mezclarlas

| | Dónde | Para qué |
|---|---|---|
| **PowerPoint** | `../Presentacion Algoritmo A-estrella.pptx` | **La que se entrega y se proyecta.** Se abre en cualquier PC |
| **Web** | el enlace de abajo | Para ver y comentar desde el navegador |

Las dos tienen el mismo contenido, pero **no están enlazadas**: cambiar una no cambia la otra.

⚠️ **El `.pptx` se genera con `construir_pptx.py`.** Si lo editan a mano en PowerPoint y
alguien vuelve a correr el guion, **esas ediciones se pierden**. A partir del momento en que lo
editen a mano, el archivo manda y el guion queda como respaldo.

```
python construir_pptx.py
```

| | |
|---|---|
| **La presentación** | https://claude.ai/artifact/4JteuRAPia4M6Ag6dR3zDZ |
| **Qué hay aquí** | `project/deck.json` (el índice), `project/deck.css` (los estilos) y un `.html` por lámina en `project/slides/` |
| **Las capturas** | Subidas a la presentación como recursos. Los originales están en `../CAPTURAS/` |

🔴 **La presentación es privada.** Para que Haniel, Junior o el profesor la abran hay que
compartirla desde el menú *Share* de la propia página.

**Para descargarla como PowerPoint o PDF:** desde la página, menú *Share → Export*.

**Para editar una lámina:** se cambia su `.html` aquí y se vuelve a publicar. También se puede
editar el texto directamente en la página, que es más rápido para corregir nombres o cifras.

## Las 19 láminas

| # | Archivo | Qué cubre |
|---|---|---|
| 1 | `portada` | Título e integrantes |
| 2 | `problema` | El laberinto, A y B, óptima ≠ corta |
| 3 | `dos-algoritmos` | Dijkstra · Greedy · A* |
| 4 | `ecuacion` | f(n) = g(n) + h(n) |
| 5 | `terminos` | Qué es g, h y f |
| 6 | `pesos` | Un solo buscador con dos pesos |
| 7 | `heuristica` | Manhattan y la admisibilidad |
| 8 | `no-usamos` | La euclidiana al cuadrado, descartada |
| 9 | `nodos` | Las dos listas |
| 10 | `ciclo` | El ciclo paso a paso |
| 11 | `traza` | El ejemplo numérico |
| 12 | `laberinto` | El laberinto de la demo |
| 13 | `demo` | A* resolviéndolo |
| 14 | `comparacion` | Los tres modos lado a lado |
| 15 | `barro` | 29 pasos los tres, 83 % más caro Greedy |
| 16 | `codigo` | Los seis archivos |
| 17 | `verificacion` | Dijkstra como oráculo |
| 18 | `cierre` | Resumen y limitación declarada |
| 19 | `fuentes` | Las seis referencias |

Todas las láminas llevan **notas del orador**, que son el guion de esa lámina.

## Los integrantes

Verificados el 12 de noviembre contra 35 documentos del proyecto. El orden y la forma de los
nombres son **los mismos de la portada oficial** de `Presentacion Proyecto Final.pptx` y
`Presentacion Robotica.pptx`:

> Junior Alexandro Castillo · Haniel García · José Javier Pacheco · José Alejandro Matos

## Lo que falta rellenar

- [ ] Si el grupo diseña otro laberinto, rehacer las capturas y cambiar las cifras de las
      láminas 12, 13, 14 y 15.
