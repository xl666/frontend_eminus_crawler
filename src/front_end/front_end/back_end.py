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

def unwrap_llaves(request, llave_aes_usr_b64, iv_usr_b64, llave_aes_pwd_b64, iv_pwd_b64):
    usuario_cif_b64 = request.session.get('usuario', '')
    pwd_cif_b64 = request.session.get('password', '')
    if not usuario_cif or not pwd_cif:
        return None
    usuario_cif = convertir_base64_dato(usuario_cif_b64)
    pwd_cif = convertir_base64_dato(pwd_cif_b64)
    llave_aes_usr = convertir_base64_dato(llave_aes_usr_b64)
    llave_aes_pwd = convertir_base64_dato(llave_aes_pwd_b64)
    iv_usr = convertir_base64_dato(iv_usr_b64)
    iv_pwd = convertir_base64_dato(iv_pwd_b64)
    usuario = descifrar(usuario_cif, llave_aes_usr, iv_usr)
    pwd = descifrar(usuario_cif, llave_aes_pwd, iv_pwd)
    return usuario, pwd
