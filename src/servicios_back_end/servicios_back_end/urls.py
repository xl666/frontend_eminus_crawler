"""servicios_back_end URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from backend_crawler.views import *
from rest_framework.authtoken import views

urlpatterns = [
    path('cursos/', curso_list),
    path('extraer_evidencias/', extraer_evidencias),
    path('trabajos_terminados/', regresar_historial_extracciones),
    path('trabajos_actuales/', regresar_extracciones_actuales),
    path('autenticacion/', views.obtain_auth_token),
]
