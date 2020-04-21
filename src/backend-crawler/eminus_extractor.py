#!/usr/bin/env python3

import os
import sys
import getopt
import getpass
from sys import exit
import time

import login 
import cursos as cr
import config
import excepciones
import cifrado
import decoradores
import credenciales
import multiprocessing
import salidas
import recolectorArchivos

def modo_uso():
    print('eminus_extractor.py [OPCIONES]')
    print('Opciones:')
    print('    -h, --help: ver esta ayuda')
    print('    -c, --credenciales: establecer credenciales en modo interactivo, es necesario realizar este paso antes de usar la herramienta')
    print('    -l, --listar: listar cursos (por defecto vigentes) mostrando ids')
    print('    -t, --terminados: activar modo cursos terminados (por defecto se usan vigentes)')
    print('    -d valor, --directorio=valor: opcional, directorio de salida (debe existir), por defecto directorio actual')
    print('    -e valor, --evidencias=valor: lista de ids de cursos a extraer evidencias')
    print('       se sigue el formato id1,id2,...,idn  sin espacios')
    print('    -p valor, --procesos valor: número de procesos (por defecto 1) paralelos/concurrentes.\n       Sólo se puede explotar cuando se extraen evidencias de varios cursos simultaneamente.\n       Se debe considerar que entre más procesos se utiliza se necesitará más memoria')
    print('    ')

    print('')
    print('Ejemplos de uso:')
    print('')
    print('Configurar credenciales:')
    print('    eminus_extractor -c')
    print('')
    print('Listar cursos terminados:')
    print('    eminus_extractor -l -t')
    print('')
    print('Extraer evidencias de un curso vigente:')
    print('    eminus_extractor -e 1000 -d /tmp/evidencias')
    print('')
    print('Extraer evidencias de tres cursos terminados:')
    print('    eminus_extractor -e 1000,2000,3000 -t -d /tmp/evidencias')
    print('Extraer evidencias de tres cursos terminados con tres procesos paralelos:')
    print('    eminus_extractor -e 1000,2000,3000 -t -d /tmp/evidencias -p 3')

def validar_ids(cadena):
    partes = cadena.split(',')
    for elemento in partes:
        if not elemento.isnumeric():
            return False
    return True

def validar_combinaciones(opcionC,  opcionL, opcionE, opcionD):
    if opcionC and True in (opcionL, opcionE, opcionD):
        return False
    if opcionL and True in (opcionC, opcionE, opcionD):
        return False
    
    return True

@decoradores.manejar_errores_credenciales
def crear_credenciales():
    usuario = input('Usuario eminus: ')
    password1 = getpass.getpass('Contraseña eminus: ')
    password2 = getpass.getpass('Repetir contraseña eminus: ')
    pw1 = getpass.getpass('Frase para recuperar credenciales: ')
    pw2 = getpass.getpass('Repetir frase: ')
    if password1 != password2 or pw1 != pw2:
        raise excepciones.CredencialesException('Los passwords no concuerdan')
    if ':' in usuario or ':' in password1:
        raise excepciones.CredencialesException('No se puede usar el caracter :')
    mensaje = cifrado.cifrar('%s:%s' % (usuario, password1), pw1, credenciales.SALT)
    credenciales.guardar_credenciales(mensaje)


@decoradores.manejar_errores_credenciales
def listar_cursos(terminados=False):
    driver = config.configure()
    usuario, password = credenciales.recuperar_credenciales()
    login.login(driver, usuario, password)
    if terminados:
        cr.ir_a_cursos_terminados(driver)
    cursos = cr.regresar_cursos(driver)
    print(cr.ver_cursos(cursos))

def run_process(terminados, idCurso, directorio, usuario, password, color=salidas.colores[0]):
    driver = config.configure()
    salidas.color_default = color
    login.login(driver, usuario, password)
    if terminados:
        cr.ciclar_cursos_hasta_terminados(driver)
    cursos = cr.regresar_cursos(driver)
    try:
        cr.extraer_evidencias_lista_cursos(driver, cursos, [idCurso], directorio, terminados)
    except KeyError as e:
        print('El id dado %s no existe, aseguráte de no estar usando el nrc, lista opciones de ids con -l o --listar, si es un curso terminado aseguráte de activar la opción -t' % e)
        exit(1)
    finally:
        driver.close()
    salidas.imprimir_salida('Fin de extracción')
    
@decoradores.manejar_errores_credenciales
def extraer_evidencias(terminados, evidencias, directorio, procesos=1):
    tiempo1 = time.time()
    usuario, password = credenciales.recuperar_credenciales()
    despachador = recolectorArchivos.Despachador(usuario, password)
    despachador.start()
    with multiprocessing.Pool(procesos) as pool:
        pool.starmap(run_process, [(terminados, evidencias[i],
                                    directorio, usuario,
                                    password,
                                    salidas.colores[i+1 % len(salidas.colores)])
                                   for i in range(len(evidencias))])
    recolectorArchivos.COLA_MENSAJES.put(('exit','exit'))
    despachador.join()
    tiempo2 = time.time()
    print('Extracción finalizada en {:.2f} segundos'.format(tiempo2 - tiempo1))
    
if __name__ == '__main__':

    if len(sys.argv) < 2:
        modo_uso()
        exit(0)
        
    try:
        options, remainder = getopt.getopt(sys.argv[1:], 'hcltd:e:p:', ['help', 'credenciales', 'listar', 'terminados', 'directorio=', 'evidencias=', 'procesos='])
    except:
        modo_uso()
        exit(1)

    if remainder:
        modo_uso()
        exit(1)
    
    terminados = False
    directorio = '.'
    evidencias = []
    procesos = 1

    opcionL = False
    opcionD = False
    opcionE = False
    opcionC = False
    opcionP = False
    
    for opcion, valor in options:
        if opcion in ('-h', '--help'):
            modo_uso()
            exit(0)
        if opcion in ('-c', '--credenciales'):
            opcionC = True
        if opcion in ('-l', '--listar'):
            opcionL = True
        if opcion in ('-t', '--terminados'):
            terminados = True
        if opcion in ('-d', '--directorio'):
            if not os.path.isdir(valor):
                print('%s no es un directorio válido' % valor)
                exit(1)
            opcionD = True
            directorio = valor
        if opcion in ('-p', '--procesos'):
            if not str.isdigit(valor) or int(valor) == 0 or int(valor) > config.MAX_PROCESS:
                print('El número de procesos debe ser un número entero mayor a cero y menor a %s' % config.MAX_PROCESS)
                exit(1)
            opcionP = True
            procesos = int(valor)
        if opcion in ('-e', '--evidencias'):
            if not validar_ids(valor):
                print('Los ids deben ser números enteros separados por coma, sin espacios')
                exit(1)
            opcionE = True
            evidencias = valor.split(',')

    if not validar_combinaciones(opcionC, opcionL, opcionE, opcionD):
        modo_uso()
        exit(1)

    if opcionL:
        listar_cursos(terminados)
        exit(0)

    if opcionE:
        extraer_evidencias(terminados, evidencias, directorio, procesos)      
        exit(0)

    if opcionC:
        crear_credenciales()
        exit(0)
