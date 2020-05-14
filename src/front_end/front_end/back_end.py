from bd import models
import datetime
import front_end.settings as settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

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
