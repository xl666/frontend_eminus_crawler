
from django.template import Template, Context
from django.shortcuts import render, redirect
from bd import models
import front_end.back_end as back_end
from front_end.decoradores import *
from front_end import excepciones

def login(request):
    t = 'login.html'
    if request.method == 'GET' and not request.session.get('logueado', False):
        errores = request.session.get('errores', None)
        request.session['errores'] = None
        return render(request, t, {'errores': errores})
    elif request.method == 'GET':
        return redirect('/listar_cursos')
    elif request.method == 'POST' and not request.session.get('logueado', False):
        if back_end.dejar_pasar_peticion_login(request):

            usuario = request.POST.get('usuario', '')
            contra = request.POST.get('password', '')

            llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd = back_end.wrap_llaves(request, usuario, contra)

            respuesta = redirect('/listar_cursos')
            respuesta.set_cookie('key1', llave_aes_usr, httponly=True, samesite='Strict')
            respuesta.set_cookie('key2', iv_usr, httponly=True, samesite='Strict')
            respuesta.set_cookie('key3', llave_aes_pwd, httponly=True, samesite='Strict')
            respuesta.set_cookie('key4', iv_pwd, httponly=True, samesite='Strict')
            request.session['logueado'] = True
            return respuesta

        else:
            return render(request, t, {'errores': 'Demasiados intentos fallidos'})

@esta_logueado
def listar_cursos(request):
    t = 'lista_cursos.html'
    if request.method == 'GET':
        try:
            token = back_end.regresar_token_sesion()
        except excepciones.TokenException as err:
            request.session['logueado'] = False
            return redirect('/logout/')
        cache = None
        try:
            terminados = request.GET.get('terminados', False)
            if terminados:
                cache = request.session.get('cache_cursos_terminados', None)
                terminados = True
            else:
                cache = request.session.get('cache_cursos_actuales', None)
            if not cache:
                cursos = back_end.regresar_cursos(request, token, terminados)
            else:
                cursos = cache
        except excepciones.CursosException as err:
            request.session['errores'] = err.__str__()
            request.session['logueado'] = False
            return redirect('/logout/')

        if terminados:
            cache = request.session.get('cache_cursos_terminados', None)
            if not cache:
                request.session['cache_cursos_terminados'] = cursos
        else:
            cache = request.session.get('cache_cursos_actuales', None)
            if not cache:
                request.session['cache_cursos_actuales'] = cursos

        
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
