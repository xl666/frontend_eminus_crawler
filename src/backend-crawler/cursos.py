import excepciones
import evaluaciones
import actividades
import almacenamiento
import salidas

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import datetime

URL_MAIN = 'https://eminus.uv.mx/eminus/PrincipalEminus.aspx'
mes_mapping = {'Ene': 1, 'Feb': 2, 'Mar': 3, 'Abr': 4, 'May': 5,
               'Jun': 6, 'Jul': 7, 'Ago': 8, 'Sep': 9, 'Oct': 10,
               'Nov': 11, 'Dic': 12}


def ciclar_cursos_hasta(driver, etiqueta):
    tipo_listado = driver.find_element_by_id('lbltipoCurso')
    if not tipo_listado.text == etiqueta:
        izquierda = driver.find_element_by_id('flechaIzq')
        while not tipo_listado.text == etiqueta:
            anterior = tipo_listado.text
            izquierda.click()
            try:
                WebDriverWait(driver, 10).until(
                    lambda useless: anterior != tipo_listado.text)
            except:
                raise excepciones.CursosException('No se pudo ciclar los tipos de cursos')

def ciclar_cursos_hasta_vigentes(driver):
    ciclar_cursos_hasta(driver, 'Cursos vigentes')

def ciclar_cursos_hasta_terminados(driver):
    ciclar_cursos_hasta(driver, 'Cursos terminados')
            
def ir_a_cursos_vigentes(driver):
    if not driver.current_url == URL_MAIN:
        driver.get(URL_MAIN)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'lblTotalCursos')))
            time.sleep(1)
        except Exception as err:
            raise excepciones.CursosException('No se pudo regresar a los cursos vigentes')
    else:
        ciclar_cursos_hasta_vigentes()

def ir_a_cursos_terminados(driver):
    if not driver.current_url == URL_MAIN:
        ir_a_cursos_vigentes(driver)

    ciclar_cursos_hasta_terminados(driver)
            
        
def regresar_cursos(driver):
    assert driver.current_url == URL_MAIN
    cursos = driver.find_elements_by_class_name('contenedorCurso')
    resultado = {}
    for curso in cursos:
        perfil = curso.find_element_by_class_name('tipoPerfil').get_attribute("textContent")
        if perfil != 'Facilitador':
            continue
        resultado[curso.get_attribute('id')] = curso
    return resultado


def regresar_date_texto(texto):
    # Se recibe algo como 27/Jun/2018 - 17/Jul/2018
    # Solo se considera primera fecha
    fecha_texto = texto.split('-')[0].strip()
    partes = fecha_texto.split('/')
    return datetime.datetime(year=int(partes[2]), month=mes_mapping.get(partes[1]),
                              day=int(partes[0]))

def ordenar_cursos_fecha(fecha_cursos):
    llaves = fecha_cursos.keys()
    fechas = (regresar_date_texto(i) for i in llaves)
    pares = zip(llaves, fechas)
    ordenado = sorted(pares, key=lambda x: x[1])
    return (p[0] for p in ordenado)

def get_nombre_curso(curso):
    return curso.find_element_by_class_name('AreaTitulo').get_attribute("textContent")

def get_fecha_curso(curso):
    return curso.find_element_by_class_name('fechaCurso').get_attribute("textContent")

def ver_cursos(cursos):
    salida = ''
    fecha_cursos = {}
    for curso in cursos.values():
        # no se usa directo text porque no muestra hidden
        identificador = curso.get_attribute('id')
        nombre = get_nombre_curso(curso)
        fecha = get_fecha_curso(curso)

        nombre = 'id:%s %s' % (identificador, nombre)
        
        if not fecha in fecha_cursos.keys():
            fecha_cursos[fecha] = [nombre]
        else:
            fecha_cursos[fecha].append(nombre)
            
    for fe in ordenar_cursos_fecha(fecha_cursos):
        salida += '\n%s:\n' % fe
        for curso in fecha_cursos[fe]:
            salida += '     %s\n' % curso 
    return salida

def esta_seleccionado_curso(curso):
    return not 'white' in curso.get_attribute("style")

def get_curso_seleccionado(driver, cursos):
    if not driver.current_url == URL_MAIN:
        return None
    for pk in cursos.keys():
        if esta_seleccionado_curso(cursos[pk]):
            return pk

def esperar_carga_curso(driver, curso):
    try:
        WebDriverWait(driver, 10).until(
            lambda useless : esta_seleccionado_curso(curso))
    except:
        raise excepciones.CursosException('No se pudo tener acceso al curso')
        
def ir_a_curso(driver, curso):
    # si el curso esta paginado o en la parte de abajo, no se le puede dar click directo
    driver.execute_script("arguments[0].click();", curso)
    esperar_carga_curso(driver, curso)


def regresar_a_curso(driver, pk, terminados=False):
    driver.back() # siempre que se regresa eminus deselcciona el curso
    driver.refresh()
    assert driver.current_url == URL_MAIN
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'lblTotalCursos')))
        time.sleep(1)
    except:
        raise excepciones.CursosException('No se puede regresar al curso')
    if terminados:
        ir_a_cursos_terminados(driver)
    cursos = regresar_cursos(driver) # es necesario para evitar stale
    curso = cursos[pk]
    ir_a_curso(driver, curso)
    
    
def extraer_evidencias_curso(driver, cursos, pk, ruta, terminados=False):
    if not pk in cursos.keys():
        raise excepciones.CursosException('No existe el curso %s' % pk)
    curso = cursos[pk]
    ir_a_curso(driver, curso) 

    actividades.ir_a_actividades(driver)
    salida = almacenamiento.crear_ruta(ruta, 'actividades')
    actividades.extraer_respuestas_actividades_curso(driver, salida)
    regresar_a_curso(driver, pk, terminados)

    evaluaciones.ir_a_evaluaciones(driver)
    salida = almacenamiento.crear_ruta(ruta, 'evaluaciones')
    evaluaciones.extraer_respuestas_evaluaciones_curso(driver, salida)
    regresar_a_curso(driver, pk, terminados)

def extraer_evidencias_lista_cursos(driver, cursos, lista, ruta, terminados=False):
    for elemento in lista:
        curso = cursos[elemento]
        nombre = get_nombre_curso(curso)
        salidas.imprimir_salida('Extrayendo datos de curso: %s' % nombre, 1)
        salida = almacenamiento.crear_ruta(ruta, nombre)
        extraer_evidencias_curso(driver, cursos, elemento, salida, terminados)

        driver.get(URL_MAIN)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'lblTotalCursos')))
            time.sleep(1)
        except:
            raise excepciones.CursosException('No se pudo refrescar página de cursos')
        if terminados:
            ir_a_cursos_terminados(driver)
        cursos = regresar_cursos(driver) # evitar stale
