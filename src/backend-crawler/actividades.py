import cursos
import entregas

URL_ACTIVIDADES = 'https://eminus.uv.mx/eminus/actividades/centroActividades.aspx'
URL_ACTIVIDADES_ALUMNOS = 'https://eminus.uv.mx/eminus/Evaluacion/IntegrantesActividades.aspx'
URL_ACTIVIDAD_DETALLE = 'https://eminus.uv.mx/eminus/actividades/RevisionActividad.aspx'
URL_DESCARGA_RESPUESTA = 'https://eminus.uv.mx/eminus/Recursos.aspx?id=%s&tipo=1'

def ir_a_actividades(driver):
    entregas.ir_a_entregas(driver, cursos.URL_MAIN, 'tileActividades', URL_ACTIVIDADES)
    

def regresar_actividades(driver):
    return entregas.regresar_entregas(driver, URL_ACTIVIDADES, 'slActividad')


def get_nombre_actividad(driver, actividad):
    return entregas.get_nombre_entrega(driver, actividad, URL_ACTIVIDADES)


def ver_actividades(driver, actividades):
    return entregas.ver_entregas(driver, actividades, URL_ACTIVIDADES)

def ir_a_actividad(driver, actividad):
    entregas.ir_a_entrega(driver, actividad, URL_ACTIVIDADES)

def regresar_alumnos_contestaron_actividad(driver, grupo=False):
    return entregas.regresar_alumnos_contestaron_entrega(driver, URL_ACTIVIDADES_ALUMNOS, grupo)
        

def ir_a_respuesta_alumno(driver, alumno):
    entregas.ir_a_respuesta_alumno(driver, alumno, URL_ACTIVIDADES_ALUMNOS)
    

def regresar_texto_respuesta_alumno(driver):
    return entregas.regresar_texto_respuesta_alumno(driver, URL_ACTIVIDAD_DETALLE)


def regresar_enlaces_archivos_respuesta_alumno(driver):
    return entregas.regresar_enlaces_archivos_respuesta_alumno(driver, URL_ACTIVIDAD_DETALLE)


def crear_descripcion_actividad(driver, ruta_salida):
    entregas.crear_descripcion_entrega(driver, ruta_salida, URL_ACTIVIDADES_ALUMNOS)

    
def extraer_respuestas_actividad(driver, actividad, ruta_salida, grupo=False):
    entregas.extraer_respuestas_entrega(driver, actividad, ruta_salida, URL_ACTIVIDADES, URL_ACTIVIDADES_ALUMNOS, URL_ACTIVIDAD_DETALLE, 'Actividad', grupo)


def extraer_respuestas_actividades_curso(driver, ruta_salida):
    entregas.extraer_respuestas_entregas_curso(driver, ruta_salida, URL_ACTIVIDADES, URL_ACTIVIDADES_ALUMNOS, URL_ACTIVIDAD_DETALLE, 'Actividad', 'slActividad')
