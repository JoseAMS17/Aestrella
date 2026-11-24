"""Revisa el informe generado: estructura, imagenes y texto, sin abrir Word."""
import re
import sys
import zipfile

import docx

RUTA = sys.argv[1] if len(sys.argv) > 1 else "Informe Tecnico Algoritmo A-estrella.docx"

documento = docx.Document(RUTA)
parrafos = [p.text for p in documento.paragraphs]
con_texto = [t for t in parrafos if t.strip()]

print("parrafos totales:", len(parrafos), "| con texto:", len(con_texto))

with zipfile.ZipFile(RUTA) as z:
    medios = [n for n in z.namelist() if n.startswith("word/media/")]
    partes = [n for n in z.namelist() if not n.startswith("word/media/")]
print("imagenes embebidas:", len(medios), medios)
print("partes del paquete:", partes)

texto = "\n".join(con_texto)
print("palabras aproximadas:", len(texto.split()))
print()

print("--- titulos ---")
for linea in con_texto:
    if re.match(r"^\d+\. ", linea) or linea.startswith("Informe Técnico"):
        print("   ", linea)
print()

print("--- comprobaciones ---")
problemas = []
if "Webots" in texto:
    problemas.append("quedo texto de Webots")

# Los datos de cabecera salen del informe de Webots ya entregado.
for dato in ("2024-0719", "2024-0699", "2021-0276", "2019-8955",
             "Robótica TMC-306", "Pedro Pablo Castro"):
    if dato not in texto:
        problemas.append("falta el dato de cabecera: " + dato)

# Las cifras medidas sobre el laberinto de la demostracion.
for cifra in ("29,00", "53,00", "111", "276", "46", "384"):
    if cifra not in texto:
        problemas.append("falta la cifra " + cifra)

for pie in ("Figura 1.", "Figura 2.", "Figura 3.", "Figuras 4, 5 y 6."):
    if pie not in texto:
        problemas.append("falta el pie " + pie)

# 5 figuras mas el logo del ITLA.
if len(medios) != 6:
    problemas.append("deberian ser 6 imagenes (5 figuras y el logo)")

if "Enlace de explicación en Teams" not in texto:
    problemas.append("falta la linea del enlace de Teams")

if problemas:
    for p in problemas:
        print("    FALLA:", p)
else:
    print("    todo correcto")
