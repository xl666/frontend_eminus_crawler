import subprocess
import os
from servicios_back_end import settings
import json

def regresar_cursos(usuario, password, terminados=False):
    os.environ.putenv('usuario_eminus', usuario.strip())
    os.environ.putenv('password_eminus', password.strip())
    comando = f'python "{settings.PATH_BACK_END}/eminus_extractor.py" -l'
    if terminados:
        comando += ' -t'    
    salida = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = salida.communicate()
    os.environ.putenv('usuario_eminus', '')
    os.environ.putenv('password_eminus', '')
    if stderr or not stdout:
        return None
    return json.loads(stdout)

