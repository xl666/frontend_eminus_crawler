import subprocess
import os
from servicios_back_end import settings
import json
from redis import Redis
from rq import Queue
from rq import get_current_job

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

def extraer(usuario, password, ids, path_salida, terminados=False, procesos=1):
    os.environ.putenv('usuario_eminus', usuario.strip())
    os.environ.putenv('password_eminus', password.strip())
    comando = f'python "{settings.PATH_BACK_END}/eminus_extractor.py" -e {ids} -d "{path_salida}" -p {procesos}'
    if terminados:
        comando += ' -t'    
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    os.environ.putenv('usuario_eminus', '')
    os.environ.putenv('password_eminus', '')
    salida = proceso.stdout.read(100)
    job = get_current_job()
    job.meta['info'] = ''
    job.meta['usuario'] = usuario
    while salida:
        job.meta['info'] += salida.decode('utf-8')
        job.save_meta()
        os.system('echo "%s" >> /tmp/log.txt' % salida.decode('utf-8'))
        salida = proceso.stdout.read(100)
    stdout, stderr = proceso.communicate()
    

def calendarizar_trabajo_extraccion(usuario, password, ids, path_salida, terminados=False):
    cola = Queue(connection=Redis())
    # dejar job en cola maximo un dia, el resultado maximo un dia, el job puede tardar hasta dos horas en ejecucion
    cola.enqueue(extraer, usuario, password, ids, path_salida, terminados, result_ttl=86400, ttl=86400, job_timeout=7200)
    
