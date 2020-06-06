#!/bin/bash

export PATH=/code:$PATH

sleep 15

# verificar existencia de usuario cliente en BD


# Lanzar servidor
su -c 'python3 -u manage.py makemigrations' limitado
su -c 'python3 -u manage.py migrate' limitado

su -c 'gunicorn --bind :8000 servicios_back_end.wsgi:application --reload' limitado
