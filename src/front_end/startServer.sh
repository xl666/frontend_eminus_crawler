#!/bin/bash

for var in $(cat settings.env); do
    export "$var"
done

python manage.py runserver
