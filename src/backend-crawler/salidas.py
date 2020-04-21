"""
Módulo para encapsular la forma en que se manipulan salidas
de información en la aplicación
"""

import config

colores = (
    "\033[0m",   # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
    "\033[32m",  # Green
    "\033[33m",  # Yellow
    "\u001b[34m", # Blue
    "\u001b[33;1m", # Bright Yellow
    "\u001b[36;1m", # Bright Cyan
    "\u001b[31;1m", # Bright Red
    "\u001b[32;1m", # Bright Green
)

color_default = colores[0]

class Coloreador():
    def __init__(self, color):
        self.color = color

    def __enter__(self):
        print(self.color, end='')

    def __exit__(self, *args):
        print("\033[0m", end='')

def imprimir_salida(texto, nivel=0):
    for i in range(nivel):
        print('  ', end='', file=config.salida)
    with Coloreador(color_default):
        print(texto, file=config.salida)


if __name__ == '__main__':
    color_default = colores[1]
    imprimir_salida('Hola')
