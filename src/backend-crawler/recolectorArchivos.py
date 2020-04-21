
import asyncio
import aiohttp
import aiofiles
from aiohttp import ClientSession
import multiprocessing

import login
import credenciales
import config
import salidas


COLA_MENSAJES = multiprocessing.Queue()

def extraer_cookies(usuario, password):
    driver = config.configure()
    login.login(driver, usuario, password)
    all_cookies = driver.get_cookies()
    cookies = {}  
    for s_cookie in all_cookies:
        cookies[s_cookie["name"]] = s_cookie["value"]
    driver.close()
    return cookies

class Despachador(multiprocessing.Process):
    def __init__(self, usuario, password):
        self.loop = asyncio.new_event_loop()
        self.cookies = extraer_cookies(usuario, password)
        self.semaforo = asyncio.Semaphore(config.MAX_DOWNLOAD_CONNECTIONS)
        multiprocessing.Process.__init__(self)


    async def descargar(self, url, ruta):
        #salidas.imprimir_salida(f'Descargando en {ruta}', 4)
        async with self.semaforo:
            async with ClientSession(cookies=self.cookies) as session:
                async with session.get(url=url) as respuesta:
                    datos = await respuesta.read()
                    async with aiofiles.open(ruta, 'wb') as archivo:
                        await archivo.write(datos)
        #salidas.imprimir_salida(f'Se terminó de descargar en {ruta}', 4)
        
    def calendarizar_descargas(self):
        while True:
            url, ruta = COLA_MENSAJES.get()
            if url == 'exit':
                break
            #self.loop.create_task(self.descargar(url, ruta))
            asyncio.run_coroutine_threadsafe(self.descargar(url, ruta), loop=self.loop)
        self.loop.stop()


    async def wrapper(self):
        await self.loop.run_in_executor(None, self.calendarizar_descargas)

    def flush_tasks(self):
        for task in asyncio.Task.all_tasks(loop=self.loop):
            self.loop.run_until_complete(task)

    
    def run(self):
        #self.loop.set_debug(True)
        self.loop.create_task(self.wrapper())
        try:
            self.loop.run_forever()
            self.flush_tasks()
        except:
            pass
        finally:
            self.loop.close()

