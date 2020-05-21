from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
import json

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def curso_list(request):
    if request.method == 'GET':
        datos_raw = '[{"periodo": "01/Feb/2020 - 31/Jul/2020", "id_eminus": "110099", "nombre": "EXPERIENCIA RECEPCIONAL (84198)"},{"periodo": "01/Feb/2020 - 31/Jul/2020", "id_eminus": "110100", "nombre": "PRUEBAS DE PENETRACION (84401)"},{"periodo": "01/Feb/2020 - 31/Jul/2020", "id_eminus": "110101", "nombre": "PROGRAMACION SEGURA (87361)"},{"periodo": "01/Feb/2020 - 31/Jul/2020", "id_eminus": "110102", "nombre": "CRIPTOGRAFIA (89705)"}]'
        datos = json.loads(datos_raw) 
        return Response(datos)
