"""
Punto de entrada. Esto es lo que se ejecuta.

    python main.py

Si pygame no esta instalado:

    pip install pygame

Y si pygame diera problemas justo antes de la presentacion, la prueba en
consola no lo necesita y demuestra que el algoritmo funciona:

    python prueba_consola.py
"""


def main():
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("Falta pygame. Instalalo con:")
        print()
        print("    pip install pygame")
        print()
        print("Mientras tanto, el algoritmo se puede comprobar sin interfaz:")
        print()
        print("    python prueba_consola.py")
        return 1

    from juego import Juego
    Juego().correr()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
