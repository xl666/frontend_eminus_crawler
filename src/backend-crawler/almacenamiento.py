
import excepciones
import recolectorArchivos

import os

def crear_ruta(ruta_base, sub_dir):
    if '/' in sub_dir:
        sub_dir = sub_dir.replace('/', '-')
    ruta = '%s/%s' % (ruta_base, sub_dir)
    try:            
        os.mkdir(ruta)
        return ruta
    except FileExistsError:
        if not os.path.isdir(ruta):
            raise excepciones.RutaException('No se puede crear directorio para guardar archivos de alumno, la ruta ya existe y no es directorio:%s' % ruta)
        raise excepciones.RutaException('No se puede crear directorio %s, ya existe' % ruta)
    except Exception:
        raise excepciones.RutaException('No se puede crear directorio para guardar archivos de alumno')


def guardar_archivo(path, contenido):
    try:
        with open(path, 'w') as archivo:
            archivo.write(contenido)
    except:
        raise excepciones.RutaException('Hubo un problema al guardar %s' % path)
    
def guardar_enlace(enlace, ruta):
    nombre, url = enlace
    salida = '%s/%s' % (ruta, nombre)
    recolectorArchivos.COLA_MENSAJES.put((url, salida))
