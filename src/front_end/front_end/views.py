
from django.template import Template, Context
from django.shortcuts import render, redirect
from bd import models
import front_end.back_end as back_end




def login(request):
    t = 'login.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        if back_end.dejar_pasar_peticion_login(request):
            #hacer chequeo de credenciales
            return render(request, t, {'errores': 'Todo OK'})
        else:
            return render(request, t, {'errores': 'Demasiados intentos fallidos'})
            

