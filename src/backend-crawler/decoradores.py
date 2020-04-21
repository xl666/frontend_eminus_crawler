
import excepciones
from sys import exit

def manejar_errores_credenciales(fun):
    def interna(*args, **kwargs):
        try:
            fun(*args, **kwargs)
        except excepciones.CredencialesException as e:
            print(e)
            print('Asegurate de haber creado correctamente las credenciales mediante la opción -c o --credenciales')
            exit(1)
        except Exception as e:
            print(e)
            print('Asegurate de tener conexión a internet y de que las credenciales creadas fueron correctas')
            exit(1)
    return interna
