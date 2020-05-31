from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
import json
from backend_crawler import back_end
from servicios_back_end import settings

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def curso_list(request):
    if request.method == 'GET':
        usuario = request.headers.get('usuario-eminus', '')
        password = request.headers.get('password-eminus', '')
        if not usuario or not password:
            return Response({'Error': 'No se tiene usuario y password'})
        terminados = False
        if request.headers.get('terminados', None):
            terminados = True
        datos = back_end.regresar_cursos(usuario, password, terminados)
        if not datos:
            return Response({'Error': 'No se pudieron recuperar los datos'})
        return Response(datos)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def extraer_evidencias(request):
    if request.method == 'GET':
        usuario = request.headers.get('usuario-eminus', '')
        password = request.headers.get('password-eminus', '')
        ids = request.headers.get('ids', '')
        periodos = request.headers.get('periodos', '')
        nombres = request.headers.get('nombres', '')
        if not usuario or not password:
            return Response({'Error': 'No se tiene usuario y password'})
        if not ids or not periodos or not nombres:
            return Response({'Error': 'No se tiene informacion para extraer'})
        terminados = False
        if request.headers.get('terminados', None):
            terminados = True
    job_id = back_end.calendarizar_trabajo_extraccion(usuario, password, ids, periodos, nombres, settings.MEDIA_DIR, terminados)
    return Response({'Status': 'OK', 'Job_id': job_id})
