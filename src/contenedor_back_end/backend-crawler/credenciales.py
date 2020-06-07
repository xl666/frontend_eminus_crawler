
import os
import getpass
import excepciones
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

def recuperar_credenciales_env():
    usuario = os.environ.get('usuario_eminus')
    pw = os.environ.get('password_eminus')
    if not usuario or not pw:
        raise excepciones.CredencialesException('No se encontraron las variables de entorno necesarias')
    return usuario, pw
    

