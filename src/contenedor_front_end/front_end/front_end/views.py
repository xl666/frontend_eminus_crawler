
from django.template import Template, Context
from django.shortcuts import render, redirect
from bd import models
import front_end.back_end as back_end
from front_end.decoradores import *
from front_end import excepciones
from django.http import JsonResponse

def login(request):
    t = 'login.html'
    if request.method == 'GET' and not request.session.get('logueado', False):
        errores = request.session.get('errores', None)
        request.session['errores'] = None
        return render(request, t, {'errores': errores})
    elif request.method == 'GET':
        return redirect('listar_cursos')
    elif request.method == 'POST' and not request.session.get('logueado', False):
        if back_end.dejar_pasar_peticion_login(request):

            usuario = request.POST.get('usuario', '')
            contra = request.POST.get('password', '')

            llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd = back_end.wrap_llaves(request, usuario, contra)

            respuesta = redirect('listar_cursos')
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
    try:
        token = back_end.regresar_token_sesion()
    except excepciones.TokenException as err:
        request.session['logueado'] = False
        return redirect('logout')

    if request.method == 'GET':
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
            return redirect('logout')

        if terminados:
            cache = request.session.get('cache_cursos_terminados', None)
            if not cache:
                request.session['cache_cursos_terminados'] = cursos
        else:
            cache = request.session.get('cache_cursos_actuales', None)
            if not cache:
                request.session['cache_cursos_actuales'] = cursos
        
        return render(request, t, {'cursos': cursos, 'terminados': terminados})

    elif request.method == 'POST':
        try:
            respuesta = back_end.iniciar_extraccion(request, token)
            request.session['job_id'] = respuesta
            return redirect('info_extraccion')
        except excepciones.ExtraccionException as err:
            request.session['errores'] = err.__str__()
            request.session['logueado'] = False
            return redirect('logout')


@esta_logueado
def info_extraccion(request):
    if request.method == 'GET':
        t = 'info_extraccion.html'
        try:
            token = back_end.regresar_token_sesion()
        except excepciones.TokenException as err:
            request.session['logueado'] = False
            return redirect('logout')
        trabajos = back_end.regresar_trabajos_terminados(request, token)
        actuales = back_end.regresar_trabajos_actuales(request, token)
        return render(request, t, {'historial': trabajos, 'pendientes': actuales})


def acerca_de(request):
    return render(request, 'acerca.html', {'logueado': request.session.get('logueado', False)})


@esta_logueado
def logout(request):
    request.session.flush()
    respuesta = redirect('login')
    respuesta.delete_cookie('key1')
    respuesta.delete_cookie('key2')
    respuesta.delete_cookie('key3')
    respuesta.delete_cookie('key4')
    return respuesta


@esta_logueado
def generar_enlace_descarga(request):
    if request.method == 'GET':
        try:
            token = back_end.regresar_token_sesion()
        except excepciones.TokenException as err:
            request.session['logueado'] = False
            return redirect('logout')
        enlace = back_end.generar_descarga(request.GET.get("periodo", ""), request.GET.get("nombre", ""), request, token)
        respuesta = {'enlace': enlace}
        return JsonResponse(respuesta)
    return JsonResponse({})
