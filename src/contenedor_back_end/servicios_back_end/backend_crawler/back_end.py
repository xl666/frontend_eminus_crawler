import subprocess
import os
import datetime
from servicios_back_end import settings
import json
from redis import Redis
from rq import Queue
from rq import get_current_job
from rq.job import Job

import django
django.setup()
from backend_crawler import models
from backend_crawler import serializers

MES_MAPPING = {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5,
               'Jun': 6, 'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10,
               'Nov': 11, 'Dic': 12}
def regresar_date_texto(texto):
    # Se recibe algo como 27/Jun/2018 - 17/Jul/2018
    # Solo se considera primera fecha
    fecha_texto = texto.split('-')[0].strip()
    partes = fecha_texto.split('/')
    return datetime.datetime(year=int(partes[2]), month=MES_MAPPING.get(partes[1]),
                              day=int(partes[0]))

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

def almacenar_trabajo_terminado(bitacora, id_eminus, usuario, periodo, nombre):
    resultados = models.Trabajos_terminados.objects.filter(idEminus=id_eminus, usuario=usuario, periodo=periodo, nombre=nombre)
    if len(resultados) == 0:
        models.Trabajos_terminados(bitacora=bitacora, idEminus=id_eminus, usuario=usuario, periodo=periodo, nombre=nombre).save()
    else:
        registro = resultados[0]
        registro.bitacora = bitacora
        registro.save()

def execute(cmd, path_bitacora):
    os.environ.putenv('LOG_PATH', path_bitacora)
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    salida, err = popen.communicate()
    if err:
        raise subprocess.CalledProcessError(err, cmd)
    return salida


def extraer(usuario, password, id_eminus, periodo, nombre, path_salida, terminados=False, procesos=1):
    os.environ.putenv('usuario_eminus', usuario.strip())
    os.environ.putenv('password_eminus', password.strip())
    comando = f'python "{settings.PATH_BACK_END}/eminus_extractor.py" -e {id_eminus} -d "{path_salida}" -p {procesos}'
    if terminados:
        comando += ' -t'    

    job = get_current_job()


    salida = 'ERROR'
    path_bitacora = settings.BITACORAS_DIR + '/%s' % job.id
    try:
        salida = execute(comando, path_bitacora)
    except Exception as err:
        with open(path_bitacora, 'ta') as archivo:
            archivo.write('\nERROR:\n')
            archivo.write(err.__str__())
        return err.__str__()
    finally:
        os.environ.putenv('usuario_eminus', '')
        os.environ.putenv('password_eminus', '')
        with open(path_bitacora, 'ta') as archivo:
            archivo.write('\nSalida:\n')
            if type(salida) != type(''):
                archivo.write(salida.decode('utf-8'))
            else:
                archivo.write(salida)
            archivo.write('\n')
        # Almacenar trabajos terminados con exito
        if not b'Error' in salida:
            almacenar_trabajo_terminado(job.id, id_eminus, usuario, periodo, nombre)

    return salida
    

def calendarizar_trabajo_extraccion(usuario, password, ids, periodos, nombres, path_salida, terminados=False):
    cola = Queue(connection=Redis(host=settings.REDIS_HOST))
    # dejar job en cola maximo un dia, el resultado maximo un dia, el job puede tardar hasta una hora en ejecucion
    jobs = []
    trabajos_activos = total_trabajos_ejecucion(usuario)
    if trabajos_activos >= settings.MAX_WORKS:
        return []
    for partes in zip(ids.split(','), periodos.split(','), nombres.split(',')):
        id_eminus, periodo, nombre = partes
        job = cola.enqueue(extraer, usuario, password, id_eminus, periodo, nombre, path_salida, terminados, result_ttl=86400, ttl=86400, job_timeout=3600, failure_ttl=86400)
        jobs.append(job.id)
        job.meta['usuario'] = usuario
        job.meta['periodo'] = periodo
        job.meta['nombre'] = nombre
        job.save_meta()
        trabajos_activos += 1
        if trabajos_activos >= settings.MAX_WORKS:
            return jobs
    return jobs

def encontrar_trabajos_cola(usuario, cola, estatus='En cola'):
    if cola.count == 0:
        return []
    resultados = []
    redis_conn = Redis(host=settings.REDIS_HOST)
    for id_job in cola.get_job_ids():
        trabajo = Job.fetch(id_job, redis_conn)
        if trabajo.meta.get('usuario', '') == usuario:
            resultados.append({'nombre': trabajo.meta['nombre'], 'periodo': trabajo.meta['periodo'], 'estatus': estatus})
    return resultados
    

def total_trabajos_ejecucion(usuario):
    redis_conn = Redis(host=settings.REDIS_HOST)
    q = Queue(connection=redis_conn)
    colas = encontrar_trabajos_cola(usuario, q, 'En cola') + encontrar_trabajos_cola(usuario, q.started_job_registry, 'Ejecutando')
    return len(colas)

def regresar_trabajos_actuales(usuario):
    redis_conn = Redis(host=settings.REDIS_HOST)
    q = Queue(connection=redis_conn)
    return encontrar_trabajos_cola(usuario, q, 'En cola') + encontrar_trabajos_cola(usuario, q.started_job_registry, 'Ejecutando') + encontrar_trabajos_cola(usuario, q.failed_job_registry, 'Error') + encontrar_trabajos_cola(usuario, q.finished_job_registry, 'Terminado')

def ordenar_trabajos_fecha(trabajos):
    fechas = [regresar_date_texto(t['periodo']) for t in trabajos]
    pares = zip(trabajos, fechas)
    ordenado = sorted(pares, key=lambda x: x[1])
    return [p[0] for p in ordenado]

def regresar_trabajos_terminados(usuario):
    trabajos = models.Trabajos_terminados.objects.filter(usuario=usuario)
    serializer = serializers.Trabajos_terminadosSerializer(trabajos, many=True)
    ordenados = ordenar_trabajos_fecha(serializer.data)
    return ordenados
