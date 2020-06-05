
from bs4 import BeautifulSoup

def agregarSaltos(texto, breakpoint=100):
    columna = 0
    resultado = ''
    for caracter in texto:
        if caracter == '\n':
            resultado += caracter
            columna = 0
        elif columna >= breakpoint and caracter in [' ']:
            resultado += '\n'
            columna = 0
        else:
            resultado += caracter
            columna += 1
    return resultado
        

def prettyfy(html):
    html = html.replace('\n', '')
    html = html.replace('</p>', '\n\n')
    html = html.replace('</div>', '\n\n')
    html = html.replace('<br>', '\n\n')
    soup = BeautifulSoup(html, 'html.parser')
    return agregarSaltos(soup.text)
    
