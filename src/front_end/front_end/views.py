
from django.template import Template, Context
from django.shortcuts import render, redirect
from bd import models
import front_end.back_end as back_end
from front_end.decoradores import *



USUARIO_PRUEBA = 'dummy'
CONTRA_PRUEBA = 'dummy'

def login(request):
    t = 'login.html'
    if request.method == 'GET' and not request.session.get('logueado', False):
        return render(request, t)
    elif request.method == 'GET':
        t = 'lista_cursos.html'
        return render(request, t)
    elif request.method == 'POST' and not request.session.get('logueado', False):
        if back_end.dejar_pasar_peticion_login(request):

            usuario = request.POST.get('usuario', '')
            contra = request.POST.get('password', '')

            if usuario == USUARIO_PRUEBA and contra == CONTRA_PRUEBA:
                request.session['logueado'] = True
                llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd = back_end.wrap_llaves(request, usuario, contra)

                respuesta = redirect('/listar_cursos')
                respuesta.set_cookie('key1', llave_aes_usr, httponly=True, samesite='Strict')
                respuesta.set_cookie('key2', iv_usr, httponly=True, samesite='Strict')
                respuesta.set_cookie('key3', llave_aes_pwd, httponly=True, samesite='Strict')
                respuesta.set_cookie('key4', iv_pwd, httponly=True, samesite='Strict') 
                return respuesta
            else:
                return render(request, t, {'errores': 'Usuario o contraseña incorrectos'})

        else:
            return render(request, t, {'errores': 'Demasiados intentos fallidos'})

@esta_logueado
def listar_cursos(request):
    t = 'lista_cursos.html'
    if request.method == 'GET':
        try:
            token = back_end.regresar_token_sesion()
        except TokenException as err:
            return redirect('/login/')
        try:
            cursos = back_end.regresar_cursos(request, token)
        except CursosException as err:
            return redirect('/login/')
        
        return render(request, t, {'cursos': cursos})    

@esta_logueado
def logout(request):
    request.session.flush()
    respuesta = redirect('/login')
    respuesta.delete_cookie('key1')
    respuesta.delete_cookie('key2')
    respuesta.delete_cookie('key3')
    respuesta.delete_cookie('key4')
    return respuesta
