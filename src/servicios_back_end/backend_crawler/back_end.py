import subprocess
import os
from servicios_back_end import settings
import json
from redis import Redis
from rq import Queue
from rq import get_current_job
from rq.job import Job


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

def execute(cmd, path_bitacora):
    os.environ.putenv('LOG_PATH', path_bitacora)
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    salida, err = popen.communicate()
    if err:
        raise subprocess.CalledProcessError(err, cmd)
    return salida

def extraer(usuario, password, id_eminus, path_salida, terminados=False, procesos=1):
    os.environ.putenv('usuario_eminus', usuario.strip())
    os.environ.putenv('password_eminus', password.strip())
    comando = f'python "{settings.PATH_BACK_END}/eminus_extractor.py" -e {id_eminus} -d "{path_salida}" -p {procesos}'
    if terminados:
        comando += ' -t'    

    job = get_current_job()
    job.meta['usuario'] = usuario
    job.save_meta()
    salida = 'ERROR'
    path_bitacora = settings.BITACORAS_DIR + '/%s' % job.id
    try:
        salida = execute(comando, path_bitacora)
    except Exception as err:
        return err.__str__()
    finally:
        os.environ.putenv('usuario_eminus', '')
        os.environ.putenv('password_eminus', '')


    return salida
    

def calendarizar_trabajo_extraccion(usuario, password, ids, path_salida, terminados=False):
    cola = Queue(connection=Redis())
    # dejar job en cola maximo un dia, el resultado maximo un dia, el job puede tardar hasta dos horas en ejecucion
    jobs = []
    for id_eminus in ids.split(','):
        job = cola.enqueue(extraer, usuario, password, id_eminus, path_salida, terminados, result_ttl=86400, ttl=86400, job_timeout=7200)
        jobs.append(job.id)
    return jobs
