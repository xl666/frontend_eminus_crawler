from bd import models
import datetime
import front_end.settings as settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
from front_end import settings
import requests
from front_end import excepciones
import json

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def dejar_pasar_peticion_login(request):
    ip = get_client_ip(request)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        registro = models.IPs.objects.get(ip=ip)
    except: # la ip nunca ha hecho peticiones
        nuevoRegistroIP = models.IPs(ip=ip, ultima_peticion=timestamp, intentos=1)
        nuevoRegistroIP.save()
        return True
    diferencia = (timestamp - registro.ultima_peticion).seconds
    if diferencia > settings.VENTANA_TIEMPO_INTENTOS_LOGIN:
        registro.ultima_peticion = timestamp
        registro.intentos=1
        registro.save()
        return True
    elif settings.INTENTOS_LOGIN > registro.intentos:
        registro.ultima_peticion = timestamp
        registro.intentos = registro.intentos+1
        registro.save()
        return True
    else:
        registro.ultima_peticion = timestamp
        registro.intentos = registro.intentos+1
        registro.save()
        return False
        

def cifrar(mensaje, llave_aes, iv):
    aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv),
                       backend=default_backend())
    cifrador = aesCipher.encryptor()    
    cifrado = cifrador.update(mensaje)
    cifrador.finalize()
    return cifrado

def descifrar(cifrado, llave_aes, iv):
    aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv),
                       backend=default_backend())
    descifrador = aesCipher.decryptor()
    plano = descifrador.update(cifrado)
    descifrador.finalize()
    return plano

def generar_llave():
    llave_aes = os.urandom(16)
    iv = os.urandom(16)
    return llave_aes, iv

def cifrar_credenciales(usuario, password, llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd):
    usuario_cifrado = cifrar(usuario.encode('utf-8'), llave_aes_usr, iv_usr)
    password_cifrado = cifrar(password.encode('utf-8'), llave_aes_pwd, iv_pwd)
    return usuario_cifrado, password_cifrado

def convertir_dato_base64(dato):
    return base64.b64encode(dato).decode('utf-8')

def convertir_base64_dato(dato_b64):
    return base64.b64decode(dato_b64)

def wrap_llaves(request, usuario, contra):
    llave_aes_usr, iv_usr = generar_llave()
    llave_aes_pwd, iv_pwd = generar_llave()
    usuario_cifrado, password_cifrado = cifrar_credenciales(usuario, contra, llave_aes_usr, iv_usr, llave_aes_pwd, iv_pwd)
    request.session['usuario'] = convertir_dato_base64(usuario_cifrado)
    request.session['password'] = convertir_dato_base64(password_cifrado)
    return (convertir_dato_base64(llave_aes_usr),
            convertir_dato_base64(iv_usr),
            convertir_dato_base64(llave_aes_pwd),
            convertir_dato_base64(iv_pwd))

def unwrap_llaves(request):
    llave_aes_usr_b64 = request.COOKIES.get('key1', '')
    iv_usr_b64 = request.COOKIES.get('key2', '')
    llave_aes_pwd_b64 = request.COOKIES.get('key3', '')
    iv_pwd_b64 = request.COOKIES.get('key4', '')
    if not llave_aes_usr_b64 or not iv_usr_b64 or not llave_aes_pwd_b64 or not iv_pwd_b64:
        return None
    usuario_cif_b64 = request.session.get('usuario', '')
    pwd_cif_b64 = request.session.get('password', '')    
    usuario_cif = convertir_base64_dato(usuario_cif_b64)
    pwd_cif = convertir_base64_dato(pwd_cif_b64)
    llave_aes_usr = convertir_base64_dato(llave_aes_usr_b64)
    llave_aes_pwd = convertir_base64_dato(llave_aes_pwd_b64)
    iv_usr = convertir_base64_dato(iv_usr_b64)
    iv_pwd = convertir_base64_dato(iv_pwd_b64)
    usuario = descifrar(usuario_cif, llave_aes_usr, iv_usr)
    pwd = descifrar(pwd_cif, llave_aes_pwd, iv_pwd)
    return usuario, pwd

def regresar_token_sesion():
    url_token = settings.URL_SERVICIOS + '/autenticacion/'
    data = {'username': settings.CLIENTE_SERVICIOS_USR, 'password': settings.CLIENTE_SERVICIOS_PWD}
    respuesta = requests.post(url_token, data=data)
    if respuesta.status_code != 200:
        raise TokenException('No se pudo recuperar el token: %s' % respuesta.status_code)
    else:
        diccionario = json.loads(respuesta.text)
        return diccionario['token']

def regresar_cursos(request, token, terminados=False):
    url_cursos = settings.URL_SERVICIOS + '/cursos/'
    usuario, password = unwrap_llaves(request)
    headers = {'Authorization': 'Token %s' % token, 'usuario-eminus': usuario.decode('utf-8'), 'password-eminus': password.decode('utf-8')}
    if terminados:
        headers['terminados'] = "true"
    respuesta = requests.get(url_cursos, headers=headers)
    if respuesta.status_code != 200:
        raise excepciones.CursosException('Hubo un error al querer recuperar los cursos: %s' % respuesta.status_code)
    else:
        cursos = json.loads(respuesta.text)
        if type(cursos) == type({}) and "Error" in cursos.keys():
            raise excepciones.CursosException('Hubo un error al querer recuperar los cursos: %s' % cursos.get('Error'))        
        return cursos

def iniciar_extraccion(request, token):
    ids = request.POST.get('ids', '')
    periodos = request.POST.get('periodos', '')
    nombres = request.POST.get('nombres', '')
    terminados = request.POST.get('terminados', False)
    if terminados:
        terminados = True
    if not ids or not nombres or not periodos:
        raise excepciones.ExtraccionException('No hay cursos seleccionados')
    
    url_extraccion = settings.URL_SERVICIOS + '/extraer_evidencias/'
    usuario, password = unwrap_llaves(request)
    headers = {'Authorization': 'Token %s' % token, 'usuario-eminus': usuario.decode('utf-8'), 'password-eminus': password.decode('utf-8'), 'ids': ids, 'periodos': periodos, 'nombres': nombres}
    if terminados:
        headers['terminados'] = "true"
    respuesta = requests.get(url_extraccion, headers=headers)
    if respuesta.status_code != 200:
        raise excepciones.ExtraccionException('Hubo un error al intentar iniciar la extracción: %s' % respuesta.status_code)
    else:
        respuesta = json.loads(respuesta.text)
        if respuesta.get('Status', '') == 'OK':
            return respuesta.get('Job_id', 'nada')
        if respuesta.get('Error', ''):
            raise excepciones.ExtraccionException('Hubo un error al intentar iniciar la extracción: %s' % respuesta.get('Error'))
        return False
