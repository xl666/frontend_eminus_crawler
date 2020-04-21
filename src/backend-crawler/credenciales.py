
import os
import getpass
import excepciones
import cifrado
import sys

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
# La ruta de ejecución cambia en un paquete frozen de pyinstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)

SALT = 'x_39'

def guardar_credenciales(mensaje):
    try:
        with open('%s/%s' % (BASE_DIR, 'credenciales.cif'), 'wb') as archivo:
            archivo.write(mensaje)
    except:
        raise excepciones.CredencialesException('No se pudo crear archivo de credenciales en %s/%s' % (BASE_DIR, 'credenciales.cif'))

def recuperar_credenciales():
    try:
        with open('%s/%s' % (BASE_DIR, 'credenciales.cif'), 'rb') as archivo:
            contenido = archivo.read()
            password = getpass.getpass('Frase para recuperar credenciales: ')
            mensaje = cifrado.descifrar(contenido, password, SALT)
            mensaje = mensaje.decode('utf-8')
            usuario, pw = mensaje.split(':')
            return usuario, pw
    except FileNotFoundError as err:
        print(err)
        raise excepciones.CredencialesException('No se encontró el archivo credenciales.cif')
    except Exception as err:
        raise excepciones.CredencialesException('Es posible que la frase dada no coincida')
