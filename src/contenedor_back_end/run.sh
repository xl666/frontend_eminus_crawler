#!/bin/bash

export PATH=/code:$PATH
export DJANGO_SETTINGS_MODULE=servicios_back_end.settings
mkdir -p bitacoras_workers
mkdir -p bitacoras
mkdir -p media

sleep 15

for i in $(seq 1 $WORKERS); do
    ./run_worker.sh  &>> bitacoras_workers/worker${i}.txt &
done

su -c 'python3 -u manage.py makemigrations' limitado
su -c 'python3 -u manage.py migrate' limitado
su -c 'python3 crear_usuario.py' limitado
su -c 'gunicorn --bind :8000 servicios_back_end.wsgi:application --reload &> log.txt' limitado
#su -c 'python3 -u manage.py runserver 0.0.0.0:8000 &> log.txt' limitado
