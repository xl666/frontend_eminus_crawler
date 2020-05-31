#!/bin/bash

for var in $(ccrypt -d -c settings.env.cpt); do
    export "$var"
done

python manage.py makemigrations
python manage.py migrate
