
from django.template import Template, Context
from django.shortcuts import render, redirect
from bd import models
import front_end.back_end as back_end
from front_end.decoradores import *


USUARIO_PRUEBA = 'dummy'
CONTRA_PRUEBA = 'dummy'

def inicio(request):
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
                llave_aes_usr, iv_usr = back_end.generar_llave()
                llave_aes_pwd, iv_pwd = back_end.generar_llave()
                usuario_cifrado, password_cifrado = back_end.cifrar_credenciales(usuario, contra, llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd)
                request.session['usuario'] = back_end.convertir_dato_base64(usuario_cifrado)
                request.session['password'] = back_end.convertir_dato_base64(password_cifrado)
                
                return render(request, 'lista_cursos.html', {'llave_aes_usr': back_end.convertir_dato_base64(llave_aes_usr), 'iv_usr': back_end.convertir_dato_base64(iv_usr), 'llave_aes_pwd': back_end.convertir_dato_base64(llave_aes_pwd), 'iv_pwd': back_end.convertir_dato_base64(iv_pwd)})
            else:
                return render(request, t, {'errores': 'Usuario o contraseña incorrectos'})

        else:
            return render(request, t, {'errores': 'Demasiados intentos fallidos'})

@esta_logueado
def listar_cursos(request):
    t = 'lista_cursos.html'
    if request.method == 'GET':
            return render(request, t)    

@esta_logueado
def logout(request):
    request.session.flush()
    return redirect('/inicio')
