
import excepciones
from sys import exit

def manejar_errores_credenciales(fun):
    def interna(*args, **kwargs):
        try:
            fun(*args, **kwargs)
        except excepciones.CredencialesException as e:
            print('{"Error": "%s"}' % e.__str__())
            return
        except Exception as e:
            print('{"Error": "%s"}' % e.__str__())
            return
    return interna
