from selenium import webdriver
import sys

salida = sys.stdout
MAX_PROCESS = 10 # Para el pull de procesos, no se recomienda más grande
MAX_DOWNLOAD_CONNECTIONS = 30 # limirar para evitar DOS en servidor

def configure():
    options = webdriver.ChromeOptions()
    #options.binary_location = '/usr/bin/chromium'
    options.add_argument('headless')
    options.add_argument('window-size=1800x1024')
    options.add_argument("--log-level=3");
    options.add_argument("--silent");
    driver = webdriver.Chrome(options=options)
    return driver
