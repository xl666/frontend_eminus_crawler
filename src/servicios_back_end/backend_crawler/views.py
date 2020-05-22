from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
import json
from backend_crawler import back_end


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
        if request.META.get('terminados', None):
            terminados = True
        datos = back_end.regresar_cursos(usuario, password, terminados)
        if not datos:
            return Response({'Error': 'No se pudieron recuperar los datos'})
        return Response(datos)
