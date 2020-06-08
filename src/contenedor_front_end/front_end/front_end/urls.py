"""front_end URL Configuration

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

from django.contrib import admin
from django.urls import path
from front_end.views import *
from front_end import settings

urlpatterns = [
    path('%slogin/' % settings.PATH_PREFIX, login, name='login'),
    path('%slistar_cursos/' % settings.PATH_PREFIX, listar_cursos, name='listar_cursos'),
    path('%sinfo_extraccion/' % settings.PATH_PREFIX, info_extraccion, name='info_extraccion'),
    path('%sacerca_de/' % settings.PATH_PREFIX, acerca_de, name='acerca_de'),
    path('%slogout/' % settings.PATH_PREFIX, logout, name='logout'),
]
