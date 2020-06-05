import login
import cursos as cr
import config
import credenciales
import evaluaciones

driver = config.configure()
usuario, password = credenciales.recuperar_credenciales()
login.login(driver, usuario, password)
cr.ir_a_cursos_terminados(driver)
cursos = cr.regresar_cursos(driver)
cr.ir_a_curso(driver, cursos['69315'])
evaluaciones.ir_a_evaluaciones(driver)
evals = list(evaluaciones.regresar_evaluaciones(driver))
print(evaluaciones.get_nombre_evaluacion(driver, evals[0]))
evaluaciones.ir_a_evaluacion(driver, evals[0])
alumnos = list(evaluaciones.regresar_alumnos_contestaron_evaluacion(driver, True))
evaluaciones.ir_a_respuesta_alumno(driver, alumnos[0][1])
print(evaluaciones.regresar_enlaces_archivos_respuesta_alumno(driver))

